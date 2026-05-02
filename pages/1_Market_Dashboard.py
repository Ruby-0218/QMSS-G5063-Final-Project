import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from utils import load_prices, load_sentiment, build_merged_data, STOCK_GROUPS, ALL_TICKERS, rolling_corr, TICKER_COLORS

st.set_page_config(page_title="Market Dashboard", layout="wide")

# storyline
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
    line=dict(color="rgba(150, 150, 150, 0.6)", width=2, dash="dot")
))
fig.update_layout(
    title=f"{ticker}: Price Action vs. {sentiment_source}",
    xaxis_title="Date",
    yaxis=dict(title="Close Price (USD)"),
    yaxis2=dict(title="Sentiment Score", overlaying="y", side="right"),
    hovermode="x unified",
    height=520
)
st.plotly_chart(fig, use_container_width=True)

st.caption("🔍 **Interpretation:** Sentiment peaks are not expected to perfectly match prices every day. The stronger question is whether sentiment spikes align with periods of elevated return or volatility.")

st.subheader("Rolling Correlation: Is the Relationship Stable?")
corr_df = rolling_corr(df, ticker, window=14)
fig_corr = px.line(
    corr_df,
    x="date",
    y="rolling_corr",
    title=f"{ticker}: 14-Day Rolling Correlation Between Sentiment and Return",
    color_discrete_sequence=[current_color] 
)
fig_corr.add_hline(y=0, line_dash="dot", line_color="gray")
st.plotly_chart(fig_corr, use_container_width=True)

st.markdown("""
**Data Insight:** Unlike daily stock prices, Reddit and retail sentiment is highly episodic. Retail investors tend to stay quiet during normal market days (sentiment ≈ 0) but show explosive engagement around key events. Therefore, rolling correlation may temporarily drop to near zero during quiet periods, which accurately reflects the "hype-driven" nature of these specific stocks.
""")

st.subheader("Sector Comparison: High-Growth vs. Value")

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
    title="Average Sentiment and Volatility by Stock Sector"
)
st.plotly_chart(fig_bar, use_container_width=True)

st.markdown("""
**Methodological Notes & Future Work:**
* **Design Choice:** This dashboard prioritizes relative comparison over pure numerical display. The key visual task is evaluating whether the "High-Growth/Meme" sector exhibits a stronger sentiment-to-volatility transmission mechanism than the traditional value control group.
* **Alternative Data Sources:** While our current model captures retail sentiment via text analysis, future iterations could incorporate prediction market data (e.g., **Kalshi, Polymarket**). Contrasting retail social hype with real-money betting odds could provide a more robust signal for impending price shocks.
""")

st.subheader("Deep Dive: Does 'Hype Volume' Drive Volatility?")
st.markdown("""
While sentiment direction (positive/negative) is noisy, the sheer **volume of discussion** might be a stronger indicator of market turbulence. 
The scatter plot below tests whether days with high message volume correlate with higher 7-day price volatility.
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

fig_scatter.update_layout(
    xaxis_title="7-Day Average Message Volume",
    yaxis_title="7-Day Price Volatility",
    yaxis_tickformat=".1%",
    height=500
)
st.plotly_chart(fig_scatter, use_container_width=True)
