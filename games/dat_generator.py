import argparse
from utilities import serialization
import goofspiel, kuhn, leduc

GAMES = ['kuhn', 'goofspiel', 'leduc']
# tie breacking rule for goofspiel
# 0: accumulate, 1: discard if all, 2: discard if high, 3: discard always
TIES = [0,1,2,3,]

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='dat generator parser')

    parser.add_argument('game', type=str, help='type of game instance (kuhn, leduc, goofspiel)')
    parser.add_argument('output',type=str, help='where to save the dat file')

    parser.add_argument('--players', '-p', type=int, default=3, help='number of players')
    parser.add_argument('--rank','-r', type=int, default=3, help='rank of the game')

    parser.add_argument('--tie_breaking', '-t', type=int, default=0, help='tie breacking for Goofspiel games.---0: accumulate; 1: discardIfAll; 2: discardIfHigh; 3: discardAlways.')

    parser.add_argument('--n_suits','-s',type=int,default=3,help='number of suits for a Leduc game')
    parser.add_argument('--first_bet_param','-fb', type=int, default=2, help='betting value for the first betting round')
    parser.add_argument('--second_bet_param', '-sb', type=int, default=4, help='betting value for the second betting round')

    args = parser.parse_args()

    game = args.game
    assert game in GAMES
    out = args.output
    players = args.players
    rank = args.rank
    tie_breaking = args.tie_breaking
    assert tie_breaking in TIES
    n_suits = args.n_suits
    assert n_suits > 0
    fb = args.first_bet_param
    sb = args.second_bet_param

    t = None

    if game == 'kuhn':
        t = kuhn.build_kuhn_tree(players, rank)
    elif(game == 'goofspiel'):
        t = goofspiel.build_goofspiel_tree(players, rank, tie_solver=tie_breaking)
    elif(game == 'leduc'):
        t = leduc.build_leduc_tree(players, n_suits, rank, [fb, sb,])

    dat_str = serialization.tree_to_colgen_dat_file(t)

    with open(out, 'w') as fout:
        fout.write(dat_str)
