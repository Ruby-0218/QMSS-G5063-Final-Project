import streamlit as st
import plotly.graph_objects as go
from utils import load_prices, load_sentiment, load_events, build_merged_data

st.set_page_config(page_title="Event Shock Explorer", layout="wide")
st.title("Event Shock Explorer")

prices = load_prices()
sentiment = load_sentiment()
events = load_events()
df = build_merged_data(prices, sentiment)

st.markdown("""
This page turns the dashboard into a clearer story. Instead of only asking whether sentiment and price correlate overall, it asks whether specific market events produce temporary sentiment and volatility shocks.
""")

event_name = st.selectbox("Choose an event", events["event_name"].tolist())
event = events[events["event_name"] == event_name].iloc[0]

ticker = event["ticker"]
event_date = event["event_date"]

window = st.slider("Days before and after event", 5, 30, 14)
tmp = df[df["ticker"] == ticker].copy()
tmp = tmp[(tmp["date"] >= event_date - __import__("pandas").Timedelta(days=window)) & 
          (tmp["date"] <= event_date + __import__("pandas").Timedelta(days=window))]

st.subheader(f"{event_name}: {ticker}")
st.write(event["description"])

fig = go.Figure()
fig.add_trace(go.Scatter(x=tmp["date"], y=tmp["close"], mode="lines+markers", name="Close price"))
fig.add_trace(go.Scatter(x=tmp["date"], y=tmp["sentiment_score"], mode="lines+markers", name="Sentiment", yaxis="y2"))
fig.add_shape(
    type="line",
    x0=event_date,
    x1=event_date,
    y0=0,
    y1=1,
    xref="x",
    yref="paper",
    line=dict(dash="dash")
)

fig.add_annotation(
    x=event_date,
    y=1,
    xref="x",
    yref="paper",
    text="Event date",
    showarrow=False,
    yanchor="bottom"
)

fig.update_layout(
    title=f"{ticker}: Market and Sentiment Around Event",
    xaxis_title="Date",
    yaxis=dict(title="Close price"),
    yaxis2=dict(title="Sentiment score", overlaying="y", side="right"),
    hovermode="x unified",
    height=560
)

st.plotly_chart(fig, use_container_width=True)

st.subheader("Event Window Table")
st.dataframe(
    tmp[["date", "ticker", "close", "return", "volatility_7d", "sentiment_score", "message_volume"]],
    use_container_width=True,
    hide_index=True
)

st.markdown("""
**Design choice:** the event view is useful because sentiment may not predict returns every day. Prior research and common market behavior suggest that sentiment is often more meaningful during attention spikes, earnings events, or large news cycles.
""")
