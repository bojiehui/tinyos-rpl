import re
import pickle
import numpy as np
from sim.utils.helper import *
from sim.config import *

class Rtt:
    def __init__(self):
        pass

    def execute(self, si):
        print ">>>> Calculating Round Trip Time <<<<"
        filenamebase = si.createfilenamebase()
        t_dict = []
        n_dict = []
        rtt_dict = []

        mean_dict = np.empty(si.nodes+1)
        mean_dict.fill(np.nan)
      
        pl_dict = np.zeros(si.nodes+1)
       
        node_re = 'DEBUG \((\d+)\):'
        node_re_c = re.compile(node_re)
        time_re = '(\d+):(\d+):(\d+.\d+)'
        time_re_c = re.compile(time_re)

        print ">>>> Read send/recive time form log file <<<<" 
        f = open (filenamebase + ".log","r")
        for line in f:
            s = line.split()         
            if s[3]=='at':
                #print line
                time_obj = time_re_c.search(line)
                #print "\t", time_obj.group(0),
                t = Time(time_obj.group(1),
                          time_obj.group(2),
                          time_obj.group(3))
                n_dict.append(s[2])
                t_dict.append(t.in_milisecond())

            if s[2] == 'Updated':   # Seperating different ping destinations
                node = int(s[7])-1
                node_id = str(node)
               
                print ">>>> Checking for packet loss for node ",node
                l  = len(n_dict)
                a  = 0
                PL = 0
        
                for i in range (0,l):
                    l_n = len(n_dict)
                    if n_dict[l_n-1] != 'Receive':
                        del t_dict[l_n-1]
                        del n_dict[l_n-1]
                        PL=PL+1
                    
                #print "lenth of n_dict =",len(n_dict)
                for i in range (0,len(n_dict)-1):
                    if n_dict[i]== 'Send' and n_dict[i] == n_dict[i+1]:
                        del t_dict[i-a]
                        a = a+1
                        PL = PL+1
                        SN = (i+a)/2
                pl_dict[node] = PL 
                print "PL = ",PL,"node",node
                if PL != 100:
                    
                    print ">>>> Calculating RTT for node ",node    
                    for i in range (1, len(t_dict), 2):
                        rtt = t_dict[i] - t_dict[i-1]
                        rtt_dict.append(rtt)
                    print "Rtt",rtt_dict
         
                    print ">>>>>> Calculation mean RTT for node ",node
                    mean = np.average(rtt_dict)
                    mean_dict[node]=mean
                else:
                    print "All packets are lost for node ", node
                
                np.save(filenamebase+"_rtt_node_"+node_id+".npy", rtt_dict)
              
                t_dict = []
                n_dict = []
                rtt_dict = []
      
        mean_dict[1] = 0
        np.save(filenamebase+"_meanrtt.npy", mean_dict)
       
        of = open(filenamebase+"_packet.txt","w")
        print >> of, "Packet loss"
        print >> of, pl_dict
        np.save(filenamebase+"_packetloss.npy", pl_dict)
        
        of.close()
