#!/usr/bin/env python

from __future__ import division
import re, copy
import math

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as col
from matplotlib.figure import SubplotParams

import numpy as np
import scipy.stats as stats

from sim.utils.helper import *
from sim.config import *
from sim.scenarios.ScenarioInformation import *
from sim.scenarios.ExecutableInformation import *

class SuiteEvaluationPackets:
    def __init__(self):
        pass

    def execute(self,
                ei,
                si,
                nodes_list,
                distance_list,
                iterations):

        print "="*40
        print "Executing SuiteEvaluationPackets:"
        print "="*40

        sent_packets = {}
        max_sent_packets = 0

        for nodes in nodes_list:
            sent_packets_sqr = []
            for distance in distance_list:

                suite_si = copy.deepcopy(si)
                suite_si.nodes = nodes
                suite_si.distance = distance#*sqr_nodes

                sent_packets_s_d =  np.load(suite_si.create_montecarlo_filenamebase() + \
                                                "_sent_packets.npy",
                                            "r")
                #print "Sent", sent_packets_s_d, max_sent_packets
                #print suite_si.create_montecarlo_filenamebase() + \
                #    "_sent_packets.npy",

                sent_packets_sqr.append(sent_packets_s_d)
                if sent_packets_s_d > max_sent_packets:
                    max_sent_packets = sent_packets_s_d


            sent_packets[nodes] = sent_packets_sqr
        #print sent_packets

########################
# Simulated packets
########################

        # Figure
        fig = plt.figure(figsize=(12, 8),
                         subplotpars = SubplotParams(left = 0.08,
                                                     bottom = 0.05,
                                                     top = 0.93,
                                                     right = 0.77))
        ax = fig.add_subplot(111)

        my_norm = col.Normalize(math.sqrt(min(nodes_list))-1,
                                math.sqrt(max(nodes_list))+1)

        for nodes in nodes_list:
            #print distance_list, sent_packets[nodes]
            distance_nodes_list = []
            for distance in distance_list:
                distance_nodes_list.append(distance*nodes)

            plt.plot(distance_nodes_list, sent_packets[nodes],
            #plt.plot(distance_list, sent_packets[nodes],
            #plt.semilogy(distance_list, sent_packets[sqr_nodes],
                         marker="s",
                         color=cm.jet(my_norm(math.sqrt(nodes))),
                         ls="-",
                         #markeredgewidth=0,
                         label=str(nodes) + " (simulated)")

            #sent_packets_poly   = np.poly1d(sent_packets_fit)

            # ax^2 + bx + c fitting:
            #sent_packets_fit = np.polyfit(distance_list, sent_packets[sqr_nodes], 2)
            #sent_packets_poly_calc   = [ (sent_packets_fit[0]*pow(x,2) + sent_packets_fit[1]*x + sent_packets_fit[2])   for x in distance_list ]

            # ax + b fitting:
            sent_packets_fit = np.polyfit(distance_nodes_list, sent_packets[nodes], 1)
            sent_packets_poly_calc   = [ (sent_packets_fit[0]*x + sent_packets_fit[1])   for x in distance_nodes_list ]

            plt.plot(distance_nodes_list, sent_packets_poly_calc,
#            plt.semilogy(distance_list, sent_packets_poly_calc,
                         marker="*",
                         color=cm.jet(my_norm(math.sqrt(sqr_nodes))),
                         ls="-",
                         #markeredgewidth=0,
                         label=str(nodes) + " (fitted)")


        text = "K: " + str(ei.defines["DISTRIBUTION_TRICKLE_K"])
        title = '#Packets vs Distance\n(' + text + ')'
        plt.title(title)

        plt.ylim(0, max_sent_packets+100)
        plt.xlim(distance_list[0]*math.sqrt(nodes_list[0])-10,
                 distance_list[-1]*math.sqrt(nodes_list[-1])+10)

        plt.xlabel("Distance [m]")
        plt.ylabel("#Packets")

        plt.legend(bbox_to_anchor=(1.02, 1),
                   loc = 2,
                   borderaxespad=0. ,
#                       loc = (.9, .5),
                   fancybox = 'True')

        plt.savefig(suite_si.create_suite_filenamebase() + "_messages.pdf")

        #Figure
        fig = plt.figure(figsize=(12, 8),
                         subplotpars = SubplotParams(left = 0.08,
                                                     bottom = 0.05,
                                                     top = 0.93,
                                                     right = 0.77))
        #fig = plt.figure(figsize=(10, 8))
        ax = fig.add_subplot(111)

        distance_nodes_list_inv = [ 1/x for x in distance_nodes_list]

        for nodes in nodes_list:
            #print distance_list_inv, sent_packets[nodes]
            plt.plot(distance_nodes_list_inv, sent_packets[nodes],
            #plt.semilogy(distance_list, sent_packets[nodes],
                         marker="s",
                         color=cm.jet(my_norm(math.sqrt(nodes))),
                         ls="-",
                         #markeredgewidth=0,
                         label=str(nodes) + " (simulated)")

        text = "K: " + str(ei.defines["DISTRIBUTION_TRICKLE_K"])
        title = '#Packets vs 1/Distance\n(' + text + ')'
        plt.title(title)

        #plt.ylim(0, max_sent_packets)
        #plt.xlim(distance_list_inv[0]-10, distance_list_inv[-1]+10)

        plt.xlabel("1/Distance [1/m]")
        plt.ylabel("#Packets")

        plt.legend(bbox_to_anchor=(1.02, 1),
                   loc = 2,
                   borderaxespad=0. ,
#                       loc = (.9, .5),
                   fancybox = 'True')

#        plt.legend(loc='upper right')

        plt.savefig(suite_si.create_suite_filenamebase() + "_messages_inv.pdf")


########################
# Neighbors
########################

        neighbors_min  = {}
        neighbors_mean = {}
        neighbors_max  = {}
        for nodes in nodes_list:
            neighbors_min_sqr  = []
            neighbors_mean_sqr = []
            neighbors_max_sqr  = []

            for distance in distance_list:
                suite_si = copy.deepcopy(si)
                suite_si.sqr_nodes = nodes
                suite_si.distance = distance

                neighbors_min_ = np.load(suite_si.create_montecarlo_filenamebase() + \
                                             "_neighbors_min.npy",
                                         "r")
                neighbors_mean_ = np.load(suite_si.create_montecarlo_filenamebase() + \
                                             "_neighbors_mean.npy",
                                         "r")
                neighbors_max_ = np.load(suite_si.create_montecarlo_filenamebase() + \
                                             "_neighbors_max.npy",
                                         "r")

                #neighbors_min_sqr.append(np.mean(neighbors_min_[1:][1:]))
                #neighbors_mean_sqr.append(np.mean(neighbors_mean_[1:][1:]))
                #neighbors_max_sqr.append(np.mean(neighbors_max_[1:][1:]))
                neighbors_min_sqr.append(np.mean(neighbors_min_[2:]))
                neighbors_mean_sqr.append(np.mean(neighbors_mean_[2:]))
                neighbors_max_sqr.append(np.mean(neighbors_max_[2:]))

            neighbors_min[nodes]  = neighbors_min_sqr
            neighbors_mean[nodes] = neighbors_mean_sqr
            neighbors_max[nodes]  = neighbors_max_sqr

        ####################
        #TODO: draw neighbors over distance (schar parameter: nodes)
        #####################

        # Figure
        fig = plt.figure(figsize=(12, 8),
                         subplotpars = SubplotParams(left = 0.08,
                                                     bottom = 0.05,
                                                     top = 0.93,
                                                     right = 0.77))
        ax = fig.add_subplot(111)

        my_norm = col.Normalize(math.sqrt(min(nodes_list))-1,
                                math.sqrt(max(nodes_list))+1)

        for nodes in nodes_list:
            distance_nodes_list = []
            for distance in distance_list:
                distance_nodes_list.append(distance*nodes)

            #print ">>>", nodes, ":", neighbors_min[sqr_nodes]
            plt.plot(distance_nodes_list, neighbors_min[nodes],
                     marker="s",
                     color=cm.jet(my_norm(math.sqrt(nodes))),
                     ls="-",
                     #markeredgewidth=0,
                     label=str(nodes))

            plt.plot(distance_nodes_list, neighbors_mean[nodes],
                     marker="*",
                     color=cm.jet(my_norm(math.sqrt(nodes))),
                     ls="-",
                     #markeredgewidth=0,
                     label=None)
                     #label=str(sqr_nodes)+"x"+str(sqr_nodes)+" mean")

            plt.plot(distance_nodes_list, neighbors_max[nodes],
                     marker="o",
                     color=cm.jet(my_norm(math.sqrt(nodes))),
                     ls="-",
                     #markeredgewidth=0,
                     label=None)
                     #label=str(sqr_nodes)+"x"+str(sqr_nodes)+" max")

        title = 'MEAN(#Neighbors) vs Distance'
        plt.title(title)

        #plt.ylim(0, max_sent_packets)
        #plt.xlim(distance_nodes_list[0]-10, distance_nodes_list[-1]+10)
        plt.xlim(0, distance_nodes_list[-1]+10)

        plt.xlabel("Distance [m]")
        plt.ylabel("MEAN(#Neighbors)")

        plt.legend(bbox_to_anchor=(1.02, 1),
                   loc = 2,
                   borderaxespad=0. ,
                   fancybox = 'True')

        plt.savefig(suite_si.create_suite_filenamebase() + "_neighbors.pdf")

####################
# neighbors_inv

        # Figure
        fig = plt.figure(figsize=(12, 8),
                         subplotpars = SubplotParams(left = 0.08,
                                                     bottom = 0.05,
                                                     top = 0.93,
                                                     right = 0.77))
        ax = fig.add_subplot(111)

        my_norm = col.Normalize(math.sqrt(min(nodes_list))-1,
                                math.sqrt(max(nodes_list))+1)

        neighbors_min_inv  = {}
        neighbors_mean_inv = {}
        neighbors_max_inv  = {}
        for nodes in nodes_list:
            neighbors_min_sqr  = []
            neighbors_mean_sqr = []
            neighbors_max_sqr  = []
            for dist_index in range(0, len(distance_list)):
                #neighbors_min_ = ((nodes)-1)/neighbors_min[nodes][dist_index]
                neighbors_min_ = 1/neighbors_min[nodes][dist_index]
                neighbors_min_sqr.append(neighbors_min_)

                #neighbors_mean_ = ((nodes)-1)/neighbors_mean[nodes][dist_index]
                neighbors_mean_ = 1/neighbors_mean[nodes][dist_index]
                neighbors_mean_sqr.append(neighbors_mean_)

                #neighbors_max_ = ((nodes)-1)/neighbors_max[nodes][dist_index]
                neighbors_max_ = 1/neighbors_max[nodes][dist_index]
                neighbors_max_sqr.append(neighbors_max_)

            neighbors_min_inv[nodes]  = neighbors_min_sqr
            neighbors_mean_inv[nodes] = neighbors_mean_sqr
            neighbors_max_inv[nodes]  = neighbors_max_sqr

        for nodes in nodes_list:
            #print ">>>", distance_list, neighbors_min[nodes]
            plt.plot(distance_list, neighbors_min_inv[nodes],
                     marker="s",
                     color=cm.jet(my_norm(math.sqrt(nodes))),
                     ls="-",
                     #markeredgewidth=0,
                     label=str(nodes))

            plt.plot(distance_list, neighbors_mean_inv[nodes],
                     marker="*",
                     color=cm.jet(my_normmath.sqrt((nodes))),
                     ls="-",
                     #markeredgewidth=0,
                     label=None)
                     #label=str(sqr_nodes)+"x"+str(sqr_nodes))

            plt.plot(distance_list, neighbors_max_inv[nodes],
                     marker="o",
                     color=cm.jet(my_norm(math.sqrt(nodes))),
                     ls="-",
                     #markeredgewidth=0,
                     label=None)
                     #label=str(sqr_nodes)+"x"+str(sqr_nodes))


        #title = '(#Nodes-1)/MEAN(#Neighbors) vs Distance'
        title = '1/MEAN(#Neighbors) vs Distance'
        plt.title(title)

        #plt.ylim(0, max_sent_packets)
        plt.xlim(distance_list[0]-10, distance_list[-1]+10)

        plt.xlabel("Distance [m]")
        plt.ylabel("1/MEAN(#Neighbors)")

        plt.legend(bbox_to_anchor=(1.02, 1),
                   loc = 2,
                   borderaxespad=0. ,
                   fancybox = 'True')

        plt.savefig(suite_si.create_suite_filenamebase() + "_neighbors_inv.pdf")

####################
# packet model
        # Figure
        fig = plt.figure(figsize=(12, 8),
                         subplotpars = SubplotParams(left = 0.08,
                                                     bottom = 0.05,
                                                     top = 0.93,
                                                     right = 0.77))
        ax = fig.add_subplot(111)

        my_norm = col.Normalize(math.sqrt(min(nodes_list))-1,
                                math.sqrt(max(nodes_list))+1)

        #TODO: integrate this here
        c = 15.269110587 # taken from output of sim/analytical.py

        packet_min_inv  = {}
        packet_mean_inv = {}
        packet_max_inv  = {}
        for nodes in nodes_list:
            distance_nodes_list = []
            for distance in distance_list:
                distance_nodes_list.append(distance*math.sqrt(nodes))

            packet_min_sqr  = []
            packet_mean_sqr = []
            packet_max_sqr  = []
            for dist_index in range(0, len(distance_nodes_list)):
                packet_min_ = ei.defines["DISTRIBUTION_TRICKLE_K"]*c*nodes*neighbors_min_inv[nodes][dist_index]
                packet_min_sqr.append(packet_min_)

                packet_mean_ = ei.defines["DISTRIBUTION_TRICKLE_K"]*c*nodes*nodes*neighbors_mean_inv[nodes][dist_index]
                packet_mean_sqr.append(packet_mean_)

                packet_max_ = ei.defines["DISTRIBUTION_TRICKLE_K"]*c*nodes*neighbors_max_inv[nodes][dist_index]
                packet_max_sqr.append(packet_max_)
            packet_min_inv[nodes]  = packet_min_sqr
            packet_mean_inv[nodes] = packet_mean_sqr
            packet_max_inv[nodes]  = packet_max_sqr


        for nodes in nodes_list:
            #print ">>>", distance_list, neighbors_min[nodes]
            distance_nodes_list = []
            for distance in distance_list:
                distance_nodes_list.append(distance*math.sqrt(nodes))

            plt.plot(distance_nodes_list, packet_min_inv[nodes],
                     marker="s",
                     color=cm.jet(my_norm(math.sqrt(nodes))),
                     ls="-",
                     #markeredgewidth=0,
                     label=str(nodes))

            plt.plot(distance_nodes_list, packet_mean_inv[nodes],
                     marker="*",
                     color=cm.jet(my_norm(math.sqrt(nodes))),
                     ls="-",
                     #markeredgewidth=0,
                     label=None)
                     #label=str(sqr_nodes)+"x"+str(sqr_nodes))

            plt.plot(distance_nodes_list, packet_max_inv[nodes],
                     marker="o",
                     color=cm.jet(my_norm(math.sqrt(nodes))),
                     ls="-",
                     #markeredgewidth=0,
                     label=None)
                     #label=str(sqr_nodes)+"x"+str(sqr_nodes))


        title = '#Packets (Modeled) vs Distance'
        plt.title(title)

        #plt.ylim(0, max_sent_packets)
        #plt.xlim(distance_list[0]-10, distance_list[-1]+10)
        #plt.xlim(0, distance_list[-1]+10)
        plt.xlim(0, distance_list[-1]*math.sqrt(nodes_list[-1])+10)

        plt.xlabel("Distance [m]")
        plt.ylabel("#Packets (modeled)")

        plt.legend(bbox_to_anchor=(1.02, 1),
                   loc = 2,
                   borderaxespad=0. ,
                   fancybox = 'True')

        plt.savefig(suite_si.create_suite_filenamebase() + "_messages_modeled.pdf")

##################################
# Comparison simulation <-> model
##################################

        # Figure
        fig = plt.figure(figsize=(12, 8),
                         subplotpars = SubplotParams(left = 0.08,
                                                     bottom = 0.05,
                                                     top = 0.93,
                                                     right = 0.77))
        ax = fig.add_subplot(111)

        my_norm = col.Normalize(math.sqrt(min(nodes_list))-1,
                                mqth.sqrt(max(nodes_list))+1)

        for nodes in nodes_list:
            distance_nodes_list = []
            for distance in distance_list:
                distance_nodes_list.append(distance*math.sqrt(nodes))

            plt.plot(distance_nodes_list, sent_packets[nodes],
                     marker="x",
                     color=cm.jet(my_norm(math.sqrt(nodes))),
                     ls="-",
                     label=str(nodes))
            plt.plot(distance_nodes_list, packet_min_inv[nodes],
                     marker="s",
                     color=cm.jet(my_norm(math.sqrt(nodes))),
                     ls=":")
            plt.plot(distance_nodes_list, packet_mean_inv[nodes],
                     marker="*",
                     color=cm.jet(my_norm(math.sqrt(nodes))),
                     ls=":")
            plt.plot(distance_nodes_list, packet_max_inv[nodes],
                     marker="o",
                     color=cm.jet(my_norm(math.sqrt(nodes))),
                     ls=":")

        text = "K: " + str(ei.defines["DISTRIBUTION_TRICKLE_K"])
        title = '#Packets vs Distance\n(' + text + ')'
        plt.title(title)

        plt.ylim(0, max_sent_packets+100)
        plt.xlim(distance_list[0]*math.sqrt(nodes_list[0])-10,
                 distance_list[-1]*math.sqrt(nodes_list[-1])+10)

        plt.xlabel("Distance [m]")
        plt.ylabel("#Packets")

        plt.legend(bbox_to_anchor=(1.02, 1),
                   loc = 2,
                   borderaxespad=0. ,
#                       loc = (.9, .5),
                   fancybox = 'True')

        plt.savefig(suite_si.create_suite_filenamebase() + "_messages_comp_sim_model.pdf")

##################################
# Comparison simulation <-> model (individual)
##################################


        for nodes in nodes_list:
            # Figure
            fig = plt.figure(figsize=(12, 8),
                             subplotpars = SubplotParams(left = 0.08,
                                                         bottom = 0.05,
                                                         top = 0.93,
                                                         right = 0.77))
            ax = fig.add_subplot(111)

            my_norm = col.Normalize(math.sqrt(min(nodes_list))-1,
                                    math.sqrt(max(nodes_list))+1)

            distance_nodes_list = []
            for distance in distance_list:
                distance_nodes_list.append(distance*math.sqrt(nodes))

            plt.plot(distance_nodes_list, sent_packets[nodes],
                     marker="x",
                     color=cm.jet(my_norm(math.sqrt(nodes))),
                     ls="-",
                     label=str(nodes)+" (simulated)")

            plt.plot(distance_nodes_list, packet_min_inv[nodes],
                     marker="s",
                     color=cm.jet(my_norm(math.sqrt(nodes))),
                     ls=":",
                     label=str(nodes)+" (modeled, min)")
            plt.plot(distance_nodes_list, packet_mean_inv[nodes],
                     marker="*",
                     color=cm.jet(my_norm(math.sqrt(nodes))),
                     ls=":",
                     label=str(nodes)+" (modeled, mean)")
            plt.plot(distance_nodes_list, packet_max_inv[nodes],
                     marker="o",
                     color=cm.jet(my_norm(math.sqrt(nodes))),
                     ls=":",
                     label=str(nodes)+" (modeled, max)")

            text = "K: " + str(ei.defines["DISTRIBUTION_TRICKLE_K"])
            title = '#Packets vs Distance\n(' + text + ')'
            plt.title(title)

            plt.ylim(0, max_sent_packets+100)
            plt.xlim(distance_list[0]*math.sqrt(nodes_list[0])-10,
                     distance_list[-1]*math.sqrt(nodes_list[-1])+10)

            plt.xlabel("Distance [m]")
            plt.ylabel("#Packets")

            plt.legend(bbox_to_anchor=(1.02, 1),
                       loc = 2,
                       borderaxespad=0. ,
                       fancybox = 'True')

            plt.savefig(suite_si.create_suite_filenamebase() + "_messages_comp_sim_model_"+str(nodes)+".pdf")

