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
         
          for node in range(2,nodes+1):
               rtt_dict = []
               rtt_dict_2 = []
               pl_dict = []          
               cx = np.empty(NUM_PING)
               cy = np.empty(NUM_PING)
               cmean = np.zeros(NUM_PING)
               cx.fill(np.inf)
               cy.fill(np.inf)
               std = 0
             
               node_id = str(node)

               rtt_dict = np.load(filenamebase+"_rtt_node_"+node_id+".npy")
               #print "rtt:", rtt_dict
               for i in range(0,NUM_PING):
                    # print "sn = ", i, receive_dict[i], send_dict[i]
                    if not math.isinf(rtt_dict[i]):
                        rtt_dict_2.append(rtt_dict[i])
               
               std = np.std(rtt_dict_2)
               #print ">>>>>>>rtt",rtt_dict_2
               mean = np.average(rtt_dict_2)
               l = len(rtt_dict)
               for i in range(0,l):
# Read values from output files
                    cx[i] = i
                    cy[i] = rtt_dict[i-1]
                    cmean[i] = mean
               #print ">>>>>>>>mean",mean
               fig = plt.figure(figsize=(13, 6))	
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
                    ax.set_xlim(0,NUM_PING+1)
                    ax.set_ylim(0,250)
                    plt.xlabel('Sequence Number')
                    plt.ylabel('RTT[ms]')
                    
                    text = "No. of Nodes: " +str(si.nodes) + ", " + SCENARIO + \
                        ", Inter node distance: " + str(si.distance) + "m"

                    title = 'Round Trip Time for Node ' + node_id + \
                               '\n(' + text + ')' 
                    plt.title(title)

                    plt.savefig(filenamebase + '_sn_node_'+node_id+'.pdf')
    
