import re
import pickle
import math
import numpy as np

from matplotlib import mpl
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as col
from matplotlib.mlab import griddata
from matplotlib.text import Text

from sim.utils.helper import *
from sim.scenarios.ScenarioInformation import *
from sim.scenarios.ExecutableInformation import *

class ContourGraphPacketLoss:
    def __init__(self):
        pass

    def execute(self,
#                ei,
                si):

        filenamebase = si.createfilenamebase()
        print "="*40
        print "Executing ContourGraph:"
        print "filenamebase\t\t", filenamebase
        print "="*40

        if SCENARIO == 'LineScenario':
            point_no = 2*si.nodes+1
            xarr = np.zeros(point_no)
            yarr = np.zeros(point_no)
            packetloss = np.zeros(point_no)
        else:
            xarr = np.zeros(si.nodes+1)
            yarr = np.zeros(si.nodes+1)
            packetloss = np.zeros(si.nodes+1)

        packs = []

        #print "Reading id2xy mapping from "+(filenamebase+"_id2xy.pickle")
        ifile = open(filenamebase+"_id2xyz.pickle", "r")
        id2xyz_dict = pickle.load(ifile)
        ifile.close()
        packetloss_dict = np.load(filenamebase+"_packetloss.npy", "r")
        for i in range(0, si.nodes+1):
            packetloss[i] = packetloss_dict[i]/NUM_PING*100
 
        for node in range(1, si.nodes+1):
            (x, y, z) = id2xyz_dict[node] 
            xarr[node] = x
            yarr[node] = y 
       
        if SCENARIO == 'LineScenario':
                for j in range(1+si.nodes, point_no):
                    index = j-si.nodes
                    xarr[j] = xarr[index]
                    yarr[j] = 1
                    packetloss[j] = packetloss[index]

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

        LOW_LEVEL = -1
        HIGH_LEVEL = 50

        levels = floatRange(LOW_LEVEL,
                            HIGH_LEVEL,
                            0.1)

        my_cm = cm.jet
        my_cm.set_over('k')

        my_norm = col.Normalize(LOW_LEVEL,
                                HIGH_LEVEL,
                                clip=False)

        #print ">>>>x", xarr
        #print ">>>>y", yarr
        #print ">>>>packet loss",packetloss

        xi = np.linspace(0, max(xarr),10)
        yi = np.linspace(0, max(yarr),10)
        zi = griddata(xarr[1:], yarr[1:], packetloss[1:], xi, yi)
    
        CS = plt.contourf(xi, yi, zi, levels,
                    cmap = my_cm, norm = my_norm,
                          extend='max')
      
      #  CS.set_clim( CS.cvalues[0], CS.cvalues[-2])
        CS.set_clim(0, 15)
        plt.colorbar(CS)

        text = "No. of Nodes: " +str(si.nodes) + ", " + \
            "Inter node distance: " + str(si.distance) + "m"
        title = 'No. of Packet Loss [%]\n(' + text + ')'

        plt.title(title)
        try:
            plt.grid(markevery=1)
        except:
            plt.grid()       

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

        plt.savefig(filenamebase+"_contour_packetloss.pdf")
