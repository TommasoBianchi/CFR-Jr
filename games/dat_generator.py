import argparse
from utilities import serialization
import goofspiel, kuhn, leduc

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
