import streamlit as st
from utils import load_prices, load_sentiment, build_merged_data, STOCK_GROUPS

st.set_page_config(
    page_title="Pricing Market Sentiment",
    layout="wide"
)

st.title("Pricing Market Sentiment")
st.subheader("How Retail Sentiment (WallStreetBets) Relates to Stock Volatility")

st.markdown("""
This interactive dashboard investigates whether high-growth technology stocks are more sensitive to retail sentiment than traditional value stocks. The project analyzes retail-oriented market sentiment, stock returns, volatility, and topic co-occurrence patterns across selected tickers based on historical **Reddit (WallStreetBets)** discussions.
""")

st.info("""
Data source strategy: Due to Reddit API limitations, this project utilizes a comprehensive historical Kaggle dataset of Reddit's r/wallstreetbets. This ensures stable data access while perfectly maintaining the core focus on retail investor behavior.
""")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Experimental group", "5 tech stocks", "NVDA, TSLA, AAPL, MSFT, AMZN")

with col2:
    st.metric("Control group", "2 value stocks", "JPM, XOM")

with col3:
    st.metric("Specialized visuals", "2 included", "Text + Network")



st.header("Research Question")
st.markdown("""
**Do speculative and high-growth technology stocks respond more strongly to sentiment shocks than traditional value stocks?**

The site is organized around four steps:

1. Compare stock price, return, volatility, and sentiment over time.
2. Analyze sentiment polarity and major discussion topics.
3. Map ticker-keyword relationships through a co-occurrence network.
4. Explore shock events where sentiment and volatility move together.
""")

st.header("Why the Reddit API issue does not weaken the project")
st.markdown("""
Reddit was only one possible source for retail sentiment. The project requirement asks for a larger dataset, interactive website, and at least two specialized visualization types. 
StockTwits is actually more directly connected to investor behavior because users discuss tickers explicitly. Alpha Vantage's News & Sentiment API is also useful as a professional-news benchmark.
""")

st.header("Website Design Logic")
st.markdown("""
Each chart includes interaction, comparison, or filtering. The dashboard avoids isolated charts and instead builds one visual argument: 
public market sentiment may matter more for stocks that are already more speculative, narrative-driven, and heavily discussed.
""")

with st.expander("Methodology: Data Substitution & Research Impact"):
    st.write("""
    Due to current Reddit API limitations, this project utilizes a high-quality historical dataset of **Reddit's r/wallstreetbets** sourced from **Kaggle**. This ensures a larger, more stable sample size while maintaining the original research intent of measuring public market sentiment.
    
    **Why we chose this specific dataset:**
    * **Pure Retail Investor Focus:** It captures authentic, unfiltered discussions from the WallStreetBets community, allowing us to perfectly isolate the impact of retail momentum and "meme-stock" dynamics.
    * **Robust Sentiment Analysis:** The historical text provides a solid foundation for NLP sentiment scoring, converting unstructured social media buzz into clear, quantifiable polarities.
    * **Targeted Ticker Coverage:** It contains dense historical data for both our experimental group (High-growth Tech: NVDA, TSLA, etc.) and control group (Value: JPM, XOM), making the comparison accurate and meaningful.
    """)

st.caption("Use the sidebar pages to explore the dashboard, text analysis, network map, and event shock explorer.")
