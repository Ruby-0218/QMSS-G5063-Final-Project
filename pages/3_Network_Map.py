import streamlit as st
import networkx as nx
from pyvis.network import Network
import streamlit.components.v1 as components
from pathlib import Path
from utils import load_network_edges

st.set_page_config(page_title="Network Map", layout="wide")
st.title("Ticker-Keyword Co-occurrence Network")

edges = load_network_edges()

st.markdown("""
This page satisfies the network visualization requirement. Each ticker and keyword is represented as a node. 
An edge means that the keyword appeared in the same message or headline as the ticker. Thicker edges indicate more frequent co-occurrence.
""")

min_weight = st.slider("Minimum edge weight", min_value=1, max_value=int(edges["weight"].max()), value=3)

filtered_edges = edges[edges["weight"] >= min_weight].copy()

G = nx.Graph()

for _, row in filtered_edges.iterrows():
    G.add_node(row["source_node"], node_type=row["source_type"])
    G.add_node(row["target_node"], node_type=row["target_type"])
    G.add_edge(row["source_node"], row["target_node"], weight=int(row["weight"]))

net = Network(height="650px", width="100%", bgcolor="#ffffff", font_color="#222222", notebook=False)

for node, attrs in G.nodes(data=True):
    node_type = attrs.get("node_type", "keyword")
    size = 28 if node_type == "ticker" else 16
    shape = "dot" if node_type == "keyword" else "box"
    net.add_node(node, label=node, size=size, shape=shape, title=f"{node_type}: {node}")

for u, v, attrs in G.edges(data=True):
    weight = attrs.get("weight", 1)
    net.add_edge(u, v, value=weight, title=f"Co-occurrence weight: {weight}")

net.set_options("""
{
  "nodes": {
    "borderWidth": 1,
    "font": {"size": 18}
  },
  "edges": {
    "smooth": false
  },
  "physics": {
    "barnesHut": {
      "gravitationalConstant": -30000,
      "centralGravity": 0.3,
      "springLength": 140,
      "springConstant": 0.04
    },
    "minVelocity": 0.75
  }
}
""")

html_path = Path("network_temp.html")
net.save_graph(str(html_path))
components.html(html_path.read_text(encoding="utf-8"), height=700, scrolling=True)

st.subheader("Edge Table")
st.dataframe(filtered_edges.sort_values("weight", ascending=False), use_container_width=True, hide_index=True)

st.markdown("""
**Interpretation:** if technology tickers cluster around narrative keywords such as AI, chips, growth, or earnings, while value stocks cluster around oil, rates, or dividends, the network helps explain why sentiment may travel differently across sectors.
""")
