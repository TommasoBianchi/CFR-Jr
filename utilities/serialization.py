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
        if(sequence == {}):
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
    
    for p in range(cfr_tree.numOfPlayers):
        
        # --------------------------
        # Print sequences
        # --------------------------
        Q_raw = list(filter(lambda q: q != {}, map(lambda n: n.base_node.getSequence(p), all_nodes)))

        # Remove duplicates
        Q = [{}] + [dict(t) for t in {tuple(d.items()) for d in Q_raw}]

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

        all_joint_sequences = [js + (q,) for js in all_joint_sequences for q in Q + [{}]]

        # --------------------------
        # Print utilities
        # --------------------------
    for player in range(cfr_tree.numOfPlayers):
        s += "param U" + str(player) + ":\n"
        for js in all_joint_sequences:
            node = root.base_node.getNodeFollowJointSequence(js)
            for p in range(cfr_tree.numOfPlayers):
                s += sequence_to_string(js[p], p) + " "
            s += str(node.utility[player] if node.isLeaf() else 0) + "\n"
        s += ";\n\n"

    return s