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
              #  ei,
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

        route = np.empty(si.nodes+1)
        route_time = np.empty(si.nodes+1)
        boot_time = np.empty(si.nodes+1)
        
        route.fill(np.nan)
        route_time.fill(np.nan)
        boot_time.fill(np.nan)

        f = open(filenamebase+".log", "r")
        for line in f:
            if line.find("Application Booted") >= 0:
                node_obj = node_re_c.search(line)
                node = int(node_obj.group(1))

                time_obj = time_re_c.search(line)
                t = Time(time_obj.group(1),
                         time_obj.group(2),
                         time_obj.group(3))
                boot_time[node] = t.in_milisecond()

            if line.find("AddEntry") >= 0:
                node_obj = node_re_c.search(line)
                node = int(node_obj.group(1))
                
                time_obj = time_re_c.search(line)

                t = Time(time_obj.group(1),
                         time_obj.group(2),
                         time_obj.group(3))

                if np.isnan(route_time[node]):
                    route[node] = t.in_milisecond()
        f.close()
        #print ">>>>route",route
        for node in range (0,si.nodes+1):
            route_time[node] = route[node]
       
        #print "route_time = ", route_time
        cdf_route = stats.cumfreq(route_time[2:], EVAL_BINS, (EVAL_LOW_TIME, EVAL_HIGH_TIME))
        #print cdf_route[0]#, max(cdf_route[0])#, cdf_avail[0]/max(cdf_avail[0])

        np.save(filenamebase+"_hist_route_appear_time.npy", route_time)

        #######################
        # cdf
        #######################

        fig = plt.figure(figsize=(13, 6))
        ax = fig.add_subplot(111)
        x = floatRange(EVAL_LOW_TIME, EVAL_HIGH_TIME, cdf_route[2])
        y = cdf_route[0]/(si.nodes-1)
       # print "x = ",x,"\ny = ",y
        plt.plot(x,
                 y,
                 'b', ls='steps', label='Time to default route')

        plt.grid()

        text = "No. of Nodes: " + str(si.nodes) + ", " + \
            "Inter node distance: " + str(si.distance) + "m"
        title = 'Time to Default Route Detection (cdf) \n(' + text + ')'
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
        plt.legend(loc='lower right')

        plt.savefig(filenamebase+"_cdf_hist.pdf")

