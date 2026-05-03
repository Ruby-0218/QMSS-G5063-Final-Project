import streamlit as st
import pandas as pd
import plotly.express as px
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt
import re
from sklearn.feature_extraction.text import CountVectorizer
from utils import load_text_posts, load_sentiment, ALL_TICKERS, sentiment_label, SENTIMENT_COLORS

st.set_page_config(page_title="Text Analysis", layout="wide")
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

st.title("Text Analysis: Reading the Market Conversation")
st.markdown("""
This page moves from prices into language. Instead of only asking whether sentiment moves with stocks, it looks at what retail investors were actually saying and how intense those comments became.

**How to use this page:** Choose a ticker in the sidebar, then adjust the sentiment score range to focus on all posts, only bullish posts, only bearish posts, or extreme emotional posts.
""")

posts = load_text_posts()
sentiment = load_sentiment()

with st.sidebar:
    st.header("Filters")
    ticker = st.selectbox("Ticker", ALL_TICKERS, index=0)
    score_range = st.slider(
        "Sentiment Score Range",
        min_value=-1.0,
        max_value=1.0,
        value=(-1.0, 1.0),
        step=0.1,
        help="Use a narrower range to isolate strongly bullish or strongly bearish messages."
    )

filtered = posts[posts["ticker"].astype(str).str.upper() == str(ticker).upper()].copy()
filtered = filtered[(filtered["sentiment_score"] >= score_range[0]) & (filtered["sentiment_score"] <= score_range[1])]

if filtered.empty:
    st.warning(f"No text data available for {ticker} in this score range.")
    st.stop()

filtered["sentiment_label"] = filtered["sentiment_score"].apply(sentiment_label)

st.subheader("Sentiment Distribution")
st.markdown("""
These charts show whether the selected ticker was discussed mostly in bullish, bearish, or neutral language. They also show whether the comments cluster near the middle or include more extreme emotional scores.

**How to use it:** Change the score range in the sidebar to compare normal discussion with more extreme posts.
""")

col1, col2 = st.columns([1, 1])
with col1:
    label_counts = filtered["sentiment_label"].value_counts().reset_index()
    label_counts.columns = ["sentiment", "count"]
    fig = px.bar(label_counts, x="sentiment", y="count", color="sentiment", color_discrete_map=SENTIMENT_COLORS, title=f"{ticker}: Sentiment Label Distribution")
    st.plotly_chart(fig, use_container_width=True)
with col2:
    fig_hist = px.histogram(filtered, x="sentiment_score", nbins=30, title=f"{ticker}: Sentiment Score Distribution", color_discrete_sequence=["#3498db"])
    st.plotly_chart(fig_hist, use_container_width=True)

st.markdown("""
**Key Takeaway:** The label chart gives a quick count of mood categories, while the histogram shows intensity. A ticker with many posts near the extremes may be more emotionally driven than one clustered near neutral.
""")

def deduplicate_text(text):
    return re.sub(r"\b(\w+)(?:\s+\1\b)+", r"\1", str(text))

clean_texts = filtered["clean_text"].dropna().apply(deduplicate_text).tolist()

st.subheader("Keyword Cloud: The Words Behind the Sentiment")
st.markdown("""
The word cloud gives a fast view of the most visible language around a ticker. Larger words appear more often in the selected posts.
""")

text = " ".join(clean_texts)
if text.strip():
    custom_stopwords = set(STOPWORDS)
    custom_stopwords.update(["stock", "ticker", "company", "share", "shares", "price", "going", "market", "day", "buy", "sell", "holding", "will", "now", "get", "one", "make", "time", "see", "really"])
    wc = WordCloud(width=1200, height=500, background_color="rgba(255, 255, 255, 0)", collocations=False, stopwords=custom_stopwords).generate(text)
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.imshow(wc, interpolation="bilinear")
    ax.axis("off")
    fig.patch.set_alpha(0.0)
    st.pyplot(fig)
else:
    st.warning("No text available for this filter.")

st.markdown("""
**Key Takeaway:** The word cloud is useful for quick pattern recognition, but it should be read as a starting point rather than proof. Repeated words show what users talked about most, not necessarily what caused market movement.
""")

st.subheader("Top Trending Phrases")
st.markdown("""
Single words can be vague, so this chart looks for common two-word and three-word phrases. These phrases help reveal the repeated narratives that shaped discussion around the selected stock.
""")

if len(clean_texts) > 0:
    try:
        vectorizer = CountVectorizer(ngram_range=(2, 3), stop_words="english", max_features=10)
        X = vectorizer.fit_transform(clean_texts)
        phrase_counts = pd.DataFrame({"Phrase": vectorizer.get_feature_names_out(), "Count": X.toarray().sum(axis=0)}).sort_values(by="Count", ascending=True)
        fig_ngram = px.bar(phrase_counts, x="Count", y="Phrase", orientation="h", title=f"Top 10 Phrases for {ticker}", color_discrete_sequence=["#2c3e50"])
        fig_ngram.update_layout(margin=dict(l=150), xaxis_showgrid=False, yaxis_showgrid=False, height=450)
        st.plotly_chart(fig_ngram, use_container_width=True)
    except ValueError:
        st.info("Not enough valid text data to generate multi-word phrases.")

st.markdown("""
**Key Takeaway:** Phrases are closer to narratives than isolated words. They help show whether discussion was about earnings, hype, technology, short-term trading, or broader market fear.
""")

st.subheader("Individual Messages")
st.markdown("""
This table lets users inspect the original text behind the summary charts. It is especially useful for checking whether the model's sentiment score matches the actual tone of the post.
""")
st.dataframe(filtered[["date", "source", "ticker", "sentiment_score", "clean_text"]].sort_values(by="sentiment_score", ascending=False).head(50), use_container_width=True, hide_index=True)
st.markdown("""
**Key Takeaway:** The table makes the text analysis more transparent. Users can check specific messages instead of only trusting aggregated sentiment scores.
""")
