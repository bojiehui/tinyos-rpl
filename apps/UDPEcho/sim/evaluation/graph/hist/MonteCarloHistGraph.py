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
from sim.scenarios.ExecutableInformation import *

from sim.config import *

logging.config.fileConfig(LOGFILENAME)
logger = logging.getLogger("evrun")

class MonteCarloHistGraph:
    def __init__(self):
        pass

    def execute(self,
                ei,
                si,
                iterations):

        #filenamebase = si.createfilenamebase()
        logger.info("="*40)
        logger.info("Executing MonteCarloHistGraph:")
        logger.info("filenamebase\t\t" +str(si.create_montecarlo_filenamebase()))
        logger.info("="*40)

        consist_avail_sum = np.zeros(si.nodes*iterations)
        consist_purge_sum = np.zeros(si.nodes*iterations)
        sent_packets_sum = 0
        #sent_packets_sum = np.zeros(si.sqr_nodes*si.sqr_nodes+2)

        neighbors_min_sum  = np.zeros(si.nodes+2)
        neighbors_mean_sum = np.zeros(si.nodes+2)
        neighbors_max_sum  = np.zeros(si.nodes+2)

        for run in range(0, iterations):

            full_si = copy.deepcopy(si)
            full_si.run = run

            consist_avail_run = np.load(full_si.createfilenamebase() + \
                                            "_hist_consist_avail.npy",
                                        "r")
            consist_purge_run = np.load(full_si.createfilenamebase() + \
                                            "_hist_consist_purge.npy",
                                        "r")

            #ignore node 0 (not available) and 1 (only IPBaseStation)
            for node in range(2, si.nodes+2):
                consist_avail_sum[si.nodes*run+node-2] = consist_avail_run[node]
                consist_purge_sum[si.nodes*run+node-2] = consist_purge_run[node]
            
            #consist_avail_sum += consist_avail_run
            #consist_purge_sum += consist_purge_run

            #print "consist_run:", consist_avail_run
            #print "consist_sum:", consist_avail_sum

            sent_packets_run = np.load(full_si.createfilenamebase() + \
                                       "_sent_packets.npy",
                                       "r")
            sent_packets_sum += sent_packets_run

            neighbors_min_run = np.load(full_si.createfilenamebase() + \
                                             "_neighbors_min.npy",
                                        "r")
            neighbors_mean_run = np.load(full_si.createfilenamebase() + \
                                             "_neighbors_mean.npy",
                                         "r")
            neighbors_max_run = np.load(full_si.createfilenamebase() + \
                                            "_neighbors_max.npy",
                                        "r")
            neighbors_min_sum  += neighbors_min_run
            neighbors_mean_sum += neighbors_mean_run
            neighbors_max_sum  += neighbors_max_run

        #consist_avail_sum /= iterations
        #consist_purge_sum /= iterations
        sent_packets_sum  /= iterations

        #print "consist_sum final:", consist_avail_sum

        neighbors_min_sum  /= iterations
        neighbors_mean_sum /= iterations
        neighbors_max_sum  /= iterations

        np.save(si.create_montecarlo_filenamebase()+"_hist_consist_avail.npy",
                consist_avail_sum)
        np.save(si.create_montecarlo_filenamebase()+"_hist_consist_purge.npy",
                consist_purge_sum)
        np.save(si.create_montecarlo_filenamebase()+"_sent_packets.npy",
                sent_packets_sum)
        np.save(si.create_montecarlo_filenamebase()+"_neighbors_min.npy",
                neighbors_min_sum)
        np.save(si.create_montecarlo_filenamebase()+"_neighbors_mean.npy",
                neighbors_mean_sum)
        np.save(si.create_montecarlo_filenamebase()+"_neighbors_max.npy",
                neighbors_max_sum)
 
        cdf_avail_sum = stats.cumfreq(consist_avail_sum,
                                      EVAL_BINS,
                                      (EVAL_LOW_TIME, EVAL_HIGH_TIME))
        cdf_purge_sum = stats.cumfreq(consist_purge_sum,
                                      EVAL_BINS,
                                      (EVAL_LOW_TIME, EVAL_HIGH_TIME))
        #print "CDF:", repr(cdf_avail_sum)

        pdf_avail_sum = stats.relfreq(consist_avail_sum,
                                      EVAL_BINS,
                                      (EVAL_LOW_TIME, EVAL_HIGH_TIME))
        pdf_purge_sum = stats.relfreq(consist_purge_sum,
                                      EVAL_BINS,
                                      (EVAL_LOW_TIME, EVAL_HIGH_TIME))

        #print "PDF:", repr(pdf_avail_sum)

        #######################
        # cdf
        #######################

        fig = plt.figure(figsize=(10, 8))
        ax = fig.add_subplot(111)

        plt.plot(floatRange(EVAL_LOW_TIME, EVAL_HIGH_TIME, cdf_avail_sum[2]),
#                 cdf_avail_sum[0]/(si.sqr_nodes*si.sqr_nodes),
                 cdf_avail_sum[0]/(si.nodes*iterations),
#                 cdf_avail_sum[0]/max(cdf_avail_sum[0]),
                 'b', ls='steps', label='Availability')
        plt.plot(floatRange(EVAL_LOW_TIME, EVAL_HIGH_TIME, cdf_purge_sum[2]),
#                 cdf_purge_sum[0]/(si.sqr_nodes*si.sqr_nodes),
                 cdf_purge_sum[0]/(si.nodes*iterations),
#                 cdf_purge_sum[0]/max(cdf_purge_sum[0]),
                 'r', ls='steps', label='Purged')

        plt.grid()
        text = "#Nodes: " + str(si.nodes) + ", " + \
            "Distance: " + str(si.distance) + ", " + \
            "K: " + str(ei.defines["DISTRIBUTION_TRICKLE_K"])
        title = 'Model Time to Consistency (cdf) \n(' + text + ')'
        plt.title(title)

        plt.ylim(0,
                 1.02)
        plt.xlim(EVAL_LOW_TIME,
                 EVAL_HIGH_TIME)

        ax.set_xticks(range(0,
                            EVAL_HIGH_TIME,
                            1))
        #ax.set_xticks(range(0,
        #                    EVAL_HIGH_TIME,
        #                    60))
        ax.set_yticks(floatRange(0, 1.1, 0.1))

        plt.xlabel("Model Time [s]")
        plt.ylabel("Nodes consistent [%]")

        plt.legend(loc='lower right')

        plt.savefig(si.create_montecarlo_filenamebase()+"_montecarlo_cdf_hist.pdf")

        #######################
        # pdf
        #######################

        fig = plt.figure(figsize=(10, 8))
        ax = fig.add_subplot(111)

        plt.plot(floatRange(EVAL_LOW_TIME, EVAL_HIGH_TIME, pdf_avail_sum[2]),
                 pdf_avail_sum[0]/(si.nodes),
#                 cdf_avail_sum[0]/max(cdf_avail_sum[0]),
                 'b', ls='steps', label='Availability')
#        plt.plot(floatRange(EVAL_LOW_TIME, EVAL_HIGH_TIME, pdf_purge_sum[2]),
#                 pdf_purge_sum[0]/(si.sqr_nodes*si.sqr_nodes),
##                 cdf_purge_sum[0]/max(cdf_purge_sum[0]),
#                 'r', ls='steps', label='Purged')

        plt.grid()
        text = "#Nodes: " + str(si.nodes) + ", " + \
            "Distance: " + str(si.distance) + ", " + \
            "K: " + str(ei.defines["DISTRIBUTION_TRICKLE_K"])
        title = 'Model Time to Consistency (pdf) \n(' + text + ')'
        plt.title(title)
        #plt.semilogy()

        #plt.ylim(0,
        #         1.02)
        plt.xlim(EVAL_LOW_TIME,
                 EVAL_HIGH_TIME)

        ax.set_xticks(range(0,
                            EVAL_HIGH_TIME,
                            2))
        ax.set_yticks(floatRange(0, 1.1, 0.1))

        plt.xlabel("Model Time [s]")
        plt.ylabel("")

        plt.legend(loc='lower right')

        plt.savefig(si.create_montecarlo_filenamebase()+"_montecarlo_pdf_hist.pdf")

#        plt.ylim(0,
#                 0.001)
#        plt.savefig(si.create_montecarlo_filenamebase()+"_montecarlo_pdf_hist_zoom.pdf")
