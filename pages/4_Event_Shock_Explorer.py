import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils import load_prices, load_sentiment, load_events, build_merged_data, TICKER_COLORS

st.set_page_config(page_title="Event Shock Explorer", layout="wide")

st.markdown("""
<style>

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    .block-container {
        padding-top: 3.5rem; 
        padding-bottom: 6rem;
        padding-left: 5rem;
        padding-right: 5rem;
    }
    
    .stPlotlyChart {
        margin-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

st.title("Event Shock Explorer: Market Impact Analysis")

prices = load_prices()
sentiment = load_sentiment()
events = load_events()
df = build_merged_data(prices, sentiment)

st.markdown("""
**Storyline: Measuring the Impact of Shocks.** General correlations often mask the truth. This page employs an **Event Study framework** to isolate specific dates—such as product launches, short squeezes, or regulatory shifts—to see if they produced a statistically visible 'shock' in sentiment and price.
""")

event_name = st.selectbox("Select a significant market event:", events["event_name"].tolist())
event = events[events["event_name"] == event_name].iloc[0]

ticker = event["ticker"]
event_date = pd.to_datetime(event["event_date"])
current_color = TICKER_COLORS.get(ticker, "#1f77b4")

window = st.slider("Analysis Window (Days before and after)", 5, 30, 14)

tmp = df[df["ticker"] == ticker].copy()
tmp["date"] = pd.to_datetime(tmp["date"])
start_date = event_date - pd.Timedelta(days=window)
end_date = event_date + pd.Timedelta(days=window)
tmp = tmp[(tmp["date"] >= start_date) & (tmp["date"] <= end_date)]

st.subheader(f"Shock Metrics: {event_name} ({ticker})")
st.info(f"**Context:** {event['description']}")

before_event = tmp[tmp["date"] < event_date]
after_event = tmp[tmp["date"] >= event_date]

col1, col2, col3 = st.columns(3)

ret_before = before_event["return"].mean() * 100
ret_after = after_event["return"].mean() * 100
col1.metric("Post-Event Avg Return", f"{ret_after:.2f}%", delta=f"{ret_after - ret_before:.2f}% vs Pre-Event")

vol_before = before_event["volatility_7d"].mean() * 100
vol_after = after_event["volatility_7d"].mean() * 100
col2.metric("Post-Event Volatility", f"{vol_after:.2f}%", delta=f"{vol_after - vol_before:.2f}%", delta_color="inverse")

sent_before = before_event["sentiment_score"].mean()
sent_after = after_event["sentiment_score"].mean()
col3.metric("Post-Event Sentiment", f"{sent_after:.3f}", delta=f"{sent_after - sent_before:.3f}")

fig = go.Figure()

fig.add_trace(go.Scatter(
    x=tmp["date"], y=tmp["close"], 
    mode="lines+markers", 
    name="Close Price",
    line=dict(color=current_color, width=3)
))

fig.add_trace(go.Scatter(
    x=tmp["date"], y=tmp["sentiment_score"], 
    mode="lines", 
    name="Sentiment Score", 
    yaxis="y2",
    line=dict(color="rgba(150, 150, 150, 0.5)", dash="dot")
))

fig.add_shape(
    type="line", x0=event_date, x1=event_date, y0=0, y1=1,
    xref="x", yref="paper",
    line=dict(color="Red", width=2, dash="dashdot")
)

fig.add_annotation(
    x=event_date, y=1, xref="x", yref="paper",
    text="EVENT DATE", showarrow=True, arrowhead=2,
    bgcolor="red", font=dict(color="white")
)

fig.update_layout(
    title=f"Impact Visualizer: {ticker} Price & Sentiment Around {event_name}",
    xaxis_title="Date",
    yaxis=dict(title="Close Price (USD)", gridcolor="rgba(200,200,200,0.2)"),
    yaxis2=dict(title="Sentiment Score", overlaying="y", side="right", range=[-1, 1]),
    hovermode="x unified",
    template="plotly_white",
    height=500
)

st.plotly_chart(fig, use_container_width=True)

st.subheader("Raw Window Data")
st.dataframe(
    tmp[["date", "ticker", "close", "return", "volatility_7d", "sentiment_score", "message_volume"]].sort_values("date"),
    use_container_width=True,
    hide_index=True
)

st.markdown("""
**Methodological Note:** This 'Event Window' analysis is a standard quantitative tool used to detect **Abnormal Returns**. By isolating the days surrounding a shock, we can observe whether social media hype precedes the price movement or acts as an echo chamber in the following days.
""")
