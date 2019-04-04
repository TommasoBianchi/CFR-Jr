import matplotlib.pyplot as plt
import networkx as nx
from networkx.drawing.nx_agraph import graphviz_layout

from data_structures.cfr_trees import CFRTree

def draw_tree(tree, title = 'Tree'):
	def add_nodes_to_graph(graph, node):
	    graph.add_node(node.id)
	    
	    for child in node.children:
	        add_nodes_to_graph(graph, child)
	        graph.add_edge(node.id, child.id)

	def add_infoset_edges_to_graph(graph, tree):
		cfr_tree = CFRTree(tree)

		for infoset in cfr_tree.information_sets.values():
			nodes = infoset.nodes
			nodes.sort(key = lambda el: el.base_node.id)

			for i in range(0, len(nodes) - 1):
				graph.add_edge(nodes[i].id, nodes[i+1].id)

	G = nx.Graph()
	add_nodes_to_graph(G, tree.root)

	plt.title(title)
	pos = graphviz_layout(G, prog='dot')
	
	add_infoset_edges_to_graph(G, tree)

	nx.draw(G, pos, with_labels = True)