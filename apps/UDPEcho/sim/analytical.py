#!/usr/bin/python

from __future__ import division
import math

from sim.config import *
from sim.utils.helper import *

import matplotlib
matplotlib.use('agg') 
import matplotlib.pyplot as plt
import matplotlib.colors as col
from matplotlib.figure import SubplotParams
from matplotlib.ticker import MultipleLocator

from scipy.special import erf

def calc_cycles(time):
    UOB_TAU_LOW_SEC  = UOB_TAU_LOW / 1000
    UOB_TAU_HIGH_SEC = UOB_TAU_HIGH / 1000

    if time > 2*UOB_TAU_HIGH_SEC - 1 - math.log(UOB_TAU_LOW_SEC, 2):
        return math.log(UOB_TAU_HIGH_SEC, 2) \
            - math.log(UOB_TAU_LOW_SEC, 2) + 1\
            + (time - (2*UOB_TAU_HIGH_SEC - 1 - math.log(UOB_TAU_LOW_SEC, 2))) \
            / UOB_TAU_HIGH_SEC

    elif time <= 2*UOB_TAU_HIGH_SEC - 1 - math.log(UOB_TAU_LOW_SEC, 2):
        return math.log(UOB_TAU_HIGH_SEC, 2) \
            - math.log(UOB_TAU_LOW_SEC, 2) + 1\
            + (time - (2*time - 1 - math.log(UOB_TAU_LOW_SEC, 2))) \
            / math.pow(math.log(time, 2) - math.log(UOB_TAU_LOW_SEC, 2) + 1, 2)

def calc_messages(k, c, sqr_nodes, neighbors):
    return 1.5 * k * c * math.pow(sqr_nodes, 2) / neighbors + 1.5 * k * sqr_nodes

#http://www.research.att.com/~njas/sequences/A000328
A000328 = [1,5,13,29,49,81,113,149,197,253,317,377,441,529,
           613,709,797,901,1009,1129,1257,1373,1517,1653,
           1793,1961,2121,2289,2453,2629,2821,3001,3209,3409,
           3625,3853,4053,4293,4513,4777,5025,5261,5525,5789,
           6077,6361,6625]

def estimate_neighbors(d):

    if d <= 46 and isinstance(d, int) :
        return A000328[d]-1
    else:
        print "WARNING: Number of Neighbors is numerically estimated",

    #Weisstein, Eric W. "Gauss's Circle Problem." From MathWorld - A
    #Wolfram WebResource.
    #http://mathworld.wolfram.com/GausssCircleProblem.html
    sum = 0
    for j in range(1, int(math.pow(d, 2))):
        sum += ( math.pow(-1, j+1) * math.floor( (math.pow(d, 2))/(2*j-1) ) )
    return 4 * sum

c = calc_cycles(SEC_AFTER_INJECT)
print "Number of cycles(",
print SEC_BEFORE_INJECT + SEC_AFTER_INJECT, "s) without turnoff:",
print c

if TURNOFF_NODE_TIME != 0:
    print "Number of cycles(",
    print TURNOFF_NODE_TIME, "s) till turnoff:",
    print calc_cycles(TURNOFF_NODE_TIME)

for d in [1, 1.5, 2, 3, 4, 5, 6]:
    print d, estimate_neighbors(d)

# print "#Messages",
# for sqr_nodes in sqr_nodes_list:
#     for distance in distance_list:
#         neighbors = estimate_neighbors()
#         print "#Messages(K=" + K + ", c=" + c + \
#             ", sqr_nodes=" + sqr_nodes + \
#             ", neighbors=" + neighbors + \
#             ")=",
#         print calc_messages(K, c, sqr_nodes, neighbors)

# sqrn dist  MU   1)        2) 
# 225
# 15   100   22   1500/70   22500 /1000
# 15   50    10    750/70   11250 /1000
# 15   5     2      75/70    1125 /1000

# 100
# 10   100   12   1000/70   10000 /1000
# 10   50    8     500/70    5000 /1000
# 10   5     1      50/70     500 /1000

# 25
# 5    100   6     500/70    2500 /1000
# 5    50    3     250/70    1250 /1000
# 5    5     1      25/70     125 /1000
# -------------
# 5  *2 = 10,   10 *1.5  = 15
# 25 *4 = 100, 100 *2.25 = 225

# 1) sqr_nodes * distance/70
# 2)     nodes * distance/1000

ROOT_TWO = math.sqrt(2)

filenamebase = "sim/output/trickle_"
my_norm = col.Normalize(min(DISTANCE_LIST)-1,
                        max(DISTANCE_LIST)+1)

for sqr_nodes in SQR_NODES_LIST:
    fig = plt.figure(figsize=(12, 8),
                     subplotpars = SubplotParams(left = 0.07,
                                                 bottom = 0.05,
                                                 top = 0.93,
                                                 right = 0.77))
    #fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111)


    for distance in DISTANCE_LIST:

        MU= sqr_nodes * distance / 70
        SIGMA=MU

        ERF = [0.5 * (1 + erf((x-MU)/SIGMA*ROOT_TWO)) for x in floatRange(EVAL_LOW_TIME, EVAL_HIGH_TIME, 1)]

        plt.plot(floatRange(EVAL_LOW_TIME, EVAL_HIGH_TIME, 1),
                 ERF,
                 color=plt.cm.jet(my_norm(distance)),
#                 ls='steps',
                 label=str(distance))

    plt.grid()
    text = str(sqr_nodes) + "x" + str(sqr_nodes) + ", " + \
        "K: " + str(K)
    title = 'Model Time to Consistency (cdf) (Analytical Model)\n(' + text + ')'
    plt.title(title)

    plt.ylim(0,
             1)
    plt.xlim(EVAL_LOW_TIME,
             EVAL_HIGH_TIME)

    plt.xlabel("Model Time [s]")
    plt.ylabel("Nodes consistent [%]")

    ax.set_xticks(range(0,
                        EVAL_HIGH_TIME,
                        60))
    minorLocator   = MultipleLocator(10)
    ax.xaxis.set_minor_locator(minorLocator)

    ax.set_yticks(floatRange(0,
                             1.1,
                             0.1))

    plt.legend(bbox_to_anchor=(1.02, 1),
               loc = 2,
               borderaxespad=0. ,
               title = "Distance [m]",
               ncol = 2,
               fancybox = 'True')

    plt.savefig(filenamebase+"_" + str(sqr_nodes) +"_" + str(sqr_nodes) + "_hist_model.pdf")

