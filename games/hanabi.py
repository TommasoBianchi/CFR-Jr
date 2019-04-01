from data_structures.trees import Tree, Node, ChanceNode
from functools import reduce
from games.utilities import all_permutations, pair_to_number, number_to_pair

def build_hanabi_tree(num_players, num_colors, color_distribution, compress_card_representation = False):
    """
    Build a tree for the game of Hanabi with a given number of players, colors and with a given distribution of
    cards inside each color (e.g. [3, 2, 2, 2, 1] is the common one, with three 1s, two 2s etc for each color).
    """

    root = ChanceNode(0)

    tree = Tree(num_players, 0, root)

    all_cards = []
    for i in range(len(color_distribution)):
        for _ in range(color_distribution[i]):
            for c in range(num_colors):
                card = (i + 1, c + 1)
                if compress_card_representation:
                    card = pair_to_number(card)
                all_cards.append(card)

    deck_permutations = all_permutations(all_cards)

    return len(deck_permutations)

# Possible deck structures:
#
#       1 color and [3, 2, 2] distribution    -> 72  deck permutations
#       1 color and [3, 2, 2, 1] distribution -> 288 deck permutations
#       1 color and [4, 2, 2] distribution    -> 96  deck permutations
#
#       2 colors and [3, 1] distribution -> 216 deck permutations
#       2 colors and [2, 2] distribution -> 384 deck permutations
#       2 colors and [3, 1] distribution -> 216 deck permutations
#       2 colors and [3, 1] distribution -> 216 deck permutations
#
#       3 colors and [1, 1] distribution -> 720 deck permutations