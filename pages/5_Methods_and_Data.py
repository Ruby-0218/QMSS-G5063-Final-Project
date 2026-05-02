import streamlit as st
import pandas as pd
from utils import load_prices, load_sentiment, build_merged_data

st.set_page_config(page_title="Methods and Data", layout="wide")

st.markdown("""
<style>

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

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

st.title("Methods & Data: Research Methodology")

st.header("Data Sources")
st.markdown("""
Our study employs a multi-source data strategy, synchronizing social media discourse with high-frequency financial metrics:

1. **Reddit r/wallstreetbets Dataset (Kaggle)**: A granular repository of thousands of retail investor posts spanning **September 2020 to August 2021**.
2. **Yahoo Finance (yfinance)**: Daily adjusted close prices, trading volume, and log-returns precisely matched to the Reddit timeframe.
3. **FinBERT Sentiment Engine**: We utilized `ProsusAI/finbert`, a pre-trained NLP model specialized for financial text, to calculate sentiment polarity for every post.
""")

st.header("Why 2020-2021? (The Natural Experiment)")
st.markdown("""
**The 'Meme Stock' Phenomenon:**
We intentionally pivoted from live API streams to this historical period because it serves as a unique **natural experiment** in retail investor behavior. 

* **The Volatility Peak:** This era captures the January 2021 GameStop and AMC short squeezes—events where social sentiment demonstrably decoupled from fundamental valuations.
* **The Stress Test:** It provides a "worst-case" scenario for market volatility, allowing us to test if NLP-derived sentiment acts as a **leading indicator** or a **lagging echo** of price movements.
""")

st.header("The Analytical Pipeline")
st.markdown("""
To ensure computational efficiency and dashboard responsiveness, we engineered a dedicated **Offline Processing Pipeline** (`data_converter.py`).
""")

with st.expander("View Technical Workflow Architecture"):
    st.code("""
    # Quantitative Pipeline:
    # 1. Text Normalization: Regex-based cleaning and redundant word deduplication.
    # 2. Sentiment Scoring: Batch processing via FinBERT (ProsusAI) for -1 to 1 polarity.
    # 3. Time-Series Alignment: Rolling 7-day average calculation for sentiment vs. volatility.
    # 4. Network Construction: Co-occurrence matrix generation between Tickers and Keywords.
    # 5. Graph Metrics: Calculation of 'Degree Centrality' to identify narrative hubs.
    # 6. Aggregation: Exporting lightweight CSVs for the Streamlit cloud environment.
    """, language="python")

st.header("Key Methodological Metrics")
st.markdown("""
* **Lead-Lag Cross-Correlation:** We measure the predictive power of sentiment by shifting the sentiment time-series relative to stock returns ($T-n$ to $T+n$).
* **Network Degree Centrality:** We quantify 'Narrative Hubs'—the keywords that serve as the strongest semantic bridges across different market sectors.
* **Shock Metrics:** We utilize an **Event Study framework** to calculate the delta in volatility and sentiment during specific market anomalies.
""")

st.header("Future Work & Limitations")
st.markdown("""
* **Prediction Market Integration:** A logical next step is incorporating data from **Kalshi or Polymarket**. Contrasting retail 'hype' (Reddit) with 'real-money conviction' (Prediction Markets) could significantly improve the signal-to-noise ratio in predictive models.
* **Normalization of Discussion Volume:** To account for organic platform growth, future iterations should normalize message volume relative to active user growth trends on Reddit.
""")

st.subheader("Reproducibility: Download Merged Dataset")
st.write("In the spirit of open science, you can download the consolidated dataset powering this dashboard:")

try:
    prices = load_prices()
    sentiment = load_sentiment()
    df = build_merged_data(prices, sentiment)
    
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download Processed Data (.csv)",
        data=csv,
        file_name='market_sentiment_merged.csv',
        mime='text/csv',
    )
except Exception as e:
    st.info("The download button will be active once data dependencies are loaded.")
