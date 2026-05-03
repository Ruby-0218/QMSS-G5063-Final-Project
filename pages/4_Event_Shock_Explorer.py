import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils import load_prices, load_sentiment, load_events, build_merged_data, TICKER_COLORS

st.set_page_config(page_title="Event Shock Explorer", layout="wide")
st.markdown("""
<style>
    footer {visibility: hidden;}

    [data-testid="stSidebar"] {
        background-color: var(--secondary-background-color);
    }

    [data-testid="stSidebarNav"] ul li:first-child {
        display: none;
    }

    .block-container {
        padding-top: 3rem;
        padding-bottom: 5rem;
        padding-left: 5rem;
        padding-right: 5rem;
        max-width: 1280px;
    }

    h1 {
        color: var(--text-color);
        font-weight: 750;
        letter-spacing: -0.025em;
        margin-bottom: 0.6rem;
    }

    h2 {
        color: var(--text-color);
        font-weight: 700;
        margin-top: 2.2rem;
        padding-top: 0.6rem;
        border-top: 1px solid rgba(128, 128, 128, 0.22);
    }

    h3 {
        color: var(--text-color) !important;
        font-weight: 750 !important;
        font-size: 1.75rem !important;
        line-height: 1.25 !important;
        background-color: var(--secondary-background-color);
        border-left: 6px solid #2C7BE5;
        border-bottom: 1px solid rgba(128, 128, 128, 0.22);
        padding: 0.9rem 1.1rem !important;
        border-radius: 12px;
        margin-top: 2.4rem !important;
        margin-bottom: 1rem !important;
        box-shadow: 0 3px 10px rgba(31, 45, 61, 0.08);
    }

    p, li {
        font-size: 1.02rem;
        line-height: 1.65;
        color: var(--text-color);
    }

    .hero-card {
        background-color: var(--secondary-background-color);
        border: 1px solid rgba(128, 128, 128, 0.22);
        border-radius: 18px;
        padding: 1.6rem 1.8rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 14px rgba(31, 45, 61, 0.08);
    }

    .guide-box {
        background-color: var(--secondary-background-color);
        border-left: 5px solid #2C7BE5;
        padding: 1rem 1.2rem;
        border-radius: 10px;
        margin-top: 1rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 2px 8px rgba(44, 123, 229, 0.08);
        color: var(--text-color);
    }

    .key-box {
        background-color: var(--secondary-background-color);
        border-left: 5px solid #F5A623;
        padding: 0.9rem 1.1rem;
        border-radius: 10px;
        margin-top: 0.75rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 2px 8px rgba(245, 166, 35, 0.08);
        color: var(--text-color);
    }

    div[data-testid="stMetric"] {
        background-color: var(--secondary-background-color);
        border: 1px solid rgba(128, 128, 128, 0.22);
        padding: 1rem;
        border-radius: 14px;
        box-shadow: 0 3px 10px rgba(31, 45, 61, 0.08);
    }

    .stPlotlyChart {
        margin-top: 0.5rem;
        margin-bottom: 1.5rem;
    }
</style>
""", unsafe_allow_html=True)

def apply_plot_style(fig):
    fig.update_layout(
        template="plotly_white",
        font=dict(family="Arial", size=14, color="#2F3A45"),
        title_font=dict(size=18, color="#1F2D3D"),
        paper_bgcolor="white",
        plot_bgcolor="white",
        margin=dict(l=40, r=40, t=70, b=40),
    )
    return fig


st.title("Event Shock Explorer: When Sentiment Meets Market Events")
st.markdown("""
This page zooms in on specific market events. Instead of looking at the full timeline, it asks what happened shortly before and after a shock date.
""")
st.markdown("""
<div class="guide-box">
<strong>How to use this page:</strong> Select an event, then adjust the window size to compare more or fewer days around that event. The vertical red line marks the event date.
</div>
""", unsafe_allow_html=True)

prices = load_prices()
sentiment = load_sentiment()
events = load_events()
df = build_merged_data(prices, sentiment)

event_name = st.selectbox("Select a significant market event:", events["event_name"].tolist())
event = events[events["event_name"] == event_name].iloc[0]

ticker = event["ticker"]
event_date = pd.to_datetime(event["event_date"])
current_color = TICKER_COLORS.get(ticker, "#1f77b4")
window = st.slider("Analysis Window: Days before and after", 5, 30, 14)

tmp = df[df["ticker"] == ticker].copy()
tmp["date"] = pd.to_datetime(tmp["date"])
start_date = event_date - pd.Timedelta(days=window)
end_date = event_date + pd.Timedelta(days=window)
tmp = tmp[(tmp["date"] >= start_date) & (tmp["date"] <= end_date)]

st.subheader(f"Shock Metrics: {event_name} ({ticker})")
st.markdown("""
These metrics compare the selected ticker before and after the event. They give a quick summary of whether return, volatility, and sentiment changed after the shock date.
""")
st.info(f"Context: {event['description']}")

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

st.markdown("""
<div class="key-box">
<strong>Key Takeaway:</strong> The metrics help users quickly see whether the post-event period looked different from the pre-event period. A strong shift does not prove causality, but it flags moments worth closer inspection.
</div>
""", unsafe_allow_html=True)

st.subheader("Event Window: Price and Sentiment Around the Shock")
st.markdown("""
This chart places price and sentiment on the same event window. The goal is to see whether sentiment rose before, during, or after the market movement.
""")
st.markdown("""
<div class="guide-box">
<strong>How to use it:</strong> Hover over the chart to compare daily close price and sentiment. Change the window slider to test whether the pattern is short-term or broader.
</div>
""", unsafe_allow_html=True)

fig = go.Figure()
fig.add_trace(go.Scatter(x=tmp["date"], y=tmp["close"], mode="lines+markers", name="Close Price", line=dict(color=current_color, width=3)))
fig.add_trace(go.Scatter(x=tmp["date"], y=tmp["sentiment_score"], mode="lines", name="Sentiment Score", yaxis="y2", line=dict(color="rgba(150, 150, 150, 0.5)", dash="dot")))
fig.add_shape(type="line", x0=event_date, x1=event_date, y0=0, y1=1, xref="x", yref="paper", line=dict(color="Red", width=2, dash="dashdot"))
fig.add_annotation(x=event_date, y=1, xref="x", yref="paper", text="EVENT DATE", showarrow=True, arrowhead=2, bgcolor="red", font=dict(color="white"))
fig.update_layout(title=f"Impact Visualizer: {ticker} Price & Sentiment Around {event_name}", xaxis_title="Date", yaxis=dict(title="Close Price (USD)", gridcolor="rgba(200,200,200,0.2)"), yaxis2=dict(title="Sentiment Score", overlaying="y", side="right", range=[-1, 1]), hovermode="x unified", height=500)
fig = apply_plot_style(fig)
st.plotly_chart(fig, use_container_width=True)
st.markdown("""
<div class="key-box">
<strong>Key Takeaway:</strong> If sentiment rises before the price movement, it may suggest early retail attention. If it rises after, it may suggest that online discussion reacted to market news rather than predicted it.
</div>
""", unsafe_allow_html=True)

st.subheader("Event Window Data Table")
st.markdown("""
The table shows the exact values used in the event window chart. It helps users check the underlying data instead of only reading the visual summary.
""")
st.dataframe(tmp[["date", "ticker", "close", "return", "volatility_7d", "sentiment_score", "message_volume"]].sort_values("date"), use_container_width=True, hide_index=True)
st.markdown("""
<div class="key-box">
<strong>Key Takeaway:</strong> The table supports transparency. Users can verify whether the visual pattern is driven by sentiment, return, volatility, or message volume.
</div>
""", unsafe_allow_html=True)
