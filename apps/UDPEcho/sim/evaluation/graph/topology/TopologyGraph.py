import re
import pickle
import math

import numpy as np

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as col
from matplotlib.text import Text
from matplotlib.lines import Line2D
from matplotlib.figure import SubplotParams

from sim.utils.helper import *
from sim.scenarios.ScenarioInformation import *
#from sim.scenarios.ExecutableInformation import *

class TopologyGraph:
    def __init__(self):
        pass

    def execute(self,
               # ei,
                si):
  
        filenamebase = si.createfilenamebase()
        #PRR is calculated by PacketMetric, loading it here
        prr = np.load(filenamebase+"_prr.npy")

        print "="*40
        print "Executing TopologyGraph:"
        print "filenamebase\t\t", filenamebase
        print "="*40

        # consist = np.zeros(si.nodes+1)
        xarr = np.zeros(si.nodes+2)
        yarr = np.zeros(si.nodes+2)

        packs = []

        ifile = open(filenamebase+"_id2xyz.pickle", "r")
        id2xyz_dict = pickle.load(ifile)
        ifile.close()

        for id1 in range(1, si.nodes+2):
            (x, y, z) = id2xyz_dict[id1]
            xarr[id1] = x
            yarr[id1] = y

        for id1 in range(1, si.nodes+2):
            for id2 in range(1, si.nodes+2):

	            if prr[id1][id2] != np.nan:
                        if prr[id1][id2] > 0:
                            linecolor = 'r'
                
                            if prr[id1][id2] >= 0.5:
                                linecolor = 'b'

                            if prr[id1][id2] >= 0.95:
                                linecolor = 'g'

                            if prr[id1][id2] >= 0.99:
                                linecolor = 'k'
             
                            (x, y, z)    = id2xyz_dict[id1]
                            (x2, y2, z2) = id2xyz_dict[id2]
          
                            packs.append(
                                Line2D([x, x2],
                                       [y, y2],
                                       color=linecolor,
                                       linewidth=1)
                                 )

        for i in range(1, si.nodes+2):
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
                     backgroundcolor='k',
                     fontsize=fs,
                     verticalalignment='center',
                     horizontalalignment='center',
                     alpha=1,
                     bbox=dict(facecolor='k'))
                 )

        fig = plt.figure(figsize=(13, 10),
                         subplotpars = SubplotParams(left = 0.05,
                                                     bottom = 0.05,
                                                     top = 0.95,
                                                     right = 0.75))

        ax = fig.add_subplot(111)

        for p in packs:
           ax.add_artist(p)
           p.set_clip_box(ax.bbox)

        text = "#Nodes: " + str(si.nodes) + ", " + \
            "Size: " + str(si.distance) 
            #+ ", " + \
            #"K: " + str(ei.defines["DISTRIBUTION_TRICKLE_K"])

        plt.title('Topology\n(' + text +')')

        #plt.yticks(range(0, si.sqr_nodes+1))
        #plt.xticks(range(0, si.si.sqr_nodes+1))
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

        #plt.xlabel("x index")
        #plt.ylabel("y index")
        plt.xlabel("x [m]")
        plt.ylabel("y [m]")
          
        prr_gt_0   = Line2D([0, 1],
                            [0, 1],
                            color='r',
                            linewidth=1)
        prr_lt_0_5 = Line2D([0, 1],
                            [0, 1],
                            color='b',
                            linewidth=1)
        prr_lt_0_95 = Line2D([0, 1],
                             [0, 1],
                             color='g',
                             linewidth=1)
        prr_gt_0_99 = Line2D([0, 1],
                             [0, 1],
                             color='k',
                             linewidth=1)
            
        plt.legend( (prr_gt_0,
                     prr_lt_0_5,
                     prr_lt_0_95,
                     prr_gt_0_99,
                    ),
                    ('0 < PRR < 0.5',
                     '0.5  < PRR < 0.95',
                     '0.95 < PRR < 0.99',
                     '0.99 < PRR < 1',
                     ),
#                       'lower right',
                    bbox_to_anchor=(1.02, 1),
                    loc = 2,
                    borderaxespad=0. ,
#                       loc = (.9, .5),
                     fancybox = 'True')

        plt.savefig(filenamebase+"_topology.pdf")
