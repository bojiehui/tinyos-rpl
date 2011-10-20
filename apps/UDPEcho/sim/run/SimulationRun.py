#! /usr/bin/python

from optparse import OptionParser

import sys
import time
import os
import traceback
import getpass
import subprocess
import shlex
import binascii
from datetime import datetime
import pickle
import logging
import logging.config

from TOSSIM import *
from tinyos.tossim.TossimApp import *

from sim.config import *

from sim.scenarios.Scenario import Scenario
from sim.scenarios.GridScenario import *
from sim.scenarios.DirectNeighborGridScenario import *
from sim.scenarios.RandomScenario import *
from sim.scenarios.LineScenario import *
from sim.scenarios.DirectNeighborLineScenario import *
from sim.scenarios.ContainerScenario import *

logging.config.fileConfig(LOGFILENAME)
logger = logging.getLogger("simrun")

class SimulationRun:
    def __init__(self):
        try:
            logger.info(">"*10 + " New simulation run " + "<"*10)

            self.t = Tossim([])
            self.t.setTime(0)
            self.t.init()
            logger.info("Start model time: " + self.t.timeStr())
        except:
            logger.exception("Exception in SimulationRun.py")

    def execute(self,
                si_file):

        logger.info("Loading scenario information.")
        si = pickle.load(open(si_file, 'rb'))

        starttime = datetime.now()

        filenamebase = si.createfilenamebase()
        logfilename = filenamebase + ".log"
        logger.info("="*40)
        logger.info("Executing SimulationRun:")
        logger.info(str(si))
        logger.info("="*40)

        # debug channels
        for ch in stdout_channels:
            self.t.addChannel(ch, sys.stdout)

        f = open(logfilename, "w")
        for ch in file_channels:
            self.t.addChannel(ch, f)

        #scenario setup
	logger.info("Scenario = " + SCENARIO)
        if SCENARIO == "GridScenario":
            s = GridScenario(self.t, si)
        elif SCENARIO == "DirectNeighborGridScenario":
            s = DirectNeighborGridScenario(self.t, si)
        elif SCENARIO == "RandomScenario":
            s = RandomScenario(self.t, si)
        elif SCENARIO == "LineScenario":
            s = LineScenario(self.t, si)
        elif SCENARIO == "ContainerScenario":
            s = ContainerScenario(self.t, si)
        elif SCENARIO == "DirectNeighborLineScenario":
            s = DirectNeighborLineScenario(self.t, si)
        elif SCENARIO == "MoteLabConnectivityScenario":
            s = MoteLabConnectivityScenario(self.t, si)
        else:
            raise Exception("No supported scenario configured. Check run/SimulationRun.py")
 
        s.setup_radio()
        s.setup_boot(randomize=si.randomize_boot,
                     randomseed=si.randomize_seed)

        tosroot = os.environ.get("TOSROOT")

        if tosroot == "":
            logger.error("TOSROOT not set. export TOSROOT=...")
            sys.exit(1)

        #run
        
        print "-"*10, "[[[[ Starting simulation of blip ]]]]", "-"*10

        if SIM_REALTIME:
            eventCtr = 0
            eventPresent = True

            sleepDelta = 0.00001

            clockStartTime = datetime.now()
            simStartTime   = self.t.time()

            try:
                
                while True:

                    clockCurrentTime = datetime.now()
                    clockTimeDifference = clockCurrentTime - clockStartTime
                    clockTimeDifferenceSec = (clockTimeDifference.seconds + clockTimeDifference.microseconds / float(1000000))
                    simCurrentTimeSec   = self.t.time() / float(self.t.ticksPerSecond())
                    sleepTime = simCurrentTimeSec - clockTimeDifferenceSec
                    
                    while sleepTime > 0:
                        time.sleep(sleepDelta)
                        sleepTime -= sleepDelta
                            
                    eventPresent = self.t.runNextEvent()
                    eventCtr = eventCtr + 1
            
            except KeyboardInterrupt:
                print ">>> Ctrl-C"

            except:
                traceback.print_exc()
                print ">>> Exception while simulating."
        else:
            print ">>> No realtime simulation."
            sim_time = SIM_TIME * self.t.ticksPerSecond() + self.t.time()
            simStartTime   = self.t.time()
            self.t.runNextEvent();

            while (sim_time > self.t.time()):
                self.t.runNextEvent()
   
                
       # finally:
            #throttle.finalize()
            #throttle.printStatistics()
       #	     pass

        logger.info("SimulationRun took: " + str(datetime.now()-starttime))
        logger.info("Finish model time: " + self.t.timeStr())
        f.close()

if __name__ == "__main__":
    try:
        optparser = OptionParser()

#       optparser.add_option("-e",
#                            "--executable_info",
#                            help="Pickled executable information filename")
        optparser.add_option("-s",
                             "--scenario_info",
                             help="Pickled scenario information filename")

        (optionsp, argsp) = optparser.parse_args()

        if not (optionsp.scenario_info):
            optparser.print_help()
            logger.error(">"*10 + " Option parsing failed " + "<"*10)
            sys.exit(-1)

        sr = SimulationRun()
#       sr.execute(optionsp.executable_info,
        sr.execute(optionsp.scenario_info)
        logger.info(">"*10 + " Simulation run finished " + "<"*10)
    except:
        logger.exception("Exception in SimulationRun.py")
