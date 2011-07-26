import matplotlib
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.text import Text
from matplotlib.figure import SubplotParams
import numpy as np
import re

from sim.utils.helper import *
from sim.scenarios.ScenarioInformation import *
from sim.scenarios.ExecutableInformation import *

NODE_RE = 'DEBUG \((\d+)\):'
NODE_RE_C = re.compile(NODE_RE)
TIME_RE = '(\d+):(\d+):(\d+.\d+)'
TIME_RE_C = re.compile(TIME_RE)

#PERIOD_RE = 'with period (\d+) \((\d+)\) is (\d+) '
#PERIOD_RE = 'Scheduling Trickle event in (\d+) \(period (\d+)\)'
#PERIOD_RE = 'generateTime\(\) \(timer = (\d+), period = (\d+), period/2 = (\d+), start = (\d+), delta = (\d+), hopcount = (\d+)\)'
PERIOD_RE = 'Generated time \[(\d+)\] \(timer = (\d+), period = (\d+), period/2 = (\d+), start = (\d+), delta = (\d+), hopcount = (\d+), old_remainder = (\d+)\)'
PERIOD_RE_C = re.compile(PERIOD_RE)

INJECT_RE = 'Injected msg at node (\d+) at time (\d+):(\d+):(\d+.\d+)'
INJECT_RE_C = re.compile(INJECT_RE)
SHUTTING_RE = 'Shutting off node (\d+) at time (\d+):(\d+):(\d+.\d+)'
SHUTTING_RE_C = re.compile(SHUTTING_RE)

PURGE_RE = 'Resetting purge timer \[(\d+)\] in (\d+)'
PURGE_RE_C = re.compile(PURGE_RE)

TMILLI = 1024

TRICKLE_PERIOD_OFFSET = .05

class TrickleGraph:
    def __init__(self):
        pass

    def parse_node_time(self, line):
        node_obj = NODE_RE_C.search(line)
        node = int(node_obj.group(1))

        time_obj = TIME_RE_C.search(line)
                #print "\t", time_obj.group(0),
        t = Time(time_obj.group(1),
                 time_obj.group(2),
                 time_obj.group(3))
                #print t.in_second()
        return (node, t)

    def execute(self,
                ei,
                si):

        filenamebase = si.createfilenamebase()
        print "="*40
        print "Executing TrickleGraph:"
        print "filenamebase\t\t", filenamebase
        print "="*40

        trickle_period = np.zeros(si.nodes + 2)

        packs = []

        f = open(filenamebase+".log", "r")
        for line in f:

            # node_on_line
            if line.find("Injected msg at") >= 0:

                inject_node_time_obj = INJECT_RE_C.search(line)
                nodeid = inject_node_time_obj.group(1),

                t = Time(inject_node_time_obj.group(2),
                         inject_node_time_obj.group(3),
                         inject_node_time_obj.group(4))

                packs.append(
                    Line2D([t.in_second(), t.in_second()],
                           [0, si.nodes + 2],
                           color='k',
                           linewidth=1,
                           alpha=1)
                    )

                packs.append(
                    Text(t.in_second(),
                         nodeid[0],
#                         (si.nodes +1)/2,
                         'Service at node '+str(nodeid[0])+' appeared',
                         color='k',
                         rotation='vertical',
                         verticalalignment='right',
                         horizontalalignment='right',
                         fontsize = 10,
                         alpha=1)
                    )

            # node_off_line
            if line.find("Shutting off node") >= 0: ## from script, not from code
                # Shutting off node 1 at 0:1:50.021821757
                shutting_node_time_obj = SHUTTING_RE_C.search(line)
                #print "\t", time_obj.group(0),

                nodeid = shutting_node_time_obj.group(1),

                t = Time(shutting_node_time_obj.group(2),
                         shutting_node_time_obj.group(3),
                         shutting_node_time_obj.group(4))
                #print t.in_second()

                packs.append(
                    Line2D([t.in_second(), t.in_second()],
                           [0, si.nodes + 2],
                           color='r',
                           linewidth=1,
                           alpha=1)
                    )

                packs.append(
                    Text(t.in_second(),
                         nodeid[0],
#                         (si.nodes +1 )/2,
                         'Service at node '+str(nodeid[0])+' disappeared',
                         color='k',
                         rotation='vertical',
                         verticalalignment='right',
                         horizontalalignment='right',
                         fontsize = 10,
                         alpha=1)
                    )

            #listenp_line, sendp_line, timer_line
            #if line.find("Scheduling Trickle event in") >= 0:
            if line.find("Generated time") >= 0:
                #print line,

                (node, t) = self.parse_node_time(line)

                period_obj = PERIOD_RE_C.search(line)
                # timer_ms     = int(period_obj.group(1))
                # period_ms    = int(period_obj.group(2))
                # timer_s      = timer_ms/TMILLI
                # period_s      = period_ms/TMILLI

                service_id       = int(period_obj.group(1))
                timer_ms         = int(period_obj.group(2))
                period_ms        = int(period_obj.group(3))
                periodhalf_ms    = int(period_obj.group(4))

                start_ms    = int(period_obj.group(5))
                delta_ms    = int(period_obj.group(6))
                hopcount    = int(period_obj.group(7))
                remainder_ms = int(period_obj.group(8))

                timer_s     = timer_ms/TMILLI
                period_s    = period_ms/TMILLI
                remainder_s = remainder_ms/TMILLI

                start_s     = start_ms/TMILLI
                delta_s     = delta_ms/TMILLI

                trickle_period[node] += 1

                packs.append(
                    Line2D([t.in_second()+remainder_s,
                            t.in_second()+remainder_s+start_s],
                           [node+TRICKLE_PERIOD_OFFSET*trickle_period[node],
                            node+TRICKLE_PERIOD_OFFSET*trickle_period[node]],
                           color='b',
                           linewidth=1,
                           alpha=0.3)
                    )

                packs.append(
                    Line2D([t.in_second()+remainder_s+start_s,
                            t.in_second()+remainder_s+period_s],
                           [node+TRICKLE_PERIOD_OFFSET*trickle_period[node],
                            node+TRICKLE_PERIOD_OFFSET*trickle_period[node]],
                           color='r',
                           linewidth=1,
                           alpha=0.5)
                    )

                #print "t", t.in_second(),
                #print "Timer in seconds?", timer_s,
                #print "-", t.in_second()+timer_s

                packs.append(
                    Line2D([t.in_second()+timer_s, t.in_second()+timer_s],
                           [node+TRICKLE_PERIOD_OFFSET*trickle_period[node]-TRICKLE_PERIOD_OFFSET,
                            node+TRICKLE_PERIOD_OFFSET*trickle_period[node]+TRICKLE_PERIOD_OFFSET],
                           color='g',
                           linewidth=1,
                           alpha=1)
                    )

            #sent_line
            if line.find("TrickleSimC: sending packet") >= 0:
                #print line,

                (node, t) = self.parse_node_time(line)

                packs.append(
                    Line2D([t.in_second(), t.in_second()],
                           [node+.2, node+.2],
                           color='k',
                           marker='^',
                           markeredgewidth=0,
                           markersize=5,
                           linewidth=0,
                           alpha=0.5)
                    )

            #rec_incons_new_line, rec_incons_old_line, cons_line
            if line.find("consistent") >= 0:
                #print line,

                (node, t) = self.parse_node_time(line)

                if line.find("inconsistent") >= 0:
                    if line.find("inconsistent newer") >= 0:
                        packs.append(
                            Line2D([t.in_second(), t.in_second()],
                                   [node+.8, node+.8],
                                   color='r',
                                   marker='v',
                                   markeredgewidth=0,
                                   markersize=5,
                                   linewidth=0,
                                   alpha=0.5)
                            )
                    elif line.find("inconsistent older") >= 0:
                        packs.append(
                            Line2D([t.in_second(), t.in_second()],
                                   [node+.8, node+.8],
                                   color='y',
                                   marker='v',
                                   markeredgewidth=0,
                                   markersize=5,
                                   linewidth=0,
                                   alpha=0.5)
                            )
                else: #consistent
                     packs.append(
                         Line2D([t.in_second(), t.in_second()],
                                [node+.8, node+.8],
                                color='g',
                                marker='v',
                                markersize=5,
                                markeredgewidth=0,
                                linewidth=0,
                                alpha=0.5)
                         )


            #TODO: rename purge to vanish Detection
            #purge_timer_line
            if line.find("Resetting vanishDetection timer") >= 0:
                #print line,

                (node, t) = self.parse_node_time(line)

                purge_obj = PURGE_RE_C.search(line)
                service_id   = int(purge_obj.group(1))
                timer_ms     = int(purge_obj.group(2))
                timer_s      = timer_ms/TMILLI

                packs.append(
                    Line2D([t.in_second()+timer_s, t.in_second()+timer_s],
                           [node+TRICKLE_PERIOD_OFFSET*trickle_period[node]-TRICKLE_PERIOD_OFFSET,
                            node+TRICKLE_PERIOD_OFFSET*trickle_period[node]+TRICKLE_PERIOD_OFFSET],
#                           [node, node+1],
                           color='r',
                           linewidth=1,
                           alpha=1)
                    )

            if line.find("TrickleSimC: sending check packet") >= 0:
                #print line,

                (node, t) = self.parse_node_time(line)

                packs.append(
                    Line2D([t.in_second(), t.in_second()],
                           [node+.2, node+.2],
                           color='y',
                           marker='^',
                           markeredgewidth=0,
                           markersize=3,
                           linewidth=0,
                           alpha=0.2)
                    )

            if line.find("TrickleSimC: sending reply packet") >= 0:
                #print line,

                (node, t) = self.parse_node_time(line)

                packs.append(
                    Line2D([t.in_second(), t.in_second()],
                           [node+.2, node+.2],
                           color='g',
                           marker='^',
                           markeredgewidth=0,
                           markersize=5,
                           linewidth=0,
                           alpha=0.2)
                    )

            #purged_line
#            if line.find("TrickleSimC: service purged (hopcount was") >= 0:
            if (line.find("TrickleSimC: Received flood vanish packet") >= 0 or
                line.find("TrickleSimC: sending flood vanish packet") >= 0):
                #print line,

                (node, t) = self.parse_node_time(line)

                packs.append(
                    Line2D([t.in_second(), t.in_second()],
                           [node+.8, node+.8],
                           color='r',
                           marker='d',
                           markersize=3,
                           markeredgewidth=0,
                           linewidth=0,
                           alpha=0.2)
                    )

            if (line.find("TrickleSimC: forwarding vanish") >= 0 or
                line.find("TrickleSimC: sending flood vanish packet") >= 0):

                (node, t) = self.parse_node_time(line)

                if line.find("TrickleSimC: forwarding vanish") >= 0:
                    tricolor = 'b'
                elif line.find("TrickleSimC: sending flood vanish packet") >= 0:
                    tricolor = 'r'
                else:
                    tricolor = 'k'

                packs.append(
                    Line2D([t.in_second(), t.in_second()],
                           [node+.2, node+.2],
                           color=tricolor,
                           marker='^',
                           markeredgewidth=0,
                           markersize=3,
                           linewidth=0,
                           alpha=0.2)
                    )

            #TODO:
            #if line.find("TrickleSimC: sending check packet") >= 0:
            #if line.find("TrickleSimC: sending reply packet") >= 0:

        f.close()

        fig = plt.figure(figsize=(12, 8),
                         subplotpars = SubplotParams(left = 0.05,
                                                     bottom = 0.05,
                                                     top = 0.93,
                                                     right = 0.77))
        ax = fig.add_subplot(111,
#                             axes = Axes(fig, [.1, .1, .7, .7]),
#                             adjustable = 'datalim',
#                             autoscale_on = 'True'
                             )

        for p in packs:
            ax.add_artist(p)
            p.set_clip_box(ax.bbox)

        ax.set_xlim(0,
                    ei.defines["INJECT_TIME"]/1024+
                    si.sec_after_inject+5)
        ax.set_ylim(1, si.nodes+2)

        if math.sqrt(si.nodes) < 10:
            ax.set_yticks(range(1, si.nodes+2))
        else:
            ax.set_yticks(range(1, si.nodes+2, 10))

        ax.set_xticks(range(0,
                            ei.defines["INJECT_TIME"]/1024+si.sec_after_inject+5,
                            60))

        ax.set_xlabel('Model time [s]')
        ax.set_ylabel('Node ID')

        text = "#Nodes: " + str(si.nodes) + ", " \
            "Distance: " + str(si.distance) + ", " + \
            "K: " + str(ei.defines["DISTRIBUTION_TRICKLE_K"])
        title = 'Trickle Scatter \n(' + text + ')'
        plt.title(title)

        listenp_line = Line2D([0, 1],
                              [0, 1],
                              color='b',
                              linewidth=1,
                              alpha=0.3)

        sendp_line = Line2D([0, 1],
                            [0, 1],
                            color='r',
                            linewidth=1,
                            alpha=0.5)

        timer_line = Line2D([0, 1],
                            [0, 1],
                            color='g',
                            linewidth=1)

        sent_line = Line2D([0, 1],
                           [0, 1],
                           color='k',
                           marker='^',
                           markeredgewidth=0,
                           markersize=5,
                           linewidth=0,
                           alpha=0.5)

        rec_incons_new_line = Line2D([0, 1],
                                     [0, 1],
                                     color='r',
                                     marker='v',
                                     markeredgewidth=0,
                                     markersize=5,
                                     linewidth=0,
                                     alpha=0.5)

        rec_incons_old_line = Line2D([0, 1],
                                     [0, 1],
                                     color='y',
                                     marker='v',
                                     markeredgewidth=0,
                                     markersize=5,
                                     linewidth=0,
                                     alpha=0.5)

        cons_line = Line2D([0, 1],
                           [0, 1],
                           color='g',
                           marker='v',
                           markeredgewidth=0,
                           markersize=5,
                           linewidth=0,
                           alpha=0.5)

        purge_timer_line = Line2D([0, 1],
                                  [0, 1],
                                  color='r',
                                  linewidth=1,
                                  alpha=1)

        purged_line = Line2D([0, 1],
                             [0, 1],
                             color='r',
                             marker='d',
                             markersize=3,
                             markeredgewidth=0,
                             linewidth=0,
                             alpha=0.2)

        check_line = Line2D([0, 1],
                            [0, 1],
                            color='y',
                            marker='^',
                            markersize=3,
                            markeredgewidth=0,
                            linewidth=0,
                            alpha=0.2)

        check_reply_line = Line2D([0, 1],
                                  [0, 1],
                                  color='g',
                                  marker='^',
                                  markersize=3,
                                  markeredgewidth=0,
                                  linewidth=0,
                                  alpha=0.2)

        purge_sent_line = Line2D([0, 1],
                                 [0, 1],
                                 color='r',
                                 marker='^',
                                 markersize=3,
                                 markeredgewidth=0,
                                 linewidth=0,
                                 alpha=0.2)

        purge_forwarded_line = Line2D([0, 1],
                                      [0, 1],
                                      color='b',
                                      marker='^',
                                      markersize=3,
                                      markeredgewidth=0,
                                      linewidth=0,
                                      alpha=0.2)

        node_on_line = Line2D([0, 1],
                              [0, 1],
                              color='k',
                              markeredgewidth=0,
                              linewidth=2,
                              alpha=1)

        node_off_line = Line2D([0, 1],
                               [0, 1],
                               color='r',
                               markeredgewidth=0,
                               linewidth=2,
                               alpha=1)

        plt.legend( (listenp_line,
                     sendp_line,
                     timer_line,
                     sent_line,
                     rec_incons_new_line,
                     rec_incons_old_line,
                     cons_line,
                     purge_timer_line,
                     purged_line,
                     check_line,
                     check_reply_line,
                     purge_sent_line,
                     purge_forwarded_line,
                     ),
                    ('Listen Period',
                     'Send Period',
                     'Timer',
                     'Trickle Sent',
                     'Inconsistent\nReceived (New)',
                     'Inconsistent\nReceived (Old)',
                     'Consistent\nReceived',
                     'Purge Timer',
                     'Purged',
                     'Check Sent',
                     'Check Reply Sent',
                     'Purge Sent',
                     'Purge Forwarded',
                     ),
#                       'lower right',
                    bbox_to_anchor=(1.02, 1),
                    loc = 2,
                    borderaxespad=0. ,
#                       loc = (.9, .5),
                    fancybox = 'True')

        try:
            plt.grid(markevery=1)
        except:
            plt.grid()
        #plt.savefig(filenamebase+"_trickle.png")
        plt.savefig(filenamebase+"_trickle.pdf")
        print "#Periods:", trickle_period
