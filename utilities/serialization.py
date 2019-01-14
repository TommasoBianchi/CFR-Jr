from functools import reduce
import itertools
from data_structures.cfr_trees import CFRTree

def tree_to_colgen_dat_file(tree, compressSequenceNames = True):
    """
    Given a tree, build a string representing a dat file for the colgen algorithm ampl implementation.
    If compressSequenceNames is True, all sequences are replaced by unique ids (to save disk space); otherwise,
    sequences are generated as a string containing all the id of the information sets and relative actions.
    """

    cfr_tree = CFRTree(tree)

    root = cfr_tree.root

    s = ""

    max_sequence_id = 0
    sequence_string_to_id = {}

    def sequence_to_string(sequence, player):
        if(len(sequence) == 0):
            string = "empty_seq_" + str(player)
        else:
            string = reduce(lambda x, y: x + y, map(lambda seq: 'a' + str(seq[0]) + "." + str(seq[1]), sequence.items()))

        if(not compressSequenceNames):
            return string

        if(string in sequence_string_to_id):
            return str(sequence_string_to_id[string])
        else:
            nonlocal max_sequence_id
            sequence_string_to_id[string] = max_sequence_id
            max_sequence_id += 1
            return str(max_sequence_id - 1)

    all_nodes = reduce(lambda x, y: x + y.nodes, cfr_tree.information_sets.values(), [])
    all_leaves = list(filter(lambda n: n.isLeaf(), reduce(lambda x, y: x + y.children, all_nodes, [])))
    all_nodes = all_nodes + all_leaves
    all_joint_sequences = [()]

    Q_holder = []

    for p in range(cfr_tree.numOfPlayers):

        # --------------------------
        # Print sequences
        # --------------------------
        Q_raw = list(filter(lambda q: q != {}, map(lambda n: n.base_node.getSequence(p), all_nodes)))

        # Remove duplicates
        Q = [{}] + [dict(t) for t in {tuple(d.items()) for d in Q_raw}]
        Q_holder.append(Q)

        s += "#|Q" + str(p) + "| = " + str(len(Q)) + "\n\n"

        s += "set Q" + str(p) + " ="
        for q in Q:
            s += " " + sequence_to_string(q, p)
        s += ";\n\n"

        # --------------------------
        # Print information sets
        # --------------------------
        H = cfr_tree.infosets_by_player[p]

        s += "#|H" + str(p) + "| = " + str(len(H) + 1) + "\n\n"

        s += "set H" + str(p) + " = empty_is_" + str(p) + " " + reduce(lambda x, y: x + " " + str(y.id), H, "") + ";\n\n"

        # --------------------------
        # Print F matrix and f vector
        # --------------------------
        s += "param F" + str(p) + ":\n"

        for q in Q:
            s += sequence_to_string(q, p) + " "
        s += ":=\nempty_is_" + str(p) + " 1" + (" 0" * (len(Q))) + "\n"
        for h in H:
            s += str(h.id) + " "
            h_seq = h.nodes[0].base_node.getSequence(p)
            h_next_sequences = []
            for a in range(h.action_count):
                seq_copy = h_seq.copy()
                seq_copy[h.id] = a
                h_next_sequences.append(seq_copy)
            for q in Q:
                if(q == h_seq):
                    s += "-1 "
                elif(q in h_next_sequences):
                    s += "1 "
                else:
                    s += "0 "
            s += "\n"
        s += ";\n\n"

        s += "param f" + str(p) + " :=\nempty_is_" + str(p) + " 1\n"
        for h in H:
            s += str(h.id) + " 0\n"
        s += ";\n\n"


        # all_joint_sequences = [js + (q,) for js in all_joint_sequences for q in Q ]
    all_joint_sequences=[]

    for seq0 in Q_holder[0]:
        for seq1 in Q_holder[1]:
            for seq2 in Q_holder[2]:
                all_joint_sequences.append((seq0, seq1, seq2))

    def __js_len(js):
        len_js = 0
        for p in range(len(js)):
            len_js += len(js[p])
        return len_js


    minimal_sequences = {}
    for js in all_joint_sequences:
        terminals = root.reachableTerminals(js)
        len_js = __js_len(js)
        for terminal in terminals:
            if terminal not in minimal_sequences:
                minimal_sequences[terminal] = js
            else:
                if(len_js < __js_len(minimal_sequences[terminal])):
                    minimal_sequences[terminal] = js

    # --------------------------
    # Print utilities
    # --------------------------
    for player in range(cfr_tree.numOfPlayers):
        s += "param U" + str(player) + " default 0 :=\n"
        for js in minimal_sequences.values():
            expected_utility = root.utilityFromJointSequence(js)
            for p in range(cfr_tree.numOfPlayers):
                s += sequence_to_string(js[p], p) + " "
            s += str(expected_utility[player]) + "\n"
        s += ";\n\n"


    return s
