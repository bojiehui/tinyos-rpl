#! /usr/bin/python

from optparse import OptionParser

import sys
import traceback
import binascii

from TOSSIM import *
from tinyos.tossim.TossimApp import *

from sim.TrickleSimMsg import *
from sim.config import *
#from sim.scenarios.RegularScenario import Scenario
from sim.scenarios.RegularScenarioWithPropagationModel import Scenario
from datetime import datetime

class NeighborCalculation:
    def __init__(self):
        print ">"*10, "New simulation run", "<"*10
        self.t = Tossim([])
        self.t.setTime(0)
        self.t.init()
        #self.sf = SerialForwarder(9001)

        print "Start model time:", self.t.timeStr()

    def execute(self, sqr_nodes, connectivity,
                randomize_boot, randomize_seed,
                sec_before_inject, sec_after_inject,
                inject_node,
                turn_off_time,
                distance,
                filenamebase):

        starttime = datetime.now()

        logfilename = filenamebase + "_nc.log"
        print "="*40
        print "Executing NeighborCalculation:"
        print "SQR(nodes)\t\t", sqr_nodes
        print "connectivity\t\t", connectivity
        print "randomize_boot\t\t", randomize_boot
        print "sec_before_inject\t", sec_before_inject
        print "sec_after_inject\t", sec_after_inject
        print "inject_node\t\t", inject_node
        print "turn_off_time\t\t", turn_off_time
        print "distance\t\t", distance
        print "logfilename\t\t", logfilename
        print "="*40

#         # debug channels
#         for ch in stdout_channels:
#             self.t.addChannel(ch, sys.stdout)

#         f = open(logfilename, "w")
#         for ch in file_channels:
#             self.t.addChannel(ch, f)

        #scenario setup
        #s = Scenario(self.t, sqr_nodes)
        #s.setup_radio(connectivity)

        s = Scenario(self.t, sqr_nodes, distance)
        s.setup_radio()
#         s.setup_boot(randomize=randomize_boot, randomseed=randomize_seed)

#         tosroot = os.environ.get("TOSROOT")

#         if tosroot == "":
#             print "TOSROOT not set. export TOSROOT=..."
#             sys.exit(1)

#         #passwd = getpass.getpass()
#         sudo_command = "sudo -b " + tosroot + "/support/sdk/c/blip/driver/ip-driver -c ./sim/serial_tun.conf localhost 9001"
#         print sudo_command

#         out = open("./ip-driver.output.1", "w")
#         err = open("./ip-driver.output.2", "w")

#         args = shlex.split(sudo_command)
#         p = subprocess.Popen(args, stdin=subprocess.PIPE)
#         #p.communicate(passwd)
#         print "Process ID of ip-driver:", p.pid

#         #run
#         while True:
#             self.t.runNextEvent()

#             if self.t.time() > (sec_before_inject + sec_after_inject) * self.t.ticksPerSecond():
#                 print "Finished SimulationRun"
#                 break

#             if (turn_off_time != 0 and
#                 self.t.getNode(inject_node).isOn() and
#                 self.t.time() > turn_off_time * self.t.ticksPerSecond()):
#                 shutting_str = "Shutting off node " + str(inject_node) +" at time " + self.t.timeStr() + "\n"
#                 print shutting_str
#                 f.write("="*20 + "\n")
#                 f.write(shutting_str)
#                 f.write("="*20 + "\n")
#                 self.t.getNode(inject_node).turnOff()

#         print "SimulationRun took", datetime.now()-starttime
#         print "Finish model time:", self.t.timeStr()
#         f.close()

if __name__ == "__main__":
    try:
        optparser = OptionParser()

        optparser.add_option("-s",
                             "--sqr_nodes",
                             type="int",
                             default=2,
                             help="Number of nodes in 1 dimension (Square root of 2D)")

        optparser.add_option("-c",
                             "--connectivity",
                             type="float",
                             default=1,
                             help="Maximum Distance to connect to neighbors.")

        optparser.add_option("-b",
                             "--randomize_boot",
                             action="store_true",
                             help="Randomize the boot sequence.")

        optparser.add_option("-r",
                             "--randomize_seed",
                             action="store_true",
                             help="Randomize the seed sequence.")

        optparser.add_option("-i",
                             "--before-inject",
                             type="float",
                             default=10,
                             help="Seconds to wait before injecting the update.")

        optparser.add_option("-a",
                             "--after-inject",
                             type="float",
                             default=300,
                             help="Seconds to wait after injecting the update.")

        optparser.add_option("-n",
                             "--node",
                             type="int",
                             default=1,
                             help="The node to inject the message at.")

        optparser.add_option("-t",
                             "--turn-off-time",
                             type="float",
                             default=0,
                             help="The node to inject the message at.")

        optparser.add_option("-d",
                             "--distance",
                             type="float",
                             help="Distance between nodes.")

        optparser.add_option("-f",
                             "--filenamebase",
                             action="store",
                             help="The prefix for the output files.")

        (optionsp, argsp) = optparser.parse_args()

        if not optionsp.filenamebase:
            optparser.print_help()
            sys.exit(-1)

        sr = NeighborCalculation()
        sr.execute(optionsp.sqr_nodes,
                   optionsp.connectivity,
                   optionsp.randomize_boot,
                   optionsp.randomize_seed,
                   optionsp.before_inject,
                   optionsp.after_inject,
                   optionsp.node,
                   optionsp.turn_off_time,
                   optionsp.distance,
                   optionsp.filenamebase)
    except:
        traceback.print_exc()
