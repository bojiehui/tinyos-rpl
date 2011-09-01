#!/usr/bin/env python

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import copy
import scipy.stats as stats
import re
import math
import logging
import logging.config

from sim.utils.helper import *
from sim.scenarios.ScenarioInformation import *
#from sim.scenarios.ExecutableInformation import *

from sim.config import *

logging.config.fileConfig(LOGFILENAME)
logger = logging.getLogger("evrun")

class MonteCarloHistGraph:
    def __init__(self):
        pass

    def execute(self,
              #  ei,
                si,
                iterations):

        #filenamebase = si.createfilenamebase()
        logger.info("="*40)
        logger.info("Executing MonteCarloHistGraph:")
        logger.info("filenamebase\t\t" +str(si.create_montecarlo_filenamebase()))
        logger.info("="*40)
        
        route_time_each = np.zeros(iterations)
        route_time_sum = np.zeros(si.nodes*iterations-iterations)
       # sent_packets_sum = 0
        #sent_packets_sum = np.zeros(si.sqr_nodes*si.sqr_nodes+2)

       # neighbors_min_sum  = np.zeros(si.nodes+2)
       # neighbors_mean_sum = np.zeros(si.nodes+2)
       # neighbors_max_sum  = np.zeros(si.nodes+2)

        for run in range(0, iterations):

            full_si = copy.deepcopy(si)
            full_si.run = run

            route_time_run = np.load(full_si.createfilenamebase() + "_hist_route_appear_time.npy","r")
           # route_time_each[run] =  np.load(full_si.createfilenamebase() + \
                                        #    "_hist_route_appear_time.npy",
                                        #"r")
           # print "route_time_dict = ",route_time_run
            
            #ignore node 0 (not available) and 1 (only IPBaseStation)
            for node in range(2, si.nodes+1):
                route_time_sum[si.nodes*run+node-2-run] = route_time_run[node]

        np.save(si.create_montecarlo_filenamebase()+"_hist_route_time.npy",
                route_time_sum)

        #########################
        # cdf for individule node
        #########################
        for node in range(2,si.nodes+1):
            for run in range(0,iterations):
                route_time_each[run] = route_time_sum[run*(si.nodes-1)]

            cdf_route_each = stats.cumfreq(route_time_each,
                                           EVAL_BINS,
                                           (EVAL_LOW_TIME, EVAL_HIGH_TIME))
       
            fig = plt.figure(figsize=(10, 8))
            ax = fig.add_subplot(111)
            x = floatRange(EVAL_LOW_TIME, EVAL_HIGH_TIME, cdf_route_each[2])
            y = cdf_route_each[0]/iterations

            plt.plot(floatRange(EVAL_LOW_TIME, EVAL_HIGH_TIME, cdf_route_each[2]),
                     cdf_route_each[0]/iterations,
#                 cdf_avail_sum[0]/max(cdf_avail_sum[0]),
                     'b', ls='steps', label='Time to default route')
            plt.grid()
            text = "#Nodes: " + str(si.nodes) + ", " + \
                "Distance: " + str(si.distance) +", "+\
                "Node: "+ str(node)
            title = 'Model Time to Route Detected Time (cdf) \n (' + text + ')'
            plt.title(title)

            plt.ylim(0,
                     1.02)
            plt.xlim(EVAL_LOW_TIME,
                     EVAL_HIGH_TIME)

           # ax.set_xticks(range(EVAL_LOW_TIME,
           #                     EVAL_HIGH_TIME,
           #                     2))
            ax.set_xticklabels(range(EVAL_LOW_TIME,
                                EVAL_HIGH_TIME,
                                100),size='small')

            ax.set_yticks(floatRange(0, 110, 10))
            
            plt.xlabel("Model Time [ms]")
            plt.ylabel("Percentage [%]")

            plt.legend(loc='lower right')

            plt.savefig(si.create_montecarlo_filenamebase()+"_montecarlo_cdf_hist_node_"+str(node)+".pdf")
          #  x = []
          #  y = []

        #######################
        # cdf for whole network
        #######################
        cdf_route_sum = stats.cumfreq(route_time_sum,
                                      EVAL_BINS,
                                      (EVAL_LOW_TIME, EVAL_HIGH_TIME))
        print "route time",route_time_sum
        print "#####",cdf_route_sum[0]

        fig = plt.figure(figsize=(10, 8))
        ax = fig.add_subplot(111)
        x = floatRange(EVAL_LOW_TIME, EVAL_HIGH_TIME, cdf_route_sum[2])
        y = cdf_route_sum[0]/(si.nodes*iterations-iterations)
#        print "MonteCarlo x = ",x
#        print "MonteCarlo y = ",y

        plt.plot(x,
#                 cdf_route_sum[0]/(si.sqr_nodes*si.sqr_nodes),
                 y,
#                 cdf_avail_sum[0]/max(cdf_avail_sum[0]),
                 'b', ls='steps', label='Time to default route')
        plt.grid()
        text = "#Nodes: " + str(si.nodes) + ", " + \
            "Distance: " + str(si.distance) +", " + \
            "Whole Network"
        title = 'Model Time to Route Detected Time (cdf) \n(' + text + ')'
        plt.title(title)

        plt.ylim(0,
                 1.02)
        plt.xlim(EVAL_LOW_TIME,
                 EVAL_HIGH_TIME)

        ax.set_xticklabels(range(EVAL_LOW_TIME,
                                EVAL_HIGH_TIME,
                                100),size='small')

        ax.set_yticks(floatRange(0, 110, 10))

        plt.xlabel("Model Time [ms]")
        plt.ylabel("Percentage [%]")

        plt.legend(loc='lower right')

        plt.savefig(si.create_montecarlo_filenamebase()+"_montecarlo_cdf_hist.pdf")
