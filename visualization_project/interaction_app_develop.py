import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import networkx as nx
from pyvis.network import Network
import os

data_file = os.path.join(os.path.dirname(__file__), "corr_node_v4_copy.csv")
df = pd.read_csv(data_file)



# Make title
st.title('Network Graph Visualization of MST')

# Implement select dropdown menu for option selection
selected_month = st.select_slider('Select a month',
    options=['ALL', '04/22', '05/22', '06/22', '07/22', '08/22', '09/22', '10/22', '11/22', '12/22', '01/23', '02/23', '03/23'])

# Create mapping dict
bool_color = {True : 'red', False: 'blue'}
month_weight = {'ALL': 'weight', '04/22': 'weight_4', '05/22': 'weight_5', '06/22': 'weight_6', '07/22': 'weight_7', '08/22': 'weight_8', 
            '09/22': 'weight_9', '10/22': 'weight_10', '11/22': 'weight_11', '12/22': 'weight_12', '01/23': 'weight_1',
            '02/23': 'weight_2', '03/23': 'weight_3'}
month_color = {'ALL': 'plus', '04/22': 'plus_4', '05/22': 'plus_5', '06/22': 'plus_6', '07/22': 'plus_7', '08/22': 'plus_8', 
            '09/22': 'plus_9', '10/22': 'plus_10', '11/22': 'plus_11', '12/22': 'plus_12', '01/23': 'plus_1',
            '02/23': 'plus_2', '03/23': 'plus_3'}

# Filter dataframe
df_select = df[['node1', 'node2', month_weight[selected_month], month_color[selected_month]]]
df_select.rename(columns = {month_weight[selected_month] : 'weight'}, inplace = True)
df_select["color"] = df_select[month_color[selected_month]].map(bool_color)

# Create networkx graph object for drawing
G = nx.from_pandas_edgelist(df_select, 'node1', 'node2', ['weight', 'color'])
T = nx.minimum_spanning_tree(G)

# Initiate PyVis network object
defi_net = Network(height='465px', bgcolor='#222222', font_color='white')
centrality = nx.betweenness_centrality(T, weight = 'weight')


# Take Networkx graph and translate it to a PyVis graph format
defi_net.from_nx(T)

for node in defi_net.nodes:
    node_id = node['id']
    node['title'] = f"""Ticker: {node_id}
    Centrality: {centrality[node_id]}"""

# centrality mean
sum = 0
for i in centrality.values():
    sum = sum + i
centrality_mean = sum / len(centrality)
st.header(f"Total Centrality: {centrality_mean}")


# Save and read graph as HTML file (on Streamlit Sharing)
try:
    path = '/tmp'
    defi_net.save_graph(f'{path}/pyvis_graph.html')
    HtmlFile = open(f'{path}/pyvis_graph.html', 'r', encoding='utf-8')

# Save and read graph as HTML file (locally)
except:
    path = '/html_files'
    defi_net.save_graph(f'{path}/pyvis_graph.html')
    HtmlFile = open(f'{path}/pyvis_graph.html', 'r', encoding='utf-8')

# Load HTML file in HTML component for display on Streamlit page
components.html(HtmlFile.read(), height=435)