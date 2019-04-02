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
    deck_probability = 1 / len(deck_permutations)
    information_sets = {}

    for deck in deck_permutations:
        node_known_infos = None# Something
        if node_known_infos in information_sets:
            information_set = information_sets[node_known_infos]
        else:
            information_set = -1

        node = tree.addNode(0, parent = root, probability = deck_probability, 
                         actionName = "TODO", information_set = information_set)

        if information_set == -1:
            information_sets[node_known_infos] = node.information_set

        #build_hanabi_deck_tree(deck, tree, information_sets, node)

    print(len(deck_permutations))

    return tree

# Some possible deck structures:
#
#       1 color and [3, 2, 2, 2, 1] distribution (real one - but single color) -> 75600  deck permutations
#
#       1 color and [2, 1] distribution       -> 3  deck permutations
#       1 color and [3, 2] distribution       -> 10  deck permutations
#       1 color and [2, 2, 1] distribution    -> 30  deck permutations
#       1 color and [3, 2, 1] distribution    -> 60  deck permutations
#       1 color and [3, 2, 2] distribution    -> 210  deck permutations
#       1 color and [3, 2, 2, 1] distribution -> 1680 deck permutations
#       1 color and [4, 2, 2] distribution    -> 420  deck permutations
#
#       2 colors and [3, 1] distribution -> 1120 deck permutations
#       2 colors and [2, 2] distribution -> 2520 deck permutations
#
#       3 colors and [1, 1] distribution -> 720 deck permutations
#
#       5 colors and [3, 2, 2, 2, 1] distribution (real one) -> roughly e+56 deck permutations
#                                 (119362714169794152069667854714196512499836511150699184128 deck permutations)