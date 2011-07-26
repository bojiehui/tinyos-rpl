#!/usr/bin/env python

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
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

class HistGraph:
    def __init__(self):
        pass

    def execute(self,
                ei,
                si):

        filenamebase = si.createfilenamebase()
        logger.info("="*40)
        logger.info("Executing HistGraph:")
        logger.info("filenamebase\t\t" +str(filenamebase))
        logger.info("="*40)

        node_re = 'DEBUG \((\d+)\):'
        node_re_c = re.compile(node_re)
        time_re = '(\d+):(\d+):(\d+.\d+)'
        time_re_c = re.compile(time_re)

        consist_avail = np.empty(si.nodes+2)
        consist_purge = np.empty(si.nodes+2)

        consist_avail.fill(np.nan)
        consist_purge.fill(np.nan)

        f = open(filenamebase+".log", "r")
        for line in f:
            #print line,
            if line.find("inconsistent") >= 0:
                #print line,

                node_obj = node_re_c.search(line)
                node = int(node_obj.group(1))

                time_obj = time_re_c.search(line)
                #print "\t", time_obj.group(0),
                t = Time(time_obj.group(1),
                         time_obj.group(2),
                         time_obj.group(3))
                #print t.in_second()

                if np.isnan(consist_avail[node]):
                    consist_avail[node] = t.in_second() - ei.defines["INJECT_TIME"]/1024

            if line.find("really purge now") >= 0:
                #print line,

                node_obj = node_re_c.search(line)
                node = int(node_obj.group(1))

                time_obj = time_re_c.search(line)
                #print "\t", time_obj.group(0),
                t = Time(time_obj.group(1),
                         time_obj.group(2),
                         time_obj.group(3))
                #print t.in_second()

                if (t.in_second() - si.turnoff_node_time < 0):
                    print "PURGED TOO EARLY:", node, t.in_second()

                consist_purge[node] = t.in_second() - ei.defines["INJECT_TIME"]/1024
        f.close()

        cdf_avail = stats.cumfreq(consist_avail[2:], EVAL_BINS, (EVAL_LOW_TIME, EVAL_HIGH_TIME))
        cdf_purge = stats.cumfreq(consist_purge[2:], EVAL_BINS, (EVAL_LOW_TIME, EVAL_HIGH_TIME))
        #print cdf_avail, max(cdf_avail[0])#, cdf_avail[0]/max(cdf_avail[0])

        pdf_avail = stats.relfreq(consist_avail[2:], EVAL_BINS, (EVAL_LOW_TIME, EVAL_HIGH_TIME))
        pdf_purge = stats.relfreq(consist_purge[2:], EVAL_BINS, (EVAL_LOW_TIME, EVAL_HIGH_TIME))

        np.save(filenamebase+"_hist_consist_avail.npy", consist_avail)
        np.save(filenamebase+"_hist_consist_purge.npy", consist_purge)

        #######################
        # cdf
        #######################

        fig = plt.figure(figsize=(10, 8))
        ax = fig.add_subplot(111)

        plt.plot(floatRange(EVAL_LOW_TIME, EVAL_HIGH_TIME, cdf_avail[2]),
                 cdf_avail[0]/(si.nodes),
#                 cdf_avail[0]/max(cdf_avail[0]),
                 'b', ls='steps', label='Availability')
        plt.plot(floatRange(EVAL_LOW_TIME, EVAL_HIGH_TIME, cdf_purge[2]),
                 cdf_purge[0]/(si.nodes),
#                 cdf_purge[0]/max(cdf_purge[0]),
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
                            60))
        ax.set_yticks(floatRange(0, 1.1, 0.1))

        plt.xlabel("Model Time [s]")
        plt.ylabel("Nodes consistent [%]")

        plt.legend(loc='lower right')

        plt.savefig(filenamebase+"_cdf_hist.pdf")

        #######################
        # pdf
        #######################

        fig = plt.figure(figsize=(10, 8))
        ax = fig.add_subplot(111)

        plt.plot(floatRange(EVAL_LOW_TIME, EVAL_HIGH_TIME, pdf_avail[2]),
                 pdf_avail[0]/(si.nodes),
#                 cdf_avail[0]/max(cdf_avail[0]),
                 'b', ls='steps', label='Availability')
#        plt.plot(floatRange(EVAL_LOW_TIME, EVAL_HIGH_TIME, pdf_purge[2]),
#                 pdf_purge[0]/(si.nodes),
##                 cdf_purge[0]/max(cdf_purge[0]),
#                 'r', ls='steps', label='Purged')

        plt.grid()
        text = "#Nodes: " + str(si.nodes) + ", " + \
            "Distance: " + str(si.distance) + ", " + \
            "K: " + str(ei.defines["DISTRIBUTION_TRICKLE_K"])
        title = 'Model Time to Consistency (pdf) \n(' + text + ')'
        plt.title(title)

        #plt.ylim(0,
        #         1.02)
        plt.xlim(EVAL_LOW_TIME,
                 EVAL_HIGH_TIME)

        #ax.set_xticks(range(0,
        #                    EVAL_HIGH_TIME,
        #                    60))
        #ax.set_yticks(floatRange(0, 1.1, 0.1))

        plt.xlabel("Model Time [s]")
        plt.ylabel("")

        plt.legend(loc='lower right')

        plt.savefig(filenamebase+"_pdf_hist.pdf")
