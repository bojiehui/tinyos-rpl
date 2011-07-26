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

from sim.evaluation.graph.montecarlo.MonteCarloEvaluation import *

from sim.config import *

logging.config.fileConfig(LOGFILENAME)
logger = logging.getLogger("evrun")

class EvaluationRunMonteCarlo:
    def __init__(self):
        logger.info(">"*10 + " New Monte Carlo evaluation run " + "<"*10)

    def execute(self,
                ei_file,
                si_file):

        ei = pickle.load(open(ei_file, 'rb'))
        si = pickle.load(open(si_file, 'rb'))

        logger.info("="*40)
        logger.info("Executing EvaluationRunMonteCarlo:")
        logger.info(str(si))
        logger.info("="*40)

        mce = MonteCarloEvaluation()
        mce.execute(ei, si, MONTE_CARLO_ITERATIONS)


if __name__ == "__main__":
    try:
        optparser = OptionParser()

        optparser.add_option("-e",
                             "--executable_info",
                             help="Pickled executable information filename")
        optparser.add_option("-s",
                             "--scenario_info",
                             help="Pickled scenario information filename")

        (optionsp, argsp) = optparser.parse_args()

        if not (optionsp.executable_info or
                optionsp.scenario_info):
             optparser.print_help()
             sys.exit(-1)

        ermc = EvaluationRunMonteCarlo()
        ermc.execute(optionsp.executable_info,
                     optionsp.scenario_info)

    except:
        logger.exception("Exception in EvaluationRunMonteCarlo.py")
