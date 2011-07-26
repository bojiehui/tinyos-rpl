import networkx as nx
import heapq
import copy

#submit to networkx or k-shortest_path on google code?

HG  = [] # needed?
HGv = {} # needed?
HGbuilt = {}
Hout = {}

def k_shortest_paths(G, source, target, K):
    """Lazy version of Eppstein's algorithm as in V.M. Jimenez,
    A. Marzal: 'A Lazy Version of Eppstein's K Shortest Paths
    Algorithm.'
    """
    global HG
    global HGv
    global HGbuilt
    global Hout

    HG  = [] # needed?
    HGv = {} # needed?
    HGbuilt = {}
    Hout = {}

    shortestpaths_not_default = []
    shortestpaths_not_default.append([])

    # 1. Compute T and delta(u,v) for all (u, v) in E.
    T = single_target_dijkstra(G, target)
    #print "T:", T
    delta = delta_u_v(G, T)
    #print "delta:", delta

    # 2. Call BuildHG (s).
    buildHG(source, target, G, T, delta)
    #print "<<<<<"
    #print "  HG:", HG
    #print "  HGv:", HGv
    #print "  HGbuilt:", HGbuilt
    #print "  Hout:", Hout
    #print ">>>>>"

    # 3.1 Initialize Q to {h(s)}. (which is the root of HG(s))
    #Q = heapq.heappop(HG)
    #Q = flattened(HGv[source])
    Q = HGv[source]
    #print "Q:", Q
    #print "#"*70

    # 3.2 For k = 2 to K:
    for k in range(2, K+1):
        #print ""
        #print "="*50
        #print "--> k:", k
        #print "--> Q:", Q
        # 3.2.1 If Q empty, stop; else, extract S^k , the element
        #       in Q with the lowest score. Let e be the last sidetrack of S^k.
        if not Q:
            print "Q empty"
            break
        else:
            S_k = heapq.heappop(Q)[1]
            print "--> S^"+str(k)+": " + str(S_k)
            shortestpaths_not_default.append(S_k)
            #print "="*50
            e = S_k[-1]
            #print "e:", e

        # 3.2.2 Call BuildHG (head(e)).
        buildHG(e[1], target, G, T, delta)
        # print "<<<<<"
        # print "  HG:", HG
        # print "  HGv:", HGv
        # print "  HGbuilt:", HGbuilt
        # print "  Hout:", Hout
        # print ">>>>>"

        # 3.2.3 Insert S^k * f in Q with score L(S^k) + delta(f),
        #       where f is the sidetrack h(head(e)).
        # HGv[e[1]][0]
        #           ^ best
        #          ...[1]
        #              ^ edgelist, not weight
        #                [0]
        #                 ^ first edge
        # pop it?
        #print "0|", HGv[e[1]]
        #print "1|", HGv[e[1]][0]
        #print "2|", HGv[e[1]][0][1]

        try:
            f = HGv[e[1]][0][1][0]

            #print "f:", f
            S_k_p_f = S_k[:]
            S_k_p_f.append(f)
            #print "S^k * f:", S_k_p_f

            L_S_k = length(S_k, delta)
            score = L_S_k + delta[f[0]][f[1]]
            #print "Score:", score

            if Q.count((score, S_k_p_f)) == 0:
                if e[0] == f[1] and e[1] == f[0]:
                    #print "Loop"
                    pass
                else:
                    #print "+"*10, "3.2.3 Inserting", (score, S_k_p_f)
                    heapq.heappush(Q, (score, S_k_p_f))
            else:
                #print "+"*10, "3.2.3 Already in Q", (score, S_k_p_f)
                pass
            #print "Q:", Q
        except:
            #print "??? no sidetracks available at", e[1]
            pass

        # 3.2.4 For each sidetrack f such that (e, f) is an
        #       arc in the graph D(G), insert prefix (S^k) * f
        #       in Q with score L(S^k) - delta(e) + delta(f).

        try:
            fs = HGv[e[1]]
            #print "sidetracks f:", fs
            for f_w in fs:
                f = f_w[1][0]
                #print "e, f:", e, f

                for f_comp in HGv[e[1]]:
                    #print "f == f_comp", f, f_comp[1][0]
                    if f == f_comp[1][0]:

                        # This would be the code according to the paper.
                        # However, somehow this does not make sense to me.

                    #     print "!!!!!! arc in D(G) !!!!!!!!", e, f

                    #     print "###### arc in D(G) ########", e, f
                    #     pre_S_k_p_f = S_k[:-1]
                    #     pre_S_k_p_f.append(f)
                    #     print "S^k:", S_k
                    #     print "prefix(S^k) * f:", pre_S_k_p_f

                    # #L_S_k = delta[S_k[0][0]][S_k[0][1]] # is this correct?
                    #     L_S_k = length(S_k, delta)
                    #     score = L_S_k - delta[e[0]][e[1]] + delta[f[0]][f[1]]
                    #     print "Score:", score, L_S_k, delta[e[0]][e[1]], delta[f[0]][f[1]]
                    #     print "+"*10, "3.2.4 Inserting", (score, pre_S_k_p_f)
                    #     heapq.heappush(Q, (score, pre_S_k_p_f))
                    #     print "Q:", Q

                        #print "###### arc in D(G) ########", e, f
                        S_k_p_f = S_k[:]
                        S_k_p_f.append(f)
                        #print "S^k:", S_k
                        #print "prefix(S^k) * f:", S_k_p_f

                        L_S_k = length(S_k, delta)
                        score = L_S_k + delta[f[0]][f[1]]
                        #print "Score:", score, L_S_k, delta[e[0]][e[1]], delta[f[0]][f[1]]

                        if Q.count((score, S_k_p_f)) == 0:
                            if e[0] == f[1] and e[1] == f[0]:
                                #print "Loop"
                                pass
                            else:
                                #print "+"*10, "3.2.4 Inserting", (score, S_k_p_f)
                                heapq.heappush(Q, (score, S_k_p_f))
                        else:
                            #print "+"*10, "3.2.4 Already in Q", (score, S_k_p_f)
                            pass
                        #print "Q:", Q
        except KeyError as e:
            print "??? KeyError", e
            pass

    #print "Paths Sidetracks:", shortestpaths_not_default
    shortestpaths = []

    for deviations in shortestpaths_not_default:
        #print ""
        #print "="*50
        #print ">", deviations
        #for deviation in deviations:
        #    print " ", deviation

        deviationindex = 0
        path = []

        this = source
        try:
            if this == deviations[deviationindex][0]:
                next = deviations[deviationindex][1]
            else:
                next = T[source][1][1]
        except:
            #print "except"
            next = T[source][1][1]

        #print "t|n", this, next
        #print "#deviations", len(deviations)
        #print "++1", (this, next)
        path.append((this, next))
        
        #### FIXME!!!!!!!!!!!!!!!!!!!!

        while next != target:
            #print "++1", (this, next)
            #path.append((this, next))

            if (len(deviations) > deviationindex):
                if this == deviations[deviationindex][0]:
                    # deviate from shortest path
                    #print "A~~~~~~~~~~~~~"
                    this = deviations[deviationindex][1]
                    #next = T[this][1][1]
                    deviationindex += 1
                else:
                    # follow shortest path
                    #print "B~~~~~~~~~~~~~"
                    this = next
                    #next = T[this][1][1]
            else:
                # no more deviations
                #print "C~~~~~~~~~~~~~"
                this = next
                #next = T[this][1][1]

            if (len(deviations) > deviationindex):
                if this == deviations[deviationindex][0]:
                    # deviate from shortest path
                    #print "An~~~~~~~~~~~~~"
                    next = deviations[deviationindex][1]
                else:
                    #print "Bn~~~~~~~~~~~~~"
                    next = T[this][1][1]
            else:
                #print "Cn~~~~~~~~~~~~~"
                next = T[this][1][1]

            #print "t|n", this, next
            #print "++2", (this, next)
            path.append((this, next))

        #print "++D", (this, next)
        #path.append((this, next))
        #print "Path:", path
        shortestpaths.append(path)

    #print "Paths", shortestpaths
    return shortestpaths

def length(path, delta):
    #print " Path", path
    sum = 0
    for arc in path:
        #print "  Arc:", arc
        try:
            sum += delta[arc[0]][arc[1]]
        except KeyError:
            #print "??? no delta for", arc[0], arc[1]
            sum += 0
        #print "  Sum:", sum
    return sum

def buildHG(v, target, G, T, delta):
    global HG
    global HGv
    global HGbuilt
    global Hout

    # A. If HG (v) has not been built before then
    if not HGbuilt.has_key(v):
        #print "*** buildHG(", v, ",", target, ", G, T, delta)"

        # A.1. Build Hout (v).
        Hout_v = []
        for v_succ in G.successors(v):
            try:
                #print "v, v_succ:", v, v_succ
                heapq.heappush(Hout_v, (delta[v][v_succ], [(v, v_succ), ]))
            except:
                #print "??? delta not available for", v, v_succ
                #if v != v_succ:
                #    heapq.heappush(Hout_v, (0, [(v, v_succ), ]))
                #else:
                # ignore not available delta's
                pass
        Hout[v] = Hout_v
        #print "Hout["+str(v)+"]"+ str(Hout[v])

        # A.2. If v = t then let HG (v) = Hout (v), else call
        #      Build HG (next T (v)) and insert Hout (v) into
        #      HG (next T (v)) to form HG (v).
        if v == target:
            HG  = Hout[v]
            HGv[v] = Hout[v]
            #print "HGv["+str(v)+"]"+ str(HGv[v])
            HGbuilt[v] = 1
        else:
            buildHG(T[v][1][1], target, G, T, delta)
            #print "*** <<<"

            #print "Merging", HGv[T[v][1][1]], Hout[v]
            #heapq.heappush(HG, (delta[v].get(v_succ, 0), Hout[v]))
            it = heapq.merge(HGv[T[v][1][1]], Hout[v])
            HG = [o for o in it]
            #print "Merged", HG
            HGv[v] = HG
            #print "HGv["+str(v)+"]"+ str(HGv[v])
            HGbuilt[T[v][1][1]] = 1
    else:
        #print "*** buildHG(", v, ",", target, ", G, T, delta) Already done."
        pass

def single_target_dijkstra(G, target):
    T_dict = {}
    for n in G.nodes():
        if n != target:
            ssd = nx.single_source_dijkstra(G, n, target)
            #print "node", n, "->", ssd
            T_dict[n] = (ssd[0][target], ssd[1][target])
        else:
            T_dict[n] = (0, [target, ])
    return T_dict

def delta_u_v(G, T):
    delta = {}
    for u in G.nodes():
        delta[u] = {}
        succ_nodes = G.successors(u)
        if succ_nodes == []:
            break
        #print "succ of", u, ":", succ_nodes
        #print "T", T
        try:
            succ_node_on_shortest_path = T[u][1][1]
            #delta[u][succ_node_on_shortest_path] = 0
            #print "short succ of", u, ":", succ_node_on_shortest_path
        except:
            succ_node_on_shortest_path = None
            #print "??? no succ on shortest path:", u
            pass

        succ_nodes_not_on_shortest_path = [v for v in succ_nodes if succ_node_on_shortest_path != v]
        #print "!short succ of", u, ":", succ_nodes_not_on_shortest_path
        for v in succ_nodes_not_on_shortest_path:
            delta[u][v] = T[v][0]-T[u][0]+G[u][v]['weight']

    return delta
