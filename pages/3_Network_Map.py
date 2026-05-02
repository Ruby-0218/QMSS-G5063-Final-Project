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

st.title("Network Map: The Web of Market Narratives")

edges = load_network_edges()

st.markdown("""
**How are stocks connected by the stories we tell?** This interactive network map reveals the underlying semantic structure of the market. 
* **Nodes:** Square nodes represent **Tickers**; circular nodes represent **Keywords**.
* **Edges:** Connections show that a keyword frequently appeared alongside a specific ticker. Thicker lines indicate a stronger narrative link.
""")

col1, col2 = st.columns([1, 2])
with col1:
    min_weight = st.slider(
        "Filter by Connection Strength", 
        min_value=1, 
        max_value=int(edges["weight"].max()), 
        value=3,
        help="Increase this value to hide weak connections and reveal only the core market narratives."
    )

filtered_edges = edges[edges["weight"] >= min_weight].copy()

if filtered_edges.empty:
    st.warning("No connections found at this strength level. Try lowering the threshold.")
    st.stop()

# NetworkX
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

# PyVis 
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
        
    net.add_node(
        node, 
        label=node, 
        size=size, 
        shape=shape, 
        color=color,
        title=f"{node_type.capitalize()}: {node}"
    )

for u, v, attrs in G.edges(data=True):
    weight = attrs.get("weight", 1)
    net.add_edge(
        u, v, 
        value=weight, 
        color="#e0e0e0",
        title=f"Co-occurrence strength: {weight}"
    )

net.set_options("""
{
  "nodes": {
    "borderWidth": 2,
    "borderWidthSelected": 4,
    "font": {
        "size": 16,
        "face": "system-ui"
    }
  },
  "edges": {
    "smooth": {
        "type": "continuous"
    }
  },
  "physics": {
    "barnesHut": {
      "gravitationalConstant": -20000,
      "centralGravity": 0.2,
      "springLength": 150,
      "springConstant": 0.05,
      "damping": 0.09
    },
    "minVelocity": 0.75,
    "stabilization": {
      "enabled": true,
      "iterations": 1000
    }
  },
  "interaction": {
    "hover": true,
    "tooltipDelay": 200
  }
}
""")

html_path = Path("network_temp.html")
net.save_graph(str(html_path))
components.html(html_path.read_text(encoding="utf-8"), height=700, scrolling=True)

st.subheader("Network Metrics: Identifying Narrative Hubs")
st.markdown("Which topics serve as the 'glue' for the entire market? Using **Degree Centrality**, we identify the keywords that act as central hubs, connecting diverse stocks.")

if centrality_data:
    cent_df = pd.DataFrame(centrality_data).sort_values(by="Centrality Score", ascending=False).head(5)
    
    import plotly.express as px
    fig_cent = px.bar(
        cent_df, 
        x="Centrality Score", 
        y="Keyword",
        orientation='h',
        title="Top 5 Central Narrative Hubs",
        color="Centrality Score",
        color_continuous_scale="Blues"
    )
    fig_cent.update_layout(showlegend=False, height=350, yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig_cent, use_container_width=True)
else:
    st.info("Increase the connection strength to see network metrics.")

st.subheader("Data Table: Connection Weights")
st.dataframe(filtered_edges.sort_values("weight", ascending=False), use_container_width=True, hide_index=True)

st.markdown("""
**Analytical Insight:** If technology tickers cluster heavily around narrative keywords such as 'AI' or 'growth', 
while value stocks cluster around 'rates' or 'dividends', this network structure provides 
quantitative evidence of distinct **sentiment silos** within the broader market.
""")
