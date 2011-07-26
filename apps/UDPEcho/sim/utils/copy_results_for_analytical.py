#!/usr/bin/python

import os
from optparse import OptionParser

if __name__ == "__main__":
    usage = "usage: %prog [options]"
    optparser = OptionParser(usage=usage)
    optparser.add_option("-r",
                         "--remote",
                         action="store", type="string",
                         help="remote user and host to copy from (e.g. mab@america:/home/mab/src/git/tinyos-2.x-contrib/uob/apps/TrickleSim )")
    optparser.add_option("-s",
                         "--suite",
                         action="store", type="string",
                         help="which suite to copy (e.g. 2011_02_17__09_22_22)")
    (optionsp, argsp) = optparser.parse_args()


    if optionsp.remote == None or optionsp.suite == None:
        optparser.print_help()
    else:
        simoutputpath = "sim/output/suite_"+optionsp.suite+"/"

        try:
            os.mkdir(simoutputpath)
            initfile = open(simoutputpath+"__init__.py", "w")
            initfile.write("")
            initfile.close()
        except OSError:
            print "Output directory already present."

        command = "scp "+optionsp.remote+"/"+simoutputpath+"config.py "+simoutputpath
        print "Executing:", command
        os.system(command)

        #print "from sim.output.suite_"+optionsp.suite+".config import *"
        exec "from sim.output.suite_"+optionsp.suite+".config import *"

        command = "scp "+optionsp.remote+"/"+simoutputpath+"executable_info.pickle "+simoutputpath
        print "Executing:", command
        os.system(command)

        command = "scp "+optionsp.remote+"/"+simoutputpath+"scenario_info.pickle "+simoutputpath
        print "Executing:", command
        os.system(command)


        for nodes in NODES_LIST:
            for distance in DISTANCE_LIST:

                dirname = "sim/output/suite_" + optionsp.suite + \
                    "/topo_" + str(nodes) + \
                    "/dist_" + str(distance) + "/"

                filename = "file_suite" + optionsp.suite + \
                    "_topo" + str(nodes) + \
                    "_dist" + str(distance)

                try:
                    os.makedirs(dirname+"run_0/")
                except OSError:
                    print "Output directory already present:", dirname+"run_0/"

                command = "scp "+optionsp.remote+"/"+dirname+filename+"_hist_consist_avail.npy"+" "+dirname
                print "Executing:", command
                os.system(command)

                command = "scp "+optionsp.remote+"/"+dirname+"run_0/"+filename+"_run0_id2xy.pickle"+" "+dirname+"run_0/"
                print "Executing:", command
                os.system(command)
