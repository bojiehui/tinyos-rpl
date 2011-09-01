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
         
          for node in range(2,nodes+1):
               rtt_dict = []
               pl_dict = []          
               cx = []
               cy = []
               cmean = []
               std = 0
             
               node_id = str(node)

               rtt_dict = np.load(filenamebase+"_rtt_node_"+node_id+".npy")
               pl_dict = np.load(filenamebase+"_packetloss.npy")
              
               std = np.std(rtt_dict)      
               l = len(rtt_dict)
 
               for i in range(1,l+1):
# Read values from output files
                    cx.append(i)
                    cy.append(rtt_dict[i-1])
                    cmean.append(mean_dict[node])
                                        
               fig = plt.figure(figsize=(13, 10))	
               ax = fig.add_subplot(111)  
               fig.autofmt_xdate()
  
# standard deviation and mean value plotting
               point_std = len(cx)//2
               ax.plot(cx,cmean,'k-',label='Mean RTT')
               ax.legend(loc='upper left')
               if len(cx) != 0:
                    plt.errorbar(cx[point_std],cmean[point_std],std,None,fmt=None,ecolor='r')  
  
                    ax.plot(cx, cy,'bo')
                    xmin,xmax = ax.get_xlim()
                    ymin,ymax = ax.get_ylim()
                    ax.set_xlim(0,xmax+1)
                    ax.set_ylim(500,ymax+500)
                    plt.xlabel('Sequence Number')
                    plt.ylabel('RTT[ms]')
                    
                    text = "#Nodes: " +str(si.nodes) + ", " + SCENARIO + \
                        ", Inter node distance: " + str(si.distance) + "m"

                    title = 'Round Trip Time for Node ' + node_id + \
                               '\n(' + text + ')' 
                    plt.title(title)

                    plt.savefig(filenamebase + '_sn_node_'+node_id+'.pdf')
    
