#!/usr/bin/python
# -*- coding: utf-8 -*-
from sim.config import * 
from pylab import *
import numpy as np
import pickle
import os
import matplotlib.pyplot as plt

tosroot=os.environ.get("TOSROOT")

class SN():
     def __init__(self):
          pass

     def execute(self,si):
          filenamebase = si.createfilenamebase()
          nodes = si.nodes
          mean_dict = []
          mean_dict = np.load(filenamebase+"_meanrtt.npy")     
         
          for node in range(2,nodes+2):
               rtt_dict = []
               pl_dict = []          
               cx = []
               cy = []
               cmean = []
               std = 0
             
               node_id = str(hex(node))

               rtt_dict = np.load(filenamebase+"_rtt_"+node_id+".npy")
               pl_dict = np.load(filenamebase+"_packetloss_"+node_id+".npy")
              
               std = np.std(rtt_dict)      
               l = len(rtt_dict)
 
               for i in range(1,l+1):
# Read values from output files
                    cx.append(i)
                    cy.append(rtt_dict[i-1])
                    cmean.append(mean_dict[node-2])
                                        
               fig = plt.figure(figsize=(13, 10))	
               ax = fig.add_subplot(111)  
               fig.autofmt_xdate()
  
# standard deviation and mean value plotting
               point_std = len(cx)/2
               ax.plot(cx,cmean,'k-',label='Mean RTT')
               ax.legend(loc='upper left')
               plt.errorbar(cx[point_std],cmean[point_std],std,None,fmt=None,ecolor='r') 
  
               ax.plot(cx, cy,'bo')
               xmin,xmax = ax.get_xlim()
               ymin,ymax = ax.get_ylim()
               ax.set_xlim(0,xmax+1)
               ax.set_ylim(0,ymax+100)
               plt.xlabel('Sequence Number')
               plt.ylabel('RTT[ms]')
               
               plt.title('RTT \n (' + SCENARIO +', ' + str(nodes) + ' Nodes topology, Node '+ node_id + ')')

               plt.savefig(filenamebase + '_sn_'+node_id+'.pdf')
    
