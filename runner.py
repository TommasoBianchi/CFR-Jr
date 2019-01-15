from games.kuhn import build_kuhn_tree
from games.leduc import build_leduc_tree
from games.goofspiel import build_goofspiel_tree

from data_structures.cfr_trees import CFRTree
from cfr_code.sample_cfr import SolveWithSampleCFR

import time
import json

log_file_name = "results/" + str(int(time.time())) + "log.log"

log = open(log_file_name, "a")

# ----------------------------------------
# Install handler to detect crashes
# ----------------------------------------
import sys
import logging
import traceback

def log_except_hook(*exc_info):
    text = "".join(traceback.format_exception(*exc_info))
    logging.error("Unhandled exception: %s", text)
    log.write("\n\n------Unhandled exception:------\n\n" + text)

sys.excepthook = log_except_hook
# ----------------------------------------

kuhn_parameters = []

for players in range(2, 4):
	for rank in range(2, 7):
		kuhn_parameters.append({
				"num_players": players,
				"rank" : rank,
				"number_iterations": 1000000,
				"bootstrap_iterations": 10000,
				"check_every_iteration": 10000,
				"bound_joint_size": False
			})

leduc_parameters = []

for players in range(2, 4):
	for num_of_ranks in range(2, 5):
		leduc_parameters.append({
				"num_players": players,
				"num_of_suits" : 2,
				"num_of_ranks" : num_of_ranks,
				"betting_parameters" : [2, 4],
				"number_iterations": 1000000,
				"bootstrap_iterations": 10000,
				"check_every_iteration": 10000,
				"bound_joint_size": False
			})

goofspiel_parameters = []

for players in range(2, 4):
	for rank in range(2, 5):
		goofspiel_parameters.append({
				"num_players": players,
				"rank" : rank,
				"number_iterations": 1000000,
				"bootstrap_iterations": 10000,
				"check_every_iteration": 10000,
				"bound_joint_size": False
			})

for p in kuhn_parameters:
	kuhn_tree = build_kuhn_tree(p["num_players"], p["rank"])
	log.write("Built a kuhn tree with parameters: " + str(p) + "\n")
	log.flush()
	cfr_tree = CFRTree(kuhn_tree)
	res = SolveWithSampleCFR(cfr_tree, p["number_iterations"], bootstrap_iterations = p["bootstrap_iterations"],
							 checkEveryIteration = p["check_every_iteration"], bound_joint_size = p["bound_joint_size"])
	log.write("Finished solving.\n\n")
	log.flush()
	
	results_file = open("results/kuhn/" + str(int(time.time())), "w+")

	results_file.write(json.dumps({"parameters": p, "data": res['graph_data']}))
	results_file.close()

for p in leduc_parameters:
	leduc_tree = build_leduc_tree(p["num_players"], p["num_of_suits"], p["num_of_ranks"], p["betting_parameters"])
	log.write("Built a leduc tree with parameters: " + str(p) + "\n")
	log.flush()
	cfr_tree = CFRTree(leduc_tree)
	res = SolveWithSampleCFR(cfr_tree, p["number_iterations"], bootstrap_iterations = p["bootstrap_iterations"],
							 checkEveryIteration = p["check_every_iteration"], bound_joint_size = p["bound_joint_size"])
	log.write("Finished solving.\n\n")
	log.flush()
	
	results_file = open("results/leduc/" + str(int(time.time())), "w+")

	results_file.write(json.dumps({"parameters": p, "data": res['graph_data']}))
	results_file.close()

for p in goofspiel_parameters:
	goofspiel_tree = build_goofspiel_tree(p["num_players"], p["rank"])
	log.write("Built a goofspiel tree with parameters: " + str(p) + "\n")
	log.flush()
	cfr_tree = CFRTree(goofspiel_tree)
	res = SolveWithSampleCFR(cfr_tree, p["number_iterations"], bootstrap_iterations = p["bootstrap_iterations"],
							 checkEveryIteration = p["check_every_iteration"], bound_joint_size = p["bound_joint_size"])
	log.write("Finished solving.\n\n")
	log.flush()
	
	results_file = open("results/goofspiel/" + str(int(time.time())), "w+")

	results_file.write(json.dumps({"parameters": p, "data": res['graph_data']}))
	results_file.close()


log.close()