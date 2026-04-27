from pathlib import Path
import pandas as pd
import numpy as np
import streamlit as st

DATA_DIR = Path(__file__).parent / "data"

STOCK_GROUPS = {
    "High-Growth Tech": ["NVDA", "TSLA", "AAPL", "MSFT", "AMZN"],
    "Traditional Value": ["JPM", "XOM"]
}

ALL_TICKERS = STOCK_GROUPS["High-Growth Tech"] + STOCK_GROUPS["Traditional Value"]

@st.cache_data(show_spinner=False)
def load_prices():
    path = DATA_DIR / "prices_sample.csv"
    df = pd.read_csv(path, parse_dates=["date"])
    return df

@st.cache_data(show_spinner=False)
def load_sentiment():
    path = DATA_DIR / "sentiment_sample.csv"
    df = pd.read_csv(path, parse_dates=["date"])
    return df

@st.cache_data(show_spinner=False)
def load_text_posts():
    path = DATA_DIR / "text_posts_sample.csv"
    df = pd.read_csv(path, parse_dates=["date"])
    return df

@st.cache_data(show_spinner=False)
def load_network_edges():
    path = DATA_DIR / "network_edges_sample.csv"
    df = pd.read_csv(path)
    return df

@st.cache_data(show_spinner=False)
def load_events():
    path = DATA_DIR / "events_sample.csv"
    df = pd.read_csv(path, parse_dates=["event_date"])
    return df

def build_merged_data(prices, sentiment):
    df = prices.merge(sentiment, on=["date", "ticker"], how="left")
    df = df.sort_values(["ticker", "date"])
    df["return"] = df.groupby("ticker")["close"].pct_change()
    df["volatility_7d"] = df.groupby("ticker")["return"].rolling(7).std().reset_index(level=0, drop=True)
    df["sentiment_7d"] = df.groupby("ticker")["sentiment_score"].rolling(7).mean().reset_index(level=0, drop=True)
    df["volume_7d"] = df.groupby("ticker")["message_volume"].rolling(7).mean().reset_index(level=0, drop=True)
    return df

def get_group(ticker):
    for group, tickers in STOCK_GROUPS.items():
        if ticker in tickers:
            return group
    return "Other"

def normalized_series(s):
    if s.std() == 0 or pd.isna(s.std()):
        return s * 0
    return (s - s.mean()) / s.std()

def rolling_corr(df, ticker, window=14):
    tmp = df[df["ticker"] == ticker].copy()
    tmp["rolling_corr"] = tmp["return"].rolling(window).corr(tmp["sentiment_score"])
    return tmp

def sentiment_label(score):
    if score > 0.15:
        return "Bullish"
    if score < -0.15:
        return "Bearish"
    return "Neutral"
