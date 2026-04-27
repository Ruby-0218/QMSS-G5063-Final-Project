import pandas as pd
import yfinance as yf
from datetime import timedelta
import os
from transformers import pipeline

print("Starting the FULL & CORRECTED Data Pipeline...")

input_file = 'data/reddit_wsb.csv'
if not os.path.exists(input_file):
    print(f"Error: Could not find {input_file}. Ensure the raw Kaggle data is in the data folder.")
    exit()

# Load and Clean Raw Data
print("Loading raw Reddit data...")
df = pd.read_csv(input_file)
df['date'] = pd.to_datetime(df['timestamp']).dt.date
df['title'] = df['title'].fillna('')
df['body'] = df['body'].fillna('')
df['Text'] = df['title'] + " " + df['body']

# Target Tickers (Alignment with your Proposal)
target_tickers = {
    'NVDA': ['NVDA', 'NVIDIA'],
    'TSLA': ['TSLA', 'TESLA'],
    'AAPL': ['AAPL', 'APPLE'],
    'MSFT': ['MSFT', 'MICROSOFT'],
    'AMZN': ['AMZN', 'AMAZON'],
    'JPM':  ['JPM', 'CHASE'],
    'XOM':  ['XOM', 'EXXON']
}

def assign_ticker_strict(text):
    text_upper = str(text).upper()
    for ticker, keywords in target_tickers.items():
        for kw in keywords:
            if f" {kw} " in f" {text_upper} ":
                return ticker
    return None

print("Filtering posts based on your 7 proposal tickers...")
df['ticker'] = df['Text'].apply(assign_ticker_strict)
df_filtered = df.dropna(subset=['ticker']).copy()

# Balanced sampling for tidy charts
df_sample = df_filtered.groupby('ticker').apply(
    lambda x: x.sample(n=min(len(x), 1000), random_state=42)
).reset_index(drop=True).sort_values(by='date')

# AI Sentiment Scoring
print("Initializing AI Model (This takes 3-5 minutes)...")
sentiment_analyzer = pipeline("sentiment-analysis", model="ProsusAI/finbert")
mapping = {'positive': 1, 'negative': -1, 'neutral': 0}

df_sample['sentiment_score'] = df_sample['Text'].apply(
    lambda x: mapping.get(sentiment_analyzer(str(x)[:512])[0]['label'], 0)
)
df_sample['clean_text'] = df_sample['Text'].str.lower().replace(r'[^a-zA-Z0-9\s]', '', regex=True)

# Save Files (Fixing the message_volume bug)
print("Formatting and saving output files")

# 1. text_posts_sample.csv
df_sample['source'] = 'Reddit'
df_sample[['date', 'source', 'ticker', 'sentiment_score', 'Text', 'clean_text']].to_csv('data/text_posts_sample.csv', index=False)

# 2. sentiment_sample.csv (CRITICAL FIX: Adding message_volume)
# We calculate BOTH the average score AND the count of posts
sent_df = df_sample.groupby(['date', 'ticker']).agg(
    sentiment_score=('sentiment_score', 'mean'),
    message_volume=('Text', 'count')  # This is the column your website was missing!
).reset_index()

def assign_group(ticker):
    return 'Traditional Value' if ticker in ['JPM', 'XOM'] else 'High-Growth Tech'

sent_df['group'] = sent_df['ticker'].apply(assign_group)
sent_df['retail_sentiment'] = sent_df['sentiment_score']
sent_df['news_sentiment'] = 0 # Placeholder
sent_df.to_csv('data/sentiment_sample.csv', index=False)

# 3. prices_sample.csv (With the strftime fix)
print("Fetching stock prices from Yahoo Finance")
prices_list = []
for ticker in target_tickers.keys():
    try:
        p_data = yf.download(ticker, start="2020-09-29", end="2021-08-20", progress=False)
        if not p_data.empty:
            p_data = p_data.reset_index()
            for i in range(len(p_data)):
                prices_list.append({
                    'date': pd.to_datetime(p_data['Date'].iloc[i]).strftime('%Y-%m-%d'),
                    'ticker': ticker,
                    'group': assign_group(ticker),
                    'close': round(float(p_data['Close'].iloc[i]), 2),
                    'volume': int(p_data['Volume'].iloc[i])
                })
    except Exception as e:
        print(f"Warning: Failed to fetch {ticker}: {e}")

pd.DataFrame(prices_list).to_csv('data/prices_sample.csv', index=False)

# 4. network_edges_sample.csv (Detailed dummy data for Network Map)
print("Mining text for network relationships...")
keywords = ['AI', 'EV', 'MOON', 'HODL', 'DIP', 'CALL', 'PUT', 'EARNINGS', 'FED', 'INFLATION']
network_results = []

for _, row in df_sample.iterrows():
    text_upper = row['Text'].upper()
    current_ticker = row['ticker']
    
    for kw in keywords:
        if f" {kw} " in f" {text_upper} ":
            network_results.append({
                'source_node': current_ticker,
                'target_node': kw,
                'source_type': 'ticker',
                'target_type': 'keyword'
            })

# Weight
if network_results:
    network_df = pd.DataFrame(network_results)
    network_edges = network_df.groupby(['source_node', 'target_node', 'source_type', 'target_type']).size().reset_index(name='weight')
    
    max_w = network_edges['weight'].max()
    network_edges['weight'] = (network_edges['weight'] / max_w * 100).astype(int)
    
    network_edges.to_csv('data/network_edges_sample.csv', index=False)
else:
    pd.DataFrame(columns=['source_node', 'target_node', 'source_type', 'target_type', 'weight']).to_csv('data/network_edges_sample.csv', index=False)

print("Tickers, Prices, and Message Volume are all synchronized.")