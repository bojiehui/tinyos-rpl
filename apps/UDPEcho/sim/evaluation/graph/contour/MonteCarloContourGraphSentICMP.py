import re
import pickle
import math
import numpy as np
import copy

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as col
from matplotlib.mlab import griddata
from matplotlib.text import Text

from sim.utils.helper import *
from sim.scenarios.ScenarioInformation import *
from sim.scenarios.ExecutableInformation import *

class MonteCarloContourGraphSentICMP:
    def __init__(self):
        pass

    def execute(self,
              #  ei,
                si,
                iterations):

        #filenamebase = si.createfilenamebase()
        print "="*40
        print "Executing MonteCarloContourGraph for ICMP sent:"
        print "filenamebase\t\t", si.create_montecarlo_filenamebase()
        print "="*40


        if SCENARIO == 'LineScenario':
             point_no = 2*si.nodes+1
             xarr = np.zeros(point_no)
             yarr = np.zeros(point_no)
             total_sentICMP_0 = np.zeros(point_no)
             total_sentICMP_1 = np.zeros(point_no)
             count = 0
        else:
            xarr = np.zeros(si.nodes+1)
            yarr = np.zeros(si.nodes+1)
            total_sentICMP_0 = np.zeros(si.nodes+1)
            total_sentICMP_1 = np.zeros(si.nodes+1)

        #loop over iterations
        for run in range(0, iterations):

            monte_si = copy.deepcopy(si)
            monte_si.run = run
            sentICMP_run_0 = np.load(monte_si.createfilenamebase() + \
                                      "_sent_ICMP_per_node_time_0.npy",
                                  "r")

            sentICMP_run_1 = np.load(monte_si.createfilenamebase() + \
                                      "_sent_ICMP_per_node_time_1.npy",
                                  "r")
            for i in range(0,si.nodes+1):
                total_sentICMP_0[i] += sentICMP_run_0[i]
                total_sentICMP_1[i] += sentICMP_run_1[i]
        
        total_sentICMP_0 = total_sentICMP_0 / iterations
        total_sentICMP_1 = total_sentICMP_1 / iterations
        
        of = open(si.create_montecarlo_filenamebase()+"_packet.txt", "aw")
        print >> of, "Mean number of Sent ICMP Packets, first 10 minutes"
        print >> of, total_sentICMP_0

        print >> of, "\nMean number of Sent ICMP Packets, second 10 minutes"
        print >> of, total_sentICMP_1

        print "Reading id2xyz mapping from " + \
            (monte_si.createfilenamebase()+"_id2xyz.pickle")
        ifile = open(monte_si.createfilenamebase()+"_id2xyz.pickle", "r")
        id2xyz_dict = pickle.load(ifile)
        ifile.close()

        for i in range(1, si.nodes+1):
            (x, y, z) = id2xyz_dict[i]
            xarr[i] = x
            yarr[i] = y

        if SCENARIO == 'LineScenario':
            for j in range(si.nodes+1, point_no):
                index = j-si.nodes
                xarr[j] = xarr[index]
                yarr[j] = 1
                total_sentICMP_0[j] = total_sentICMP_0[index]
                total_sentICMP_1[j] = total_sentICMP_1[index]

        packs = []
        for i in range(1, si.nodes+1):
            (x, y, z) = id2xyz_dict[i]
            if math.sqrt(si.nodes) >= 10:
                fs = 7
            else:
                fs = 12
            packs.append(
                Text(x,
                     y,
                     str(i),
                     color='w',
                     fontweight='bold',
                     fontsize=fs,
                     verticalalignment='center',
                     horizontalalignment='center',
                     alpha=1,
                     bbox=dict(facecolor='k'))
                )

        if SCENARIO == 'GridScenario':
            fig = plt.figure(figsize=(10, 8))
        
        if SCENARIO == 'LineScenario':
            fig = plt.figure(figsize=(10, 5))
        
        ax = fig.add_subplot(111)
     
        for p in packs:
            ax.add_artist(p)
            p.set_clip_box(ax.bbox)

#################first 10mins interval#############################3
        LOW_LEVEL = -1
        HIGH_LEVEL = max(total_sentICMP_0)+10


        levels = floatRange(LOW_LEVEL,
                            HIGH_LEVEL,
                            0.5)
        #print levels

        my_cm = cm.jet
        my_cm.set_over('k')

        my_norm = col.Normalize(LOW_LEVEL,
                                HIGH_LEVEL,
                                clip=False)

        #print ">>>>x", xarr
        #print ">>>>y", yarr
        #print ">>>>sentICMP_0", total_sentICMP_0

        xi = np.linspace(0, max(xarr), 10)
        yi = np.linspace(0, max(yarr), 10)
        zi = griddata(xarr[1:], yarr[1:], total_sentICMP_0[1:], xi, yi)

        CS0 = plt.contourf(xi, yi, zi, levels,
                          cmap = my_cm, norm = my_norm,
                          extend='max')
       
        CS0.set_clim(CS0.cvalues[0], CS0.cvalues[-2])

        plt.colorbar(CS0)

        try:
            plt.grid(markevery=1)
        except:
            plt.grid()

        text = "No. of Nodes: " + str(si.nodes) + ", " + \
            "Inter-node Distance: " + str(si.distance) + "m, " + \
            " No. of Runs: " + str(iterations)
        title = 'Mean No. of Control Messages Sent in the First 10 Minutes Interval\n(' + text + ')'
        plt.title(title)

        if max(xarr) > max(yarr):
            max_xy = max(xarr)
        else:
            max_xy = max(yarr)
       
        if SCENARIO == 'GridScenario':
            lim_delta = (math.sqrt(si.nodes)-1)*si.distance*0.1
            plt.xlim((-lim_delta, max_xy+lim_delta))
            plt.ylim((-lim_delta, max_xy+lim_delta))
            plt.xlabel("x [m]")
            plt.ylabel("y [m]")

        if SCENARIO == 'LineScenario':
            lim_delta = (si.nodes-1)*si.distance*0.1 
            plt.xlim((-lim_delta, max_xy+lim_delta))
            plt.ylim((-5, 5))
            plt.xlabel("x [m]")
            plt.ylabel("y")

        plt.savefig(si.create_montecarlo_filenamebase()+"_montecarlo_contour_sent_ICMP_0.pdf")

##################second 10 minutes#################################

        LOW_LEVEL = -1
        HIGH_LEVEL = max(total_sentICMP_1)+10


        levels = floatRange(LOW_LEVEL,
                            HIGH_LEVEL,
                            0.5)
        #print levels

        my_cm = cm.jet
        my_cm.set_over('k')

        my_norm = col.Normalize(LOW_LEVEL,
                                HIGH_LEVEL,
                                clip=False)

        #print ">>>>x", xarr
        #print ">>>>y", yarr
        #print ">>>>sentICMP_1", total_sentICMP_1

    #    xi = np.linspace(0, max(xarr), 10)
    #    yi = np.linspace(0, max(yarr), 10)
        zi = griddata(xarr[1:], yarr[1:], total_sentICMP_1[1:], xi, yi)

        CS1 = plt.contourf(xi, yi, zi, levels,
                          cmap = my_cm, norm = my_norm,
                          extend='max')
       
        CS1.set_clim(CS0.cvalues[0],CS0.cvalues[-2])

     #   plt.colorbar(CS1)

        try:
            plt.grid(markevery=1)
        except:
            plt.grid()

        text = "No. of Nodes: " + str(si.nodes) + ", " + \
            "Inter-node Distance: " + str(si.distance) + "m, " + \
            " No. of Runs: " + str(iterations)
        title = 'Mean No. of Control Messages Sent in the Second 10 Minutes Interval\n(' + text + ')'
        plt.title(title)

        if SCENARIO == 'GridScenario':
            lim_delta = (math.sqrt(si.nodes)-1)*si.distance*0.1 
            plt.xlim((-lim_delta, max_xy+lim_delta))
            plt.ylim((-lim_delta, max_xy+lim_delta))
            plt.xlabel("x [m]")
            plt.ylabel("y [m]")

        if SCENARIO == 'LineScenario':
            lim_delta = (si.nodes-1)*si.distance*0.1
            plt.xlim((-lim_delta, max_xy+lim_delta))
            plt.ylim((-5, 5))
            plt.xlabel("x [m]")
            plt.ylabel("y")

        plt.savefig(si.create_montecarlo_filenamebase()+"_montecarlo_contour_sent_ICMP_1.pdf")
