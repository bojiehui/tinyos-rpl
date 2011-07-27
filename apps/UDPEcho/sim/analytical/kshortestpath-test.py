import networkx as nx
import matplotlib.pyplot as plt

from sim.analytical.kshortestpaths import *

# G = nx.DiGraph()

# G.add_node(1)
# G.add_node(2)
# G.add_node(3)
# G.add_node(4)

# G.add_edge(1,2,color='k')
# G.add_edge(2,3,color='k')
# G.add_edge(3,4,color='k')

# G.add_edge(1,3,color='k')
# G.add_edge(2,4,color='k')

# #G.add_edge(1,4,color='k')

G2 = nx.house_graph()
#print G2
#print G2.nodes()
#print G2.edges()

G3 = nx.DiGraph()
G3.add_edge( 0,  1, weight= 2)
G3.add_edge( 1,  2, weight=20)
G3.add_edge( 2,  3, weight=14)

G3.add_edge( 4,  5, weight= 9)
G3.add_edge( 5,  6, weight=10)
G3.add_edge( 6,  7, weight=25)

G3.add_edge( 8,  9, weight=18)
G3.add_edge( 9, 10, weight= 8)
G3.add_edge(10, 11, weight=11)

G3.add_edge( 0,  4, weight=13)
G3.add_edge( 4,  8, weight=15)

G3.add_edge( 1,  5, weight=27)
G3.add_edge( 5,  9, weight=20)

G3.add_edge( 2,  6, weight=14)
G3.add_edge( 6, 10, weight=12)

G3.add_edge( 3,  7, weight=15)
G3.add_edge( 7, 11, weight= 7)
print G3.nodes()
print G3.edges()

shortestpath = nx.dijkstra_path(G3, 0, 11)
print("Shortest path "+str(shortestpath))

plt.figure(1,figsize=(8,8))

# prev_node = None
# for node in shortestpath:
#     if prev_node == None:
#         prev_node = node
#         continue
#     G[prev_node][node]['color']='r'
#     prev_node = node

# elarge=[(u,v) for (u,v,d) in G.edges(data=True) if d['color'] == 'r']
# esmall=[(u,v) for (u,v,d) in G.edges(data=True) if d['color'] != 'r']

#pos=nx.spring_layout(G)
nx.draw_networkx(G3)
#nx.draw_networkx_nodes(G,pos)
#nx.draw_networkx_edges(G,pos,edgelist=elarge,edge_color='r')
#nx.draw_networkx_edges(G,pos,edgelist=esmall,edge_color='k')

plt.savefig("graph.png",dpi=75)

k_shortest_paths(G3, 0, 11, 10)
