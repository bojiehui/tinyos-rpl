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
        hopcount_re = 'with lower hopcount (\d+).'
        hopcount_re_c = re.compile(hopcount_re)

        sent_packets = np.zeros(si.nodes+2)
        rec_packets  = np.zeros((si.nodes+2, si.nodes+2))
        prr_rate     = np.zeros((si.nodes+2, si.nodes+2))

        hopcounts = np.ones(si.nodes+2) * -1

        if GRAPH_EVAL_LIST.count("SN") > 0 or GRAPH_EVAL_LIST.count("ContourGraph") > 0: 
            rtt = Rtt()
            rtt.execute(si)

        f = open(filenamebase+".log", "r")
        for line in f:
            #if (line.find("TrickleSimC: sending") >= 0 and
            #    line.find("packet") >= 0):
            # without switching off node, only count Trickle messages
            if (line.find("TrickleSimC: sending packet") >= 0):
                #print line,

                node_obj = node_re_c.search(line)
                node = int(node_obj.group(1))

                time_obj = time_re_c.search(line)
                #print "\t", time_obj.group(0),
                t = Time(time_obj.group(1),
                         time_obj.group(2),
                         time_obj.group(3))
                #print t.in_second()
                sent_packets[node] += 1

            #if (line.find("TrickleSimC: Received") >= 0 and
            #    line.find("packet from node") >= 0):
            # without switching off node, only count Trickle messages
            if (line.find("TrickleSimC: Received packet from node") >= 0):
                node_obj = node_re_c.search(line)
                rx_node = int(node_obj.group(1))

                rec_node_obj = rec_node_re_c.search(line)
                tx_node = int(rec_node_obj.group(1))

                rec_packets[rx_node][tx_node] += 1

            if line.find("TrickleSimC: Service is received with lower hopcount") >= 0:
                #print line,

                node_obj = node_re_c.search(line)
                node = int(node_obj.group(1))

                hopcount_obj = hopcount_re_c.search(line)
                hopcount = int(hopcount_obj.group(1))

                hopcounts[node] = hopcount

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

        of = open(filenamebase+"_packet.txt", "w")

       # print >> of, "Total number of Sent Packets"
       # print >> of, np.sum(sent_packets)
       # np.save(filenamebase+"_sent_packets.npy", np.sum(sent_packets))

       # print >> of, "Number of Sent Packets individually"
       # print >> of, np.sum(sent_packets)
       # np.save(filenamebase+"_sent_packets_individual.npy", sent_packets)

       # print >> of, "Sent Packets per Node"
       # print >> of, sent_packets
       # np.save(filenamebase+"_sent_packets_per_node.npy", sent_packets)

       # print >> of, "Average Sent Packets per Node"
       # print >> of, np.sum(sent_packets)/float(si.nodes)
       # np.save(filenamebase+"_average_sent_packets_per_node.npy", np.sum(sent_packets)/float(si.nodes) )

       # print >> of, "\nTotal number of Received Packets"
       # print >> of, np.sum(rec_packets)
       # np.save(filenamebase+"_received_packets.npy", np.sum(rec_packets))

       # print >> of, "Received Packets per Node"
       # print >> of, rec_packets
       # np.save(filenamebase+"_received_packets_per_node.npy", rec_packets)

       # print >> of, "Average Received Packets per Node"
       # print >> of, np.sum(rec_packets)/float(si.nodes)
       # np.save(filenamebase+"_average_received_packets_per_node.npy", np.sum(rec_packets)/float(si.nodes))

        np.set_printoptions(threshold=np.nan)
        print >> of, "\nPRR"
        print >> of, prr_rate
        np.save(filenamebase+"_prr.npy", prr_rate)

       # print >> of, "Received/Sent Ratio"
       # print >> of, (np.sum(rec_packets)-1)/float(np.sum(sent_packets))

       # print >> of, "\n\nReceived Hop Count"
       # print >> of, hopcounts
       # np.save(filenamebase+"_hopcounts.npy", hopcounts)

        of.close()
