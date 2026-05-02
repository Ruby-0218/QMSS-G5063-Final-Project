import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from utils import load_prices, load_sentiment, build_merged_data, STOCK_GROUPS, ALL_TICKERS, rolling_corr, TICKER_COLORS

st.set_page_config(page_title="Market Dashboard", layout="wide")

# Storyline
st.title("Market Dashboard: Does Retail Hype Move Markets?")
st.markdown("""
**Executive Summary:** In the era of meme stocks, financial markets are no longer driven solely by fundamentals. 
This dashboard explores the relationship between asset prices and the digital "voice" of the crowd. 
Are social media sentiment spikes a lagging indicator of price action, or do they predict future volatility?
""")

prices = load_prices()
sentiment = load_sentiment()
df = build_merged_data(prices, sentiment)

# prevent rolling correlation being NA
df['sentiment_score'] = df['sentiment_score'].fillna(0)
df['retail_sentiment'] = df['retail_sentiment'].fillna(0)
df['news_sentiment'] = df['news_sentiment'].fillna(0)

with st.sidebar:
    st.header("Filters")
    ticker = st.selectbox("Ticker", ALL_TICKERS, index=0)
    min_date, max_date = df["date"].min(), df["date"].max()
    date_range = st.date_input("Date range", [min_date, max_date], min_value=min_date, max_value=max_date)
    sentiment_source = st.selectbox("Sentiment source", ["Combined sentiment", "Retail sentiment", "News sentiment"])

if len(date_range) == 2:
    start_date, end_date = date_range
    df = df[(df["date"] >= str(start_date)) & (df["date"] <= str(end_date))]

stock_df = df[df["ticker"] == ticker].copy()

if sentiment_source == "Retail sentiment":
    sent_col = "retail_sentiment"
elif sentiment_source == "News sentiment":
    sent_col = "news_sentiment"
else:
    sent_col = "sentiment_score"

col1, col2, col3, col4 = st.columns(4)
col1.metric("Selected Ticker", ticker)
col2.metric("Average Sentiment", f"{stock_df[sent_col].mean():.3f}")
col3.metric("Average Daily Return", f"{stock_df['return'].mean() * 100:.2f}%")
col4.metric("Average 7-Day Volatility", f"{stock_df['volatility_7d'].mean() * 100:.2f}%")

current_color = TICKER_COLORS.get(ticker, "#1f77b4")

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=stock_df["date"], y=stock_df["close"],
    mode="lines", name="Close Price",
    line=dict(color=current_color, width=3) 
))
fig.add_trace(go.Scatter(
    x=stock_df["date"], y=stock_df[sent_col],
    mode="lines", name=sentiment_source,
    yaxis="y2",
    line=dict(color="rgba(150,
