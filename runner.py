from games.kuhn import build_kuhn_tree
from games.leduc import build_leduc_tree
from games.goofspiel import build_goofspiel_tree, TieSolver
from games.hanabi import build_hanabi_tree

from data_structures.trees import randomTree
from data_structures.cfr_trees import CFRTree
from cfr_code.sample_cfr import SolveWithSampleCFR
from cfr_code.cfr import SolveWithCFR
from cfr_code.reconstruction_cfr import SolveWithReconstructionCFR
from utilities.serialization import tree_to_colgen_dat_file

import time
import json
import argparse

parser = argparse.ArgumentParser(description='runner parser')

parser.add_argument('game', type=str, help='type of game instance (random, kuhn, leduc, goofspiel, hanabi)', choices=['kuhn','leduc','goofspiel','random','hanabi'])

parser.add_argument('--players', '-p', type=int, default=3, help='number of players')
parser.add_argument('--rank', '-r', type=int, default=3, help='rank of the game')
parser.add_argument('--suits', '-s', type=int, default=3, help='number of suits (only for leduc')
parser.add_argument('--betting_parameters', '-bp', type=int, default=[2,4], nargs='*', help='betting parameters (only for leduc')
parser.add_argument('--tie_solver', '-ts', type=str, default='accumulate', help='strategy for solving ties (only for goofspiel)',
                    choices=['accumulate','discard_if_all','discard_if_high','discard_always'])
parser.add_argument('--branching_factor', '-bf', type=int, default=2, help='branching factor of the tree (only for random)')
parser.add_argument('--depth', '-d', type=int, default=4, help='depth of the tree (only for random)')
parser.add_argument('--iset_probability', '-ip', type=float, default=1, help='information set probability (only for random)')

parser.add_argument('--cards_per_player', '-cpp', type=int, default=1, help='how many cards are dealt to each player (only for hanabi')
parser.add_argument('--starting_clue_tokens', '-sct', type=int, default=1, help='how many clue tokens are available at the beginning of the game (only for hanabi)')
parser.add_argument('--color_distribution', '-cd', type=int, default=[1,1], nargs='*', help='distribution of card values inside of a single color/suit (only for hanabi')

parser.add_argument('--number_iterations', '-t', type=int, default=100000, help='number of iterations to run')
parser.add_argument('--bootstrap_iterations', '-bt', type=int, default=0, help='number of iterations to run without sampling')
parser.add_argument('--check_every_iteration', '-ct', type=int, default=-1, help='every how many iterations to check the epsilon')
parser.add_argument('--bound_joint_size', '-bjs', const=True, nargs='?', help='bound or not the limit of the resulting joint strategy')
parser.add_argument('--reconstruct_every_iteration', '-rei', type=int, default=1, help='every how many iterations to reconstruct a joint from the marginals')
parser.add_argument('--reconstruct_not_optimal_plan', '-rnop', const=True, nargs='?', help='do not try to find the optimal plan to reconstruct at each reconstruction iteration')

parser.add_argument('--algorithm', '-a', type=str, default='scfr', choices=['scfr', 'cfr', 'cfr+', 'rcfr'], help='algorithm to be used')

parser.add_argument('--logfile', '-log', type=str, default=(str(int(time.time())) + "log.log"), help='file in which to log events and errors')
parser.add_argument('--results', '-res', type=str, default='results/', help='folder where to put the results (must contain subfolders for each game')

args = parser.parse_args()
parameters_dict = vars(args)

num_players = args.players
rank = args.rank
num_of_suits = args.suits
betting_parameters = args.betting_parameters
tie_solver = {'accumulate':TieSolver.Accumulate,'discard_if_all':TieSolver.DiscardIfAll,'discard_if_high':TieSolver.DiscardIfHigh,
              'discard_always':TieSolver.DiscardAlways}[args.tie_solver]
cards_per_player = args.cards_per_player
starting_clue_tokens = args.starting_clue_tokens
color_distribution = args.color_distribution

number_iterations = args.number_iterations
bootstrap_iterations = args.bootstrap_iterations
check_every_iteration = args.check_every_iteration
bound_joint_size = args.bound_joint_size != None
reconstructEveryIteration = args.reconstruct_every_iteration
reconstructWithOptimalPlan = args.reconstruct_not_optimal_plan == None

log_file_name = args.logfile
results_directory = args.results

def log_line(string):
    log_file = open(log_file_name, "a")
    log_file.write(time.strftime("%Y.%m.%d %H:%m:%S: ") + string + "\n")
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

def solve_function(cfr_tree):
    if args.algorithm == 'scfr':
        return SolveWithSampleCFR(cfr_tree, number_iterations, bootstrap_iterations = bootstrap_iterations,
                             checkEveryIteration = check_every_iteration, bound_joint_size = bound_joint_size,
                             check_callback = log_result_point_callback(results_file_name))
    if args.algorithm == 'cfr' or args.algorithm == 'cfr+':
        return SolveWithCFR(cfr_tree, number_iterations, checkEveryIteration = check_every_iteration,
                            check_callback = log_result_point_callback(results_file_name), use_cfr_plus = args.algorithm == 'cfr+')
    if args.algorithm == 'rcfr':
        return SolveWithReconstructionCFR(cfr_tree, number_iterations, checkEveryIteration = check_every_iteration,
                                          reconstructEveryIteration = reconstructEveryIteration,
                                          reconstructWithOptimalPlan = reconstructWithOptimalPlan,
                                          check_callback = log_result_point_callback(results_file_name))

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
    
    results_file_name = results_directory + "kuhn/" + str(int(time.time())) + "_" + str(num_players) + "_" + str(rank)
    results_file = open(results_file_name, "w+")
    results_file.write(json.dumps({"parameters": parameters_dict, "data": []}))
    results_file.close()

    res = solve_function(cfr_tree)
    log_line("Finished solving with " + args.algorithm + ".")
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

    results_file_name = results_directory + "leduc/" + str(int(time.time())) + "_" + str(num_players) + "_" + str(num_of_suits) + "_" + str(rank)
    results_file = open(results_file_name, "w+")
    results_file.write(json.dumps({"parameters": parameters_dict, "data": []}))
    results_file.close()

    res = solve_function(cfr_tree)
    log_line("Finished solving with " + args.algorithm + ".")
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

    results_file_name = results_directory + "goofspiel/" + str(int(time.time())) + "_" + str(num_players) + "_" + str(rank)
    results_file = open(results_file_name, "w+")
    results_file.write(json.dumps({"parameters": parameters_dict, "data": []}))
    results_file.close()

    res = solve_function(cfr_tree)
    log_line("Finished solving with " + args.algorithm + ".")
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

if args.game == 'random':
    random_tree = randomTree(args.depth, args.branching_factor, args.iset_probability, num_players,
                             min_utility = 0, max_utility = 1, int_utility = False)
    log_line("Built a random tree with parameters: " + str(parameters_dict))
    cfr_tree = CFRTree(random_tree)

    results_file_name = results_directory + "random/" + str(int(time.time())) + "_" + str(num_players) + "_" + str(args.depth) + \
                                "_" + str(args.branching_factor)
    results_file = open(results_file_name, "w+")
    results_file.write(json.dumps({"parameters": parameters_dict, "data": []}))
    results_file.close()

    with open(results_file_name + '.dat', 'w') as f:
        f.write(tree_to_colgen_dat_file(random_tree))
    log_line("Dat file created (for random tree).")

    res = solve_function(cfr_tree)
    log_line("Finished solving with " + args.algorithm + ".")
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

if args.game == 'hanabi':
    hanabi_tree = build_hanabi_tree(num_players, num_of_suits, color_distribution, cards_per_player, starting_clue_tokens)
    log_line("Built a hanabi tree with parameters: " + str(parameters_dict))
    cfr_tree = CFRTree(hanabi_tree)

    string_description = str(num_players) + '_' + str(num_of_suits) + '_' + str(color_distribution) + \
                        '_' + str(cards_per_player) + '_' + str(starting_clue_tokens)   
    results_file_name = results_directory + "hanabi/" + str(int(time.time())) + "_" + string_description
    results_file = open(results_file_name, "w+")
    results_file.write(json.dumps({"parameters": parameters_dict, "data": []}))
    results_file.close()

    res = solve_function(cfr_tree)
    log_line("Finished solving with " + args.algorithm + ".")
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