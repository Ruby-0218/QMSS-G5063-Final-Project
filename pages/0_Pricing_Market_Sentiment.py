import streamlit as st
from utils import load_prices, load_sentiment, build_merged_data, STOCK_GROUPS

st.set_page_config(
    page_title="Pricing Market Sentiment",
    layout="wide"
)

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

st.title("Pricing Market Sentiment")
st.subheader("How WallStreetBets sentiment connects to stock volatility")
st.markdown("""
This project turns online market conversation into a guided visual story about sentiment, attention, and volatility.
""")

st.markdown("""
Markets are not only shaped by earnings reports, interest rates, or company fundamentals. During the meme-stock era, online communities also became part of the market story. This website follows that story by asking whether the language of retail investors on **Reddit's r/wallstreetbets** moved together with stock prices, returns, and volatility.

The main research question is simple: **Do speculative, high-growth technology stocks react more strongly to retail sentiment shocks than traditional value stocks?** To explore this, the project compares five high-growth technology stocks with two traditional value stocks and turns social media text into interactive visual evidence.
""")

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("High-growth tech group", "5 stocks", "NVDA, TSLA, AAPL, MSFT, AMZN")
with col2:
    st.metric("Traditional value group", "2 stocks", "JPM, XOM")
with col3:
    st.metric("Specialized visualizations", "2 types", "Text + Network")

st.header("What this website is for")
st.markdown("""
This website is designed as a guided path rather than a collection of separate charts. It begins with the market-level relationship between prices and sentiment, then moves into the language behind that sentiment, the keyword networks connecting stocks, and finally specific event windows where sentiment and volatility changed around market shocks.

The goal is not to claim that Reddit sentiment directly causes stock prices to move. The goal is to help users see when sentiment, attention, and volatility appear to move together, and whether those patterns look stronger for narrative-driven technology stocks than for more traditional value stocks.
""")

st.header("Data used in this project")
st.markdown("""
The project uses three main data components:

1. **Reddit r/wallstreetbets dataset from Kaggle.** This provides historical retail investor posts from the 2020 to 2021 meme-stock period. We use this because it gives a stable and large sample of retail discussion without depending on live Reddit API access.
2. **Yahoo Finance data through `yfinance`.** Daily stock prices and trading volume are matched to the Reddit timeframe so that market behavior can be compared with discussion patterns.
3. **FinBERT sentiment scoring.** Reddit text is scored with `ProsusAI/finbert`, a financial language model that converts posts into sentiment values.

This data choice keeps the project focused on retail sentiment. Even though the original proposal considered live APIs and professional news sentiment, the final website prioritizes WallStreetBets because it is closer to the core question about retail investor attention and market volatility.
""")

st.header("Website navigation guide")
st.markdown("""
Use the sidebar to move through the project in this order:

**Market Dashboard** shows how price, sentiment, return, volatility, and message volume move over time.  
**Text Analysis** looks inside the posts to show sentiment distribution, common words, and frequent phrases.  
**Network Map** shows how tickers connect to repeated market narratives such as AI, EV, earnings, and inflation.  
**Event Shock Explorer** zooms into specific events and compares market behavior before and after the shock.

This guide is placed near the beginning because users should understand the path before reading the deeper methods section.
""")

st.header("Methods and analytical pipeline")
st.markdown("""
The data pipeline is built offline so the Streamlit website can load quickly. The raw Reddit text is cleaned, matched to selected tickers, scored with FinBERT, aggregated by date and ticker, and then merged with stock price data. The same processed data also supports the text analysis, network map, and event shock explorer.
""")

with st.expander("View technical workflow"):
    st.code("""
# Quantitative Pipeline:
# 1. Text cleaning and ticker matching from Reddit posts.
# 2. FinBERT sentiment scoring for financial text.
# 3. Daily aggregation of sentiment score and message volume.
# 4. Yahoo Finance price collection for selected tickers.
# 5. Time-series merge by date and ticker.
# 6. Rolling return, volatility, sentiment, and volume calculations.
# 7. Ticker-keyword network construction for narrative analysis.
    """, language="python")

st.header("Future Work & Limitations")
st.markdown("""
This project is strongest as an exploratory visualization tool, not as a full prediction model. The Reddit dataset captures a historically important period, but it does not represent all investors or all market conditions. Sentiment scoring can also miss sarcasm, slang, and context-specific jokes, which are common in WallStreetBets posts.

Future versions could add professional news sentiment, StockTwits messages, or prediction market data from sources such as Kalshi or Polymarket. Comparing retail hype with professional news or real-money expectations could help separate noisy excitement from signals that may be more useful for forecasting volatility.
""")

st.header("Reproducibility: Download Merged Dataset")
st.write("Download the processed dataset used by the dashboard for checking, reproduction, or further analysis.")

try:
    prices = load_prices()
    sentiment = load_sentiment()
    df = build_merged_data(prices, sentiment)
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Download Processed Data (.csv)",
        data=csv,
        file_name="market_sentiment_merged.csv",
        mime="text/csv",
    )
except Exception:
    st.info("The download button will be active once data dependencies are loaded.")
