import re
import pickle
import math
import numpy as np

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as col
from matplotlib.mlab import griddata
from matplotlib.text import Text

from sim.utils.helper import *
from sim.scenarios.ScenarioInformation import *
from sim.scenarios.ExecutableInformation import *

from sim.config import *

class ContourGraphSentICMP:
    def __init__(self):
        pass

    def execute(self,
#                ei,
                si):

        filenamebase = si.createfilenamebase()
        print "="*40
        print "Executing ContourGraphSentICMP:"
        print "filenamebase\t\t", filenamebase
        print "="*40

        if SCENARIO == 'LineScenario':
            point_no = (si.nodes+1)*si.nodes
            xarr = np.zeros(point_no)
            yarr = np.zeros(point_no)
            sent_ICMP_time_0 = np.zeros(point_no)
            sent_ICMP_time_1 = np.zeros(point_no)
            count = 0
        else:
            xarr = np.zeros(si.nodes+1)
            yarr = np.zeros(si.nodes+1)
            sent_ICMP_time_0 = np.zeros(si.nodes+1)
            sent_ICMP_time_1 = np.zeros(si.nodes+1)
        packs = []

        print "Reading id2xyz mapping from "+(filenamebase+"_id2xyz.pickle")
        ifile = open(filenamebase+"_id2xyz.pickle", "r")
        id2xyz_dict = pickle.load(ifile)
        ifile.close()

        sent_ICMP_time_0_dict = np.load(filenamebase+"_sent_ICMP_per_node_time_0.npy", "r")
        sent_ICMP_time_1_dict = np.load(filenamebase+"_sent_ICMP_per_node_time_1.npy", "r")
        
        for i in range(0,si.nodes+1):
            sent_ICMP_time_0[i] = sent_ICMP_time_0_dict[i]
            sent_ICMP_time_1[i] = sent_ICMP_time_1_dict[i]

        for node in range(1, si.nodes+1):
            (x, y, z) = id2xyz_dict[node]
            xarr[node] = x
            yarr[node] = y

        if SCENARIO == 'LineScenario':
                for j in range(1+si.nodes, point_no):
                    index = j-si.nodes
                    xarr[j] = xarr[index]
                    yarr[j] = 1
                    sent_ICMP_time_0[j] = sent_ICMP_time_0[index]
                    sent_ICMP_time_1[j] = sent_ICMP_time_1[index]

        for i in range(1, si.nodes+1):
            (x, y, z) = id2xyz_dict[i]
            if si.nodes >= 100:
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

############# first 10mins interval######################
        LOW_LEVEL = -1
        HIGH_LEVEL = max(sent_ICMP_time_0)+10

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
        #print ">>>>sent", sent_ICMP_time_0

        xi = np.linspace(0, max(xarr), 10)
        yi = np.linspace(0, max(yarr), 10)
        zi = griddata(xarr[1:], yarr[1:], sent_ICMP_time_0[1:], xi, yi)

        CS0 = plt.contourf(xi, yi, zi, levels,
                          cmap = my_cm, norm = my_norm,
                          extend='max')
        CS0.set_clim(CS0.cvalues[0], CS0.cvalues[-2])

        plt.colorbar(CS0)

        try:
            plt.grid(markevery=1)
        except:
            plt.grid()

        text = "No. of Nodes: " +str(si.nodes) + ", " + \
            "Inter node distance: " + str(si.distance) + "m" 

        title = 'No. of Control Messages Sent in the First 10 Minutes Interval\n(' + text + ')'

        plt.title(title)

        if max(xarr) > max(yarr):
            max_xy = max(xarr)
        else:
            max_xy = max(yarr)

        if SCENARIO == 'GridScenario':
            lim_delta = (math.sqrt(si.nodes)-1)*si.distance*0.1
#            if si.nodes > 100:
#                lim_delta = 20
#            else:
#                lim_delta = 10
            plt.xlim((-lim_delta, max_xy+lim_delta))
            plt.ylim((-lim_delta, max_xy+lim_delta))
            plt.xlabel("x [m]")
            plt.ylabel("y [m]")

        if SCENARIO == 'LineScenario':
            lim_delta = (si.nodes-1)*si.distance*0.1 
#           if si.distance > 50:
#                if si.nodes > 8:
#                    lim_delta = 50
#                else:
#                    lim_delta =10
#            else:
#                lim_delta = 20
            plt.xlim((-lim_delta, max_xy+lim_delta))
            plt.ylim((-5, 5))
            plt.xlabel("x [m]")
            plt.ylabel("y")
      
        plt.savefig(filenamebase+"_contour_sent_ICMP_0.pdf")

##################second time interval #########################################
        
        LOW_LEVEL = 0
        HIGH_LEVEL = max(sent_ICMP_time_1)+10

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
        #print ">>>>sent", sent_ICMP_time_1

        xi = np.linspace(0, max(xarr), 10)
        yi = np.linspace(0, max(yarr), 10)
        zi = griddata(xarr[1:], yarr[1:], sent_ICMP_time_1[1:], xi, yi)

        CS1 = plt.contourf(xi, yi, zi, levels,
                          cmap = my_cm, norm = my_norm,
                          extend='max')
        CS1.set_clim(CS0.cvalues[0], CS0.cvalues[-2])

       # plt.colorbar(CS1)

        try:
            plt.grid(markevery=1)
        except:
            plt.grid()

        text = "No. of Nodes: " +str(si.nodes) + ", " + \
            "Inter node distance: " + str(si.distance) + "m" 

        title = 'No. of Control Messages Sent in the Second 10 Minutes Interval\n(' + text + ')'

        plt.title(title)

        if SCENARIO == 'GridScenario':
            lim_delta = (math.sqrt(si.nodes)-1)*si.distance*0.1
#            if si.nodes > 100:
#                lim_delta = 20
#            else:
#                lim_delta = 10
            plt.xlim((-lim_delta, max_xy+lim_delta))
            plt.ylim((-lim_delta, max_xy+lim_delta))
            plt.xlabel("x [m]")
            plt.ylabel("y [m]")

        if SCENARIO == 'LineScenario':
            lim_delta = (si.nodes-1)*si.distance*0.1
#            if si.distance > 50: 
#                if si.nodes > 8:
#                    lim_delta = 50
#                else:
#                    lim_delta =10
#            else:
#                lim_delta = 20
            plt.xlim((-lim_delta, max_xy+lim_delta))
            plt.ylim((-5, 5))
            plt.xlabel("x [m]")
            plt.ylabel("y")

        plt.savefig(filenamebase+"_contour_sent_ICMP_1.pdf")
