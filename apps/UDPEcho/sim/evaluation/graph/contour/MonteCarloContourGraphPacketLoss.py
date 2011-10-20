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

class MonteCarloContourGraphPacketLoss:
    def __init__(self):
        pass

    def execute(self,
                si,
                iterations):

        print "="*40
        print "Executing MonteCarloContourGraph for Packeloss:"
        print "filenamebase\t\t", si.create_montecarlo_filenamebase()
        print "="*40

        max_packetloss = np.zeros(iterations)

        if SCENARIO == 'LineScenario':
             point_no = 2*si.nodes+1
             xarr = np.zeros(point_no)
             yarr = np.zeros(point_no)
             total_packetloss = np.zeros(point_no)
             count = 0
        else:
            xarr = np.zeros(si.nodes+1)
            yarr = np.zeros(si.nodes+1)
            total_packetloss = np.zeros(si.nodes+1)
        #loop over iterations
        for run in range(0, iterations):

            monte_si = copy.deepcopy(si)
            monte_si.run = run
            packetloss_run = np.load(monte_si.createfilenamebase() + \
                                      "_packetloss.npy",
                                  "r")
            max_packetloss[run] = max(packetloss_run)
            for i in range (0, si.nodes+1):
                total_packetloss[i] += packetloss_run[i]

        total_packetloss = total_packetloss / iterations
        
        # do for last run, topology should not change over runs
        # (ensured by config)
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
            for j in range(1+si.nodes, point_no):
                index = j-si.nodes
                xarr[j] = xarr[index]
                yarr[j] = 1
                total_packetloss[j] = total_packetloss[index]

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

        LOW_LEVEL = -1
        HIGH_LEVEL = 50

        levels = floatRange(LOW_LEVEL,
                            HIGH_LEVEL,
                            0.1)
        #print levels

        my_cm = cm.jet
        my_cm.set_over('k')

        my_norm = col.Normalize(LOW_LEVEL,
                                HIGH_LEVEL,
                                clip=False)

        #print ">>>>x", xarr
        #print ">>>>y", yarr
        #print ">>>>packetloss ", total_packetloss
        print ">>>> most packet loss in each run ", max_packetloss
        of =open(si.create_montecarlo_filenamebase()+"_most_packetloss.txt","w")
        print >> of, "Most packet loss in each run"
        print >> of, max_packetloss
        of.close()

        xi = np.linspace(0, max(xarr), 10)
        yi = np.linspace(0, max(yarr), 10)
        zi = griddata(xarr[1:], yarr[1:], total_packetloss[1:], xi, yi)

        CS = plt.contourf(xi, yi, zi, levels,
                          cmap = my_cm, norm = my_norm,
                          extend='max')
        CS.set_clim(0, 15)
        
        plt.colorbar(CS)
    
        try:
            plt.grid(markevery=1)
        except:
            plt.grid()

        text = "No. of Nodes: " + str(si.nodes) + ", " + \
            "Inter-node Distance: " + str(si.distance) + "m, " +\
            "No. of Runs: " + str(iterations)
        title = 'Mean Packet Loss Rate [%]\n(' + text + ')'
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

        plt.savefig(si.create_montecarlo_filenamebase()+"_montecarlo_contour_packetloss.pdf")
