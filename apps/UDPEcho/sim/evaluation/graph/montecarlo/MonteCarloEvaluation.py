import logging
import logging.config

from sim.evaluation.graph.contour.MonteCarloContourGraph import *
from sim.evaluation.graph.contour.MonteCarloContourGraphSentPackets import *
from sim.evaluation.graph.hist.MonteCarloHistGraph import *

from sim.utils.helper import *
from sim.config import *

logging.config.fileConfig(LOGFILENAME)
logger = logging.getLogger("evrun")

class MonteCarloEvaluation:
    def __init__(self):
        pass

    def execute(self,
                executable_info,
                scenario_info,
                iterations):

        logger.info("="*40)
        logger.info("Executing MonteCarloEvaluation:")
        logger.info("="*40)

        if MONTECARLO_EVAL_LIST.count("MonteCarloContourGraph") > 0:
            mccg = MonteCarloContourGraph()
            mccg.execute(executable_info, scenario_info, iterations)
        else:
            logger.warn("????MonteCarloContourGraph evaluation disabled")

        if MONTECARLO_EVAL_LIST.count("MonteCarloContourGraphSentPackets") > 0:
            mccgsp = MonteCarloContourGraphSentPackets()
            mccgsp.execute(executable_info, scenario_info, iterations)
        else:
            logger.warn("????MonteCarloContourGraphSentPackets evaluation disabled")

        if MONTECARLO_EVAL_LIST.count("MonteCarloHistGraph") > 0:
            mchg = MonteCarloHistGraph()
            mchg.execute(executable_info, scenario_info, iterations)
        else:
            logger.warn("????MonteCarloHistGraph evaluation disabled")
