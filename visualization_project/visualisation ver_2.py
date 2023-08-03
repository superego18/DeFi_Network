import pandas as pd
import plotly.graph_objects as go
import networkx as nx

df = pd.read_csv("/Users/admin/Desktop/파이썬 실습/파이썬 프로그래밍/visualization project/data/chains_data_v4.csv")
df_1 = df[['chain','protocol']]


# Create a Plotly figure object
fig = go.Figure()

# Create a network graph object
G = nx.from_pandas_edgelist(df_1, 'chain', 'protocol')

# Define the spring layout
pos = nx.spring_layout(G)
  

# Make a list of the chains, we'll use it later
chains = list(df_1.chain.unique())
# Make a list of the protocols, we'll use it later
protocols = list(df.protocol.unique())
# Set chain size
chain_size = [G.degree(chain) * 30 for chain in chains]


# Add the edges to the figure
edge_trace = go.Scatter(x=[], y=[], mode='lines', line=dict(width=0.5, color='#888'))
for edge in G.edges():
    x0, y0 = pos[edge[0]]
    x1, y1 = pos[edge[1]]
    edge_trace['x'] += tuple([x0, x1, None])
    edge_trace['y'] += tuple([y0, y1, None])
fig.add_trace(edge_trace)

# Add the nodes to the chain figure
c_node_traces = []

for node in chains:
    
    trace = go.Scatter(x=[pos[node][0]], y=[pos[node][1]], mode='markers', marker=dict(size= G.degree(node), color='blue'), text = "Chian name: " + node + ".\n # of protocols: " + str(G.degree(node)), hoverinfo='text')
    c_node_traces.append(trace) 
fig.add_traces(c_node_traces)

# Add the nodes to the chain figure
p_node_traces = []
for node in protocols:
    trace = go.Scatter(x=[pos[node][0]], y=[pos[node][1]], mode='markers', marker=dict(size= 5, color='red'), text=node, hoverinfo='text')
    p_node_traces.append(trace)
fig.add_traces(p_node_traces)



# Customize the figure layout
fig.update_layout(title='Spring Layout Network Graph Example', showlegend=False, xaxis=dict(showticklabels=False, zeroline=False, showgrid=False), yaxis=dict(showticklabels=False, zeroline=False, showgrid=False))
fig.show()



