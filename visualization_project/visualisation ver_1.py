import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt


df = pd.read_csv("/Users/admin/Desktop/파이썬 실습/파이썬 프로그래밍/visualization project/data/chains_data_v4.csv")
df_1 = df[['chain','protocol']]

# Make a list of the chains, we'll use it later
chains = list(df_1.chain.unique())
chains
# Make a list of the protocols, we'll use it later
protocols = list(df.protocol.unique())
protocols
# Make a label
dict(zip(chains, chains))


####
plt.figure(figsize=(12, 12))

# 1. Create the graph
G = nx.Graph()
G = nx.from_pandas_edgelist(df_1, 'chain', 'protocol')
# 2. Create a layout for our nodes 
layout = nx.spring_layout(G, iterations=50)

# 3. Draw the parts we want
# Edges thin and grey
# Protocols small and grey
# Chains sized according to their number of connections
# Chains blue
# Labels for chains ONLY
# Protocols which are highly connected are a highlighted color

# Go through every chain name, ask the graph how many
# connections it has. Multiply that by 80 to get the circle size
chain_size = [G.degree(chain) * 30 for chain in chains]
nx.draw_networkx_nodes(G, 
                       layout, 
                       nodelist=chains, 
                       node_size=chain_size, # a LIST of sizes, based on g.degree
                       node_color='lightblue')

# Draw EVERYONE
nx.draw_networkx_nodes(G, layout, nodelist=protocols, node_color='#cccccc', node_size=20)

# Draw POPULAR Protocols
popular_protocols = [protocol for protocol in protocols if G.degree(protocol) > 1]
nx.draw_networkx_nodes(G, layout, nodelist=popular_protocols, node_color='orange', node_size=20)

nx.draw_networkx_edges(G, layout, width=1, edge_color="#cccccc")

node_labels = dict(zip(chains, chains))
nx.draw_networkx_labels(G, layout, labels=node_labels, font_size = 5)

# 4. Turn off the axis because I know you don't want it
plt.axis('off')

plt.title("OMG")

plt.show()