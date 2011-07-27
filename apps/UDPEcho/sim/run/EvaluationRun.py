#! /usr/bin/python

from optparse import OptionParser

import sys
import traceback
import pickle
import logging
import logging.config

#fix: use agg, otherwise non-interactive machines do not work
import matplotlib
matplotlib.use('agg')

#from sim.evaluation.metric.MetricEvaluation import *
from sim.evaluation.graph.GraphEvaluation import *
from sim.evaluation.graph.topology.TopologyGraph import *
from sim.evaluation.Rtt import *

from sim.config import *

logging.config.fileConfig(LOGFILENAME)
logger = logging.getLogger("evrun")

class EvaluationRun:
    def __init__(self):
        logger.info(">"*10 + " New evaluation run " + "<"*10)

    def execute(self,
     #           ei_file,
                si_file):

     #   ei = pickle.load(open(ei_file, 'rb'))
        si = pickle.load(open(si_file, 'rb'))

        logger.info("="*40)
        logger.info("Executing EvaluationRun:")
        logger.info(str(si))
        logger.info("="*40)

        rtt = Rtt()
        rtt.execute(si)

        if METRIC_EVAL == True:
            me = MetricEvaluation()
      #      me.execute(ei, si)
            me.execute(si)
        else:
            logger.warn("????MetricEvaluation disabled")

        if GRAPH_EVAL == True:
            ge = GraphEvaluation()
            ge.execute(si)
            #me.execute(si)
        else:
            logger.warn("????GraphEvaluation disabled")

if __name__ == "__main__":
    try:
        optparser = OptionParser()

    #    optparser.add_option("-e",
    #                         "--executable_info",
    #                         help="Pickled executable information filename")
        optparser.add_option("-s",
                             "--scenario_info",
                             help="Pickled scenario information filename")

        (optionsp, argsp) = optparser.parse_args()

    #    if not (optionsp.executable_info or
        if not (optionsp.scenario_info):
             optparser.print_help()
             sys.exit(-1)

        er = EvaluationRun()
     #   er.execute(optionsp.executable_info,
     #              optionsp.scenario_info)

        er.execute(optionsp.scenario_info)
     
    except:
        logger.exception("Exception in EvaluationRun.py")
