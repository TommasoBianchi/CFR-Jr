import matplotlib.pyplot as plt

def epsilon_graph(results):
	"""
	Draw graph for the epsilon from the data obtained from a run of SCFR.
	"""

	iteration_counts = list(map(lambda el: el['iteration_number'], results['graph_data']))
	epsilons_graph = list(map(lambda el: max(0, -min(el['epsilon'])), results['graph_data']))
	plt.plot(iteration_counts, epsilons_graph)
	plt.ylabel("Epsilon")
	plt.xlabel("Iteration")
	plt.ylim(bottom = -0.5)
	plt.show()

def comparative_epsilon_graph(results_array):
	"""
	Draw graph for the epsilons from the data obtained from multiple runs of SCFR in a single graph.
	"""

	for res in results_array:
		iteration_counts = list(map(lambda el: el['iteration_number'], res['graph_data']))
		epsilons_graph = list(map(lambda el: max(0, -min(el['epsilon'])), res['graph_data']))
		plt.plot(iteration_counts, epsilons_graph)
	plt.ylabel("Epsilon")
	plt.xlabel("Iteration")
	plt.legend(["Result " + str(i+1) for i in range(len(results_array))])
	plt.ylim(bottom = -0.5)
	plt.show()

def graphs_from_cfr_results(results):
	"""
	Draw graphs from the data obtained from a run of SCFR.
	"""

	absolute_joint_size_graph = list(map(lambda el: el['absolute_joint_size'], results['graph_data']))
	relative_joint_size_graph = list(map(lambda el: el['relative_joint_size'], results['graph_data']))
	max_plan_frequency = list(map(lambda el: el['max_plan_frequency'], results['graph_data']))
	iteration_counts = list(map(lambda el: el['iteration_number'], results['graph_data']))
	
	epsilon_graph(results)

	plt.plot(iteration_counts, absolute_joint_size_graph)
	plt.ylabel("Absolute joint size")
	plt.xlabel("Iteration")
	plt.show()
	plt.plot(iteration_counts, relative_joint_size_graph)
	plt.ylabel("Relative joint size")
	plt.xlabel("Iteration")
	plt.show()
	plt.plot(iteration_counts, max_plan_frequency)
	plt.ylabel("Most frequent joint plan")
	plt.xlabel("Iteration")
	plt.show()