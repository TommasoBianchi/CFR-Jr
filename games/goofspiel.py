from data_structures.trees import Tree, Node, ChanceNode
from functools import reduce

def build_goofspiel_tree(num_players, rank):
    """
    Build a tree for the game of Goofspiel with a given number of players and a given number of ranks in the deck (i.e. how
    many cards).
    """

    root = ChanceNode(0)

    tree = Tree(num_players, 0, root)

    hands = all_permutations(list(range(1, rank+1)))
    hand_probability = 1 / len(hands)
    all_nodes = []

    for hand in hands:
        n = tree.addNode(0, parent = root, probability = hand_probability, actionName = str(hand))
        n.known_information = (0, hand[:1], [[] for p in range(num_players)])
        all_nodes.append(n)
        all_nodes += build_goofspiel_hand_tree(hand, [list(range(1, rank+1)) for p in range(num_players)],
                                  [[] for p in range(num_players)], 0, 1, n, tree)

    # Merge nodes into infosets based on the available information at each node
    for i1 in range(len(all_nodes)):
        for i2 in range(i1+1, len(all_nodes)):
            if(all_nodes[i1].player != all_nodes[i2].player or all_nodes[i1].isLeaf() or all_nodes[i2].isLeaf()):
                continue
            if(all_nodes[i1].known_information == all_nodes[i2].known_information):
                iset_id = min(all_nodes[i1].information_set, all_nodes[i2].information_set)
                all_nodes[i1].information_set = iset_id
                all_nodes[i2].information_set = iset_id
            
    return tree

def build_goofspiel_hand_tree(hand, remaining_cards, played_cards, current_round, current_player, current_node, tree):
    """
    Recursively build the subtree for the Kuhn game where the hand is fixed.
    """

    num_players = tree.numOfPlayers
    if(current_player == num_players-1):
        next_player = 0
        next_round = current_round + 1
    else:
        next_player = current_player + 1
        next_round = current_round
        
    current_player_cards = remaining_cards[current_player].copy()

    # Create a leaf as a children of the last effective decision node (there is no decision for players that
    # have only their last card in hand)
    if(len(remaining_cards[current_player]) == 2 and len(remaining_cards[next_player]) == 1):
        for card in current_player_cards:
            actionName = "p" + str(current_node.player) + "c" + str(card)
            remaining_cards[current_player].remove(card)
            played_cards[current_player].append(card)
            final_played_cards = [played_cards[i] + remaining_cards[i] for i in range(len(played_cards))]
            l = tree.addLeaf(parent = current_node, utility = goofspiel_utility(hand, final_played_cards))
            remaining_cards[current_player].append(card)
            played_cards[current_player].remove(card)
        return [l]

    information_set = -1
    nodes = []

    for card in current_player_cards:
        actionName = "p" + str(current_node.player) + "c" + str(card)
        n = tree.addNode(current_player, information_set, parent = current_node, actionName = actionName)
        n.known_information = (current_round, hand[:current_round+1], [c[:current_round] for c in played_cards])
        nodes.append(n)
        remaining_cards[current_player].remove(card)
        played_cards[current_player].append(card)
        nodes += build_goofspiel_hand_tree(hand, remaining_cards, played_cards, next_round, next_player, n, tree)
        remaining_cards[current_player].append(card)
        played_cards[current_player].remove(card)

    return nodes

def build_all_possible_hands(num_players, ranks):
    """
    Build all the possible hands for the game of Goofspiel with a given number of players and a given set of cards.
    """

    perm = all_permutations(range(1, ranks+1))

    if(num_players == 0):
        return list(map(lambda el: [el], perm))

    hands = []
    smaller_hands = build_all_possible_hands(num_players-1, ranks)

    for p in perm:
        for hand in smaller_hands:
            hands.append(hand + [p])

    return hands

def all_permutations(items):
    """
    Build all the possible permutations of a set of items.
    """

    if(len(items) == 0):
        return [[]]

    permutations = []

    for item in items:
        other_items = list(filter(lambda el: el != item, items))
        permutations_of_other = all_permutations(other_items)
        for p in permutations_of_other:
            p.append(item)
            permutations.append(p)

    return permutations

def goofspiel_utility(hand, moves):
    """
    Get the utility of a Goofspiel game given the hand and how the players have played.
    """

    num_players = len(moves)
    u = [0] * num_players
    additional_utility = 0

    for i in range(len(hand)):
        round_moves = [moves[p][i] for p in range(num_players)]
        winner = winner_player(round_moves)

        if(winner == -1):
            additional_utility += hand[i]
        else:
            u[winner] += hand[i] + additional_utility
            additional_utility = 0

    return u

def winner_player(round_moves):
    """
    Calculate the winner player given the cards that were played in a round.
    """

    moves_dict = {}
    for p in range(len(round_moves)):
        move = round_moves[p]
        if(move in moves_dict):
            moves_dict[move].append(p)
        else:
            moves_dict[move] = [p]

    single_moves = list(filter(lambda el: len(el[1]) == 1, moves_dict.items()))

    if(len(single_moves) == 0):
        return -1

    winner = max(single_moves, key = lambda el: el[0])[1][0]

    return winner