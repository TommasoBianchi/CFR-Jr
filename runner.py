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

def log_line(string):
	log_file = open(log_file_name, "a")
	log_file.write(string + "\n")
	log_file.flush()
	log_file.close()

def log_result_point_callback(results_file_name):
	def __callback(datapoint):
		results_file = open(results_file_name, "r")
		old_data = json.load(results_file)
		results_file.close()
		old_data['data'].append(datapoint)
		results_file = open(results_file_name, "w+")
		results_file.write(json.dumps(old_data))
		results_file.close()
	return __callback

# ----------------------------------------
# Install handler to detect crashes
# ----------------------------------------
import sys
import logging
import traceback

def log_except_hook(*exc_info):
    text = "".join(traceback.format_exception(*exc_info))
    logging.error("Unhandled exception: %s", text)
    log_line("\n\n------Unhandled exception:------\n\n" + text)

sys.excepthook = log_except_hook
# ----------------------------------------

if args.game == 'kuhn':
	kuhn_tree = build_kuhn_tree(num_players, rank)
	log_line("Built a kuhn tree with parameters: " + str(parameters_dict))
	cfr_tree = CFRTree(kuhn_tree)
	
	results_file_name = "results/kuhn/" + str(int(time.time())) + "_" + str(num_players) + "_" + str(rank)
	results_file = open(results_file_name, "w+")
	results_file.write(json.dumps({"parameters": parameters_dict, "data": []}))
	results_file.close()

	res = SolveWithSampleCFR(cfr_tree, number_iterations, bootstrap_iterations = bootstrap_iterations,
							 checkEveryIteration = check_every_iteration, bound_joint_size = bound_joint_size,
							 check_callback = log_result_point_callback(results_file_name))
	log_line("Finished solving.")
	log_line("Time elapsed = " + str(res['tot_time']) + " seconds.\n")
	
	results_file = open(results_file_name, "r")
	old_data = json.load(results_file)
	results_file.close()
	old_data["total_duration"] = res['tot_time']
	old_data["average_iterations_per_second"] = number_iterations / res['tot_time']
	old_data["utility"] = res['utility']
	results_file = open(results_file_name, "w+")
	results_file.write(json.dumps(old_data))
	results_file.close()

if args.game == 'leduc':
	leduc_tree = build_leduc_tree(num_players, num_of_suits, rank, betting_parameters)
	log_line("Built a leduc tree with parameters: " + str(parameters_dict))
	cfr_tree = CFRTree(leduc_tree)

	results_file_name = "results/leduc/" + str(int(time.time())) + "_" + str(num_players) + "_" + str(num_of_suits) + "_" + str(rank)
	results_file = open(results_file_name, "w+")
	results_file.write(json.dumps({"parameters": parameters_dict, "data": []}))
	results_file.close()

	res = SolveWithSampleCFR(cfr_tree, number_iterations, bootstrap_iterations = bootstrap_iterations,
							 checkEveryIteration = check_every_iteration, bound_joint_size = bound_joint_size,
							 check_callback = log_result_point_callback(results_file_name))
	log_line("Finished solving.")
	log_line("Time elapsed = " + str(res['tot_time']) + " seconds.\n")
	
	results_file = open(results_file_name, "r")
	old_data = json.load(results_file)
	results_file.close()
	old_data["total_duration"] = res['tot_time']
	old_data["average_iterations_per_second"] = number_iterations / res['tot_time']
	old_data["utility"] = res['utility']
	results_file = open(results_file_name, "w+")
	results_file.write(json.dumps(old_data))
	results_file.close()

if args.game == 'goofspiel':
	goofspiel_tree = build_goofspiel_tree(num_players, rank, tie_solver)
	log_line("Built a goofspiel tree with parameters: " + str(parameters_dict))
	cfr_tree = CFRTree(goofspiel_tree)

	results_file_name = "results/goofspiel/" + str(int(time.time())) + "_" + str(num_players) + "_" + str(rank)
	results_file = open(results_file_name, "w+")
	results_file.write(json.dumps({"parameters": parameters_dict, "data": []}))
	results_file.close()

	res = SolveWithSampleCFR(cfr_tree, number_iterations, bootstrap_iterations = bootstrap_iterations,
							 checkEveryIteration = check_every_iteration, bound_joint_size = bound_joint_size,
							 check_callback = log_result_point_callback(results_file_name))
	log_line("Finished solving.")
	log_line("Time elapsed = " + str(res['tot_time']) + " seconds.\n")

	results_file = open(results_file_name, "r")
	old_data = json.load(results_file)
	results_file.close()
	old_data["total_duration"] = res['tot_time']
	old_data["average_iterations_per_second"] = number_iterations / res['tot_time']
	old_data["utility"] = res['utility']
	results_file = open(results_file_name, "w+")
	results_file.write(json.dumps(old_data))
	results_file.close()