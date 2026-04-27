import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from utils import load_prices, load_sentiment, build_merged_data, STOCK_GROUPS, ALL_TICKERS, rolling_corr

st.set_page_config(page_title="Market Dashboard", layout="wide")
st.title("Market and Sentiment Dashboard")

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

st.markdown("""
This page compares market movement with sentiment. The main chart uses two axes because stock price and sentiment are measured on different scales.
""")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Selected ticker", ticker)
col2.metric("Average sentiment", f"{stock_df[sent_col].mean():.3f}")
col3.metric("Average daily return", f"{stock_df['return'].mean() * 100:.2f}%")
col4.metric("Average 7-day volatility", f"{stock_df['volatility_7d'].mean() * 100:.2f}%")

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=stock_df["date"], y=stock_df["close"],
    mode="lines", name="Close price"
))
fig.add_trace(go.Scatter(
    x=stock_df["date"], y=stock_df[sent_col],
    mode="lines", name=sentiment_source,
    yaxis="y2"
))
fig.update_layout(
    title=f"{ticker}: Price and Sentiment Over Time",
    xaxis_title="Date",
    yaxis=dict(title="Close price"),
    yaxis2=dict(title="Sentiment score", overlaying="y", side="right"),
    hovermode="x unified",
    height=520
)
st.plotly_chart(fig, use_container_width=True)

st.caption("Interpretation: sentiment peaks are not expected to perfectly match prices every day. The stronger question is whether sentiment spikes align with periods of elevated return or volatility.")

st.subheader("Rolling Correlation")
corr_df = rolling_corr(df, ticker, window=14)
fig_corr = px.line(
    corr_df,
    x="date",
    y="rolling_corr",
    title=f"{ticker}: 14-Day Rolling Correlation Between Sentiment and Return"
)
fig_corr.add_hline(y=0, line_dash="dot")
st.plotly_chart(fig_corr, use_container_width=True)

st.markdown("""
**Data Insight:** Unlike daily stock prices, Reddit sentiment is highly episodic. Retail investors tend to stay quiet during normal days (sentiment = 0) but show explosive engagement around key events. Therefore, rolling correlation may temporarily drop to zero during quiet periods, which accurately reflects the "hype-driven" nature of meme stocks.
""")

st.subheader("Sector Comparison")

group_col = "group_x" if "group_x" in df.columns else "group"

group_summary = df.groupby(group_col).agg(
    avg_sentiment=("sentiment_score", "mean"),
    avg_volatility=("volatility_7d", "mean"),
    avg_message_volume=("message_volume", "mean")
).reset_index()

fig_bar = px.bar(
    group_summary,
    x=group_col,
    y=["avg_sentiment", "avg_volatility"],
    barmode="group",
    title="Average Sentiment and Volatility by Stock Group"
)

st.plotly_chart(fig_bar, use_container_width=True)

st.markdown("""
**Design choice:** this page prioritizes comparison rather than showing raw market data only. The key visual task is to let users compare whether the high-growth group has stronger sentiment-volatility movement than the control group.
""")
