import logging
import logging.config

from sim.evaluation.graph.contour.MonteCarloContourGraph import *
from sim.evaluation.graph.contour.MonteCarloContourGraphPacketLoss import *
from sim.evaluation.graph.contour.MonteCarloContourGraphSentICMP import *
from sim.evaluation.graph.hist.MonteCarloHistGraph import *

from sim.utils.helper import *
from sim.config import *

logging.config.fileConfig(LOGFILENAME)
logger = logging.getLogger("evrun")

class MonteCarloEvaluation:
    def __init__(self):
        pass

    def execute(self,
#                executable_info,
                scenario_info,
                iterations):

        logger.info("="*40)
        logger.info("Executing MonteCarloEvaluation:")
        logger.info("="*40)

        if MONTECARLO_EVAL_LIST.count("MonteCarloContourGraph") > 0:
            mccg = MonteCarloContourGraph()
            mccg.execute(scenario_info, iterations)
        else:
            logger.warn("????MonteCarloContourGraph evaluation disabled")

        if MONTECARLO_EVAL_LIST.count("MonteCarloContourGraphPacketLoss") > 0:
            mccgp = MonteCarloContourGraphPacketLoss()
            mccgp.execute(scenario_info, iterations)
        else:
            logger.warn("????MonteCarloContourGraphPacketloss evaluation disabled")


        if MONTECARLO_EVAL_LIST.count("MonteCarloContourGraphSentICMP") > 0:
            mccgsi = MonteCarloContourGraphSentICMP()
            mccgsi.execute(scenario_info, iterations)
        else:
            logger.warn("????MonteCarloContourGraphSentICMP evaluation disabled")

        if MONTECARLO_EVAL_LIST.count("MonteCarloHistGraph") > 0:
            mchg = MonteCarloHistGraph()
            mchg.execute(scenario_info, iterations)
        else:
            logger.warn("????MonteCarloHistGraph evaluation disabled")
