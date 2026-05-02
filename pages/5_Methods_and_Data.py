import streamlit as st
import pandas as pd
from utils import load_prices, load_sentiment, build_merged_data

st.set_page_config(page_title="Methods and Data", layout="wide")
st.title("Methods and Data")

st.header("Data Sources")
st.markdown("""
Our final data strategy utilizes a robust historical dataset combined with offline natural language processing:

1. **Reddit r/wallstreetbets Dataset (Kaggle)**: A comprehensive dataset containing thousands of retail investor posts spanning from **September 2020 to August 2021**.
2. **Yahoo Finance (yfinance)**: Daily stock prices, trading volume, and returns precisely matched to our Reddit dataset's timeframe.
3. **Precomputed FinBERT Sentiment**: We used `ProsusAI/finbert`, an industry-standard NLP model, to score the sentiment of thousands of posts offline.
""")

st.header("Why 2020-2021 Reddit Data? (The Meme Stock Era)")
st.markdown("""
**The Challenge with Live APIs:**
Initially, we considered using live APIs (like Reddit API, NewsAPI, or StockTwits). However, free tiers heavily restrict historical data (often limited to the last 30 days) and cap request limits. 

**The Solution:**
We pivoted to a static, historical dataset from **2020-2021**. This specific timeframe is arguably the most important period in retail investing history, the **"Meme Stock Era"**. 
* It captures the extreme retail frenzy (e.g., the January 2021 GameStop short squeeze).
* It provides a perfect "stress test" environment to analyze whether extreme social media sentiment (hype, fear, FOMO) can effectively predict irrational stock market volatility.
""")

st.header("Sentiment & Data Pipeline")
st.markdown("""
To ensure the Streamlit dashboard loads instantly without forcing the user to wait for AI processing, we engineered an **Offline Data Pipeline** (`data_converter.py`).
""")

with st.expander("Click to view our Offline Pipeline Architecture"):
    st.code("""
    # Our Offline Data Pipeline Workflow:
    # 1. Load massive raw Reddit dataset (CSV)
    # 2. Filter posts by target tickers (NVDA, TSLA, AAPL, etc.)
    # 3. Perform deep text cleaning (Regex, lowercasing) for Keyword Clouds
    # 4. Feed text into FinBERT (Hugging Face) to generate Sentiment Scores (-1 to 1)
    # 5. Extract Co-occurrence Keywords for Network Mapping
    # 6. Synchronize dates and fetch corresponding yfinance stock prices
    # 7. Export lightweight, aggregated CSVs to power this Streamlit app
    """, language="python")

st.header("Visualizations Included")
st.markdown("""
The processed data powers the following interactive components:

* **Interactive Time-Series Dashboard**: Overlaying stock prices with message volume and sentiment.
* **Text Analysis & Word Cloud**: Extracting the most frequent terminology used during market hype.
* **Ticker-Keyword Network Map**: Visualizing the dynamic relationships between stocks and trending topics.
* **Event Shock Explorer**: Pinpointing specific dates of extreme market anomalies.
""")

st.header("Deployment Notes")
st.markdown("""
Because all AI processing is handled offline, this application is highly optimized for Streamlit Community Cloud:

1. The heavy `transformers` (FinBERT) library is removed from the live app's dependencies.
2. The app simply reads the pre-aggregated `data/` folder.
3. No external API keys or secrets are required for the live deployment, preventing rate-limit crashes during presentations.
""")

st.header("Methodological Limitations & Future Work")
st.markdown("""
In response to academic feedback, we acknowledge the following considerations for future iterations:
* **Prediction Markets (Kalshi / Polymarket):** Currently, we rely on unstructured social media text as a proxy for retail sentiment. Future models should incorporate betting data from prediction markets. Real-money odds provide a contrasting signal to social hype, helping filter "noise" from actual market conviction.
* **Data Normalization:** Message volume is subject to organic growth over time. For robust cross-sectional comparison, time-series volume metrics should be strictly normalized by trailing population growth or platform active user counts.
""")

st.markdown("---")
st.subheader("Reproducibility: Download Processed Data")
st.write("For open research and reproducibility, you can download the fully merged and pre-processed dataset here:")

try:
    prices = load_prices()
    sentiment = load_sentiment()
    df = build_merged_data(prices, sentiment)
    
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download Merged Dataset (CSV)",
        data=csv,
        file_name='market_sentiment_merged.csv',
        mime='text/csv',
    )
except Exception as e:
    st.info("Data files will be available for download once the application is fully deployed.")
