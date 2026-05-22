# QMSS-G5063 Final Project: Pricing Market Sentiment

**Live Dashboard URL:** https://qmss-g5063-final-project-gpjqh8qnnvlb6j24csauf2.streamlit.app/

> **Deployment Note:** > Due to GitHub Organization third-party application restrictions preventing direct deployment to Streamlit Cloud, this application is deployed via a mirrored public repository. All source code and data files in this repository are identical to the deployed version.

## Project Overview
This interactive dashboard investigates whether high-growth technology stocks (e.g., NVDA, TSLA) are more sensitive to retail investor sentiment than traditional value stocks (e.g., JPM, XOM). The project compares stock returns, volatility, and sentiment polarity using historical discussion data.

## Data Source & Methodology 
## Data Source & Methodology 
Originally intended to use live Reddit API scraping, this project was adapted to use a comprehensive historical **[Kaggle dataset of Reddit's r/wallstreetbets](https://www.kaggle.com/datasets/gpreda/reddit-wallstreetsbets-posts)**.

This pivot not only resolves current Reddit API access limitations but also provides a more stable, higher-volume historical sample of pure retail investor behavior. By focusing entirely on this retail-driven dataset, we can cleanly observe the "meme-stock" era dynamics and how retail sentiment shocks interact differently across equity types.
