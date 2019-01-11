from data_structures.cfr_trees import CFRJointStrategy
from functools import reduce

def sampleCFR(node, player, pi, action_plan):
    n_players = len(pi)
    node.visits += reduce(lambda x, y: x * y, pi, 1)
    
    if(node.isChance()):
        return sampleCFR(node.children[node.sampleAction()], player, pi, action_plan)
    
    if(node.isLeaf()):
        return node.utility[player]        
    
    iset = node.information_set
    v = 0
    v_alt = [0 for a in node.children]
    
    sampled_action = action_plan[iset.id]
    
    if(max(pi) == 0):
        return sampleCFR(node.children[sampled_action], player, pi, action_plan)
    
    for a in range(len(node.children)):
        if(a == sampled_action):
            v_alt[a] = sampleCFR(node.children[a], player, pi, action_plan)
        else:
            old_pi = pi[iset.player]
            pi[iset.player] = 0
            v_alt[a] = sampleCFR(node.children[a], player, pi, action_plan)
            pi[iset.player] = old_pi
            
        #############################################################################################
        # TODO: check (do I really need to use current_strategy, or is it more correct to say
        # that v = v_alt[sampled_action]?)
        #v += v_alt[a] * iset.current_strategy[a]
        #############################################################################################
        
    v = v_alt[sampled_action]
    
    if(iset.player == player):
        pi_other = 1
        for i in range(len(pi)):
            if(i != player):
                pi_other *= pi[i]

        for a in range(len(node.children)):            
            #################################################################################
            ###### CFR+ seems not to be working
            #iset.cumulative_regret[a] += pi_other * max(0, (v_alt[a] - v)) # CFR+
            #################################################################################
            
            ##### CFR+ #####
            iset.cumulative_regret[a] = max(iset.cumulative_regret[a] + pi_other * (v_alt[a] - v), 0)
            
            ##### This is useless for NFCCE #####
            iset.cumulative_strategy[a] += pi[player] * iset.current_strategy[a]
    
    return v

def SolveWithSampleCFR(cfr_tree, iterations, perc = 10, show_perc = False, checkEveryIteration = -1,
                      bound_joint_size = True):
    if(bound_joint_size):
        jointStrategy = CFRJointStrategy(cfr_tree.numOfActions * 2)
    else:
        jointStrategy = CFRJointStrategy(-1)
    player_count = cfr_tree.numOfPlayers
    
    # Graph data
    graph_data = []
    
    for i in range(iterations):
        if(show_perc and (i+1) % (iterations / 100 * perc) == 0):
            print(str((i+1) / (iterations / 100 * perc) * perc) + "%")
            
        # Sample a joint action plan from the current strategies
        action_plan = cfr_tree.sampleActionPlan()
            
        # Run CFR for each player
        for p in range(player_count):
            sampleCFR(cfr_tree.root, p, [1] * player_count, action_plan)
        
        # Run CFR for each player (in parallel)
        #with Pool(player_count) as p:
        #    p.starmap(sampleCFR, 
        #              [(cfr_tree.root, p_id, [1] * player_count, action_plan) for p_id in range(player_count)])
            
        # Update the current strategy for each information set
        for infoset in cfr_tree.information_sets.values():
            infoset.updateCurrentStrategy()
            
        jointStrategy.addActionPlan(CFRJointStrategy.reduceActionPlan(action_plan, cfr_tree))
        
        if(checkEveryIteration > 0 and i % checkEveryIteration == 0 and i != 0):
            data = {'epsilon': cfr_tree.checkEquilibrium(jointStrategy),
                    'absolute_joint_size': jointStrategy.frequencyCount,
                    'relative_joint_size': jointStrategy.frequencyCount / (i + 1),
                    'max_plan_frequency': max(jointStrategy.plans.values()),
                    'iteration_number': i}
            graph_data.append(data)
        
    return {'utility': cfr_tree.getUtility(jointStrategy), 'joint': jointStrategy, 'graph_data': graph_data}