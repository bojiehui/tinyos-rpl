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
                ei,
                si,
                iterations):

        #filenamebase = si.createfilenamebase()
        print "="*40
        print "Executing MonteCarloContourGraph:"
        print "filenamebase\t\t", si.create_montecarlo_filenamebase()
        print "="*40

        total_consist = np.zeros(si.nodes+2)
        #total_consist.fill(np.nan)

        #loop over iterations
        for run in range(0, iterations):

            monte_si = copy.deepcopy(si)
            monte_si.run = run

            consist_run = np.load(monte_si.createfilenamebase() + \
                                      "_consist_contour.npy",
                                  "r")
            #print "cr", consist_run
            total_consist += consist_run

        total_consist = total_consist / iterations

        # do for last run, topology should not change over runs
        # (ensured by config)
        print "Reading id2xy mapping from " + \
            (monte_si.createfilenamebase()+"_id2xy.pickle")
        ifile = open(monte_si.createfilenamebase()+"_id2xy.pickle", "r")
        id2xy_dict = pickle.load(ifile)
        ifile.close()

        xarr = np.zeros(si.nodes+2)
        yarr = np.zeros(si.nodes+2)
        for i in range(1, si.nodes+2):
            (x, y) = id2xy_dict[i]
            xarr[i] = x
            yarr[i] = y

        packs = []
        for i in range(1, si.nodes+2):
            (x, y) = id2xy_dict[i]
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

        #print "! Max. Time to Consistency:", np.max(consist)
        #print "! Min. Time to Consistency:", np.min(consist)

        LOW_LEVEL = 0
        HIGH_LEVEL = 3*math.sqrt(si.nodes)

        levels = floatRange(LOW_LEVEL,
                            HIGH_LEVEL,
                            .5)
        #print levels

        my_cm = cm.jet
        my_cm.set_over('k')

        my_norm = col.Normalize(LOW_LEVEL,
                                HIGH_LEVEL,
                                clip=False)

        print ">>>>x", xarr
        print ">>>>y", yarr
        print ">>>>consist", total_consist

        xi = np.linspace(0, max(xarr), 100)
        yi = np.linspace(0, max(yarr), 100)
        zi = griddata(xarr[2:], yarr[2:], total_consist[2:], xi, yi)

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
            "Size: " + str(si.distance) + ", " + \
            "K: " + str(ei.defines["DISTRIBUTION_TRICKLE_K"])
        title = 'Model Time to Consistency [s]\n(' + text + ')'

        plt.title(title)

        #if si.sqr_nodes <= 10:
        #plt.yticks(range(si.sqr_nodes+1))
        #plt.xticks(range(si.sqr_nodes+1))
        #else:
        #    plt.yticks(range(0, si.sqr_nodes, 2))
        #    plt.xticks(range(0, si.sqr_nodes, 2))

        if math.sqrt(si.nodes) >= 10:
            lim_delta = 1
        else:
            lim_delta = .2

        #plt.xlim(-lim_delta, si.sqr_nodes+lim_delta)
        #plt.ylim(-lim_delta, si.sqr_nodes+lim_delta)

        if max(xarr) > max(yarr):
            max_xy = max(xarr)
        else:
            max_xy = max(yarr)

        plt.xlim(-lim_delta, max_xy+lim_delta)
        plt.ylim(-lim_delta, max_xy+lim_delta)


        plt.xlabel("x [m]")
        plt.ylabel("y [m]")

        plt.savefig(si.create_montecarlo_filenamebase()+"_montecarlo_contour.pdf")
