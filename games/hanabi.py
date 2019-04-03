from data_structures.trees import Tree, Node, ChanceNode
from functools import reduce
from games.utilities import all_permutations, pair_to_number, number_to_pair

class HanabiState:
    def __init__(self, remaining_deck, player_hands, cards_in_play, discarded_cards, clue_tokens_available, 
                 clue_history, player_clued_hands):
        self.remaining_deck = remaining_deck
        self.player_hands = player_hands
        self.cards_in_play = cards_in_play
        self.discarded_cards = discarded_cards
        self.clue_tokens_available = clue_tokens_available
        self.clue_history = clue_history
        self.player_clued_hands = player_clued_hands

    def toPlayerState(self, player):
        player_visible_hands = self.player_hands[:player] + [self.player_clued_hands[player]] + \
                                self.player_hands[player+1:]
        return (player_visible_hands, self.cards_in_play, self.discarded_cards, 
                self.clue_tokens_available, self.clue_history)

    def getLegalActions(self, player):
        return []

    def getChildState(self, action):
        return None

    def createBaseState(deck, num_players, cards_per_player, num_colors):
        deck = deck.copy()

        player_hands = []
        for p in range(num_players):
            player_hands.append(deck[:cards_per_player])
            deck = deck[cards_per_player:]

        return HanabiState(remaining_deck = deck, player_hands = player_hands, 
                           cards_in_play = [0 for _ in range(num_colors)], discarded_cards = [], 
                           clue_tokens_available = 1, clue_history = [], 
                           player_clued_hands = [[-1 for _ in range(cards_per_player)] for _ in range(num_players)])                           

def build_hanabi_tree(num_players, num_colors, color_distribution, num_cards_per_player,
                      compress_card_representation = False):
    """
    Build a tree for the game of Hanabi with a given number of players, a given number of cards in each player's
    hand, given cards colors and with a given distribution of cards inside each color (e.g. [3, 2, 2, 2, 1] is 
    the common/regular one, with three 1s, two 2s etc for each color).
    If compress_card_representation is set to True, each card is represented by a single integer number instead
    of a tuple (number, color).
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
        baseState = HanabiState.createBaseState(deck, num_players, num_cards_per_player, num_colors)

        node_known_infos = baseState.toPlayerState(0)
        if node_known_infos in information_sets:
            information_set = information_sets[node_known_infos]
        else:
            information_set = -1

        node = tree.addNode(player = 0, parent = root, probability = deck_probability, 
                         actionName = str(deck), information_set = information_set)

        if information_set == -1:
            information_sets[node_known_infos] = node.information_set

        build_hanabi_state_tree(baseState, tree, information_sets, node, 0)

    return tree

def build_hanabi_state_tree(hanabiState, tree, information_sets, parent_node, current_player):
    actions = hanabiState.getLegalActions(current_player)
    next_player = (current_player + 1) % tree.numOfPlayers

    for action in actions:
        childState = hanabiState.getChildState(action)

        node_known_infos = baseState.toPlayerState(next_player)
        if node_known_infos in information_sets:
            information_set = information_sets[node_known_infos]
        else:
            information_set = -1

        node = tree.addNode(player = next_player, parent = parent_node, 
                            actionName = str(action), information_set = information_set)

        if information_set == -1:
            information_sets[node_known_infos] = node.information_set

        build_hanabi_state_tree(childState, tree, information_sets, node, next_player)



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