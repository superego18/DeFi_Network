import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import networkx as nx
from pyvis.network import Network
import requests
import os
import numpy as np

### Make Background
# Make title
st.title('Network Graph Visualization of Defi_Beta')

### load data
response = requests.get("https://api.llama.fi/protocols")
if response.status_code == 200:
    headers =response.headers
    data = response.json()
    df = pd.DataFrame(data)

    # drop CEX 
    df = df[df.category != 'CEX']

    # extract needed columns
    df = df[['name', 'category', 'chains', 'tvl']]

    # make tidy
    df = pd.concat([
        pd.DataFrame(
            {'protocol': row['name'], 'protocol_category': row['category'], 'chain': row['chains'], 'tvl': row['tvl']}
        ) for _, row in df.iterrows()]
        )
    
    # add (C) to chains' name
    df["chain"] = "(C)" + df["chain"] 

    # make chain_tvl and protocol_tvl
    df_ct = df.groupby('chain').agg(chain_tvl = ('tvl', 'sum')).reset_index()
    df_pt = df.groupby('protocol').agg(protocol_tvl = ('tvl', 'sum')).reset_index()
    
    merge_1 = pd.merge(df,df_ct, how='inner',on='chain')
    merge_2 = pd.merge(merge_1, df_pt, how='inner', on='protocol')

    df = merge_2

    # drop if chain_tvl or protocol_tvl is zero
    df = df[(df['chain_tvl'] != 0) & (df['protocol_tvl'] != 0)]

    # drop if protocol_tvl value is under their median value
    df = df[df['protocol_tvl']  >= df['protocol_tvl'].median()]

    # drop if chain_tvl value is under their median value
    df = df[df['chain_tvl']  >= 0.5 * df['chain_tvl'].median()]

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
        defi_net = Network(height="700px", width="100%", bgcolor='#222222', font_color='white')

        ## Take Networkx graph and translate it to a PyVis graph format

        # Make a list of the chains, we'll use it later
        chains = list(df_select.chain.unique())
        # Make a list of the protocols, we'll use it later
        protocols = list(df_select.protocol.unique())
        # Make a list of the edges. we'll use it later
        edges_list = list(g.edges())
        # Make a list of chains' tvl.
        chains_tvl = {chain : df.loc[df['chain'] == chain, 'chain_tvl'].unique().tolist() for chain in chains}
        # Make a list of protocols' tvl.
        protocols_tvl = {protocol : df.loc[df['protocol'] == protocol, 'protocol_tvl'].unique().tolist() for protocol in protocols}

        # # Set nodes size
        # chain_size = [0.000000001 * chains_tvl[chain][0] for chain in chains]
        # protocol_size = [0.000000001 * protocols_tvl[protocol][0] for protocol in protocols]
        
        #add chain_nodes
        for chain, value in chains_tvl.items():
            G.add_node(chain, size = 0.0000000005 * value[0] + 10)

        #add protocol_nodes
        for protocol, value in protocols_tvl.items():
            G.add_node(protocol, size = 0.0000000005 * value[0] + 10, color = 'white')

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


else:
    error = response.status_code
    st.header(error)
