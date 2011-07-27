#! /usr/bin/python

import numpy as np
from optparse import OptionParser
from sim.scenarios.ScenarioInformation import *

if __name__ == "__main__":
    optparser = OptionParser()
    optparser.add_option("-s",
                         "--suite")
    (optionsp, argsp) = optparser.parse_args()

    if optionsp.suite == None:
        print "Usage: python sim/utils/load_numpy.py -s <suite>"
    else:
        exec "from sim.output.suite_"+optionsp.suite+".config import *"
        print DISTANCE_LIST
        print SQR_NODES_LIST


        for nodes in SQR_NODES_LIST:
            print ">NODES:", nodes
            for distance in DISTANCE_LIST:
                print ">>DISTANCE:", distance, distance*nodes

                #stub_si = ScenarioInformation(optionsp.suite,
                #                              0, 0, 0, 0, 0, 0, 0)
                #print stub_si

                filename = "sim/output/suite_" + \
                    optionsp.suite + \
                    "/topo_" + str(nodes) + "_" + str(nodes) + \
                    "/dist_" + str(distance*nodes) + \
                    "/file_suite" + optionsp.suite + \
                    "_topo" + str(nodes) + "_" + str(nodes) + \
                    "_dist" + str(distance*nodes) + \
                    "_neighbors_min.npy"
                #print filename

                obj = np.load(filename, "r")
                print obj
#                 print "   ", obj[1:][1:]
#                 print "   ", obj[2:][2:]
#                 print "   ", obj[1:]
#                print "   ", obj[2:]
#                 print "   ", np.mean(obj[1:][1:])
#                 print "   ", np.mean(obj[2:][2:])
                print "   ", np.mean(obj[1:])
                print "   ", np.mean(obj[2:])
