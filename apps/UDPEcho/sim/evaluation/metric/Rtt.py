import re
import pickle
import numpy as np
from sim.utils.helper import *

class Rtt:
    def __init__(self):
        pass

    def execute(self, si):
        filenamebase = si.createfilenamebase()
        t_dict = []
        n_dict = []
        rtt_dict = []
        mean_dict = []
        pl_dict = []

        print ">>>> Read send/recive time form log file <<<<" 
        f = open (filenamebase + ".log","r")
        lines = f.readlines()
        for line in lines:
            s = line.split()         
            if s[3]=='at':
                n_dict.append(s[2])
                d = s[4].split(':')
                #print d[0],d[1],d[2]
                t = Time(d[0],d[1],d[2])
                t_dict.append(t.in_milisecond())

            if s[2] == 'Updated':   # Seperating different ping destinations
                node_id = str(hex(int(s[7],16)-1))
    
                print ">>>> Checking for packet loss <<<<"
                l  = len(n_dict)
                a  = 0
                PL = 0
                if n_dict[l-1] == 'Send':
                    del t_dict[l-1]
                    del n_dict[l-1]
                    PL=PL+1
                    print "Packet loss for last ping"
                    pl_dict.append(l-1)
                    
                print "lenth of n_dict =",len(n_dict)
                for i in range (0,len(n_dict)):
                    if n_dict[i]== 'Send' and n_dict[i] == n_dict[i+1]:
                        del t_dict[i-a]
                        a = a+1
                        PL = PL+1
                        SN = (i+a)/2
                        pl_dict.append(SN)
                        print "Packet loss for sequence no.",SN
                print "Totally",PL,"packets are lost!!"   
                    
                print ">>>> Calculating RTT <<<<"        
                for i in range (1, len(t_dict), 2):
                    rtt = t_dict[i] - t_dict[i-1]
                    rtt_dict.append(rtt)
                    print "RTT for node ", node_id, " = ", rtt, "ms"
         
                print ">>>>>> Calculation mean RTT <<<<<<<"
                mean = np.average(rtt_dict)
                mean_dict.append(mean)
                print "Mean Rtt for node ",node_id," = ",mean,"ms"

                np.save(filenamebase+"_rtt_"+node_id+".npy", rtt_dict)
                np.save(filenamebase+"_packetloss_"+node_id+".npy", pl_dict)
              
                t_dict = []
                n_dict = []
                rtt_dict = []
                pl_dict = []
        mean_dict.insert(0,0)
        mean_dict.insert(0,0)
        np.save(filenamebase+"_meanrtt.npy", mean_dict)
