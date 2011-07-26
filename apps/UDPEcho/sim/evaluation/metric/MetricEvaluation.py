import gc
import logging
import logging.config

from sim.evaluation.metric.PacketMetric import *

from sim.utils.helper import *
from sim.config import *

logging.config.fileConfig(LOGFILENAME)
logger = logging.getLogger("evrun")

class MetricEvaluation:
    def __init__(self):
        logger.info(">"*10 + " New metric evaluation" + "<"*10)

    def execute(self,
                executable_info,
                scenario_info):

        logger.info("="*40)
        logger.info("Executing MetricEvaluation:")
        logger.info("="*40)

        pm = PacketMetric()
        pm.execute(executable_info, scenario_info)
        del pm
        gc.collect()
