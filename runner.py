from games.kuhn import build_kuhn_tree
from games.leduc import build_leduc_tree
from games.goofspiel import build_goofspiel_tree, TieSolver

from data_structures.cfr_trees import CFRTree
from cfr_code.sample_cfr import SolveWithSampleCFR

import time
import json
import argparse

parser = argparse.ArgumentParser(description='runner parser')

parser.add_argument('game', type=str, help='type of game instance (kuhn, leduc, goofspiel)', choices=['kuhn','leduc','goofspiel'])

parser.add_argument('--players', '-p', type=int, default=3, help='number of players')
parser.add_argument('--rank', '-r', type=int, default=3, help='rank of the game')
parser.add_argument('--suits', '-s', type=int, default=3, help='number of suits (only for leduc')
parser.add_argument('--betting_parameters', '-bp', type=int, default=[2,4], nargs='*', help='betting parameters (only for leduc')
parser.add_argument('--tie_solver', '-ts', type=str, default='accumulate', help='strategy for solving ties (only for goofspiel)',
					choices=['accumulate','discard_if_all','discard_if_high','discard_always'])

parser.add_argument('--number_iterations', '-t', type=int, default=100000, help='number of iterations to run')
parser.add_argument('--bootstrap_iterations', '-bt', type=int, default=0, help='number of iterations to run without sampling')
parser.add_argument('--check_every_iteration', '-ct', type=int, default=-1, help='every how many iteration to check the epsilon')
parser.add_argument('--bound_joint_size', '-bjs', const=True, nargs='?', help='bound or not the limit of the resulting joint strategy')

parser.add_argument('--logfile', '-log', type=str, default=(str(int(time.time())) + "log.log"))

args = parser.parse_args()
parameters_dict = vars(args)

num_players = args.players
rank = args.rank
num_of_suits = args.suits
betting_parameters = args.betting_parameters
tie_solver = {'accumulate':TieSolver.Accumulate,'discard_if_all':TieSolver.DiscardIfAll,'discard_if_high':TieSolver.DiscardIfHigh,
			  'discard_always':TieSolver.DiscardAlways}[args.tie_solver]

number_iterations = args.number_iterations
bootstrap_iterations = args.bootstrap_iterations
check_every_iteration = args.check_every_iteration
bound_joint_size = args.bound_joint_size != None

log_file_name = args.logfile
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

if args.game == 'kuhn':
	kuhn_tree = build_kuhn_tree(num_players, rank)
	log.write("Built a kuhn tree with parameters: " + str(parameters_dict) + "\n")
	log.flush()
	cfr_tree = CFRTree(kuhn_tree)
	res = SolveWithSampleCFR(cfr_tree, number_iterations, bootstrap_iterations = bootstrap_iterations,
							 checkEveryIteration = check_every_iteration, bound_joint_size = bound_joint_size)
	log.write("Finished solving.\n")
	log.write("Time elapsed = " + str(res['tot_time']) + " seconds.\n\n")
	log.flush()
	
	results_file = open("results/kuhn/" + str(int(time.time())) + "_" + str(num_players) + "_" + str(rank), "w+")

	results_file.write(json.dumps({"parameters": parameters_dict, "data": res['graph_data']}))
	results_file.write("\n\nTotal duration = " + str(res['tot_time']) + " seconds.\n")
	results_file.write("Average iterations per second = " + str(number_iterations / res['tot_time']) + "\n")
	results_file.close()

if args.game == 'leduc':
	leduc_tree = build_leduc_tree(num_players, num_of_suits, rank, betting_parameters)
	log.write("Built a leduc tree with parameters: " + str(parameters_dict) + "\n")
	log.flush()
	cfr_tree = CFRTree(leduc_tree)
	res = SolveWithSampleCFR(cfr_tree, number_iterations, bootstrap_iterations = bootstrap_iterations,
							 checkEveryIteration = check_every_iteration, bound_joint_size = bound_joint_size)
	log.write("Finished solving.\n")
	log.write("Time elapsed = " + str(res['tot_time']) + " seconds.\n\n")
	log.flush()
	
	results_file = open("results/leduc/" + str(int(time.time())) + "_" + str(num_players) + "_" + str(num_of_suits) \
						+ "_" + str(rank), "w+")

	results_file.write(json.dumps({"parameters": parameters_dict, "data": res['graph_data']}))
	results_file.write("\n\nTotal duration = " + str(res['tot_time']) + " seconds.\n")
	results_file.write("Average iterations per second = " + str(number_iterations / res['tot_time']) + "\n")
	results_file.close()

if args.game == 'goofspiel':
	goofspiel_tree = build_goofspiel_tree(num_players, rank, tie_solver)
	log.write("Built a goofspiel tree with parameters: " + str(parameters_dict) + "\n")
	log.flush()
	cfr_tree = CFRTree(goofspiel_tree)
	res = SolveWithSampleCFR(cfr_tree, number_iterations, bootstrap_iterations = bootstrap_iterations,
							 checkEveryIteration = check_every_iteration, bound_joint_size = bound_joint_size)
	log.write("Finished solving.\n")
	log.write("Time elapsed = " + str(res['tot_time']) + " seconds.\n\n")
	log.flush()
	
	results_file = open("results/goofspiel/" + str(int(time.time())) + "_" + str(num_players) + "_" + str(rank), "w+")

	results_file.write(json.dumps({"parameters": parameters_dict, "data": res['graph_data']}))
	results_file.write("\n\nTotal duration = " + str(res['tot_time']) + " seconds.\n")
	results_file.write("Average iterations per second = " + str(number_iterations / res['tot_time']) + "\n")
	results_file.close()


log.close()