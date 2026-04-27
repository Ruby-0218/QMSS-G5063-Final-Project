import streamlit as st
import plotly.express as px
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from utils import load_text_posts, load_sentiment, ALL_TICKERS, sentiment_label

st.set_page_config(page_title="Text Analysis", layout="wide")
st.title("Text Analysis: What Is the Market Talking About?")

posts = load_text_posts()
sentiment = load_sentiment()

with st.sidebar:
    ticker = st.selectbox("Ticker", ALL_TICKERS, index=0)

filtered = posts[posts["ticker"].astype(str).str.upper() == str(ticker).upper()].copy()

if filtered.empty:
    st.warning(f"No text data available for {ticker}.")
    st.stop()

filtered["sentiment_label"] = filtered["sentiment_score"].apply(sentiment_label)

st.markdown("""
This page satisfies the text analysis visualization requirement. It shows how unstructured market language can be converted into sentiment labels, keywords, and interpretable topic patterns.
""")

col1, col2 = st.columns([1, 1])

with col1:
    label_counts = filtered["sentiment_label"].value_counts().reset_index()
    label_counts.columns = ["sentiment", "count"]
    fig = px.bar(
        label_counts,
        x="sentiment",
        y="count",
        title=f"{ticker}: Sentiment Label Distribution"
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    fig_hist = px.histogram(
        filtered,
        x="sentiment_score",
        nbins=30,
        title=f"{ticker}: Sentiment Score Distribution"
    )
    st.plotly_chart(fig_hist, use_container_width=True)

st.subheader("Keyword Cloud")
text = " ".join(filtered["clean_text"].dropna().astype(str).tolist())

if text.strip():
    wc = WordCloud(width=1200, height=500, background_color="white", collocations=False).generate(text)
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.imshow(wc, interpolation="bilinear")
    ax.axis("off")
    st.pyplot(fig)
else:
    st.warning("No text available for this filter.")

st.subheader("Example Messages and Headlines")
st.dataframe(
    filtered[["date", "source", "ticker", "sentiment_score", "clean_text"]].head(20),
    use_container_width=True,
    hide_index=True
)

st.markdown("""
**Design choice:** the word cloud is used only as a quick qualitative overview. The bar chart and histogram provide more reliable evidence because they show the distribution of classified sentiment.
""")
