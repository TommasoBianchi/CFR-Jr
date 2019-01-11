from data_structures.cfr_trees import CFRJointStrategy
from functools import reduce

def CFR(node, player, pi):
    n_players = len(pi)
    node.visits += reduce(lambda x, y: x * y, pi, 1)
    
    if(node.isLeaf()):
        return node.utility[player]
    
    iset = node.information_set
    v = 0
    v_alt = [0 for a in node.children]
    
    for a in range(len(node.children)):
        
        old_pi = pi[player]
        #pi[player] *= iset.current_strategy[a]
        v_alt[a] = CFR(node.children[a], player, pi)        
        pi[player] = old_pi
            
        v += v_alt[a] * iset.current_strategy[a]
    
    if(iset.player == player):
        for a in range(len(node.children)):
            iset.cumulative_regret[a] += pi[player] * max(0, (v_alt[a] - v)) # CFR+
            iset.cumulative_strategy[a] += pi[player] * iset.current_strategy[a]
         
        # This should not happen until every player has run CFR
        #iset.updateCurrentStrategy()
    
    return v

def SolveWithCFR(cfr_tree, player_count, iterations, perc = 10, show_perc = False):
    jointStrategy = CFRJointStrategy(cfr_tree.numOfActions * 2)
    
    for i in range(iterations - 1):
        if(show_perc and (i+1) % (iterations / 100 * perc) == 0):
            print(str((i+1) / (iterations / 100 * perc) * perc) + "%")
            
        # Run CFR for each player
        for p in range(player_count):
            CFR(cfr_tree.root, p, [1] * player_count)
            
        # Update the current strategy for each information set
        for infoset in cfr_tree.information_sets.values():
            infoset.updateCurrentStrategy()
            
        actionPlan = cfr_tree.sampleActionPlan()
        jointStrategy.addActionPlan(actionPlan)
        
    utility = [CFR(cfr_tree.root, p, [1] * player_count) for p in range(player_count)]
    actionPlan = cfr_tree.sampleActionPlan()
    jointStrategy.addActionPlan(actionPlan)
        
    return {'utility': utility, 'joint': jointStrategy}