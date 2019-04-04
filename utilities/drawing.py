import matplotlib.pyplot as plt
import networkx as nx
from networkx.drawing.nx_agraph import graphviz_layout

def draw_tree(tree, title = 'Tree'):
	def add_nodes_to_graph(graph, node):
	    graph.add_node(node.id)
	    
	    for child in node.children:
	        add_nodes_to_graph(graph, child)
	        graph.add_edge(node.id, child.id)

	G = nx.Graph()
	add_nodes_to_graph(G, tree.root)

	plt.title(title)
	pos = graphviz_layout(G, prog='dot')
	nx.draw(G, pos, with_labels = True)