from cfr_code.cfr import CFR
from data_structures.cfr_trees import CFRJointStrategy
import time

def SolveWithReconstructionCFR(cfr_tree, iterations, perc = 10, show_perc = False, 
                               checkEveryIteration = -1, reconstructEveryIteration = 1,
                               check_callback = None, use_cfr_plus = False):
    
    jointStrategy = CFRJointStrategy()

    # Graph data
    graph_data = []

    start_time = time.time()
    last_checkpoint_time = start_time

    player_count = cfr_tree.numOfPlayers

    for i in range(iterations - 1):
        if(show_perc and (i+1) % (iterations / 100 * perc) == 0):
            print(str((i+1) / (iterations / 100 * perc) * perc) + "%")
            
        u = []

        # Run CFR for each player
        for p in range(player_count):
            u.append(CFR(cfr_tree.root, p, [1] * player_count, use_cfr_plus))
            
        # Update the current strategy for each information set
        for infoset in cfr_tree.information_sets.values():
            infoset.updateCurrentStrategy()

        # Reconstruct a joint from the marginals and add it to the current joint strategy
        if (i % reconstructEveryIteration == 0):
            jointStrategy.addJointDistribution(cfr_tree.buildJointFromMarginals())

        if(checkEveryIteration > 0 and i % checkEveryIteration == 0):
            data = {'epsilon': cfr_tree.checkEquilibrium(jointStrategy),
                    'marginal_epsilon': cfr_tree.checkMarginalsEpsilon(),
                    'iteration_number': i,
                    'duration': time.time() - last_checkpoint_time,
                    'utility': u}
            graph_data.append(data)

            if(check_callback != None):
                check_callback(data)
                
            last_checkpoint_time = time.time()
        
    return {'utility': u, 'graph_data': graph_data, 'tot_time': time.time() - start_time, 'joint': jointStrategy}