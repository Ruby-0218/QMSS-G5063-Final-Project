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

st.title("Text Analysis: Decoding the Market Narrative")

posts = load_text_posts()
sentiment = load_sentiment()

with st.sidebar:
    st.header("Filters")
    ticker = st.selectbox("Ticker", ALL_TICKERS, index=0)
    
    score_range = st.slider(
        "Sentiment Score Range", 
        min_value=-1.0, max_value=1.0, 
        value=(-1.0, 1.0), step=0.1,
        help="Filter to see extreme sentiment (e.g., scores > 0.8 or < -0.8)"
    )

# Ticker filter
filtered = posts[posts["ticker"].astype(str).str.upper() == str(ticker).upper()].copy()

filtered = filtered[
    (filtered["sentiment_score"] >= score_range[0]) & 
    (filtered["sentiment_score"] <= score_range[1])
]

if filtered.empty:
    st.warning(f"No text data available for {ticker} in this score range.")
    st.stop()

filtered["sentiment_label"] = filtered["sentiment_score"].apply(sentiment_label)

st.markdown("""
**Storyline: Understanding Market Psychology** How do retail investors talk about their favorite stocks? This page transforms raw social media posts 
into a structured 'Sentiment Landscape,' allowing us to see not just *what* they are saying, but how *intense* their emotions are.
""")

col1, col2 = st.columns([1, 1])

with col1:
    label_counts = filtered["sentiment_label"].value_counts().reset_index()
    label_counts.columns = ["sentiment", "count"]
    
    fig = px.bar(
        label_counts,
        x="sentiment",
        y="count",
        color="sentiment",
        color_discrete_map=SENTIMENT_COLORS,
        title=f"{ticker}: Sentiment Label Distribution"
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    fig_hist = px.histogram(
        filtered,
        x="sentiment_score",
        nbins=30,
        title=f"{ticker}: Sentiment Score Distribution (Intensity Analysis)",
        color_discrete_sequence=['#3498db']
    )
    st.plotly_chart(fig_hist, use_container_width=True)

def deduplicate_text(text):
    return re.sub(r'\b(\w+)(?:\s+\1\b)+', r'\1', str(text))

#  N-gram 
clean_texts = filtered["clean_text"].dropna().apply(deduplicate_text).tolist()


st.subheader("Keyword Cloud: What's the Core Message?")
# use clean_texts
text = " ".join(clean_texts)

if text.strip():
    custom_stopwords = set(STOPWORDS)
    custom_stopwords.update([
        "stock", "ticker", "company", "share", "shares", "price", 
        "going", "market", "day", "buy", "sell", "holding", "will",
        "now", "get", "one", "make", "time", "see", "really"
    ])
    
    wc = WordCloud(
        width=1200, height=500, 
        background_color="rgba(255, 255, 255, 0)", 
        collocations=False,
        stopwords=custom_stopwords
    ).generate(text)
    
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.imshow(wc, interpolation="bilinear")
    ax.axis("off")
    fig.patch.set_alpha(0.0)
    st.pyplot(fig)
else:
    st.warning("No text available for this filter.")

# N-gram 
st.subheader("Beyond Single Words: Top Trending Phrases")
st.markdown("While individual words are useful, retail investor narratives are driven by catchphrases. Here we extract the most common 2-to-3 word combinations.")

# use clean_texts
if len(clean_texts) > 0:
    try:
        vectorizer = CountVectorizer(ngram_range=(2, 3), stop_words='english', max_features=10)
        X = vectorizer.fit_transform(clean_texts)
        
        phrase_counts = pd.DataFrame({
            'Phrase': vectorizer.get_feature_names_out(),
            'Count': X.toarray().sum(axis=0)
        }).sort_values(by='Count', ascending=True) 

        fig_ngram = px.bar(
            phrase_counts, 
            x="Count", 
            y="Phrase", 
            orientation='h',
            title=f"Top 10 Phrases for {ticker}",
            color_discrete_sequence=["#2c3e50"] 
        )
        fig_ngram.update_layout(
            margin=dict(l=150),
            xaxis_showgrid=False,
            yaxis_showgrid=False,
            height=450
        )
        st.plotly_chart(fig_ngram, use_container_width=True)
    except ValueError:
        st.info("Not enough valid text data to generate multi-word phrases.")

st.subheader("Deep Dive: Individual Messages")
st.dataframe(
    filtered[["date", "source", "ticker", "sentiment_score", "clean_text"]].sort_values(by="sentiment_score", ascending=False).head(50),
    use_container_width=True,
    hide_index=True
)

st.markdown("""
**Technical Note:** The keyword analysis dynamically excludes generic terms and redundant repetitive words to highlight context-specific discussions. Use the **Score Range** in the sidebar to isolate extreme emotional voices.
""")
