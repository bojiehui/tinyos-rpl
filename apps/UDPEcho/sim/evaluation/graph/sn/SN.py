#!/usr/bin/python
# -*- coding: utf-8 -*-
from sim.config import * 
from pylab import *
import numpy
import pickle
import os
import matplotlib.pyplot as plt

tosroot=os.environ.get("TOSROOT")

class SN():
     def __init__(self):
          pass

     def execute(self,si):
          
          filenamebase = si.createfilenamebase()
          ifile = open(filenamebase+"_rtt.pickle","r")
          rtt_dict = pickle.load(ifile)
          ifile.close
     
          cx = []
          cy = []
          cmean = []
          mean = 0
          std = 0
          l = len(rtt_dict)
          
          mean = numpy.average(rtt_dict)
          std = numpy.std(rtt_dict)
          
          for i in range(1,l+1):
# Read values from output files 
               cx.append(i)
               cy.append(rtt_dict[i-1])
               cmean.append(mean)
            
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
          Num_node = str(NODES_LIST[0]+1)
          plt.title('RTT \n (' + SCENARIO +', ' + Num_node + ' Nodes topology, Node 4)')

          #plt.show()
          plt.savefig(filenamebase + "_sn.pdf")
    
