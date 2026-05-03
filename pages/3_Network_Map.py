import streamlit as st
import networkx as nx
from pyvis.network import Network
import streamlit.components.v1 as components
from pathlib import Path
import pandas as pd
from utils import load_network_edges, TICKER_COLORS

st.set_page_config(page_title="Network Map", layout="wide")
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
        border-left: 6px solid #7C3AED;
        border-bottom: 1px solid rgba(128, 128, 128, 0.22);
        padding: 0.9rem 1.1rem !important;
        border-radius: 12px;
        margin-top: 2.4rem !important;
        margin-bottom: 1rem !important;
        box-shadow: 0 3px 10px rgba(124, 58, 237, 0.12);
    }

    p, li {
        font-size: 1.02rem;
        line-height: 1.65;
        color: var(--text-color);
    }

    .visual-header {
        color: var(--text-color);
        font-weight: 750;
        font-size: 1.75rem;
        line-height: 1.25;
        background-color: var(--secondary-background-color);
        border-left: 6px solid #7C3AED;
        border-bottom: 1px solid rgba(128, 128, 128, 0.22);
        padding: 0.9rem 1.1rem;
        border-radius: 12px;
        margin-top: 2.4rem;
        margin-bottom: 1rem;
        box-shadow: 0 3px 10px rgba(124, 58, 237, 0.12);
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
        font=dict(family="Arial", size=14, color="#243447"),
        title_font=dict(size=18, color="#1F2D3D"),
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        legend=dict(font=dict(color="#243447"), bgcolor="rgba(255,255,255,0.85)"),
        margin=dict(l=55, r=55, t=88, b=55),
    )
    fig.update_xaxes(
        showgrid=True,
        gridcolor="#E6ECF1",
        zerolinecolor="#9AA7B2",
        linecolor="#9AA7B2",
        tickfont=dict(color="#243447"),
        title_font=dict(color="#243447"),
    )
    fig.update_yaxes(
        showgrid=True,
        gridcolor="#E6ECF1",
        zerolinecolor="#9AA7B2",
        linecolor="#9AA7B2",
        tickfont=dict(color="#243447"),
        title_font=dict(color="#243447"),
    )
    return fig


st.title("Network Map: The Web of Market Narratives")
st.markdown("""
This page shows how stocks become connected through shared language. If several tickers are linked to the same keywords, it suggests that investors may be grouping those stocks inside the same market story.
""")
st.markdown("""
<div class="guide-box">
<strong>How to use this page:</strong> Move the connection-strength slider to hide weaker links. Hover over nodes and edges to inspect tickers, keywords, and co-occurrence strength.
</div>
""", unsafe_allow_html=True)

edges = load_network_edges()

st.subheader("Ticker-Keyword Co-occurrence Network")
st.markdown("""
The network connects ticker symbols to keywords that frequently appear with them in WallStreetBets posts. Square nodes are stocks, circular nodes are keywords, and thicker connections mean stronger repeated association.
""")

col1, col2 = st.columns([1, 2])
with col1:
    min_weight = st.slider("Filter by Connection Strength", min_value=1, max_value=int(edges["weight"].max()), value=3, help="Increase this value to remove weaker connections and reveal the core narratives.")

filtered_edges = edges[edges["weight"] >= min_weight].copy()
if filtered_edges.empty:
    st.warning("No connections found at this strength level. Try lowering the threshold.")
    st.stop()

G = nx.Graph()
for _, row in filtered_edges.iterrows():
    G.add_node(row["source_node"], node_type=row["source_type"])
    G.add_node(row["target_node"], node_type=row["target_type"])
    G.add_edge(row["source_node"], row["target_node"], weight=int(row["weight"]))

centrality = nx.degree_centrality(G)
centrality_data = []
for node, score in centrality.items():
    if G.nodes[node].get("node_type") == "keyword":
        centrality_data.append({"Keyword": node, "Centrality Score": score})

net = Network(height="650px", width="100%", bgcolor="#ffffff", font_color="#222222", notebook=False)
for node, attrs in G.nodes(data=True):
    node_type = attrs.get("node_type", "keyword")
    if node_type == "ticker":
        size = 35
        shape = "box"
        color = TICKER_COLORS.get(node, "#1f77b4")
    else:
        size = 15
        shape = "dot"
        color = "#bdc3c7"
    net.add_node(node, label=node, size=size, shape=shape, color=color, title=f"{node_type.capitalize()}: {node}")

for u, v, attrs in G.edges(data=True):
    weight = attrs.get("weight", 1)
    net.add_edge(u, v, value=weight, color="#e0e0e0", title=f"Co-occurrence strength: {weight}")

net.set_options("""
{
  "nodes": {"borderWidth": 2, "borderWidthSelected": 4, "font": {"size": 16, "face": "system-ui"}},
  "edges": {"smooth": {"type": "continuous"}},
  "physics": {"barnesHut": {"gravitationalConstant": -20000, "centralGravity": 0.2, "springLength": 150, "springConstant": 0.05, "damping": 0.09}, "minVelocity": 0.75, "stabilization": {"enabled": true, "iterations": 1000}},
  "interaction": {"hover": true, "tooltipDelay": 200}
}
""")

html_path = Path("network_temp.html")
net.save_graph(str(html_path))
components.html(html_path.read_text(encoding="utf-8"), height=700, scrolling=True)
st.markdown("""
<div class="key-box">
<strong>Key Takeaway:</strong> The network helps show whether a stock is discussed alone or as part of a larger story. Strong shared keywords suggest that investors may be linking multiple stocks through the same themes.
</div>
""", unsafe_allow_html=True)

st.subheader("Central Narrative Hubs")
st.markdown("""
This bar chart identifies the keywords that connect most strongly across the network. These are the topics that act like bridges between stocks.
""")

if centrality_data:
    import plotly.express as px
    cent_df = pd.DataFrame(centrality_data).sort_values(by="Centrality Score", ascending=False).head(5)
    fig_cent = px.bar(cent_df, x="Centrality Score", y="Keyword", orientation="h", title="Top 5 Central Narrative Hubs", color="Centrality Score", color_continuous_scale="Blues")
    fig_cent.update_layout(showlegend=False, height=350, yaxis={"categoryorder": "total ascending"})
    fig_cent = apply_plot_style(fig_cent)
    st.plotly_chart(fig_cent, use_container_width=True)
else:
    st.info("Increase the connection strength to see network metrics.")

st.markdown("""
<div class="key-box">
<strong>Key Takeaway:</strong> A central keyword is not just frequent; it connects different parts of the conversation. These hubs help identify the market stories that travel across several tickers.
</div>
""", unsafe_allow_html=True)

st.subheader("Connection Weights Table")
st.markdown("""
The table shows the raw links used to build the network. It is useful for checking which ticker-keyword pairs are driving the visual structure.
""")
st.dataframe(filtered_edges.sort_values("weight", ascending=False), use_container_width=True, hide_index=True)
st.markdown("""
<div class="key-box">
<strong>Key Takeaway:</strong> The table makes the network more interpretable by showing the exact connection weights behind each visual link.
</div>
""", unsafe_allow_html=True)
