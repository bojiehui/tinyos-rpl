#!/usr/bin/env python

from __future__ import division
import copy
import math

import matplotlib
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

class SuiteEvaluationHist:
    def __init__(self):
        pass

    def execute(self,
                ei,
                si,
                nodes_list,
                distance_list,
                iterations):

        print "="*40
        print "Executing SuiteEvaluationHist:"
        print "filenamebase\t\t", si.createfilenamebase()
        print "="*40

        my_norm = col.Normalize(min(distance_list)*math.sqrt(min(nodes_list))-1,
                                max(distance_list)*math.sqrt(max(nodes_list))+1)

        for nodes in nodes_list:

            topo_si = copy.deepcopy(si)
            topo_si.nodes = nodes

            #############################
            # simulated hist:
            #############################

            fig = plt.figure(figsize=(12, 8),
                             subplotpars = SubplotParams(left = 0.07,
                                                         bottom = 0.05,
                                                         top = 0.93,
                                                         right = 0.77))
            ax = fig.add_subplot(111)
            for distance in distance_list:

                suite_si = copy.deepcopy(si)
                suite_si.nodes = nodes
                suite_si.distance = distance#*sqr_nodes

                consist_avail_sum = np.load(suite_si.create_montecarlo_filenamebase()+"_hist_consist_avail.npy",
                                            "r")
                consist_purge_sum = np.load(suite_si.create_montecarlo_filenamebase()+"_hist_consist_purge.npy",
                                            "r")
                cdf_avail_sum = stats.cumfreq(consist_avail_sum,
                                              EVAL_BINS,
                                              (EVAL_LOW_TIME, EVAL_HIGH_TIME))
                cdf_purge_sum = stats.cumfreq(consist_purge_sum,
                                              EVAL_BINS,
                                              (EVAL_LOW_TIME, EVAL_HIGH_TIME))

                plt.plot(floatRange(EVAL_LOW_TIME, EVAL_HIGH_TIME, cdf_avail_sum[2]),
                         #cdf_avail_sum[0]/(sqr_nodes*sqr_nodes),
                         cdf_avail_sum[0]/(nodes*iterations),
                         color=plt.cm.jet(my_norm(distance*math.sqrt(nodes))),
                         ls='steps',
                         label=str(distance))
                #plt.plot(floatRange(EVAL_LOW_TIME, EVAL_HIGH_TIME, cdf_purge_sum[2]),
                ##         cdf_purge_sum[0]/(sqr_nodes*sqr_nodes),
                #          cdf_purge_sum[0]/(sqr_nodes*sqr_nodes*iterations),
                #         color=plt.cm.jet(my_norm(distance*sqr_nodes)),
                #         ls='steps',
                #         label=str(distance*sqr_nodes))

            plt.grid()
            text = "#Nodes: " + str(nodes) + ", " + \
                "K: " + str(ei.defines["DISTRIBUTION_TRICKLE_K"])
            title = 'Model Time to Consistency (cdf) \n(' + text + ')'
            plt.title(title)

            plt.ylim(0,
                     1)
            plt.xlim(EVAL_LOW_TIME,
                     EVAL_HIGH_TIME)

            plt.xlabel("Model Time [s]")
            plt.ylabel("Nodes consistent [%]")

            ax.set_xticks(range(0,
                                EVAL_HIGH_TIME,
                                2))
            #plt.minorticks_on()
            #minorLocator   = MultipleLocator(10)
            #ax.xaxis.set_minor_locator(minorLocator)

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

            plt.savefig(topo_si.create_topo_filenamebase() + "_hist.pdf")

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
            RADIO_RANGE = 143

            for distance in distance_list:

                #MU = sqr_nodes * distance / 70
                #SIGMA = MU
                HOPS = 2 * (math.sqrt(nodes)-1) * distance / RADIO_RANGE

                MU = HOPS * .75 * ei.defines["DISTRIBUTION_TRICKLE_TAU_LOW"] / 1024 / 2
                #SIGMA = math.sqrt(HOPS) * math.sqrt( math.pow(ei.defines["DISTRIBUTION_TRICKLE_TAU_LOW"] / 1024, 2) / 48)
                #SIGMA = math.sqrt(HOPS) * ei.defines["DISTRIBUTION_TRICKLE_TAU_LOW"] / 1024
                SIGMA = HOPS * ei.defines["DISTRIBUTION_TRICKLE_TAU_LOW"] / 1024 / 4

                ERF = [0.5 * (1 + erf((x-MU)/SIGMA*ROOT_TWO)) for x in floatRange(EVAL_LOW_TIME, EVAL_HIGH_TIME, 1)]

                plt.plot(floatRange(EVAL_LOW_TIME, EVAL_HIGH_TIME, 1),
                         ERF,
                         color=plt.cm.jet(my_norm(distance*math.sqrt(nodes))),
                         label=str(distance))

            plt.grid()
            text = "#Nodes: " + str(nodes) + ", " + \
                "K: " + str(ei.defines["DISTRIBUTION_TRICKLE_K"])
            title = 'Model Time to Consistency (cdf) \n(' + text + ', analytical model)'
            plt.title(title)

            plt.ylim(0,
                     1)
            plt.xlim(EVAL_LOW_TIME,
                     EVAL_HIGH_TIME)

            plt.xlabel("Model Time [s]")
            plt.ylabel("Nodes consistent [%]")

            ax.set_xticks(range(0,
                                EVAL_HIGH_TIME,
                                2))
            #plt.minorticks_on()
            #minorLocator   = MultipleLocator(10)
            #ax.xaxis.set_minor_locator(minorLocator)

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

            plt.savefig(topo_si.create_topo_filenamebase() + "_hist_modeled.pdf")
