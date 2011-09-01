#!/usr/bin/env python

import numpy as np
import re
import math
from scipy.special import erfc

from sim.utils.helper import *
from sim.scenarios.ScenarioInformation import *
#from sim.scenarios.ExecutableInformation import *
from sim.evaluation.metric.Calc_Gain import *
from sim.evaluation.metric.Rtt import *

class PacketMetric:
    def __init__(self):
        pass

    def execute(self,
               # ei,
                si):
        noise = -98

        filenamebase = si.createfilenamebase()
        print "="*40
        print "Executing PacketMetric:"
        print "filenamebase\t\t", filenamebase
        print "="*40

        node_re = 'DEBUG \((\d+)\):'
        node_re_c = re.compile(node_re)
        time_re = '(\d+):(\d+):(\d+.\d+)'
        time_re_c = re.compile(time_re)
        rec_node_re = 'from node (\d+).'
        rec_node_re_c = re.compile(rec_node_re)
#        hopcount_re = 'with lower hopcount (\d+).'
#        hopcount_re_c = re.compile(hopcount_re)

        sent_packets = np.zeros(si.nodes+1)
        sent_ICMP = np.zeros(si.nodes+1)
        sent_ICMP_time = np.zeros(si.nodes+1)
        rec_packets  = np.zeros((si.nodes+1, si.nodes+1))
        prr_rate     = np.zeros((si.nodes+1, si.nodes+1))
        hopcounts = np.ones(si.nodes+1) * -1

        rtt = Rtt()
        rtt.execute(si)

        f = open(filenamebase+".log", "r")
        for line in f:
             if (line.find("ICMPCore:Send") >= 0):
                 node_obj = node_re_c.search(line)
                 node = int(node_obj.group(1))
               
                 time_obj = time_re_c.search(line)
                 t = Time(time_obj.group(1),
                          time_obj.group(2),
                          time_obj.group(3))
                 sent_ICMP[node] += 1
                
                 #print line,"sent_ICMP",sent_ICMP
                 if t.in_second() <= 600:
                     sent_ICMP_time[node] += 1
                
        f.close()
        for id1 in range(1, si.nodes+1):
            for id2 in range(1, si.nodes+1):
                if id1 != id2:
                # prr_rate[id1][id2] = (rec_packets[id1][id2] /
                #                       float(sent_packets[id2]))
                    g = Calc_Gain(si)
                    gain = g.execute(id1,id2)

                    if not gain:
                        SNR = 1
                    else:
                        SNR  = (0 - gain) - noise
        
                        beta1 = 0.9794
                        beta2 = 2.3851
                        X = SNR-beta2
                        PSE = 0.5*erfc(beta1*X/math.sqrt(2))
                        prr = round(pow(1-PSE, 23*2),2)
	
                        if (prr > 1):
                            prr = 1.1
                        elif (prr < 0):
                            prr = -0.1

                    prr_rate[id1][id2] = prr

        of = open(filenamebase+"_packet.txt", "aw")

        print >> of, "\nTotal number of Sent ICMP Packets"
        print >> of, np.sum(sent_ICMP)
       # np.save(filenamebase+"_sent_ICMP.npy", np.sum(sent_ICMP))


        print >> of, "Sent ICMP per Node"
        print >> of, sent_ICMP
       # np.save(filenamebase+"_sent_ICMP_per_node.npy", sent_ICMP)

        print >> of, "\nTotal number of Sent ICMP Packets in 10 Minutes"
        print >> of, np.sum(sent_ICMP_time)
       # np.save(filenamebase+"_sent_ICMP.npy", np.sum(sent_ICMP_time))

        print >> of, "Sent ICMP per Node in 10 Minutes"
        print >> of, sent_ICMP_time
        np.save(filenamebase+"_sent_ICMP_per_node_time.npy", sent_ICMP_time)

        np.set_printoptions(threshold=np.nan)
        print >> of, "\nPRR"
        print >> of, prr_rate
        np.save(filenamebase+"_prr.npy", prr_rate)

        of.close()
