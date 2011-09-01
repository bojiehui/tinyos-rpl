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

class ContourGraph:
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
             mean = np.zeros(point_no)
             new  = np.zeros(point_no)
        else:
            xarr = np.zeros(si.nodes+1)
            yarr = np.zeros(si.nodes+1)
            mean = np.zeros(si.nodes+1)
            new  = np.zeros(si.nodes+1)

        packs = []

        print "Reading id2xyz mapping from "+(filenamebase+"_id2xyz.pickle")
        ifile = open(filenamebase+"_id2xyz.pickle", "r")
        id2xyz_dict = pickle.load(ifile)
        ifile.close()
        mean_dict = np.load(filenamebase+"_meanrtt.npy")

        for i in range(0,si.nodes+1):
            mean[i] = mean_dict[i] 

        for i in range(1, si.nodes+1):
            (x, y, z) = id2xyz_dict[i]
            xarr[i] = x
            yarr[i] = y 
       
        if SCENARIO == 'LineScenario':
            for j in range(si.nodes+1, point_no):
                index = j-si.nodes
                xarr[j] = xarr[index]
                yarr[j] = 1
                mean[j] = mean[index]
            for i in range (0,2*(si.nodes)+1):  
                if math.isnan(mean[i]):
                    mean[i] = 2048
                else:
                    new[i] = mean[i]
        else:
            for i in range (0,si.nodes+1):
                if math.isnan(mean[i]):
                    mean[i] = 2048
                else:
                    new[i] = mean[i]

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

        fig = plt.figure(figsize=(10, 8))
        ax = fig.add_subplot(111)

        for p in packs:
            ax.add_artist(p)
            p.set_clip_box(ax.bbox)

        LOW_LEVEL = 0
        HIGH_LEVEL = max(new)+100
    
        levels = floatRange(LOW_LEVEL,
                            HIGH_LEVEL,
                            5)
        #print "HIGH_LEVEL",HIGH_LEVEL

        my_cm = cm.jet
        my_cm.set_over('k')

        my_norm = col.Normalize(LOW_LEVEL,
                                HIGH_LEVEL,
                                clip=False)

        #print ">>>>x", xarr
        #print ">>>>y", yarr
        if SCENARIO == 'LineScenario':
            xi = np.linspace(0, max(xarr),10)
            yi = np.linspace(0, max(yarr),10)
        else:
            xi = np.linspace(0, max(xarr),100)
            yi = np.linspace(0, max(yarr),100)

        zi = griddata(xarr[1:], yarr[1:], mean[1:], xi, yi)

        CS = plt.contourf(xi, yi, zi, levels,
                    cmap = my_cm, norm = my_norm,
                          extend='max')
        CS.set_clim(CS.cvalues[0], CS.cvalues[-2])

        plt.colorbar(CS)

        try:
            plt.grid(markevery=1)
        except:
            plt.grid()

        text = "#Nodes: " +str(si.nodes) + ", " + \
            "Inter node distance: " + str(si.distance) + "m"

        title = 'Mean RTT [ms] \n(' + text + ')'

        plt.title(title)

        if max(xarr) > max(yarr):
            max_xy = max(xarr)
        else:
            max_xy = max(yarr)
        
        if si.distance >= 50:
                lim_delta = 10
        else:
                lim_delta = 5

        if SCENARIO == 'GridScenario':
           
            plt.xlim(-lim_delta, max_xy+lim_delta)
            plt.ylim(-lim_delta, max_xy+lim_delta)

        if SCENARIO == 'LineScenario':    

            plt.xlim(-lim_delta, max_xy+lim_delta)
            plt.ylim(-lim_delta, lim_delta)

        plt.xlabel("x [m]")
        plt.ylabel("y [m]")

        plt.savefig(filenamebase+"_contour.pdf")
