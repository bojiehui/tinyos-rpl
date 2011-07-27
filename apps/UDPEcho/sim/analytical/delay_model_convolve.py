#!/usr/bin/python

from __future__ import division

import sys
import math
import pprint
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.colors as col
from matplotlib.figure import SubplotParams
import numpy as np

from sim.utils.helper import floatRange
from sim.utils.cpm import *
from sim.analytical.AnalyticalScenario import *
from sim.analytical.intpart import *

#########################
# use current config
#from sim.config import *

# use config from previous simulations

# small, more detailed distances
#SUITE = "2011_03_22__17_05_38" # linedirect 2..4 done
SUITE = "2011_03_24__08_52_49" # linecpm 2..4 done
#SUITE = "2011_03_22__09_26_10" # grid 4 done
#SUITE = "2011_03_25__08_55_20" # random 2..4 done

# big:
# SUITE = "2011_01_28__11_08_33" # linedirect 4..225, done
# SUITE = "2011_01_26__08_36_27" # line 4..225, done
# SUITE = "2011_01_11__11_14_27" # grid, 4..225, done

# small:
# SUITE = "2011_03_xx__xx_xx_xx" # grid 4             #todo
# SUITE = "2011_02_18__15_46_59" # linedirect 2..4 done
# SUITE = "2011_02_17__09_22_22" # linecpm 2..4 done
exec "from sim.output.suite_"+SUITE+".config import *"
#########################

TAU_L = 2.
#TAU_L_HALF = TAU_L/2.
#TAU_L_ONE_AND_HALF = TAU_L + TAU_L_HALF

RESOLUTION = 0.04
DOTS_PER_TAU_HALF = 1/RESOLUTION
NUMBER_OF_UNITS = 4

#YMAX = 1.5
YMAX = 1.0
#XMAX = 2*EVAL_HIGH_TIME
XMAX = EVAL_HIGH_TIME
RETRANSMISSIONS = 1

my_norm = col.Normalize(min(DISTANCE_LIST)*math.sqrt(min(NODES_LIST))-1,
                        max(DISTANCE_LIST)*math.sqrt(max(NODES_LIST))+1)
t = floatRange(0, 3*EVAL_HIGH_TIME, RESOLUTION)

#########################

try:
    print "trying to load distributions"
    UNITS = pickle.load(
        open("sim/analytical/dists/units_0_" + str(max(NODES_LIST)+10) + ".pickle",
             'rb'))
    DISTRIBUTIONS = pickle.load(
        open("sim/analytical/dists/dist_0_" + str(max(NODES_LIST)+10) + ".pickle",
             'rb'))
    print "distributions successfully loaded"
except:
    print "loading distribution failed"

    print "Setting up unit functions"
    UNITS = {}
    prev_stopped_at = 0
    for n in range (0, NUMBER_OF_UNITS):
        UNIT_n = []

        for i in range(0, int(prev_stopped_at+(n+1)*DOTS_PER_TAU_HALF)):
            UNIT_n.append(0)
        for i in range(0, int((n+1)*DOTS_PER_TAU_HALF)):
            UNIT_n.append(1/(n+1))
        prev_stopped_at += 2*i
        for i in range(0, int((n+1)*DOTS_PER_TAU_HALF)):
            UNIT_n.append(0)

        UNIT_n = np.array(UNIT_n)
        UNIT_n.resize(3*int(EVAL_HIGH_TIME*DOTS_PER_TAU_HALF))

        UNITS[n] = UNIT_n

    print "Setting up convoluted distribution functions"
    DISTRIBUTIONS = {}

    DISTRIBUTIONS[0] = {}
    #jump
    a = np.array([1],)
    a.resize(3*int(EVAL_HIGH_TIME*DOTS_PER_TAU_HALF))
    DISTRIBUTIONS[0][0] = a

    # no retransmissions for hop 0
    b = np.array([0],)
    b.resize(3*int(EVAL_HIGH_TIME*DOTS_PER_TAU_HALF))
    DISTRIBUTIONS[0][1] = b

    #for n in range (0, max(NODES_LIST)-1):
    for n in range (0, max(NODES_LIST)+10): # create some more
        print "Setting up convolution for", n
        CONV = np.array(UNITS[0])
        for c in range(0, n):
            CONV = np.convolve(CONV, UNITS[0])
                #print len(CONV)
                #print int(EVAL_HIGH_TIME*DOTS_PER_TAU_HALF)
        CONV.resize(3*int(EVAL_HIGH_TIME*DOTS_PER_TAU_HALF))
        DISTRIBUTIONS[n+1] = {}
        DISTRIBUTIONS[n+1][0] = CONV* RESOLUTION**n

        for r in range (1, RETRANSMISSIONS+1):
            CONV_RETR = np.array(UNITS[1])
            for c in range(0, n):
                if c < r-1:
                    CONV_RETR = np.convolve(CONV_RETR, UNITS[1])
                else:
                    CONV_RETR = np.convolve(CONV_RETR, UNITS[0])
                CONV_RETR.resize(3*int(EVAL_HIGH_TIME*DOTS_PER_TAU_HALF))
            DISTRIBUTIONS[n+1][r] = CONV_RETR* RESOLUTION**n

    print "Finished setting up convolutions"

    #print "Distributions", DISTRIBUTIONS

    of = open("sim/analytical/dists/units_0_" + str(max(NODES_LIST)+10) + ".pickle", "w")
    pickle.dump(UNITS, of)
    of.close()

    of = open("sim/analytical/dists/dist_0_" + str(max(NODES_LIST)+10) + ".pickle", "w")
    pickle.dump(DISTRIBUTIONS, of)
    of.close()

    print "Saved distributions"

if False:

    ################
    print "Creating figures for distributions"
    fig = plt.figure(figsize=(12, 8),
                     subplotpars = SubplotParams(left = 0.07,
                                                 bottom = 0.05,
                                                 top = 0.93,
                                                 right = 0.77))
    ax = fig.add_subplot(111)

    for n in range (0, NUMBER_OF_UNITS):
        plt.plot(t, UNITS[n],
                 linestyle='-',
                 label=str(n))

    plt.xlim(0, XMAX)
    plt.ylim(0, YMAX)

    plt.legend(bbox_to_anchor=(1.02, 1),
               loc = 2,
               borderaxespad=0. ,
               ncol = 2,
               fancybox = 'True')

    plt.savefig("sim/analytical/output/delaymodel_units.pdf")

    ################
    fig = plt.figure(figsize=(12, 8),
                     subplotpars = SubplotParams(left = 0.07,
                                                 bottom = 0.05,
                                                 top = 0.93,
                                                 right = 0.77))
    ax = fig.add_subplot(111)

    for n in range (0, max(NODES_LIST)):
        plt.plot(t, DISTRIBUTIONS[n][0],
                 linestyle='-',
                 label=str(n))

    plt.xlim(0, XMAX)
    plt.ylim(0, YMAX)

    plt.legend(bbox_to_anchor=(1.02, 1),
                   loc = 2,
                   borderaxespad=0. ,
                   ncol = 2,
                   fancybox = 'True')

    plt.savefig("sim/analytical/output/delaymodel_convolutions.pdf")

    ##
    fig = plt.figure(figsize=(12, 8),
                     subplotpars = SubplotParams(left = 0.07,
                                                 bottom = 0.05,
                                                 top = 0.93,
                                                 right = 0.77))
    ax = fig.add_subplot(111)

    for n in range (0, max(NODES_LIST)):
        for r in range (1, RETRANSMISSIONS+1):
            plt.plot(t, DISTRIBUTIONS[n][r],
                     linestyle='-',
                     label=str(n) + " retr " + str(r))

    plt.xlim(0, XMAX)
    plt.ylim(0, YMAX)

    plt.legend(bbox_to_anchor=(1.02, 1),
                   loc = 2,
                   borderaxespad=0. ,
                   #loc = (.9, .5),
                   fancybox = 'True')

    plt.savefig("sim/analytical/output/delaymodel_convolutions_retr.pdf")

    ##
    fig = plt.figure(figsize=(12, 8),
                     subplotpars = SubplotParams(left = 0.07,
                                                 bottom = 0.05,
                                                 top = 0.93,
                                                 right = 0.77))
    ax = fig.add_subplot(111)

    plt.plot(t, DISTRIBUTIONS[2][0],
             linestyle='-',
             label="h2 r0")
    plt.plot(t, DISTRIBUTIONS[2][1],
             linestyle=':',
             label="h2 r1")
    plt.plot(t, DISTRIBUTIONS[3][0],
             linestyle='-',
             label="h3 r0")

    plt.xlim(0, XMAX)
    plt.ylim(0, YMAX)

    plt.legend(bbox_to_anchor=(1.02, 1),
               loc = 2,
               borderaxespad=0. ,
               fancybox = 'True')
    plt.savefig("sim/analytical/output/delaymodel_distributions.pdf")

pp = pprint.PrettyPrinter(indent=2)

print "Creating analytical general delay model for some distances"

#TODO: derive PRR from the scenario:
NODES = 4

PRR = {}
for DIST in DISTANCE_LIST:
    PRR[DIST] = {}
    anasc = AnalyticalScenario(SUITE, NODES, DIST)

    for i in anasc.scen:
        #print i
        if i == 1 or i == 2:
            # ignore basestation and seed node
            pass
        else:
            dist = calc_distance(anasc.scen, 2, i)
            prr = dist2prr(dist)
            # second index: neighbor number, not hopcount
            PRR[DIST][i-2] = prr

print "PRR:"
pp.pprint(PRR)

prr_h_n_p = {}
retransmissions = {}

# for DIST in DISTANCE_LIST:
#     print ">"*20, "DIST", DIST
#     Hr[DIST] = {}
#     H_BASE[DIST] = {}

#     for h in range(1, NODES):
#         Hr[DIST][h] = {}
#         for r in range(0, RETRANSMISSIONS+1):
#             if r == 0:
#                 Hr[DIST][h][r] = 1
#             else:
#                 Hr[DIST][h][r] = 0

#     #---------- no retransmissions
#     #n1,h1,i1
#     #n2,h1,i2
#     #n2,h1,i1 (NO)
#     #n3,h1,i3
#     #n3,h1,i2 (NO)
#     #n3,h1,i1 (NO)

#     #n2,h2,i2
#     #n3,h2,i3,p1
#     #n3,h2,i3,p2
#     #n3,h2,i2 (NO)

#     #n3,h3,i3

#     #---------- 1 retransmission
#     #n1,h1,i1,r1
#     #n2,h1,i2,r1
#     #n2,h1,i1,r1 (NO)
#     #n3,h1,i3,r1
#     #n3,h1,i2,r1 (NO)
#     #n3,h1,i1,r1 (NO)

#     #n2,h2,i2,r1
#     #n3,h2,i3,p1,r1
#     #n3,h2,i3,p2,r1
#     #n3,h2,i2,r1 (NO)

#     #n3,h3,i3,r1

#     #########################
#     #########################
#     # 1. hop
#     #########################
#     #---------- no retransmissions
#     #n1,h1,i1
#     #n2,h1,i2
#     #n2,h1,i1 (NO)
#     #n3,h1,i3
#     #n3,h1,i2 (NO)
#     #n3,h1,i1 (NO)
#     n1_h1_i1 = PRR[DIST][1]
#     n2_h1_i2 = PRR[DIST][3]
#     n3_h1_i3 = PRR[DIST][3]

#     onehop = 0
#     for h in range(1, NODES):
#         #print "h", h
#         H_BASE[DIST][h] = {}
#         H_BASE[DIST][h][1] = PRR[DIST][h]
#         onehop += PRR[DIST][h]
#         print "1", PRR[DIST][h]
#     Hr[DIST][1][0] = onehop

#     #########################
#     # 1. hop
#     #########################
#     #---------- 1 retransmission
#     #red:
#     #n1,h1,i1,r1
#     #n2,h1,i2,r1
#     #n2,h1,i1,r1 (NO)
#     #n3,h1,i3,r1
#     #n3,h1,i2,r1 (NO)
#     #n3,h1,i1,r1 (NO)

#     onehop_retr = 0
#     for n in range(1, NODES):
#         print "n", n
#         retr = (1-PRR[DIST][n]) * PRR[DIST][n]
#         print "(1-PRR[",n,"]) * PRR[",n,"]"

#         for h in range(1, n):
#             #print " h", h
#             retr *= (1-PRR[DIST][h])
#             print "*(1-PRR[",h,"])"

#         onehop_retr += retr
#         print "1r*", retr
#     Hr[DIST][1][1] = onehop_retr
#     #Hr[DIST][1][1] = 0

#     #########################
#     #########################
#     # 2. hop
#     #########################
#     #---------- no retransmissions
#     #n2,h2,i2
#     #n3,h2,i3,p1
#     #n3,h2,i3,p2
#     #n3,h2,i2 (NO)
#     #FIXME: make this possible for varying number of nodes
#     n2_h2_i2    = (1-PRR[DIST][2]) * PRR[DIST][1] * PRR[DIST][1]
#     n3_h2_i3_p1 = (1-PRR[DIST][3]) * PRR[DIST][2] * PRR[DIST][1]
#     n3_h2_i3_p2 = (1-PRR[DIST][3]) * (1-PRR[DIST][2]) * PRR[DIST][1] * PRR[DIST][2]
#     print "2", n2_h2_i2
#     print "2", n3_h2_i3_p1
#     print "2", n3_h2_i3_p2

#     #H[DIST][2]     = n2_h2_i2 + n3_h2_i3_p1 + n3_h2_i3_p2
#     Hr[DIST][2][0] = n2_h2_i2 + n3_h2_i3_p1 + n3_h2_i3_p2

#     #########################
#     # 2. hop
#     #########################
#     #---------- 1 retransmission
#     #green:
#     #n2,h2,i2,r1 (2PRR1 possibilities)
#     #n3,h2,i3,p1,r1 (additional *(1-PRR[DIST][1]) possibly from n2,h2,i2,r1)
#     #n3,h2,i3,p2,r1 (additional *(1-PRR[DIST][1]) possibly from n2,h2,i2,r1)
#     #n3,h2,i2,r1 (NO)
#     #FIXME: make this possible for varying number of nodes
#     n2_h2_i2_r1    = (1-PRR[DIST][2]) * PRR[DIST][1] * (1-PRR[DIST][1]) * PRR[DIST][1]*2
#     #              = n2_h2_i2 * (1-PRR[DIST][1])*2
#     n2_h2_i2_p1_r1 = (1-PRR[DIST][3]) * PRR[DIST][2] * (1-PRR[DIST][1]) * PRR[DIST][1] \
#         *(1-PRR[DIST][1])
#     #              = n2_h2_i2_p1 * (1-PRR[DIST][1]) *(1-PRR[DIST][1])
#     n2_h2_i2_p2_r1 = (1-PRR[DIST][3]) * (1-PRR[DIST][2]) * PRR[DIST][1] * (1-PRR[DIST][2]) * PRR[DIST][2] \
#         *(1-PRR[DIST][1])
#     #              = n2_h2_i2_p2 * (1-PRR[DIST][2]) *(1-PRR[DIST][1])

#     print "2r", n2_h2_i2_r1
#     print "2r", n2_h2_i2_p1_r1
#     print "2r", n2_h2_i2_p2_r1

#     Hr[DIST][2][1] = n2_h2_i2_r1 + n2_h2_i2_p1_r1 + n2_h2_i2_p2_r1
#     #Hr[DIST][2][1] = 0

#     # TEST::::
#     n2_h2_i2_r1    = \
#         (1-PRR[DIST][2]) * PRR[DIST][1] * (1-PRR[DIST][1]) * PRR[DIST][1] * PRR[DIST][1] + \
#         (1-PRR[DIST][2]) * PRR[DIST][1] * (1-PRR[DIST][1]) * PRR[DIST][1] * PRR[DIST][1]
#     n2_h2_i2_p1_r1 = \
#         (1-PRR[DIST][3]) * PRR[DIST][2] * (1-PRR[DIST][1]) * PRR[DIST][1]
#     n2_h2_i2_p2_r1 = \
#         (1-PRR[DIST][3]) * (1-PRR[DIST][2]) * PRR[DIST][1] * (1-PRR[DIST][2]) * PRR[DIST][2]

#     # n2_h2_i2_r1    = \
#     #     (1-PRR[DIST][2]) * PRR[DIST][1] * (1-PRR[DIST][1]) * PRR[DIST][1] *PRR[DIST][1]+ \
#     #     (1-PRR[DIST][2]) * (1-PRR[DIST][1]) * PRR[DIST][1] * PRR[DIST][1] *PRR[DIST][1]

#     # n2_h2_i2_p1_r1 = \
#     #     (1-PRR[DIST][3]) * (1-PRR[DIST][2]) * PRR[DIST][1] * PRR[DIST][1] * PRR[DIST][2] *(1-PRR[DIST][1]) + \
#     #     (1-PRR[DIST][3]) * PRR[DIST][2] * (1-PRR[DIST][1]) * PRR[DIST][1] * PRR[DIST][1]         *(1-PRR[DIST][1])
#     # # added  *(1-PRR[DIST][1])

#     # n2_h2_i2_p2_r1 = \
#     #     (1-PRR[DIST][3]) * (1-PRR[DIST][2]) * (1-PRR[DIST][1]) * PRR[DIST][2] * PRR[DIST][1] *(1-PRR[DIST][1])+ \
#     #     (1-PRR[DIST][3]) * (1-PRR[DIST][2]) * PRR[DIST][1] * (1-PRR[DIST][2]) * PRR[DIST][2]      *(1-PRR[DIST][1])
#     # # added  *(1-PRR[DIST][1])

#     Hr[DIST][2][1] = n2_h2_i2_r1 #+ n2_h2_i2_p1_r1# + n2_h2_i2_p2_r1
#     #Hr[DIST][2][1] = 0

#     #########################
#     #########################
#     # 3. hop
#     #########################
#     #---------- no retransmissions
#     #n3,h3,i3
#     #FIXME: make this possible for varying number of nodes
#     n3_h3_i3 = (1-PRR[DIST][3])*(1-PRR[DIST][2])*PRR[DIST][1]*(1-PRR[DIST][2])*PRR[DIST][1]*PRR[DIST][1]
#     #n3_h3_i3 = (1-PRR[DIST][3])*(1-PRR[DIST][2])*PRR[DIST][1]*(1-PRR[DIST][2])*PRR[DIST][1]*PRR[DIST][1]*PRR[DIST][1]
#     #n3_h3_i3 = (1-PRR[DIST][3])*(1-PRR[DIST][2])*PRR[DIST][1]*PRR[DIST][1]*PRR[DIST][1]*PRR[DIST][1]
#     print "3", n3_h3_i3

#     Hr[DIST][3][0] = n3_h3_i3

#     #########################
#     #---------- 1 retransmission
#     #n3,h3,i3,r1 (PRR1 might happen on 3 links)
#     #FIXME: make this possible for varying number of nodes
#     n3_h3_i3_r1 = (1-PRR[DIST][3]) * (1-PRR[DIST][2]) * PRR[DIST][1] * (1-PRR[DIST][2]) * PRR[DIST][1] * (1-PRR[DIST][1]) * PRR[DIST][1]
#     print "3r", n3_h3_i3_r1

#     Hr[DIST][3][1] = 3*n3_h3_i3_r1
#     #Hr[DIST][3][1] = 0


#     # TEST::::
#     n3_h3_i3_r1 = \
#         (1-PRR[DIST][3]) * (1-PRR[DIST][2]) * PRR[DIST][1] * (1-PRR[DIST][2]) * PRR[DIST][1] * (1-PRR[DIST][1]) * PRR[DIST][1] + \
#         (1-PRR[DIST][3]) * (1-PRR[DIST][2]) * PRR[DIST][1] * (1-PRR[DIST][2]) * PRR[DIST][1] * (1-PRR[DIST][1]) * PRR[DIST][1] + \
#         (1-PRR[DIST][3]) * (1-PRR[DIST][2]) * PRR[DIST][1] * (1-PRR[DIST][2]) * PRR[DIST][1] * (1-PRR[DIST][1]) * PRR[DIST][1]
#     # n3_h3_i3_r1 = \
#     #     (1-PRR[DIST][3]) * (1-PRR[DIST][2]) * (1-PRR[DIST][1]) * (1-PRR[DIST][2]) * PRR[DIST][1] * PRR[DIST][1] * PRR[DIST][1] + \
#     #     (1-PRR[DIST][3]) * (1-PRR[DIST][2]) * PRR[DIST][1] * (1-PRR[DIST][2]) * (1-PRR[DIST][1]) * PRR[DIST][1] * PRR[DIST][1] + \
#     #     (1-PRR[DIST][3]) * (1-PRR[DIST][2]) * PRR[DIST][1] * (1-PRR[DIST][2]) * PRR[DIST][1] * (1-PRR[DIST][1]) * PRR[DIST][1]
#     print "3r", n3_h3_i3_r1

#     Hr[DIST][3][1] = n3_h3_i3_r1
#     #Hr[DIST][3][1] = 0

#     #########################
#     #########################
#     #########################

#     #                                       0-1-2-3

#     # split up path to node n into h hops, all permutations
#     # h = 1 hop
#     # n = 1 -> prr1 (h1,n1,i1)              0-1
#     #          PRR[DIST][1]
#     # n = 2 -> prr2 (h2,n1,i2)              0---2
#     #          PRR[DIST][2]
#     # n = 3 -> prr3 (h3,n1,i3)              0-----3
#     #          PRR[DIST][3]

#     # h = 2 hops
#     # n = 2 -> prr1, prr1 (n2_h2_i2)        0-1-2
#     #          (1-PRR[DIST][2]) * PRR[DIST][1] * PRR[DIST][1]
#     #          = (1-PRR[DIST][2]) *
#     #            PRR[DIST][1] * PRR[DIST][1]
#     # n = 3 -> prr2, prr1 (n2_h2_i2_p1)     0---2-3
#     #          (1-PRR[DIST][3]) * PRR[DIST][2] * PRR[DIST][1]
#     #          = (1-PRR[DIST][3]) *
#     #            PRR[DIST][2] * PRR[DIST][1]
#     # n = 3 -> prr1, prr2 (n2_h2_i2p2)      0-1---3
#     #          (1-PRR[DIST][3]) * (1-PRR[DIST][2]) * PRR[DIST][1] * PRR[DIST][2]
#     #          = (1-PRR[DIST][3]) * (1-PRR[DIST][2]) *
#     #            PRR[DIST][1] * PRR[DIST][2]

#     # h = 3 hops
#     # n = 3 -> prr1, prr1, prr1 (n3_h3_i3)  0-1-2-3
#     #          (1-PRR[DIST][3])*(1-PRR[DIST][2])*PRR[DIST][1]*(1-PRR[DIST][2])*PRR[DIST][1]*PRR[DIST][1]
#     #          = (1-PRR[DIST][3]) * (1-PRR[DIST][2]) * PRR[DIST][1] * (1-PRR[DIST][2]) *
#     #            PRR[DIST][1]*PRR[DIST][1]
#     #            (missing *PRR[DIST][1], already in remainder)

for DIST in DISTANCE_LIST:
    print ">"*20, "DIST", DIST

    remainder = {}
    hop_path = {}
    prr_h_n_p[DIST] = {}
    retransmissions[DIST] = {}

    for n in range(1, NODES): # node number
        hop_path[n] = create_perm_partitions(n)
    print "Hop Path", hop_path

    for h in range(1, NODES): # hops
        remainder[h] = {}
        prr_h_n_p[DIST][h] = {}
        retransmissions[DIST][h] = {}
        for n in range(h, NODES): # node number

            remainder[h][n] = []
            prr_h_n_p[DIST][h][n] = {}
            retransmissions[DIST][h][n] = 0

            print "~"*20
            print "hop_path[n][h]", hop_path[n][h]

            for p in range(0, len(hop_path[n][h])): # hop path
                print "~"*10
                print "hops", h, "node", n, "path", p
                #print "Hop Path", hop_path[n][h][p]

                print "prr = ",
                ##### retrieve previous remainder for n, h, p
                if h == 1:
                    print "1*",
                    prev_remainder = 1
                else:
                    # h != 1:
                    if p == 0:
                        print "remainder([", h-1, "][", n, "][", p, "]",
                        print "|", remainder[h-1][n][p], "|)*",
                        #prev_remainder = remainder[h-1][n][p]
                        prev_remainder = remainder[h-1][n][-1]
                    else:
                        prev_remainder = 1
                        #CHECK: is this correct?
                        for n_index in range(n-p, n):
                            print "remainder([", h-1, "][", n_index, "][", 0, "]",
                            print "|", remainder[h-1][n_index][0], "|)*",
                            prev_remainder *= remainder[h-1][n_index][0]
                print "|||",

                ##### calculate path prr for n, h, p
                path_prr_not_already_in_remainder_n_h_p = 1
                print "1",
                if p == 0:
                    for hp_index in range(0, len(hop_path[n][h][p])):
                        #print "hp_index", hp_index
                        #print h
                        #print hop_path[n][h]
                        #print hop_path[n][h][p][hp_index]

                        try:
                            if hop_path[n][h][p][hp_index] != hop_path[n][h-1][p][hp_index]:
                                path_prr_not_already_in_remainder_n_h_p *= PRR[DIST][ hop_path[n][h][p][hp_index] ]
                                print "(prr", hop_path[n][h][p][hp_index], "|", PRR[DIST][ hop_path[n][h][p][hp_index] ], "|)*",
                            else:
                                #already in remainder
                                pass
                        except:
                            #unequal length
                            print "(prr", hop_path[n][h][p][hp_index], "|", PRR[DIST][ hop_path[n][h][p][hp_index] ], "|)*",
                            path_prr_not_already_in_remainder_n_h_p *= PRR[DIST][ hop_path[n][h][p][hp_index] ]
                else:
                    for hp_index in range(0, len(hop_path[n][h][p])):

                        try:
                            if hop_path[n][h][p][hp_index] != hop_path[n][h][p][hp_index-1]:
                                path_prr_not_already_in_remainder_n_h_p *= PRR[DIST][ hop_path[n][h][p][hp_index] ]
                                print "(prr", hop_path[n][h][p][hp_index], "|", PRR[DIST][ hop_path[n][h][p][hp_index] ], "|)*",
                            else:
                                #already in remainder
                                pass
                        except:
                            #unequal length
                            path_prr_not_already_in_remainder_n_h_p *= PRR[DIST][ hop_path[n][h][p][hp_index] ]
                            print "(prr", hop_path[n][h][p][hp_index], "|", PRR[DIST][ hop_path[n][h][p][hp_index] ], "|)*",
                #print ">>", h-1, n, p

                ##### calculate prr for n, h, p
                prr_h_n_p[DIST][h][n][p] = prev_remainder * path_prr_not_already_in_remainder_n_h_p ## CHECK
                print "=", prr_h_n_p[DIST][h][n][p]
                print "#####~", n, h, p, "->", prr_h_n_p[DIST][h][n][p]
                print ""

                ##### calculate remainder for n, h, p
                if p == 0:
                    try:
                        remainder[h][n].append(prr_h_n_p[DIST][h][n][p] \
                                                   / PRR[DIST][ hop_path[n][h][-1][-1] ] \
                                                   * (1-PRR[DIST][ hop_path[n][h][-1][-1] ]))
                        print "remainder([", h, "][", n, "] |", remainder[h][n], "|) appendA ",
                        #print "remainder([", h, "][", n, "][-1] |", remainder[h][n][-1],

                        print "prr_h_n_p[DIST][",h,"][",n,"][",p,"] |", prr_h_n_p[DIST][h][n][p],
                        print "/(prr", hop_path[n][h][-1][-1], "|", PRR[DIST][ hop_path[n][h][-1][-1] ], "|)",
                        print "*(1-prr", hop_path[n][h][-1][-1], "|", 1-PRR[DIST][ hop_path[n][h][-1][-1] ], "|)",
                        print "=", prr_h_n_p[DIST][h][n][p] \
                            / PRR[DIST][ hop_path[n][h][-1][-1] ] \
                            * (1-PRR[DIST][ hop_path[n][h][-1][-1] ])
                    except ZeroDivisionError:
                        print "Could not divide by PRR[DIST][hop_path[",n,"][",h,"][",-1,"][",-1,"]] |",
                        print "PRR[DIST][", hop_path[n][h][-1][-1], "] |",
                        print PRR[DIST][ hop_path[n][h][-1][-1] ]

                        ###FIXME: 26.04.2011, remainder for n3h3 is not OK, check @ DIST 120

                        try:
                            remainder[h][n].append(remainder[h-1][n][-1]*(1-PRR[DIST][ hop_path[n][h][-1][-1] ]))
                            print "remainder([", h, "][", n, "] |", remainder[h][n], "|) appendB1 ",
                            print "(remainder[",h-1,"][",n,"][",-1,"] |", remainder[h-1][n][-1], "|)",
                            print "*(1-prr", hop_path[n][h][-1][-1], "|", 1-PRR[DIST][ hop_path[n][h][-1][-1] ], "|)",
                            print "=", remainder[h-1][n][-1]*(1-PRR[DIST][ hop_path[n][h][-1][-1] ])
                        except:
                            print "Could not use remainder[",h-1,"][",n,"]"
                            remainder[h][n].append(1)
                            print "remainder([", h, "][", n, "] |", remainder[h][n], "|) appendB2 ",
                            print "=", 1
                else:
                    #print "A", n, h-1
                    #print "B", hop_path[n][h]
                    #print "C1", hop_path[n][h][p]
                    #print "C2", hop_path[n][h][p-1]

                    print "remainder([", h, "][", n, "] |", remainder[h][n], "|) appendC ",
                    print "(remainder[",h,"][",n,"][",p-1,"] |", remainder[h][n][p-1], "|)",

                    new_remainder = 1
                    for hp_index in range(0, len(hop_path[n][h][p])):
                        #print "^^^^^", hp_index, len(hop_path[n][h][p])
                        if hp_index == len(hop_path[n][h][p])-1:
                            print "*(1- prr", hop_path[n][h][p][hp_index], "|", 1-PRR[DIST][ hop_path[n][h][p][hp_index] ], "|)",
                            new_remainder *= (1-PRR[DIST][ hop_path[n][h][p][hp_index] ])
                        else:
                            print "*prr", hop_path[n][h][p][hp_index], "|", PRR[DIST][ hop_path[n][h][p][hp_index] ], "|",
                            new_remainder *= PRR[DIST][ hop_path[n][h][p][hp_index] ]

                    remainder[h][n].append(remainder[h][n][p-1] * new_remainder)

                    print "=", remainder[h][n][p-1] * new_remainder
                print "~remainder"

                ##### calculate retransmission for n, h, p
                if h == 1:
                    ret_val = prr_h_n_p[DIST][h][n][p] * remainder[h][n][-1]
                    for n2 in range(1, n):
                        #print "*(1-PRR[",n2,"])"
                        ret_val *= (1-PRR[DIST][n2])
                    retransmissions[DIST][h][n] = ret_val
                elif n == h:
                    retransmissions[DIST][h][n] = prr_h_n_p[DIST][h][n][p] * (1-PRR[DIST][ 1 ]) * n

    print "#"*20
    print DIST, prr_h_n_p[DIST]
    print DIST, retransmissions[DIST]
    print "#"*20

P2 = {}
print ""
for DIST in DISTANCE_LIST:
    prr_h_n = {}
    prr_h = {}
    prr_h[0] = 1
    retransmissions_h = {}

    #print "h", range(1, NODES)
    for h in range(1, NODES): # hops
        prr_h[h] = 0
        prr_h_n[h] = {}
        retransmissions_h[h] = 0
        #print " n", range(h, NODES)
        for n in range(h, NODES): # node number
            sum = 0
            #print "  p", range(0, len(hop_path[n][h]))
            for p in range(0, len(hop_path[n][h])): # hop path
                sum += prr_h_n_p[DIST][h][n][p]
            # CHECK: divide by number of paths?
            if h == 1:
                prr_h_n[h][n] = sum
            else:
                prr_h_n[h][n] = sum
                #prr_h_n[h][n] = sum/len(hop_path[n][h])
                #prr_h_n[h][n] = sum/len(hop_path[n][h-1])
            prr_h[h] += prr_h_n[h][n]
            try:
                #print n, h, retransmissions[DIST][h][n]
                retransmissions_h[h] += retransmissions[DIST][h][n]
            except KeyError:
                pass

    #print DIST, prr_h_n
    print DIST, " ",
    p_entry = {}

    for key in prr_h:
        if not p_entry.has_key(key):
            p_entry[key] = {}
        p_entry[key][0] = prr_h[key]

    p_entry[0][1] = 0
    for key in retransmissions_h:
        if not p_entry.has_key(key):
            p_entry[key] = {}
        p_entry[key][1] = retransmissions_h[key]

    P2[DIST] = p_entry
    pp.pprint(prr_h)
    pp.pprint(retransmissions_h)

print ""
print "P2:"
pp.pprint(P2)
P = P2

##################
# PDF
##################
fig = plt.figure(figsize=(12, 8),
                 subplotpars = SubplotParams(left = 0.07,
                                             bottom = 0.05,
                                             top = 0.93,
                                             right = 0.77))
ax = fig.add_subplot(111)

plt.title('Analytical Model for the Time to Consistency\n(#Nodes: '+str(NODES)+')')
plt.xlabel("Model Time [s]")
plt.ylabel("Node Consistency PDF")

plt.grid()

ax.set_yticks(floatRange(0,
                         1.1,
                         0.1))

#create the joint pdf
JOINT = {}

print "="*60
for DIST in DISTANCE_LIST:
    JOINT[DIST] = []
    sum = 0

    for t_index in range(0, len(t)):

        sum = 0
        for n in range(0, NODES):
            #sum += H[DIST][n]* (P[DIST][n][0]* DISTRIBUTIONS[n][0][t_index] + \
            sum += (P[DIST][n][0]* DISTRIBUTIONS[n][0][t_index] + \
                                    P[DIST][n][1]* DISTRIBUTIONS[n][1][t_index] \
                       )

        JOINT[DIST].append(1/float(NODES)*sum)

    plt.plot(t, JOINT[DIST],
             linestyle='-',
             label=str(DIST))

plt.xlim(0, XMAX)
plt.ylim(0, YMAX)

plt.legend(bbox_to_anchor=(1.02, 1),
           loc = 2,
           borderaxespad=0. ,
           title = "Distance [m]",
           ncol = 2,
           fancybox = 'True')

plt.savefig("sim/analytical/output/delaymodel_convolve_"+str(NODES)+"_test_pdf.pdf")

##################
# CDF
##################
fig = plt.figure(figsize=(12, 8),
                 subplotpars = SubplotParams(left = 0.07,
                                             bottom = 0.05,
                                             top = 0.93,
                                             right = 0.77))
ax = fig.add_subplot(111)

plt.title('Analytical Model for the Time to Consistency\n(#Nodes: '+str(NODES)+')')
plt.xlabel("Model Time [s]")
plt.ylabel("Nodes consistent")
plt.grid()

ax.set_xticks(range(0,
                    10,
                    2))

ax.set_yticks(floatRange(0,
                         YMAX,
                         0.1))

JOINT_CDF = {}

for DIST in DISTANCE_LIST:
    JOINT_CDF[DIST] = []
    sum = 0
    for t_index in range(0, len(JOINT[DIST])):
        if t_index == 0:
            sum += JOINT[DIST][t_index]
        else:
            sum += JOINT[DIST][t_index]*RESOLUTION
        JOINT_CDF[DIST].append(sum)

    np.save("sim/analytical/npy/suite_"+SUITE+"_dist"+str(DIST)+"_hist_consist_avail_model.npy",
            JOINT_CDF[DIST])


    plt.plot(t, JOINT_CDF[DIST],
             linestyle='-',
             color=plt.cm.jet(my_norm(DIST*math.sqrt(NODES))),
             label=str(DIST)
             )

plt.xlim(-0.2, XMAX)
#plt.ylim(0, 1.02)
plt.ylim(0, YMAX)

plt.legend(bbox_to_anchor=(1.02, 1),
           loc = 2,
           borderaxespad=0. ,
           title = "Distance [m]",
           ncol = 2,
           #loc = (.9, .5),
           fancybox = 'True')
plt.savefig("sim/analytical/output/delaymodel_convolve_"+str(NODES)+"_test_cdf.pdf")

################
################
################
sys.exit(0)


################
# DEPRECATED:  #
################

#JOINT_CDF_PRR = []
#JOINT_CDF_PRR_2 = []
#JOINT_CDF_SIMPLIFIED = []


print "Creating general analytical delay model"

for NODES in [4]:
#for NODES in NODES_LIST:
    print "*"*60
    print "Calculating analytical model for", NODES

    fig = plt.figure(figsize=(12, 8),
                     subplotpars = SubplotParams(left = 0.07,
                                                 bottom = 0.05,
                                                 top = 0.93,
                                                 right = 0.77))
    ax = fig.add_subplot(111)

    ##################
    # PDF
    ##################
    plt.title('Analytical Model for the Time to Consistency\n(#Nodes: '+str(NODES)+')')
    plt.xlabel("Model Time [s]")
    plt.ylabel("Node Consistency PDF")

    plt.grid()

    ax.set_yticks(floatRange(0,
                             YMAX,
                             0.1))

    for n in range(0, NODES):
        #print key
        #print DISTRIBUTIONS[key]
        plt.plot(t, 1/float(NODES)*DISTRIBUTIONS[n][0],
                 linestyle='-',
                 #marker='.',
                 label=str(n)+ " " + "hops")

    #create the joint pdf
    JOINT = {}

    for DIST in DISTANCE_LIST:
        JOINT[DIST] = []
        print "="*60
        print "Calculating analytical model for", NODES, DIST

        anasc = AnalyticalScenario(SUITE, NODES, DIST)
        (distribution_quantity, distribution_quantity_mod, distribution_freq) = anasc.get_distribution_quantity(
            NODES,
            RETRANSMISSIONS)

        no_pathes = 0
        for h in distribution_freq:
            no_pathes += h[1]
        print "#Pathes", no_pathes

        print "####Dist Quant:", distribution_quantity
        print "####Dist Quant Mod:", distribution_quantity_mod
        print "####Dist Freq:", distribution_freq

        for t_index in range(0, len(t)):
            sum = 0

            for (distribution, retransmission, quantity) in distribution_quantity_mod:
                #print "####no retransmission", distribution, quantity
                if distribution > 1:
                #if False:
                    sum += DISTRIBUTIONS[distribution][retransmission][t_index]*quantity*distribution_freq[distribution][1]/distribution_freq[1][1]
                else:
                    sum += DISTRIBUTIONS[distribution][retransmission][t_index]*quantity
                pass


            # #print "JOINT CDF"
            #JOINT[DIST].append(sum)
            JOINT[DIST].append(1/float(NODES)*sum)
            #JOINT[DIST].append(1/float(no_pathes)*sum)

        plt.plot(t, JOINT[DIST],
                 linestyle='-',
                 label="joint ("+str(DIST)+")" )

    plt.xlim(0, XMAX)
    plt.ylim(0, YMAX)

    plt.legend(bbox_to_anchor=(1.02, 1),
               loc = 2,
               borderaxespad=0. ,
               title = "Distance [m]",
               ncol = 2,
               #loc = (.9, .5),
               fancybox = 'True')

    plt.savefig("sim/analytical/output/delaymodel_convolve_"+str(NODES)+"_pdf.pdf")

    ##################
    # CDF
    ##################
    fig = plt.figure(figsize=(12, 8),
                     subplotpars = SubplotParams(left = 0.07,
                                                 bottom = 0.05,
                                                 top = 0.93,
                                                 right = 0.77))
    #fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111)

    plt.title('Analytical Model for the Time to Consistency\n(#Nodes: '+str(NODES)+')')
    plt.xlabel("Model Time [s]")
    plt.ylabel("Nodes consistent")
    plt.grid()

    ax.set_yticks(floatRange(0,
                             YMAX,
                             0.1))

    JOINT_CDF = {}
    JOINT_CDF_PRR = []
    JOINT_CDF_PRR_2 = []
    JOINT_CDF_SIMPLIFIED = []

    # DETAILED
    for DIST in DISTANCE_LIST:
        JOINT_CDF[DIST] = []
        sum = 0
        for t_index in range(0, len(JOINT[DIST])):
            if t_index == 0:
                sum += JOINT[DIST][t_index]
            else:
                sum += JOINT[DIST][t_index]*RESOLUTION
            JOINT_CDF[DIST].append(sum)

        plt.plot(t, JOINT_CDF[DIST],
                 linestyle='-',
                 #marker='.',
                 #label="joint"
                 color=plt.cm.jet(my_norm(DIST*math.sqrt(NODES))),
                 label=str(DIST)
                 #label="detailed ("+str(DIST)+")"
                 )

    # # SIMPLIFIED
    # sum = 0
    # for t_index in range(0, len(JOINT)):
    #     #sum += 1/float(NODES)*JOINT[t_index]
    #     if t_index == 0:
    #         sum += JOINT[t_index]/NODES
    #     elif DOTS_PER_TAU_HALF <= t_index <= 2*DOTS_PER_TAU_HALF:
    #         sum += 1/float(NODES)*RESOLUTION
    #     elif t_index >= 2*DOTS_PER_TAU_HALF:
    #         sum += 1/float(NODES)*0.67*RESOLUTION
    #     JOINT_CDF_SIMPLIFIED.append(sum)

    # plt.plot(t, JOINT_CDF_SIMPLIFIED,
    #          linestyle='-',
    #          #marker='.',
    #          label="simplified"
    #          )

    plt.xlim(-0.2, XMAX)
    plt.ylim(0, YMAX)

    plt.legend(bbox_to_anchor=(1.02, 1),
               loc = 2,
               borderaxespad=0. ,
               title = "Distance [m]",
               ncol = 2,
               #loc = (.9, .5),
               fancybox = 'True')
    plt.savefig("sim/analytical/output/delaymodel_convolve_"+str(NODES)+"_cdf.pdf")
