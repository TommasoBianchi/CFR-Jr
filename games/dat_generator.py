import argparse
from utilities import serialization
import goofspiel, kuhn, leduc

#     parser = argparse.ArgumentParser(description='input parser')
#     parser.add_argument('game_instance', type=str, help='game instance to '
#                                                         'be solved: '
#                                                         'kuhn3_3cards, '
#                                                         'kuhn3_4cards')
#     parser.add_argument('solver_type', type=str, help='alg to be employed: '
#                                                       'no_discard')
#     parser.add_argument('-ps', '--pool_size', type=int, default=50, \
#                         help='number of '
#                              'sigmas '
#                              'considered '
#                              'at the same '
#                              'time in the '
#                              'auxiliry '
#                              'tree')
#     parser.add_argument('-n_iter', '--n_iterations_cfr', type=int, default=1000,
#                         help='number of iterations for each regret minimizer')
#     parser.add_argument('-init', '--init_type', type=str, default='random',
#                         help='type of pool init: random')
#     parser.add_argument('-n_iter_fictitious',
#                         '--n_iterations_fictitious_play', type=int,
#                         default=1000)
#
#     args = parser.parse_args()
#
#     game_instance = args.game_instance
# solver_type = args.solver_type

# TODO LEDUC
GAMES = ['kuhn', 'goofspiel']

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='dat generator parser')

    parser.add_argument('game', type=str, help='type of game instance (kuhn, leduc, goofspiel)')
    parser.add_argument('output',type=str, help='where to save the dat file')

    parser.add_argument('--players', '-p', type=int, default=3, help='number of players')
    parser.add_argument('--rank','-r', type=int, default=3, help='rank of the game')

    args = parser.parse_args()

    game = args.game
    assert game in GAMES
    out = args.output
    players = args.players
    rank = args.rank

    t = None

    if game == 'kuhn':
        t = kuhn.build_kuhn_tree(players, rank)
    elif(game == 'goofspiel'):
        t = goofspiel.build_goofspiel_tree(players, rank)

    dat_str = serialization.tree_to_colgen_dat_file(t)

    with open(out, 'w') as fout:
        fout.write(dat_str)
