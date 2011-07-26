import os
import math
import pickle
import numpy as np
from array import *
from scipy.special import erfc

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as col
from mpl_toolkits.mplot3d import axes3d, Axes3D
from mpl_toolkits.mplot3d.art3d import Line3D
from matplotlib.lines import Line2D


from sim.scenarios.Scenario import Scenario
from sim.evaluation.Calc_Gain import Calc_Gain
from sim.utils.helper import *

tosroot = os.environ.get("TOSROOT")

class TopologyGraph(Calc_Gain):
#class TopologyGraph:

    def __init__(self):
        self.noise = -98
       
    def Prr(self, filenamebase, id1, id2):
     
        gain = self.calc_gain(filenamebase, id1, id2)
	if not gain:
            SNR = 1
        else:
            SNR  = (0 - gain) - self.noise
        
        beta1 = 0.9794
        beta2 = 2.3851
        X = SNR-beta2
        PSE = 0.5*erfc(beta1*X/math.sqrt(2))
        prr = round(pow(1-PSE, 23*2),2)
	
        if (prr > 1):
            prr = 1.1
        elif (prr < 0):
            prr = -0.1
        
	return prr


    def execute(self,
	         si):
        filenamebase = si.createfilenamebase()
        #PRR is calculated by PacketMetric, loading it here
       # prr = np.load(filenamebase+"_prr.npy")

        fig = plt.figure()
        ax = axes3d.Axes3D(fig, azim = 90, elev = 0)
        
   # def Plotting(self):

        consist = np.zeros(si.nodes+1)
        xarr = np.zeros(si.nodes+1)
        yarr = np.zeros(si.nodes+1)
        zarr = np.zeros(si.nodes+1)

        packs = []

        ifile = open(filenamebase+"_id2xyz.pickle", "r")
        id2xyz_dict = pickle.load(ifile)
        ifile.close()

        for id1 in range(1, si.nodes+2):
            print id2xyz_dict[id1]
            (x, y, z) = id2xyz_dict[id1]
            xarr[id1-1] = x
            yarr[id1-1] = y
            zarr[id1-1] = z
    
        ax.set_xlim3d(0, 13)
        ax.set_ylim3d(0, 13)
        ax.set_zlim3d(0, 13)

        ax.set_xlabel('X [m]')
        ax.set_ylabel('Y [m]')
        ax.set_zlabel('Z [m]')

        ax.scatter(xarr,yarr,zarr,zdir='z')

#### Start plotting lines####  
        for id1 in range(1, si.nodes+2):
            for id2 in range(1, si.nodes+2):
                if id1 >= id2:
                    continue
		
                PRR = self.Prr(filenamebase, id1, id2)
		#print "node", id1, id2,"Prr = ",PRR  
               
                if PRR == 0:
                    linecolor = None	
	            alpha = 0.0

                if PRR > 0 and PRR < 0.5:
                    linecolor = None
		    alpha = 1.0
                        
                if PRR >= 0.5 and PRR < 0.95:
                    linecolor = 'b'
                    alpha = 1.0

                if PRR >= 0.95 and PRR < 0.99:
                    linecolor = 'g'
                    alpha = 1.0

                if PRR >= 0.99:
                    linecolor = 'r'
		    alpha = 1.0
             
                (x, y, z)   = id2xyz_dict[id1]
                (x2, y2, z2) = id2xyz_dict[id2]
          
                packs.append(
                    Line3D([x, x2],
                           [y, y2],
                           [z, z2],
                           color=linecolor,
                           linewidth=0.5,
			   alpha=alpha
                        ))
  
        plt.title('Topology\n( 33 nodes')

       # ax = fig.add_subplot(111)
        for p in packs:
           ax.add_artist(p)
           p.set_clip_box(ax.bbox)
          
      #  prr_gt_0   = Line2D([0, 0.1],
      #                      [0, 0.1],
      #                      color='r',
      #                      linewidth=0.5)
        prr_lt_0_5 = Line2D([0, 0.1],
                            [0, 0.1],
                            color='b',
                            linewidth=0.8)
        prr_lt_0_95 = Line2D([0, 1],
                             [0, 1],
                             color='g',
                             linewidth=0.8)
        prr_gt_0_99 = Line2D([0, 1],
                             [0, 1],
                             color='r',
                             linewidth=0.8)
            
        plt.legend( (#prr_gt_0,
                     prr_lt_0_5,
                     prr_lt_0_95,
                     prr_gt_0_99,
                    ),
                    (#'0 < PRR < 0.5',
                     '0.5  <= PRR < 0.95',
                     '0.95 <= PRR < 0.99',
                     '0.99 <= PRR <= 1',
                     ),
                     loc = 2,
                     fancybox = 'True'
			)

        plt.savefig(filenamebase+"_topology.pdf")

        plt.show()

