import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import networkx as nx
from pyvis.network import Network
import os

data_file = os.path.join(os.path.dirname(__file__), "chains_data_v5_copy.csv")
df = pd.read_csv(data_file)

# Make title
st.title('Network Graph Visualization of Defi')

# Define selection options and sort alphabetically
category_list = list(df['protocol_category'].unique())
category_list.sort()

# Implement multiselect dropdown menu for option selection
selected_category = st.multiselect('Select protocol_category to visualize', category_list)

# Set info message on initial site load
if len(selected_category) == 0:
   st.text('Please choose at least 1 category to get started')
# Create network graph when user selects >= 1 item
else:
# Code for filtering dataframe and generating network
    df_select = df.loc[df['protocol_category'].isin(selected_category)]
    df_select = df_select.reset_index(drop=True)

    # Create networkx graph object for drawing
    G = nx.Graph()

    # Create networkx graph object from pandas dataframe 
    g = nx.from_pandas_edgelist(df_select, 'chain', 'protocol')

    # Initiate PyVis network object
    defi_net = Network(height='465px', bgcolor='#222222', font_color='white')

    ## Take Networkx graph and translate it to a PyVis graph format

    # Make a list of the chains, we'll use it later
    chains = list(df_select.chain.unique())
    # Make a list of the protocols, we'll use it later
    protocols = list(df_select.protocol.unique())
    # Make a list of the edges. we'll use it later
    edges_list = list(g.edges())

    # Set nodes size
    chain_size = [g.degree(chain) * 30 for chain in chains]
    protocol_size = [g.degree(protocol) for protocol in protocols]
    
    #add chain_nodes
    G.add_nodes_from(chains, value = chain_size)

    #add protocol_nodes
    G.add_nodes_from(protocols, value = protocol_size, color = "white")

    #add edges
    G.add_edges_from(edges_list)

    defi_net.from_nx(G)

    # Generate network with specific layout settings
    defi_net.repulsion(node_distance=420, central_gravity=0.33,
                       spring_length=110, spring_strength=0.10,
                       damping=0.95)

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
    components.html(HtmlFile.read(), height=700)