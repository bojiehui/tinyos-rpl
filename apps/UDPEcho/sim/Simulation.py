#! /usr/bin/python

print "~"*40
print "UDPEcho"
print "~"*40

import os, sys

from optparse import OptionParser

from datetime import datetime
import pickle
import shutil
import smtplib
import logging
import logging.config
import time

from sim.scenarios.ScenarioInformation import *

from sim.config import *

logging.config.fileConfig(LOGFILENAME)
logger = logging.getLogger("suite")

logger.info("")
logger.info("")
logger.info("")

class SimulationSuite:
    def __init__(self, startdate):
        if startdate == None:
            self.startdate = datetime.now().strftime("%Y_%m_%d__%H_%M_%S")
        else:
            self.startdate = startdate
	print "Start date", self.startdate

        self.stub_si = ScenarioInformation(self.startdate,
                                           0, 0, 0, 0, 0)

        if startdate == None:
            os.makedirs(self.stub_si.get_suite_full_dir())

            shutil.copy("./_TOSSIMmodule.so", self.stub_si.get_suite_full_dir())
            shutil.copy("./TOSSIM.py", self.stub_si.get_suite_full_dir())
            shutil.copy("./sim/config.py", self.stub_si.get_suite_full_dir())
            shutil.copy("./sim/__init__.py", self.stub_si.get_suite_full_dir())

    def execute(self):
        for nodes in NODES_LIST:
            for distance in DISTANCE_LIST:
                for run in range(0, MONTE_CARLO_ITERATIONS):
                    logger.info(">"*5 + "setting up simulation " + \
                                    str(nodes) + " " + \
                                    str(distance) + " " + \
                                    str(run))

                    si = ScenarioInformation(self.startdate,
                                             run,
                                             nodes,
                                             distance,
                                             RANDOMIZE_BOOT,
                                             RANDOMIZE_SEED)
                    os.makedirs(si.get_full_dir())
                    pickle.dump(si, open(si.get_suite_full_dir()+'scenario_info.pickle', 'wb'))

                    cmd = "python sim/run/SimulationRun.py"+" -s " + si.get_suite_full_dir()+"scenario_info.pickle"

                    logger.info("*"*5 + " Executing: " + cmd)
                    os.system(cmd)
                    logger.info("~"*5 + " Done executing: " + cmd)
                    time.sleep(1.0)

    def evaluate(self):
        if ((METRIC_EVAL == True) or (GRAPH_EVAL == True)):
            for nodes in NODES_LIST:
                for distance in DISTANCE_LIST:
                    for run in range(0, MONTE_CARLO_ITERATIONS):
                        logger.info(">"*5 + "setting up evaluation " + \
                                        str(nodes) + " " + \
                                        str(distance) + " " + \
                                        str(run))

                        si = ScenarioInformation(self.startdate,
                                                 run,
                                                 nodes,
                                                 distance,
                                                 RANDOMIZE_BOOT,
                                                 RANDOMIZE_SEED)

                        #os.makedirs(si.get_full_dir())
                        pickle.dump(si, open(si.get_suite_full_dir()+'scenario_info_run.pickle', 'wb'))

                        cmd = "python sim/run/EvaluationRun.py" + " -s " + si.get_suite_full_dir()+"scenario_info_run.pickle"

                        logger.info("*"*5 + " Evaluating: " + cmd)
                        os.system(cmd)
                        logger.info("~"*5 + " Done evaluating: " + cmd)

                    if (MONTECARLO_EVAL == True):
                        mc_si = ScenarioInformation(self.startdate,
                                                    0,
                                                    nodes,
                                                    distance,
                                                    RANDOMIZE_BOOT,
                                                    RANDOMIZE_SEED)

                        #os.makedirs(mc_si.get_full_dir())
                        pickle.dump(mc_si, open(mc_si.get_suite_full_dir()+'scenario_info_mc.pickle', 'wb'))

                        cmd = "python sim/run/EvaluationRunMonteCarlo.py" \
                            + " -s " + mc_si.get_suite_full_dir()+"scenario_info_mc.pickle"

                        logger.info("*"*5 + " Evaluating (Monte Carlo): " + cmd)
                        os.system(cmd)
                        logger.info("~"*5 + " Done evaluating (Monte Carlo): " + cmd)

        if (SUITE_EVAL == True):
            suite_si = ScenarioInformation(self.startdate,
                                           0,
                                           0,
                                           0,
                                           RANDOMIZE_BOOT,
                                           RANDOMIZE_SEED)

            #os.makedirs(suite_si.get_full_dir())
            pickle.dump(suite_si, open(suite_si.get_suite_full_dir()+'scenario_info_suite.pickle', 'wb'))

            cmd = "python sim/run/EvaluationSuite.py" \
                + " -s " + suite_si.get_suite_full_dir()+"scenario_info_suite.pickle"

            logger.info("*"*5 + " Evaluating (Suite): " + cmd)
            os.system(cmd)
            logger.info("~"*5 + " Done evaluating (Suite): " + cmd)



if __name__ == "__main__":
    optparser = OptionParser()
    optparser.add_option("-s",
                         "--simulation",
                         action="store_true",
                         default=False,
                         help="Just do simulation")

    optparser.add_option("-e",
                         "--evaluation",
                         action="store_true",
                         default=False,
                         help="Just do the evaluation (based on data from previous run)")

    optparser.add_option("-d",
                         "--datetime",
                         help="If only evaluation is done, specify the datetime in the format 2010_08_24__15_30_00''.")

    (optionsp, argsp) = optparser.parse_args()

    ss = SimulationSuite(optionsp.datetime)

    if not optionsp.simulation and not optionsp.evaluation:
        optionsp.simulation = True
        optionsp.evaluation = True

    if optionsp.simulation:
        logger.info("*"*10+" Starting Simulations")
        ss.execute()
        logger.info("~"*10+" Finished Simulations")

    if optionsp.evaluation:
        logger.info("*"*10+" Starting Evaluation")
        ss.evaluate()
        logger.info("~"*10+" Finished Evaluation")

    if optionsp.datetime == None:
        ff = open(ss.stub_si.get_suite_full_dir()+"finishtime_"+ datetime.now().strftime("%Y_%m_%d__%H_%M_%S"), "w")
        ff.close()

    logger.info("~"*40+" Finished Suite")

    logger.info("")
    logger.info("")
