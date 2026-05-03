import streamlit as st

st.set_page_config(page_title="Pricing Market Sentiment", layout="wide")

# Hide sidebar label (hack)
st.markdown("""
<style>
[data-testid="stSidebarNav"] ul li:first-child {
    display: none;
}
</style>
""", unsafe_allow_html=True)

st.title("Welcome")
st.write("Please select 'Pricing Market Sentiment' from the sidebar.")
