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

from sim.config import *

logging.config.fileConfig(LOGFILENAME)
logger = logging.getLogger("evrun")

class MonteCarloHistGraph:
    def __init__(self):
        pass

    def execute(self,
                si,
                iterations):

        logger.info("="*40)
        logger.info("Executing MonteCarloHistGraph:")
        logger.info("filenamebase\t\t" +str(si.create_montecarlo_filenamebase()))
        logger.info("="*40)
        
        route_time_each = np.zeros(iterations)
        route_time_sum = np.zeros(si.nodes*iterations-iterations)

        for run in range(0, iterations):

            full_si = copy.deepcopy(si)
            full_si.run = run

            route_time_run = np.load(full_si.createfilenamebase() + "_hist_route_appear_time.npy","r")
            
            #ignore node 0 (not available) and 1 (only IPBaseStation)
            for node in range(2, si.nodes+1):
                route_time_sum[si.nodes*run+node-2-run] = route_time_run[node]

        np.save(si.create_montecarlo_filenamebase()+"_hist_route_time.npy",
                route_time_sum)


        #######################
        # cdf for whole network
        #######################
        #print "cdf_route_sum",route_time_sum
        cdf_route_sum = stats.cumfreq(route_time_sum,
                                      EVAL_BINS,
                                      (EVAL_LOW_TIME, EVAL_HIGH_TIME))
        fig = plt.figure(figsize=(13, 6))
        fig.subplots_adjust(left=0.05,right=0.98)
        ax = fig.add_subplot(111)

        x = floatRange(EVAL_LOW_TIME, EVAL_HIGH_TIME, cdf_route_sum[2])
        y = cdf_route_sum[0]/(si.nodes*iterations-iterations)
    
#        print "MonteCarlo x = ",x
#        print "MonteCarlo y = ",y

        plt.plot(x,
                 y,
                 'b', ls='steps', label='Time to default route')
        plt.grid()
        text = "No. of Nodes: " + str(si.nodes) + ", " + \
            "Inter-node Distance: " + str(si.distance) +"m, " + \
            "No. of Runs: " + str(iterations)+ ", " +\
            "Whole Network"
        title = 'Time to Default Route Discovery (cdf) \n(' + text + ')'
        plt.title(title)

        plt.ylim(0,
                 1.02)
        plt.xlim(0,
                 max(x)+100)
        
        ax.set_xticks(floatRange(0,
                            max(x)+100,
                            256))

        ax.set_yticks(floatRange(0, 1.02, 0.1))

        plt.xlabel("Time [ms]")
        plt.ylabel("y")

        plt.legend(loc='lower right')

        plt.savefig(si.create_montecarlo_filenamebase()+"_montecarlo_cdf_hist.pdf")
