import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from utils import load_prices, load_sentiment, build_merged_data, STOCK_GROUPS, ALL_TICKERS, rolling_corr, TICKER_COLORS

st.set_page_config(page_title="Market Dashboard", layout="wide")

st.markdown("""
<style>
    footer {visibility: hidden;}
    
    [data-testid="stSidebarNav"] ul li:first-child {
        display: none;
    }

    .block-container {
        padding-top: 3.5rem;
        padding-bottom: 6rem;
        padding-left: 5rem;
        padding-right: 5rem;
    }
    
    .stPlotlyChart {margin-bottom: 2rem;}
</style>
""", unsafe_allow_html=True)

st.title("Market Dashboard: Does Retail Hype Move Markets?")
st.markdown("""
This page starts with the market story. It places stock prices, sentiment, returns, volatility, and discussion volume side by side so users can see whether online attention rises during unstable market moments.

**How to use this page:** Choose a ticker and date range in the sidebar. Hover over each chart to compare exact dates, prices, sentiment values, and volatility measures.
""")

prices = load_prices()
sentiment = load_sentiment()
df = build_merged_data(prices, sentiment)

df["sentiment_score"] = df["sentiment_score"].fillna(0)

with st.sidebar:
    st.header("Filters")
    ticker = st.selectbox("Ticker", ALL_TICKERS, index=0)
    min_date, max_date = df["date"].min(), df["date"].max()
    date_range = st.date_input("Date range", [min_date, max_date], min_value=min_date, max_value=max_date)

if len(date_range) == 2:
    start_date, end_date = date_range
    df = df[(df["date"] >= str(start_date)) & (df["date"] <= str(end_date))]

stock_df = df[df["ticker"] == ticker].copy()
sent_col = "sentiment_score"
sentiment_source = "Combined sentiment"

col1, col2, col3, col4 = st.columns(4)
col1.metric("Selected Ticker", ticker)
col2.metric("Average Sentiment", f"{stock_df[sent_col].mean():.3f}")

avg_return = stock_df["return"].mean() * 100
avg_volatility = stock_df["volatility_7d"].mean() * 100
col3.metric("Average Daily Return", f"{avg_return:.2f}%", delta="Positive Trend" if avg_return > 0 else "Negative Trend")
col4.metric("Average 7-Day Volatility", f"{avg_volatility:.2f}%", delta="High Volatility" if avg_volatility > 3 else "Normal", delta_color="inverse")

current_color = TICKER_COLORS.get(ticker, "#1f77b4")

st.subheader("Price and Sentiment Over Time")
st.markdown("""
This chart asks whether the market price and the crowd's mood moved in the same periods. The price line shows the market outcome, while the sentiment line shows the daily tone of WallStreetBets discussion.

**How to use it:** Hover over the line chart to compare close price and sentiment on the same date.
""")

fig = go.Figure()
fig.add_trace(go.Scatter(x=stock_df["date"], y=stock_df["close"], mode="lines", name="Close Price", line=dict(color=current_color, width=3)))
fig.add_trace(go.Scatter(x=stock_df["date"], y=stock_df[sent_col], mode="lines", name=sentiment_source, yaxis="y2", line=dict(color="rgba(150, 150, 150, 0.6)", width=2, dash="dot")))
fig.update_layout(
    title=f"{ticker}: Price Action vs. {sentiment_source}",
    xaxis_title="Date",
    yaxis=dict(title="Close Price (USD)"),
    yaxis2=dict(title="Sentiment Score", overlaying="y", side="right"),
    hovermode="x unified",
    height=520
)
st.plotly_chart(fig, use_container_width=True)
st.markdown("""
**Key Takeaway:** Sentiment does not need to match prices every day to be useful. The more important pattern is whether sentiment spikes appear near periods of stronger returns or higher volatility.
""")

st.subheader("Rolling Correlation: Is the Relationship Stable?")
st.markdown("""
This chart shows whether sentiment and daily returns move together consistently or only during certain periods. A relationship that appears only in short bursts may suggest event-driven retail attention rather than a stable market rule.

**How to use it:** Look for periods above or below the zero line. Positive values mean sentiment and returns moved together; negative values mean they moved in opposite directions.
""")

corr_df = rolling_corr(df, ticker, window=14)
fig_corr = px.line(corr_df, x="date", y="rolling_corr", title=f"{ticker}: 14-Day Rolling Correlation Between Sentiment and Return", color_discrete_sequence=[current_color])
fig_corr.add_hline(y=0, line_dash="dot", line_color="gray")
st.plotly_chart(fig_corr, use_container_width=True)
st.markdown("""
**Key Takeaway:** Reddit sentiment is episodic. Quiet periods can push the correlation toward zero, while major discussion moments can temporarily make the relationship look much stronger.
""")

st.subheader("Sector Comparison: High-Growth vs. Value")
st.markdown("""
This comparison steps back from one ticker and asks whether the project groups behave differently. If high-growth stocks show higher volatility or sentiment intensity, it supports the idea that narrative-driven stocks may be more exposed to retail attention.
""")

group_col = "group_x" if "group_x" in df.columns else "group"
group_summary = df.groupby(group_col).agg(
    avg_sentiment=("sentiment_score", "mean"),
    avg_volatility=("volatility_7d", "mean"),
    avg_message_volume=("message_volume", "mean")
).reset_index()

fig_bar = px.bar(group_summary, x=group_col, y=["avg_sentiment", "avg_volatility"], barmode="group", title="Average Sentiment and Volatility by Stock Sector")
st.plotly_chart(fig_bar, use_container_width=True)
st.markdown("""
**Key Takeaway:** This chart is meant for relative comparison. The key question is whether the high-growth group shows a stronger sentiment-to-volatility pattern than the value-stock control group.
""")

st.subheader("Discussion Volume vs. Price Volatility")
st.markdown("""
Sometimes the amount of discussion matters more than whether the average tone is positive or negative. This scatter plot tests whether days with heavier WallStreetBets attention also tend to show higher short-term volatility.

**How to use it:** Hover over each point to see the ticker, date, and price. Points farther to the right represent higher discussion volume.
""")

fig_scatter = px.scatter(
    df[df["volatility_7d"].notna() & df["volume_7d"].notna()],
    x="volume_7d",
    y="volatility_7d",
    color="ticker",
    color_discrete_map=TICKER_COLORS,
    hover_data=["date", "close"],
    opacity=0.6,
    title="Discussion Volume vs. Price Volatility"
)
fig_scatter.update_layout(xaxis_title="7-Day Average Message Volume", yaxis_title="7-Day Price Volatility", yaxis_tickformat=".1%", height=500)
st.plotly_chart(fig_scatter, use_container_width=True)
st.markdown("""
**Key Takeaway:** Extreme emotion can matter, but attention itself is also important. High message volume can signal moments when a stock becomes part of a broader market conversation.
""")

st.subheader("Lead-Lag Cross-Correlation")
st.markdown("""
This chart asks a timing question: does sentiment appear before price movement, or does it mostly react after the market has already moved? The chart shifts sentiment backward and forward to compare it with daily returns.

**How to use it:** Negative lag values mean sentiment leads returns. Positive lag values mean sentiment follows returns.
""")

lags = range(-5, 6)
corr_values = []
for lag in lags:
    shifted_sent = stock_df[sent_col].shift(-lag)
    corr = stock_df["return"].corr(shifted_sent)
    corr_values.append(corr)

lag_df = pd.DataFrame({"Lag (Days)": lags, "Correlation": corr_values})
lag_df["Indicator Type"] = ["Leading (Sentiment Predicts)" if x < 0 else "Same Day" if x == 0 else "Lagging (Market Drives Sentiment)" for x in lag_df["Lag (Days)"]]

fig_lag = px.bar(
    lag_df,
    x="Lag (Days)",
    y="Correlation",
    color="Indicator Type",
    color_discrete_map={"Leading (Sentiment Predicts)": "#2ecc71", "Same Day": "#95a5a6", "Lagging (Market Drives Sentiment)": "#e74c3c"},
    title=f"{ticker}: Lead-Lag Correlation (Sentiment vs Daily Return)"
)
fig_lag.update_layout(xaxis_title="Lag in Days (Negative = Sentiment Leads Price)", yaxis_title="Correlation Coefficient", height=450)
st.plotly_chart(fig_lag, use_container_width=True)
st.markdown("""
**Key Takeaway:** If negative-lag bars are stronger, sentiment may be acting as an early signal. If positive-lag bars are stronger, retail discussion is more likely reacting to market movement that already happened.
""")
