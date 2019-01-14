from functools import reduce
from data_structures.trees import Tree, Node, Leaf, randomTree
import random
import math
import re
import time

class CFRTree:
    """
    Wrapper around an extensive-form tree for holding additional CFR-related code and data.
    """

    def __init__(self, base_tree):
        """
        Create a CFRTree starting from a base Tree.
        """

        self.root = CFRChanceNode(base_tree.root) if base_tree.root.isChance() else CFRNode(base_tree.root)
        self.information_sets = {}
        self.numOfActions = 0
        self.numOfPlayers = base_tree.numOfPlayers

        nodes_to_expand = [ self.root ]

        while(len(nodes_to_expand) > 0):
            node = nodes_to_expand.pop()

            if(node.isChance()):
                for child in node.children:
                    nodes_to_expand.append(child)
                continue

            iset_id = node.base_node.information_set
            if(iset_id < 0):
                # This is a leaf (or an error has occurred)
                continue

            for child in node.children:
                nodes_to_expand.append(child)
                self.numOfActions += 1

            if(iset_id in self.information_sets):
                node.information_set = self.information_sets[iset_id]
                node.information_set.addNode(node)
            else:
                iset = CFRInformationSet(iset_id, node.player, len(node.children), node.base_node.getSequence(node.player), self)
                iset.addNode(node)
                self.information_sets[iset_id] = iset
                node.information_set = iset

        self.infosets_by_player = []
        for p in range(self.numOfPlayers):
            p_isets = list(filter(lambda i: i.player == p, self.information_sets.values()))
            self.infosets_by_player.append(p_isets)

    def sampleActionPlan(self):
        """
        Sample a joint action plan from the tree (one action per each information set).
        """

        actionPlan = {}
        for id in self.information_sets:
            actionPlan[id] = self.information_sets[id].sampleAction()
        return actionPlan

    def getUtility(self, joint):
        """
        Get the utility obtained by the players when playing a given joint strategy over this tree.
        """

        utility = [0] * self.numOfPlayers

        for actionPlanString in joint.plans:
            actionPlan = CFRJointStrategy.stringToActionPlan(actionPlanString)
            frequency = joint.plans[actionPlanString] / joint.frequencyCount

            leafUtility = self.root.utilityFromActionPlan(actionPlan, default = [0] * self.numOfPlayers)
            for i in range(len(utility)):
                utility[i] += leafUtility[i] * frequency

        return utility

    def checkEquilibrium(self, joint):
        """
        Given a joint strategy, calculate for which value of epsilon it is an epsilon-NFCCE.
        The epsilon are obtained as utility attained following the recommendations minus best utility if deviating, thus a
        positive value means the constraint are satisfied, while a negative value mean we are not at the equilibium yet.
        """

        for iset in self.information_sets.values():
            iset.cached_V = None

        utility = self.getUtility(joint)

        for p in range(self.numOfPlayers):
            root_infosets = list(filter(lambda i: i.player == p and i.sequence == {}, self.information_sets.values()))

            # If there are no root information sets, it means that player p has no information sets
            # at all, so the equilibrium constraints are checked by default
            if(len(root_infosets) == 0):
                continue

            # If the root is a chance node, take it into consideration
            # TODO: make more generic
            if(self.root.isChance()):
                root = self.root
                def map_lambda(i):
                    probability = 0
                    for n in i.nodes:
                        probability += root.distribution[root.base_node.getActionLeadingToNode(n.base_node)]
                    return i.V(joint) * probability
                cum_v = sum(map(map_lambda, root_infosets))
            else:
                cum_v = reduce(lambda acc, i: acc + i.V(joint), root_infosets, 0)

            utility[p] -= cum_v

        return utility

class CFRNode:
    """
    Wrapper around an extensive-form node for holding additional CFR-related code and data.
    """

    def __init__(self, base_node, parent = None):
        """
        Create a CFRNode starting from a base Node.
        It recursively creates also all the CFRNodes from the children of the base Node, up to the leaves.
        """

        self.id = base_node.id
        self.parent = parent
        self.player = base_node.player
        self.children = []
        self.incoming_action = base_node.incoming_action

        for child in base_node.children:
            n = CFRChanceNode(child, self) if child.isChance() else CFRNode(child, self)
            self.children.append(n)

        self.visits = 0
        self.base_node = base_node

        self.is_leaf = len(self.children) == 0

        if(self.isLeaf()):
            self.utility = base_node.utility

    def isLeaf(self):
        return self.is_leaf

    def isChance(self):
        return False

    def getAllLeafVisits(self):
        if(self.isLeaf()):
            return self.visits
        else:
            return reduce(lambda x, y: x + y, map(lambda i: i.getAllLeafVisits(), self.children))

    def getLeafDistribution(self, norm_factor):
        """
        Returns the distribution over the leaves under this node, normalized by a given norm_factor.
        It uses the number of visits of the node stored by the execution of the CFR code.
        """

        if(self.isLeaf()):
            return str(self.visits / norm_factor) + ":" + str(self.base_node) + "\n"
        else:
            return reduce(lambda x, y: x + y,
                          map(lambda i: i.getLeafDistribution(norm_factor), self.children))

    def utilityFromActionPlan(self, actionPlan, default = None):
        """
        Return the utility from the leaf reached following actionPlan and starting from this node.
        If no leaf is reached, return the default value.
        """

        if(self.isLeaf()):
            return self.utility
        elif(self.information_set.id not in actionPlan):
            return default
        else:
            return self.children[actionPlan[self.information_set.id]].utilityFromActionPlan(actionPlan, default)

    def utilityFromJointSequence(self, js):
        """
        Return the expected utility when players follow the joint sequence 'js'. (Chance's actions are not considered in 'js')
        """
        if(self.isLeaf()):
            return self.utility
        elif(self.information_set.id not in js[self.player]):
            return tuple(0 for p in js)
        else:
            cur_player = self.player
            cur_infoset = self.information_set.id
            new_action = js[cur_player][cur_infoset]

            return self.children[new_action].utilityFromJointSequence(js)


    def utilityFromModifiedActionPlan(self, actionPlan, modification, default = None):
        """
        Return the utility from the leaf reached following a modification of actionPlan and starting from this node.
        Action listed in modification are followed first, if no one is found then actionPlan is followed.
        If no leaf is reached, return the default value.
        """

        if(self.isLeaf()):
            return self.utility

        id = self.information_set.id

        if(id in modification and modification[id] >= 0):
            # As if actionPlan[id] was overwritten
            return self.children[modification[id]].utilityFromModifiedActionPlan(actionPlan, modification, default)
        if(id in modification and modification[id] < 0):
            # As if actionPlan[id] was deleted
            return default
        if(id in actionPlan):
            return self.children[actionPlan[id]].utilityFromModifiedActionPlan(actionPlan, modification, default)

        return default

    def computeReachability(self, actionPlan, pi):
        """
        Computes the reachability of this node and its descendants under the given action plan, provided a vector
        pi containing the probability of reaching this node from the point of view of each player.
        """

        self.reachability = pi[self.player]

        if(self.isLeaf()):
            return

        sampled_action = actionPlan[self.information_set.id]

        for a in range(len(self.children)):
            if(sampled_action == a):
                self.children[a].computeReachability(actionPlan, pi)
            else:
                old_pi = pi[self.player]
                pi[self.player] = 0
                self.children[a].computeReachability(actionPlan, pi)
                pi[self.player] = old_pi

class CFRChanceNode(CFRNode):
    """
    Wrapper around an extensive-form chance node for holding additional CFR-related code and data.
    """

    def __init__(self, base_node, parent = None):
        CFRNode.__init__(self, base_node, parent)
        self.distribution = base_node.distribution

    def isChance(self):
        return True

    def sampleAction(self):
        """
        Sample an action from the static distribution of this chance node.
        """

        r = random.random()
        count = 0

        for i in range(len(self.distribution)):
            count += self.distribution[i]
            if(r < count):
                return i

    def computeReachability(self, actionPlan, pi):
        """
        Computes the reachability of this node and its descendants under the given action plan, provided a vector
        pi containing the probability of reaching this node from the point of view of each player.
        """

        if(self.parent != None):
            self.reachability = pi[self.parent.player]
        else:
            self.reachability = 1

        for a in range(len(self.children)):
            self.children[a].computeReachability(actionPlan, pi)

    def utilityFromActionPlan(self, actionPlan, default = None):
        """
        Return the utility from the leaf reached following actionPlan and starting from this node.
        If no leaf is reached, return the default value.
        """

        u = default

        for i in range(len(self.children)):
            childUtility = self.children[i].utilityFromActionPlan(actionPlan, default)

            if(u == default):
                u = childUtility.copy()
                for p in range(len(childUtility)):
                    u[p] *= self.distribution[i]
            else:
                for p in range(len(childUtility)):
                    u[p] += childUtility[p] * self.distribution[i]

        return u

    def utilityFromJointSequence(self, js):
        """
        Returns the convex combination of expected utilities obtained from actions at the current chance node.
        """
        expected_utility = [0.0 for p in js]

        for child_id in range(len(self.children)):
            observed_utility = self.children[child_id].utilityFromJointSequence(js)
            for p in range(len(js)):
                expected_utility[p] += observed_utility[p] * self.distribution[child_id]

        return tuple(expected_utility)


    def utilityFromModifiedActionPlan(self, actionPlan, modification, default = None):
        """
        Return the utility from the leaf reached following a modification of actionPlan and starting from this node.
        Action listed in modification are followed first, if no one is found then actionPlan is followed.
        If no leaf is reached, return the default value.
        """

        u = default

        for i in range(len(self.children)):
            childUtility = self.children[i].utilityFromModifiedActionPlan(actionPlan, modification, default)

            if(u == default):
                u = childUtility.copy()
                for p in range(len(childUtility)):
                    u[p] *= self.distribution[i]
            else:
                for p in range(len(childUtility)):
                    u[p] += childUtility[p] * self.distribution[i]

        return u

class CFRInformationSet:
    """
    Represents an information set and all the code and data related to it when used for the CFR algorithm.
    """

    def __init__(self, id, player, action_count, sequence, cfr_tree, random_initial_strategy = False):
        """
        Create an information set with a given id, player, action_count (i.e. number of actions available in its nodes),
        sequence and cfr_tree it belongs to.
        If random_initial_strategy is True, it is initialized with a random local strategy; otherwise is uses the usual
        uniform distribution over actions.
        """

        self.id = id
        self.player = player
        self.action_count = action_count
        self.sequence = sequence
        self.nodes = []
        self.cfr_tree = cfr_tree

        self.cumulative_regret = [0 for a in range(self.action_count)]
        self.cumulative_strategy = [0 for a in range(self.action_count)]
        self.current_strategy = [1 / self.action_count for a in range(self.action_count)]

        if(random_initial_strategy):
            self.current_strategy = [random.random() for a in range(self.action_count)]
            sum = reduce(lambda x, y: x + y, self.current_strategy, 0)
            self.current_strategy = [self.current_strategy[a] / sum for a in range(self.action_count)]

        self.cached_V = None

    def __str__(self):
        return "<InfoSet" + str(self.id) + " - Player" + str(self.player) + ">"

    def __repr__(self):
        return str(self)

    def addNode(self, node):
        self.nodes.append(node)

    def updateCurrentStrategy(self):
        """
        Recalculate the current strategy based on the cumulative regret.
        """

        sum = reduce(lambda x, y: x + max(0, y), self.cumulative_regret, 0)

        for a in range(0, self.action_count):
            if(sum > 0):
                self.current_strategy[a] = max(0, self.cumulative_regret[a]) / sum
            else:
                self.current_strategy[a] = 1 / self.action_count

    def getAverageStrategy(self):
        """
        Get the average strategy experienced so far.
        """

        norm = reduce(lambda x, y: x + y, self.cumulative_strategy)
        if(norm > 0):
            return [self.cumulative_strategy[a] / norm for a in range(self.action_count)]
        else:
            return [1 / self.action_count for a in range(self.action_count)]

    def sampleAction(self):
        """
        Sample an action from the current strategy.
        """

        if(self.nodes[0].isChance()):
            return self.nodes[0].sampleAction()

        r = random.random()
        count = 0

        for i in range(len(self.current_strategy)):
            count += self.current_strategy[i]
            if(r < count):
                return i

    def V(self, joint, db = False):
        """
        Calculate the V value, that is the best value of utility attainable from this information set when deviating
        from a given joint strategy.
        It is used for calculate the epsilon value of equilibria.
        """

        start_time = time.time()
        if(self.cached_V != None):
            return self.cached_V

        v = [0] * self.action_count

        this_player_infosets = self.cfr_tree.infosets_by_player[self.player]

        sequence = self.sequence.copy()
        modification_sequence = self.sequence.copy()

        # Delete from actionPlan all the actions by the current player
        for iset in this_player_infosets:
            if(iset.id not in sequence):
                modification_sequence[iset.id] = -1

        for a in range(self.action_count):
            sequence[self.id] = a
            modification_sequence[self.id] = a

            children = list(filter(lambda iset: iset.sequence == sequence, this_player_infosets))

            # "Leaves" part of the sum
            # TODO: optimize this loop, it is too much to loop over all plans in the joint
            for actionPlanString in joint.plans:
                actionPlan = CFRJointStrategy.stringToActionPlan(actionPlanString)
                frequency = joint.plans[actionPlanString] / joint.frequencyCount

                u = self.cfr_tree.root.utilityFromModifiedActionPlan(actionPlan, modification_sequence,
                                                                     default = [0] * self.cfr_tree.numOfPlayers)

                if(u != None):
                    if(db):
                        print(u)
                        print(frequency)
                        print(v[a])
                        print(frequency * u[self.player])
                    v[a] += frequency * u[self.player]

            if(db):
                print("Children via action " + str(a) + " = " + str(children))

            # "Recursive" part of the sum
            for child in children:
                v[a] += child.V(joint)

        self.cached_V = max(v)

        return self.cached_V

    def getChildrenOfPlayer(self, player):
        """
        Get all the information sets (including this one) of the given player and descendants of this information set.
        """

        children = set()
        for node in self.nodes:
            for child in node.children:
                if(not child.isLeaf()):
                    children.update(child.information_set.getChildrenOfPlayer(player))
        if(self.player == player):
            children.add(self)
        return children

class CFRJointStrategy:
    """
    A joint strategy progressively built by the SCFR algorithm.
    """

    def __init__(self, maxPlanCount = -1):
        """
        Create a joint strategy able to hold a maximum of maxPlanCount plans.
        If the value is not given, it is able to hold an arbitrary number of plans.
        """

        self.maxPlanCount = maxPlanCount
        self.frequencyCount = 0
        self.plans = {}

        CFRJointStrategy.action_plans_cache = {}

    def addActionPlan(self, actionPlan):
        """
        Add an action plan (a dictionary from information set id to action) to the joint strategy.
        """

        string = CFRJointStrategy.actionPlanToString(actionPlan)

        if(string in self.plans):
            self.plans[string] += 1
            self.frequencyCount += 1
        elif(self.maxPlanCount == -1 or len(self.plans) < self.maxPlanCount):
            self.plans[string] = 1
            self.frequencyCount += 1
        else:
            # Remove the least frequent plan
            plan = min(self.plans, key = lambda p: self.plans[p])
            self.frequencyCount -= self.plans[plan]
            del self.plans[plan]

            # Add the new one
            self.plans[string] = 1
            self.frequencyCount += 1

    def actionPlanToString(actionPlan):
        """
        Transform an action plan in dictionary representation to the corresponding string representation.
        """

        string = ""

        for infoset in actionPlan:
            string += "a" + str(infoset) + "." + str(actionPlan[infoset])

        return string

    action_plans_cache = {}

    def stringToActionPlan(string):
        """
        Transform an action plan in string representation to the corresponding dictionary representation.
        """

        if(string in CFRJointStrategy.action_plans_cache):
            return CFRJointStrategy.action_plans_cache[string]

        actions = string.split("a")[1:]
        actionPlan = {}

        for a in actions:
            (infoset, action) = a.split(".")
            actionPlan[int(infoset)] = int(action)

        CFRJointStrategy.action_plans_cache[string] = actionPlan

        return actionPlan

    def reduceActionPlan(actionPlan, tree):
        """
        Transform an action plan into a reduced one, in the given tree.
        """

        reducedActionPlan = {}

        tree.root.computeReachability(actionPlan, [1] * tree.numOfPlayers)

        for (id, iset) in tree.information_sets.items():
            reachability = max(map(lambda n: n.reachability, iset.nodes))
            if(reachability > 0):
                reducedActionPlan[id] = actionPlan[id]

        return reducedActionPlan
