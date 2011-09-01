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

class MonteCarloContourGraph:
    def __init__(self):
        pass

    def execute(self,
              #  ei,
                si,
                iterations):

        #filenamebase = si.createfilenamebase()
        print "="*40
        print "Executing MonteCarloContourGraph:"
        print "filenamebase\t\t", si.create_montecarlo_filenamebase()
        print "="*40

        if SCENARIO == 'LineScenario':
            point_no = 2*si.nodes+1
            xarr = np.zeros(point_no)
            yarr = np.zeros(point_no)
            total_meanrtt = np.zeros(point_no)
            new = np.zeros(point_no)
        else:
            xarr = np.zeros(si.nodes+1)
            yarr = np.zeros(si.nodes+1)
            total_meanrtt = np.zeros(si.nodes+1)
            new = np.zeros(si.nodes+1)

        #loop over iterations
        for run in range(0, iterations):
            monte_si = copy.deepcopy(si)
            monte_si.run = run
            meanrtt_run = np.load(monte_si.createfilenamebase() + \
                                      "_meanrtt.npy",
                                  "r")
            for i in range(0, si.nodes+1):
                total_meanrtt[i] += meanrtt_run[i]

        total_meanrtt = total_meanrtt / iterations
        
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
            total_meanrtt[0] = 0
            for j in range(1+si.nodes,point_no):
                index = j-si.nodes
                xarr[j] = xarr[index]
                yarr[j] = 1
                total_meanrtt[j] = total_meanrtt[index]
            print "total_meanrtt",total_meanrtt
            for i in range (1,2*(si.nodes)+1):
                if math.isnan(total_meanrtt[i]):
                    total_meanrtt[i] = 2048
                else:
                    new[i] = total_meanrtt[i]
        else:
            for i in range (1,si.nodes+1):
                if math.isnan(total_meanrtt[i]):
                    total_meanrtt[i] = 2048
                else:
                    new[i] = total_meanrtt[i]
            
         
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

        my_cm = cm.jet
        my_cm.set_over('k')

        my_norm = col.Normalize(LOW_LEVEL,
                                HIGH_LEVEL,
                                clip=False)

        print ">>>>x", xarr
        print ">>>>y", yarr
        print ">>>>meanrtt", total_meanrtt
        if SCENARIO == 'LineScenario':
            xi = np.linspace(0, max(xarr), 10)
            yi = np.linspace(0, max(yarr), 10)
        else:
            xi = np.linspace(0, max(xarr), 100)
            yi = np.linspace(0, max(yarr), 100)
        
        zi = griddata(xarr[1:], yarr[1:], total_meanrtt[1:], xi, yi)
        CS = plt.contourf(xi, yi, zi, levels,
                          cmap = my_cm, norm = my_norm,
                          extend='max')
        CS.set_clim(CS.cvalues[0], CS.cvalues[-2])

        plt.colorbar(CS)

        try:
            plt.grid(markevery=1)
        except:
            plt.grid()

        text = "#Nodes: " + str(si.nodes) + ", " + \
            "Inter node distance: " + str(si.distance) + "m," +\
            " #Runs: " + str(iterations)
        title = 'Mean RTT [ms]\n(' + text + ')'

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
        print si.create_montecarlo_filenamebase()
        plt.savefig(si.create_montecarlo_filenamebase()+"_montecarlo_contour.pdf")
