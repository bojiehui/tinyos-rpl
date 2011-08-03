import re
import pickle
import math

import numpy as np
from array import *

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as col
from matplotlib.text import Text
from matplotlib.lines import Line2D
from matplotlib.figure import SubplotParams
from mpl_toolkits.mplot3d import axes3d, Axes3D
from mpl_toolkits.mplot3d.art3d import Line3D

from sim.utils.helper import *
from sim.scenarios.ScenarioInformation import *
#from sim.scenarios.ExecutableInformation import *


class TopologyGraph_3D:
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

        fig = plt.figure(figsize=(13,10),
                         subplotpars = SubplotParams(left = 0.05,
                                                     bottom = 0.05,
                                                     top = 0.95,
                                                     right = 0.75))
        ax = axes3d.Axes3D(fig, azim = -60, elev = 30)

        consist = np.zeros(si.nodes)
        xarr = np.zeros(si.nodes)
        yarr = np.zeros(si.nodes)
        zarr = np.zeros(si.nodes)

        packs = []

        ifile = open(filenamebase+"_id2xyz.pickle", "r")
        id2xyz_dict = pickle.load(ifile)	
        ifile.close()
       # print id2xyz_dict

        for id1 in range(1, si.nodes+1):
            (x, y, z) = id2xyz_dict[id1]
            xarr[id1-1] = x
            yarr[id1-1] = y
            zarr[id1-1] = z
           # print "x = ",xarr[id1-1]

        xmin,xmax = ax.get_xlim3d()
        ymin,ymax = ax.get_ylim3d()
        zmin,zmax = ax.get_zlim3d()
        ax.set_xlim3d(0, xmax+1)
        ax.set_ylim3d(0, ymax+1)
        ax.set_zlim3d(0, zmax+1)

        ax.set_xlabel('X [m]')
        ax.set_ylabel('Y [m]')
        ax.set_zlabel('Z [m]')

        ax.scatter(xarr,yarr,zarr,zdir='z')

#### Start plotting lines####  
        for id1 in range(1, si.nodes+1):
            for id2 in range(1, si.nodes+1):
                if prr[id1][id2] == 0:
                    linecolor = None	
                    alpha = 0.0	
                
                if prr[id1][id2] >= 0.5:
                    linecolor = 'b'
                    alpha = 1.0
                    
                if prr[id1][id2] >= 0.95:
                    linecolor = 'g'
                    alpha = 1.0
                
                if prr[id1][id2] >= 0.99:
                    linecolor = 'k'
                    alpha = 1.0

                (x, y, z)    = id2xyz_dict[id1]
                (x2, y2, z2) = id2xyz_dict[id2]
          
                packs.append(
                    Line3D([x, x2],
                           [y, y2],
                           [z, z2],
                           color=linecolor,
                           linewidth=0.5,
                           alpha=alpha)
                    )


        text = "#Nodes: " + str(si.nodes) + ", " + \
            "Size: " + str(si.distance) 
        plt.title('Topology\n(' + text +')')
     
        for p in packs:
           ax.add_artist(p)
           p.set_clip_box(ax.bbox)
          
        prr_gt_0   = Line2D([0, 0.1],
                            [0, 0.1],
                            color='r',
                            linewidth=0.8)
        prr_lt_0_5 = Line2D([0,0.1],
                            [0, 0.1],
                            color='b',
                            linewidth=0.8)
        prr_lt_0_95 = Line2D([0, 0.1],
                             [0, 0.1],
                             color='g',
                             linewidth=0.8)
        prr_gt_0_99 = Line2D([0, 0.1],
                             [0, 0.1],
                             color='k',
                             linewidth=0.8)
            
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
#                    bbox_to_anchor=(0.05,0.95),
#                    borderaxespad = 0.,
                    loc = 2,
                    fancybox = 'True')
			
        plt.savefig(filenamebase+"_topology.pdf")
