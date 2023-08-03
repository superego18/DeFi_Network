import streamlit as st
from PIL import Image
import streamlit.components.v1 as components
import pandas as pd
import networkx as nx
from pyvis.network import Network
import requests
import os
import plotly.graph_objects as go
import plotly.express as px

# page setting
st.set_page_config(page_title="Cryptoasset Network", layout="wide")
# page_icon= 으로 favicon 설정

style_file = os.path.join(os.path.dirname(__file__), "style.css")
image_file = os.path.join(os.path.dirname(__file__), 'logo.png')
TVL_Category_file = os.path.join(os.path.dirname(__file__), 'TVL_Category.csv')
allChains_file = os.path.join(os.path.dirname(__file__), 'allChains.csv')
data_file = os.path.join(os.path.dirname(__file__), "corr_node_v4_copy.csv")

with open(style_file) as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

header = st.container()
with header:
    col14, col15 = st.columns([1, 13])
    with col14:
        image = Image.open(image_file)
        st.image(image, width=60, use_column_width=False)
    with col15:
        st.markdown(
            "<p style='text-align: left; font-size: 50px; font-weight: bold;'>Cryptoasset Network</p>", unsafe_allow_html=True)
    st.markdown(
        "<p style='text-align: center; font-size: 15px; font-weight: bold;'>We offer network graphs as a new way of looking at the Cryptoasset Ecosystem,<br>providing users with visuals to determine the risks posed by complex connections and portfolios to hedge them.</p>", unsafe_allow_html=True)


st.markdown("<div style='height:600px;></div>", unsafe_allow_html=True)

# header
tab1, tab2, tab3, tab4 = st.tabs(["DeFi-MainNet Ecosystem","Coin Price Correlations",
                                    "TVL for each DeFi Protocol Category", "TVL Change over a year for each Chain"])

with tab1:

    st.markdown(
        "<div style='height: 30px;'></div>", unsafe_allow_html=True)

    network1 = st.container()
    with network1:

        st.write("<p style='color: #97C2FC; text-align: center; font-size: 20px; font-weight: bold;'>Network Graph Visualization of DeFi-MainNet Ecosystem</p>", unsafe_allow_html=True)

        ##########
        # load data
        response = requests.get("https://api.llama.fi/protocols")
        if response.status_code == 200:
            headers = response.headers
            data = response.json()
            df = pd.DataFrame(data)

            # drop CEX
            df = df[df.category != 'CEX']

            # extract needed columns
            df = df[['name', 'category', 'chains', 'tvl']]

            # make tidy
            df = pd.concat([
                pd.DataFrame(
                    {'protocol': row['name'], 'protocol_category': row['category'],
                        'chain': row['chains'], 'tvl': row['tvl']}
                ) for _, row in df.iterrows()]
            )

            # add (C) to chains' name
            df["chain"] = "(C)" + df["chain"]

            # make chain_tvl and protocol_tvl
            df_ct = df.groupby('chain').agg(
                chain_tvl=('tvl', 'sum')).reset_index()
            df_pt = df.groupby('protocol').agg(
                protocol_tvl=('tvl', 'sum')).reset_index()

            merge_1 = pd.merge(df, df_ct, how='inner', on='chain')
            merge_2 = pd.merge(merge_1, df_pt, how='inner', on='protocol')

            df = merge_2

            # drop if chain_tvl or protocol_tvl is zero
            df = df[(df['chain_tvl'] != 0) & (df['protocol_tvl'] != 0)]

            # drop if protocol_tvl value is under their median value
            df = df[df['protocol_tvl'] >= 0.5 * df['protocol_tvl'].median()]

            # drop if chain_tvl value is under their median value
            df = df[df['chain_tvl'] >= 0.5 * df['chain_tvl'].median()]

            # Define selection options and sort alphabetically
            category_list = list(df['protocol_category'].unique())
            category_list.sort()
            default = [category_list[6]]

            # Implement multiselect dropdown menu for option selection
            selected_category = st.multiselect(
                'Select protocol_category to visualize', category_list, default=default)

            st.markdown("<div style='height: 10xpx;'></div>",
                        unsafe_allow_html=True)

            # Set info message on initial site load
            if len(selected_category) == 0:
                st.text('Please choose at least 1 category to get started')
            # Create network graph when user selects >= 1 item
            else:
                # Code for filtering dataframe and generating network
                df_select = df.loc[df['protocol_category'].isin(
                    selected_category)]
                df_select = df_select.reset_index(drop=True)

                # Create networkx graph object for drawing
                G = nx.Graph()

                # Create networkx graph object from pandas dataframe
                g = nx.from_pandas_edgelist(df_select, 'chain', 'protocol')

                # Initiate PyVis network object
                defi_net = Network(height="450px", width="100%",
                                    bgcolor='#000000', font_color='white')

                # Take Networkx graph and translate it toㄴㅎ a PyVis graph format

                # Make a list of the chains, we'll use it later
                chains = list(df_select.chain.unique())
                # Make a list of the protocols, we'll use it later
                protocols = list(df_select.protocol.unique())
                # Make a list of the edges. we'll use it later
                edges_list = list(g.edges())
                # Make a list of chains' tvl.
                chains_tvl = {chain: df.loc[df['chain'] == chain, 'chain_tvl'].unique(
                ).tolist() for chain in chains}
                # Make a list of protocols' tvl.
                protocols_tvl = {protocol: df.loc[df['protocol'] == protocol, 'protocol_tvl'].unique(
                ).tolist() for protocol in protocols}

                # # Set nodes size
                # chain_size = [0.000000001 * chains_tvl[chain][0] for chain in chains]
                # protocol_size = [0.000000001 * protocols_tvl[protocol][0] for protocol in protocols]

                # add chain_nodes
                for chain, value in chains_tvl.items():
                    G.add_node(chain, size=0.0000000005 * value[0] + 10)

                # add protocol_nodes
                for protocol, value in protocols_tvl.items():
                    G.add_node(protocol, size=0.0000000005 *
                                value[0] + 10, color='white')

                # add edges
                G.add_edges_from(edges_list)

                defi_net.from_nx(G)

                # Generate network with specific layout settings
                defi_net.repulsion(node_distance=420, central_gravity=0.33,
                                    spring_length=110, spring_strength=0.10,
                                    damping=0.95)

                # # Save and read graph as HTML file (on Streamlit Sharing)
                # try:
                path = '/tmp'
                defi_net.save_graph(f'{path}/pyvis_graph.html')
                HtmlFile = open(f'{path}/pyvis_graph.html',
                                'r', encoding='utf-8')

                # st.download_button(
                #     label='Download HTML file',
                #     data=HtmlFile,
                #     file_name='pyvis_graph.html',
                #     mime='text/html'
                #  )
                components.html(HtmlFile.read(), height=450)

        else:
            error = response.status_code
            st.header(error)
        ##########

        col8, col9, col10 = st.columns(3)
        with col8:
            st.write(
                f"<p style='color: #00CCF3; font-size: 50px; font-weight: bold;'>{len(chains)}</p>", unsafe_allow_html=True)
            st.write(
                "<p style='font-size: 15px; font-weight: bold;'>Chain(MainNet) Nodes</p>", unsafe_allow_html=True)
        with col9:
            st.write(
                f"<p style='color: #00CCF3; font-size: 50px; font-weight: bold;'>{len(protocols)}</p>", unsafe_allow_html=True)
            st.write(
                "<p style='font-size: 15px; font-weight: bold;'>Protocol(DeFi) Nodes</p>", unsafe_allow_html=True)
        with col10:
            st.write(
                f"<p style='color: #00CCF3; font-size: 50px; font-weight: bold;'>{len(edges_list)}</p>", unsafe_allow_html=True)
            st.write(
                "<p style='font-size: 15px; font-weight: bold;'>Edges</p>", unsafe_allow_html=True)

    st.markdown("<div style='height: 200px;></div>", unsafe_allow_html=True)

with tab2:

    st.markdown(
        "<div style='height: 30px;'></div>", unsafe_allow_html=True)

    network2 = st.container()
    with network2:
        st.write("<p style='color: #97C2FC; text-align: center; font-size: 20px; font-weight: bold;'>Network Graph Visualization of Coin Price Correlations</p>", unsafe_allow_html=True)

        #########
        df = pd.read_csv(data_file)

        # Implement select dropdown menu for option selection
        selected_month = st.select_slider('Select a month',
                                            options=['ALL', '04/22', '05/22', '06/22', '07/22', '08/22', '09/22', '10/22', '11/22', '12/22', '01/23', '02/23', '03/23'])

        # Create mapping dict
        bool_color = {True: 'white', False: 'red'}
        month_weight = {'ALL': 'weight', '04/22': 'weight_4', '05/22': 'weight_5', '06/22': 'weight_6', '07/22': 'weight_7', '08/22': 'weight_8', 
        '09/22': 'weight_9', '10/22': 'weight_10', '11/22': 'weight_11', '12/22': 'weight_12', '01/23': 'weight_1',
        '02/23': 'weight_2', '03/23': 'weight_3'}
        month_color = {'ALL': 'plus', '04/22': 'plus_4', '05/22': 'plus_5', '06/22': 'plus_6', '07/22': 'plus_7', '08/22': 'plus_8', 
        '09/22': 'plus_9', '10/22': 'plus_10', '11/22': 'plus_11', '12/22': 'plus_12', '01/23': 'plus_1',
        '02/23': 'plus_2', '03/23': 'plus_3'}

        # Filter dataframe
        df_select = df[[
            'node1', 'node2', month_weight[selected_month], month_color[selected_month]]]
        df_select.rename(
            columns={month_weight[selected_month]: 'weight'}, inplace=True)
        df_select["color"] = df_select[month_color[selected_month]].map(
            bool_color)

        # Create networkx graph object for drawing
        G = nx.from_pandas_edgelist(
            df_select, 'node1', 'node2', ['weight', 'color'])
        T = nx.minimum_spanning_tree(G)

        # Initiate PyVis network object
        defi_net = Network(
            height='450px', bgcolor='#000000', font_color='white')
        # , select_menu=False, filter_menu=False
        centrality = nx.betweenness_centrality(T, weight = 'weight')

        # Take Networkx graph and translate it to a PyVis graph format
        defi_net.from_nx(T)

        for node in defi_net.nodes:
            node_id = node['id']
            node['title'] = f"Ticker: {node_id}, Degree Centrality: {round(centrality[node_id], 3)}"

        # centrality mean
        sum = 0
        for i in centrality.values():
            sum = sum + i
        centrality_mean = sum / len(centrality)

        ##3
        # enable the select menu
        # defi_net.toggle_physics(False)
        # defi_net.show_buttons(filter_=['physics'])
        # defi_net.show("graph.html")

        # set the select menu options
        # defi_net.set_options(select_mode='nodes')
        # defi_net.set_options(select_label='label')


        path = '/tmp'
        defi_net.save_graph(f'{path}/pyvis_graph.html')
        HtmlFile = open(f'{path}/pyvis_graph.html', 'r', encoding='utf-8')

        # Load HTML file in HTML component for display on Streamlit page
        components.html(HtmlFile.read(), height=450)
        ##########

        col11, col12, col13, col16 = st.columns(4)
        with col11:
            st.write(
                f"<p style='color: #00CCF3; font-size: 50px; font-weight: bold;'>{len(defi_net.nodes)}</p>", unsafe_allow_html=True)
            st.write(
                "<p style='font-size: 15px; font-weight: bold;'>Token Nodes</p>", unsafe_allow_html=True)
        with col12:
            ct_edges = 0
            ct_reds = 0
            for (u, v, c) in T.edges.data('color', default='red'):
                ct_edges += 1
                if c == 'red':
                    ct_reds += 1
            st.write(
                f"<p style='color: #00CCF3; font-size: 50px; font-weight: bold;'>{ct_edges}</p>", unsafe_allow_html=True)
            st.write(
            "<p style='font-size: 15px; font-weight: bold;'>Edges</p>", unsafe_allow_html=True)
        with col13:
            st.write(
                f"<p style='color: #00CCF3; font-size: 50px; font-weight: bold;'>{ct_reds}</p>", unsafe_allow_html=True)
            st.write(
            "<p style='font-size: 15px; font-weight: bold;'>Red Edges</p>", unsafe_allow_html=True)
            st.write(
            "<p style='font-size: 15px; font-weight: bold;'>(Negative Correlation)</p>", unsafe_allow_html=True)
        with col16:
            st.write(
                f"<p style='color: #00CCF3; font-size: 50px; font-weight: bold;'>{round(centrality_mean,3)}</p>", unsafe_allow_html=True)
            st.write(
            "<p style='font-size: 15px; font-weight: bold;'>Total Centrality</p>", unsafe_allow_html=True)


with tab3:
    st.markdown(
        "<div style='height: 30px;'></div>", unsafe_allow_html=True)
    
    df = pd.read_csv(TVL_Category_file)
    fig = px.bar(df, x="Category", y="TVL",
                    title="TVL for each DeFi Protocol Category")
    st.plotly_chart(fig, use_container_width=True)

with tab4:
    st.markdown(
        "<div style='height: 30px;'></div>", unsafe_allow_html=True)
    
    fig = go.Figure()
    df = pd.read_csv(allChains_file)
    for chain in list(df['Chain'].unique()):
        chain_df = df[df['Chain'] == chain]
        fig.add_trace(
            go.Scatter(x=chain_df.Date, y=chain_df.tvl, name=chain))
    fig.update_layout(title="TVL Change over a year for each Chain",
                        xaxis=dict(rangeslider_visible=True))
    st.plotly_chart(fig, use_container_width=True)

