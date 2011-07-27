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

class ContourGraphSentPackets:
    def __init__(self):
        pass

    def execute(self,
                ei,
                si):

        filenamebase = si.createfilenamebase()
        print "="*40
        print "Executing ContourGraphSentPackets:"
        print "filenamebase\t\t", filenamebase
        print "="*40

        #node_re = 'DEBUG \((\d+)\):'
        #node_re_c = re.compile(node_re)
        #time_re = '(\d+):(\d+):(\d+.\d+)'
        #time_re_c = re.compile(time_re)

        #consist = np.empty(si.nodes+2)
        #consist.fill(np.nan)
        xarr = np.zeros(si.nodes+2)
        yarr = np.zeros(si.nodes+2)

        packs = []

        #print "Reading id2xy mapping from "+(filenamebase+"_id2xy.pickle")
        ifile = open(filenamebase+"_id2xy.pickle", "r")
        id2xy_dict = pickle.load(ifile)
        ifile.close()

        for i in range(1, si.nodes+2):
            (x, y) = id2xy_dict[i]
            xarr[i] = x
            yarr[i] = y

        sent_packets = np.load(filenamebase+"_sent_packets_per_node.npy", "r")

        for i in range(1, si.nodes+2):
            (x, y) = id2xy_dict[i]
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
        HIGH_LEVEL = ei.defines["DISTRIBUTION_TRICKLE_K"] * SEC_AFTER_INJECT/(ei.defines["DISTRIBUTION_TRICKLE_TAU_HIGH"]/1024)

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
        print ">>>>sent", sent_packets

        xi = np.linspace(0, max(xarr), 100)
        yi = np.linspace(0, max(yarr), 100)
        #print ">>>>xi", xi
        #print ">>>>yi", yi
        zi = griddata(xarr[2:], yarr[2:], sent_packets[2:], xi, yi)

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
            "Size: " + str(si.distance) + ", " + \
            "K: " + str(ei.defines["DISTRIBUTION_TRICKLE_K"])
        title = '#Packets\n(' + text + ')'

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

        plt.savefig(filenamebase+"_contour_sent_packets.pdf")
