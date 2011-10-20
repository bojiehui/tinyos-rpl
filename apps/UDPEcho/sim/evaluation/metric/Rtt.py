import re
import pickle
import numpy as np
from sim.utils.helper import *
from sim.config import *
import math

class Rtt:
    def __init__(self):
        pass

    def execute(self, si):
        print ">>>> Calculating Round Trip Time <<<<"
        filenamebase = si.createfilenamebase()
        send_dict = np.empty(NUM_PING)
        receive_dict = np.empty(NUM_PING)
        mean_dict =np.empty(si.nodes+1)
        pl_dict = np.zeros(si.nodes+1)
        rtt_dict = np.empty(NUM_PING)
        rtt_dict_2=[]

        send_dict.fill(np.inf)
        receive_dict.fill(np.inf)
        mean_dict.fill(np.nan)
        rtt_dict.fill(np.inf)
        PL = 0
       
        node_re = 'DEBUG \((\d+)\):'
        node_re_c = re.compile(node_re)
        time_re = '(\d+):(\d+):(\d+.\d+)'
        time_re_c = re.compile(time_re)

        print ">>>> Read send/recive time form log file <<<<" 
        f = open (filenamebase + ".log","r")
        for line in f:
            s = line.split()
            
            if s[2]=='Send':
                time_obj = time_re_c.search(line)
                #print "\t", time_obj.group(0),
                t = Time(time_obj.group(1),
                         time_obj.group(2),
                         time_obj.group(3))
                
                #print t.in_milisecond()
                sn = int(s[6])
                #print "sn =",sn
                send_dict[sn] = t.in_milisecond()

            if s[2]=='Receive':
                time_obj = time_re_c.search(line)
                #print "\t", time_obj.group(0),
                t = Time(time_obj.group(1),
                         time_obj.group(2),
                         time_obj.group(3))

                sn = int(s[6])
                #print "sn=",sn
                receive_dict[sn] = t.in_milisecond()

            if s[2] == 'Updated':   # Seperating different ping destinations
                node = int(s[7])-1
                node_id = str(node)

                print ">>>> Calculating ", node
                for i in range(0,NUM_PING):
                   # print "sn = ", i, receive_dict[i], send_dict[i]
                    if math.isinf(receive_dict[i]):
                        PL += 1
                    else:
                        rtt_dict[i] = receive_dict[i] - send_dict[i] - 512 # response was sent after a 521 ms delay
                        rtt_dict_2.append(rtt_dict[i])
                pl_dict[node] = PL 
                mean_dict[node] = np.average(rtt_dict_2)
                
                np.save(filenamebase+"_rtt_node_"+node_id+".npy", rtt_dict)
              
                send_dict = np.empty(NUM_PING)
                receive_dict = np.empty(NUM_PING)
                rtt_dict = np.empty(NUM_PING)
                rtt_dict_2=[]
                PL = 0

                send_dict.fill(np.inf)
                receive_dict.fill(np.inf)
                rtt_dict.fill(np.inf)
      
        mean_dict[1] = 0
        np.save(filenamebase+"_meanrtt.npy", mean_dict)
       
        of = open(filenamebase+"_packet.txt","w")
        print >> of, "Packet loss"
        print >> of, pl_dict
        np.save(filenamebase+"_packetloss.npy", pl_dict)
        
        of.close()
