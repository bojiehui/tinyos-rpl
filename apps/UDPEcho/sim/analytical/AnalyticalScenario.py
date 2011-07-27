from __future__ import division

import pickle
import math
import networkx as nx

from sim.utils.cpm import *
from sim.analytical.kshortestpaths import *

SOURCE = 2 # TODO: move to somewhere else

class AnalyticalScenario:
    def __init__(self,
                 suite, nodes, distance):
        #sim/output/suite_2011_02_17__09_22_22/topo_4/dist_100/run_0/file_suite2011_02_17__09_22_22_topo4_dist100_run0_id2xy.pickle
        # suite = "2011_02_17__09_22_22"
        self.scen = pickle.load(
            open("sim/output/suite_" + suite +
                 "/topo_" + str(nodes) +
                 "/dist_" + str(distance) +
                 "/run_0/file_suite" + suite +
                 "_topo" + str(nodes) +
                 "_dist" + str(distance) +
                 "_run0_id2xy.pickle",
                 'rb'))

    def get_distribution_quantity(self,
                                  nodes,
                                  retransmissions):

        print "Node positions:", self.scen
        links = self.instantiate_links(self.scen)
        graph = self.instantiate_graph(links)
        (hop_distribution_prr, hop_distribution_mod_prr, hop_freq) = \
            self.get_hop_distribution(SOURCE,
                                      links,
                                      nodes,
                                      graph,
                                      retransmissions)

        distribution_freq = []
        distribution_freq.append((0, 1)) # hop 0
        distribution_quantity = []
        distribution_quantity.append((0, 0, 1)) # hop 0
        distribution_quantity_mod = []
        distribution_quantity_mod.append((0, 0, 1)) # hop 0

        for h in hop_freq:
            distribution_freq.append((h, hop_freq[h]))

        for h in hop_distribution_prr:
            for r in hop_distribution_prr[h]:
                distribution_quantity.append((h, r, hop_distribution_prr[h][r]))

        for h in hop_distribution_mod_prr:
            for r in hop_distribution_mod_prr[h]:
                distribution_quantity_mod.append((h, r, hop_distribution_mod_prr[h][
r]))

        return (distribution_quantity, distribution_quantity_mod, distribution_freq)

    #TODO: use Scenarios

    # only for -CPM scenarios!!!!

    def instantiate_links(self, scenario):
        links = {}
        for i in scenario:
            if i == 1:
                # ignore node 0
                continue
            for j in scenario:
                if i == j:
                    continue
                if j == 1:
                    # ignore node 0
                    continue
                dist = calc_distance(scenario, i, j)
                print "Dist", i, j, dist,
                prr = dist2prr(dist)
                print "PRR", prr
                if links.has_key(i):
                    link = links[i]
                else:
                    link = {}
                if prr != 0.0:
                    link[j] = prr
                if not links.has_key(i):
                    links[i] = link
        print "Links:", links
        print ""
        return links

    #only for Line-Direct scenario!!!!

    # def instantiate_links(self, scenario):
    #     links = {}
    #     for i in scenario:
    #         if i == 1:
    #             # ignore node 0
    #             continue
    #         for j in scenario:
    #             if i == j:
    #                 continue
    #             if j == 1:
    #                 # ignore node 0
    #                 continue
    #             dist = calc_distance(scenario, i, j)
    #             print "Dist", i, j, dist,
    #             prr = dist2prr(dist)
    #             print "PRR", prr
    #             if links.has_key(i):
    #                 link = links[i]
    #             else:
    #                 link = {}
    #             if prr != 0.0:
    #                 if abs(i - j) == 1:
    #                     # only connect direct neighbor, with realistic
    #                     # propagation, though
    #                     link[j] = prr
    #             if not links.has_key(i):
    #                 links[i] = link
    #     print "Links:", links
    #     print ""
    #     return links

    def instantiate_graph(self, links):
        graph = nx.DiGraph()
        for linkstart in links:
            #print "Link", linkstart
            for linkend in links[linkstart]:
                print "edge>>> ", linkstart, linkend, 1/links[linkstart][linkend]
                graph.add_edge(linkstart, linkend,
                               weight=1)
#                               weight=1/links[linkstart][linkend])
        print "Graph:", graph.edges()
        return graph

    def get_hop_distribution(self, source, links, nodes, graph, retransmissions):
        print "get_hop_distribution"

        K = 5

        hop_freq = {}
        hop_distribution = {}
        hop_distribution_mod = {}

        for n in range(source+1, nodes+2):

            hop_freq_node = {}
            hop_distribution_node = {}
            hop_distribution_mod_node = {}

            print "~"*10, "Calc", K, "shortest paths for", source, n
            paths = k_shortest_paths(graph, source, n, K)
            print "Paths:", paths

            unique_paths = unique(paths)
            print "Unique Paths:", unique_paths

            paths = remove_looped_paths(unique_paths)

            prob = {}
            for path in paths:
                prr = calc_multiple_prr(path, links)
                prob[str(path)] = prr

                # if prob.has_key(str(path)):
                #     prob[str(path)].append(prr)
                #     #if prob[len(path)] <= prr:
                #     #    hop_freq[len(path)] += 1
                # else:
                #     prob[str(path)] = [prr, ]
                #     #hop_freq[len(path)] = 1

            print ">>>Prob:", prob

            # avg_prob = {}
            # for key in prob:
            #     #avg_prob[key] = sum(prob[key])/len(prob[key])
            #     #avg_prob[key] = sum(prob[key])
            #     if prob[key].count(1.0) >= 1:
            #         avg_prob[key] = len(prob[key])
            #     else:
            #         avg_prob[key] = sum(prob[key])
            # print "AVG Prob:", avg_prob

            # best_prob = {}
            # for key in prob.keys():
            #     print "key", key, prob[key], max(prob[key])
            #     best_prob[key] = max(prob[key])
            # print "best Prob:", best_prob

            best_prob = 0
            for key in prob.keys():
                if prob[key] > best_prob:
                    best_prob = prob[key]
            print "best Prob:", best_prob

            for path in paths:
                if hop_freq_node.has_key(len(path)):
                    hop_freq_node[len(path)] += 1
                else:
                    hop_freq_node[len(path)] = 1

            mod_prob = {}
            sum_prob = 0
            #prr = 1.0
            #prr = best_prob
            for path in paths:
                prr = (1-sum_prob) * prob[str(path)]
                # assumes nodes of same length have same total PRR:
                mod_prob[str(path)] = prr
                #mod_prob[str(path)] = prr * hop_freq_node[len(path)]
                #mod_prob[str(path)] = prr * hop_freq_node[len(path)]
                sum_prob += prr
                print "mp calc", str(path), prr, mod_prob[str(path)], sum_prob

                if mod_prob[str(path)] < 0 or mod_prob[str(path)] > 1.0:
                    print "ERROR: prob not in [0, 1]", str(path), mod_prob[str(path)]
                    raise Exception
                #prr = prr * (1-prob[str(path)])
                #prr = (1-prr) * prob[str(path)]

#            for p in prob:
#                mod_prob[p] = best_prob * cond_prob(prob, p)

#                try:
#                    mod_prob[p] = prob[p] * (1-mod_prob[p-1])
#                except:
#                    print "mod except"
#                    mod_prob[p] = prob[p]
            print "Mod Prob:", mod_prob

            # prr_1_index = K
            # for p in prob:
            #     if prob[p] == 1.0:
            #         prr_1_index = p
            #         break
            # print "PRR==1.0 at index", prr_1_index
            path_length_distribution = {}
            for path in paths:
                if path_length_distribution.has_key(len(path)):
                    path_length_distribution[len(path)] += 1
                else:
                    path_length_distribution[len(path)] = 1
            print "Path Length Dist", path_length_distribution

            for path in paths:
                p = prob[str(path)]
                mp = mod_prob[str(path)]
                print "Path", path, "p", p, "mp", mp

                if not hop_distribution_node.has_key(len(path)):
                    hop_distribution_node[len(path)] = {}

                path_prr = p/path_length_distribution[len(path)]
                hop_distribution_node_val = path_prr

                for r in range(0, retransmissions):

                    if not hop_distribution_node[len(path)].has_key(r):
                        hop_distribution_node[len(path)][r] = 0

                    hop_distribution_node[len(path)][r] += hop_distribution_node_val
                    hop_distribution_node_val = (1-path_prr)*hop_distribution_node_val

            print "#"*10
            print "hop_freq_node", hop_freq_node
            print "hop_distribution_node", hop_distribution_node

            for path in paths:
                p = prob[str(path)]
                mp = mod_prob[str(path)]
                print "Path", path, "p", p, "mp", mp

                if not hop_distribution_mod_node.has_key(len(path)):
                    hop_distribution_mod_node[len(path)] = {}

                mod_path_prr = mp/path_length_distribution[len(path)]
                hop_distribution_mod_node_val = mod_path_prr

                for r in range(0, retransmissions+1):

                    print "r", r

                    if not hop_distribution_mod_node[len(path)].has_key(r):
                        hop_distribution_mod_node[len(path)][r] = 0

                    hop_distribution_mod_node[len(path)][r] += hop_distribution_mod_node_val
                    print "-->", len(path), r, hop_distribution_mod_node[len(path)][r]
                    try:
                        print "A", (hop_freq_node[len(path)]-hop_distribution_mod_node[len(path)][r])
                        # FIXME: lower retransmission needed, but gets calculated later....:
                        print "B", (hop_freq_node[len(path)+1]-hop_distribution_node[len(path)+1][r])
                        print "B|", hop_freq_node[len(path)+1], hop_distribution_node[len(path)+1][r]
                        print "C", (1-mod_path_prr)
                        print "D", hop_distribution_mod_node_val

                        # hop_distribution_mod_node_val = \
                        #     (hop_freq_node[len(path)]-hop_distribution_mod_node[len(path)][r]) * \
                        #     (hop_freq_node[len(path)+1]-hop_distribution_node[len(path)+1][r]) * \
                        #     (1-mod_path_prr) * \
                        #     hop_distribution_mod_node_val

                        hop_distribution_mod_node_val = \
                            (hop_freq_node[len(path)]-hop_distribution_mod_node[len(path)][r]) * \
                            (1-hop_distribution_node[len(path)+1][r]) * \
                            (1-mod_path_prr) * \
                            hop_distribution_mod_node_val

                        print ">>", hop_distribution_mod_node_val

                    except:
                        try:
                            print "A2", (hop_freq_node[len(path)]-hop_distribution_mod_node[len(path)][r])
                            print "C2", (1-mod_path_prr)
                            print "D2", hop_distribution_mod_node_val

                            hop_distribution_mod_node_val = \
                                (hop_freq_node[len(path)]-hop_distribution_mod_node[len(path)][r]) * \
                                (1-mod_path_prr) * \
                                hop_distribution_mod_node_val

                            print ">>", hop_distribution_mod_node_val

                        except:
                            print "EXCCCCCEPT"
                            hop_distribution_mod_node_val = (1-mod_path_prr)*hop_distribution_mod_node_val
                            print ">>", hop_distribution_mod_node_val

            # print "hop_distribution_node", hop_distribution_node
            # print "hop_distribution_node_mod", hop_distribution_mod_node
            # print "hop_freq_node", hop_freq_node

            # print "~get_hop_distribution", hop_distribution
            # print "~get_hop_distribution_mod", hop_distribution_mod
            # print "~get_hop_freq", hop_freq

            for h in hop_freq_node.keys():
                if hop_distribution.has_key(h):
                    hop_freq[h] += hop_freq_node[h]
                else:
                    hop_freq[h] = hop_freq_node[h]

            for h in hop_distribution_node.keys():
                if not hop_distribution.has_key(h):
                        hop_distribution[h] = {}

                for r in hop_distribution_node[h].keys():
                    if not hop_distribution[h].has_key(r):
                        hop_distribution[h][r] = 0

                    hop_distribution[h][r] += hop_distribution_node[h][r]


            for h in hop_distribution_mod_node.keys():
                if not hop_distribution_mod.has_key(h):
                        hop_distribution_mod[h] = {}

                for r in hop_distribution_mod_node[h].keys():
                    if not hop_distribution_mod[h].has_key(r):
                        hop_distribution_mod[h][r] = 0

                    hop_distribution_mod[h][r] += hop_distribution_mod_node[h][r]

            # print "~get_hop_distribution", hop_distribution
            # print "~get_hop_distribution_mod", hop_distribution_mod
            # print "~get_hop_freq", hop_freq

        print "~get_hop_distribution", hop_distribution
        print "~get_hop_distribution_mod", hop_distribution_mod
        print "~get_hop_freq", hop_freq

        return (hop_distribution, hop_distribution_mod, hop_freq)

def calc_multiple_prr(path, links):
    prr = 1
    for link in path:
        prr *= links[link[0]][link[1]]
    print "Path PRR", path, prr
    return prr

def calc_distance(scenario, id1, id2):
    (x, y)   = scenario[id1]
    (x2, y2) = scenario[id2]
    return math.sqrt((x-x2)**2 + (y-y2)**2)

def remove_looped_paths(paths):
    loop_free_paths = []

    for path in paths:
        loop_detected = False
        for link1 in path:
            for link2 in path:
                if link1[0] == link2[1] and link1[1] == link2[0]:
                    print "loop detected in path", path
                    loop_detected = True

        if loop_detected == False:
            loop_free_paths.append(path)

    return loop_free_paths

def cond_prob(prob, p):
    #print "p=", p
    if p == 0:
        mod_prob = 1
        #print "p==0"
    else:
        try:
            mod_prob = (1-prob[p-1]) * cond_prob(prob, p-1)
            #print "try succ", prob[p]
        except:
            #print "try fail", prob[p]
            mod_prob = 1
    #print "mod_prob", mod_prob
    return mod_prob

def unique(seq):
    # order preserving
    noDupes = []
    [noDupes.append(i) for i in seq if not noDupes.count(i)]
    return noDupes
