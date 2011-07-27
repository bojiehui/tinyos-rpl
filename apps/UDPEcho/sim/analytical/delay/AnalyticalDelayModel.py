#!/usr/bin/env python

from __future__ import division
import copy
import traceback
from optparse import OptionParser
import sys

import matplotlib
matplotlib.use('agg') 

import matplotlib.pyplot as plt
import matplotlib.colors as col
from matplotlib.figure import SubplotParams
from matplotlib.ticker import MultipleLocator

import numpy as np
import scipy.stats as stats

from sim.utils.helper import *
from sim.config import *
from sim.scenarios.ScenarioInformation import *
from sim.scenarios.ExecutableInformation import *

from scipy.special import erf

ROOT_TWO = math.sqrt(2)

class AnalyticalDelayModel:
    def __init__(self):
        pass

    def execute(self,
                ei,
                si,
                sqr_nodes_list,
                distance_list,
                iterations):

        print "="*40
        print "Executing AnalyticalDelayModel:"
        print "filenamebase\t\t", si.createfilenamebase()
        print "="*40

        print si
        print ei

        my_norm = col.Normalize(min(distance_list)*min(sqr_nodes_list)-1,
                                max(distance_list)*max(sqr_nodes_list)+1)

        for sqr_nodes in sqr_nodes_list:

            topo_si = copy.deepcopy(si)
            topo_si.sqr_nodes = sqr_nodes

            #############################
            # modeled hist:
            #############################

            fig = plt.figure(figsize=(12, 8),
                             subplotpars = SubplotParams(left = 0.07,
                                                         bottom = 0.05,
                                                         top = 0.93,
                                                         right = 0.77))
            ax = fig.add_subplot(111)

            #TODO: move from here and scenario to config
            #RADIO_RANGE = 143

            for distance in distance_list:
                print "Distance:", distance

                dist_si = copy.deepcopy(topo_si)
                dist_si.distance = distance*sqr_nodes

                prr_sum = np.zeros((si.sqr_nodes*si.sqr_nodes,
                                    si.sqr_nodes*si.sqr_nodes))

                for run in range(0, iterations):

                    full_si = copy.deepcopy(dist_si)
                    full_si.run = run

                    #print "Load:", full_si.createfilenamebase() + \
                    #                      "_prr.npy"
                    prr_run = np.load(full_si.createfilenamebase() + \
                                          "_prr.npy",
                                      "r")
                    #print prr_sum
                    #print prr_run
                    #print prr_run[2:][2:]
                    prr_sum += prr_run[2:, 2:]

                #print "PRR:", prr_sum
                #print "iter:", iterations
                
                prr_sum /= iterations
                print "PRR:", prr_sum
                #print ""

#                 print prr_sum[0][0]
#                 print prr_sum[0][1]
#                 print prr_sum[0][2]
#                 print prr_sum[0][3]

#                 print ""

#                 print prr_sum[0][0]
#                 print prr_sum[1][0]
#                 print prr_sum[2][0]
#                 print prr_sum[3][0]

                ei.defines["DISTRIBUTION_TRICKLE_TAU_LOW"] / 1024 / 2

                x = [
                    -.001,
                      0,
                      ei.defines["DISTRIBUTION_TRICKLE_TAU_LOW"] / 1024 / 2,
#                      2* ei.defines["DISTRIBUTION_TRICKLE_TAU_LOW"] / 1024 / 2,
#                      4* ei.defines["DISTRIBUTION_TRICKLE_TAU_LOW"] / 1024 / 2,
#                      8* ei.defines["DISTRIBUTION_TRICKLE_TAU_LOW"] / 1024 / 2,
                      ]

                BASE_PROP = 1/(si.sqr_nodes*si.sqr_nodes)
                ONE_HOP = BASE_PROP*prr_sum[1][0]+ \
                    BASE_PROP*prr_sum[2][0]+ \
                    BASE_PROP*prr_sum[3][0]

                TWO_HOP = \
                    ((1-BASE_PROP-ONE_HOP)*prr_sum[1][0]*prr_sum[1][3]+ \
                         (1-BASE_PROP-ONE_HOP)*prr_sum[2][0]*prr_sum[2][3])/2
                print BASE_PROP, ONE_HOP, TWO_HOP

                y = [
                    0,
                    BASE_PROP,
                    BASE_PROP,

#                    BASE_PROP+
#                    ONE_HOP,

#                    BASE_PROP+
#                    ONE_HOP+
#                    TWO_HOP,

#                    BASE_PROP+
#                    ONE_HOP+
#                    TWO_HOP+
                    
#                    (1-BASE_PROP-ONE_HOP-TWO_HOP) * (1 + erf((8* ei.defines["DISTRIBUTION_TRICKLE_TAU_LOW"] / 1024 / 2 - 1.5 * ei.defines["DISTRIBUTION_TRICKLE_TAU_LOW"] / 1024 / 2)/.5))/2

                    ]

#                       (1-BASE_PROP-ONE_HOP-TWO_HOP) * (1 + erf(xval - 1.5*4 * ei.defines["DISTRIBUTION_TRICKLE_TAU_LOW"] / 1024 / 2))/2)  \

                XY = [(xval, 
                       BASE_PROP+
                       ONE_HOP+
#                       TWO_HOP+
#                       (1-BASE_PROP-ONE_HOP-TWO_HOP) * 
                       (1-BASE_PROP-ONE_HOP) *
                       (prr_sum[1][0]*prr_sum[1][3] + prr_sum[2][0]*prr_sum[2][3]) /2 *
                       (1 + erf(1.5*(xval - 1.5*2 * ei.defines["DISTRIBUTION_TRICKLE_TAU_LOW"] / 1024 / 2)))/2)  \

#                        (1-BASE_PROP-ONE_HOP) * 
#                        (1-
#                         ((1+
#                          (-1-erf(xval - 1.5*2 * ei.defines["DISTRIBUTION_TRICKLE_TAU_LOW"]/1024/2)
#                         )/2)**2
#                        )))  \
                      for xval in floatRange(
                    2* ei.defines["DISTRIBUTION_TRICKLE_TAU_LOW"] / 1024 / 2,
                    12* ei.defines["DISTRIBUTION_TRICKLE_TAU_LOW"] / 1024 / 2,
                    .2)]

                for xy in XY:
                    x.append(xy[0])
                    y.append(xy[1])

                print "x", x
                print "y", y

                plt.plot(x,
                         y,
                         color=plt.cm.jet(my_norm(distance*sqr_nodes)),
                         label=str(distance*sqr_nodes))
                

#                 #MU = sqr_nodes * distance / 70
#                 #SIGMA = MU
#                 HOPS = 2 * (sqr_nodes-1) * distance / RADIO_RANGE

#                 MU = HOPS * .75 * ei.defines["DISTRIBUTION_TRICKLE_TAU_LOW"] / 1024 / 2
#                 #SIGMA = math.sqrt(HOPS) * math.sqrt( math.pow(ei.defines["DISTRIBUTION_TRICKLE_TAU_LOW"] / 1024, 2) / 48)
#                 #SIGMA = math.sqrt(HOPS) * ei.defines["DISTRIBUTION_TRICKLE_TAU_LOW"] / 1024
#                 SIGMA = HOPS * ei.defines["DISTRIBUTION_TRICKLE_TAU_LOW"] / 1024 / 4

#                 ERF = [0.5 * (1 + erf((x-MU)/SIGMA*ROOT_TWO)) for x in floatRange(EVAL_LOW_TIME, EVAL_HIGH_TIME, 1)]

#                 plt.plot(floatRange(EVAL_LOW_TIME, EVAL_HIGH_TIME, 1),
#                          ERF,
#                          color=plt.cm.jet(my_norm(distance*sqr_nodes)),
#                          label=str(distance*sqr_nodes))

            plt.grid()
            text = str(sqr_nodes) + "x" + str(sqr_nodes) + ", " + \
                "K: " + str(ei.defines["DISTRIBUTION_TRICKLE_K"])
            title = 'Model Time to Consistency (cdf) \n(' + text + ', analytical model)'
            plt.title(title)

            plt.ylim(0,
                     1)
#                     1.1)
            plt.xlim(EVAL_LOW_TIME,
                     EVAL_HIGH_TIME)

            plt.xlabel("Model Time [s]")
            plt.ylabel("Nodes consistent [%]")

            ax.set_xticks(range(0,
                                EVAL_HIGH_TIME,
                                2))
#                                60))
            #plt.minorticks_on()
            minorLocator   = MultipleLocator(10)
            ax.xaxis.set_minor_locator(minorLocator)

            ax.set_yticks(floatRange(0,
                                     1.1,
                                     0.1))

            #plt.legend(loc='lower right')
            plt.legend(bbox_to_anchor=(1.02, 1),
                       loc = 2,
                       borderaxespad=0. ,
                       title = "Distance [m]",
                       ncol = 2,
                       #loc = (.9, .5),
                       fancybox = 'True')

            plt.savefig(topo_si.create_topo_filenamebase() + "_hist_modeled_2.pdf")

if __name__ == "__main__":
    try:
        optparser = OptionParser()

        optparser.add_option("-e",
                             "--executable_info",
                             help="Pickled executable information filename")
        optparser.add_option("-s",
                             "--scenario_info",
                             help="Pickled scenario information filename")

        (optionsp, argsp) = optparser.parse_args()

        if not (optionsp.executable_info or
                optionsp.scenario_info):
             optparser.print_help()
             sys.exit(-1)
             
        #TODO: read this in from sim/output/suite_*/config.py
        sqr_nodes_list = [2]
        distance_list = [70, 80, 90, 100, 110, 120, 130, 140]
        #distance_list = [70]
        iterations = 300

        adm = AnalyticalDelayModel()
        adm.execute(pickle.load(open(optionsp.executable_info, "rb")),
                    pickle.load(open(optionsp.scenario_info, "rb")),
                    sqr_nodes_list,
                    distance_list,
                    iterations)
    except:
        traceback.print_exc()
