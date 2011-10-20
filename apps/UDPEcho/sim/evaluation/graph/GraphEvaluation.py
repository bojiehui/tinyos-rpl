import gc
import logging

from sim.evaluation.graph.sn.SN import *
from sim.evaluation.graph.contour.ContourGraph import *
from sim.evaluation.graph.contour.ContourGraphSentICMP import *
from sim.evaluation.graph.contour.ContourGraphPacketLoss import *
from sim.evaluation.graph.hist.HistGraph import *
from sim.evaluation.graph.topology.TopologyGraph import *
from sim.evaluation.graph.topology.TopologyGraphBare import *
from sim.evaluation.graph.topology.TopologyGraph_3D import *

from sim.utils.helper import *
from sim.config import *

logging.config.fileConfig(LOGFILENAME)
logger = logging.getLogger("evrun")

class GraphEvaluation:
    def __init__(self):
        logger.info(">"*10 + " New graph evaluation" + "<"*10)

    def execute(self,
                scenario_info):

        logger.info("="*40)
        logger.info("Executing GraphEvaluation:" + str(GRAPH_EVAL_LIST))
        logger.info("="*40)

        if GRAPH_EVAL_LIST.count("SN") > 0:
            sn = SN()
            sn.execute(scenario_info)	
            del sn
            gc.collect()
        else:
            logger.warn("????SN evaluation disabled")

        if GRAPH_EVAL_LIST.count("ContourGraph") > 0:
            cg = ContourGraph()
            cg.execute(scenario_info)	
            del cg
            gc.collect()
        else:
            logger.warn("????ContourGraph evaluation disabled")

        if GRAPH_EVAL_LIST.count("ContourGraphSentICMP") > 0:
            cgsp = ContourGraphSentICMP()
            cgsp.execute(scenario_info)	
            del cgsp
            gc.collect()

        if GRAPH_EVAL_LIST.count("ContourGraphPacketLoss") > 0:
            cgpl = ContourGraphPacketLoss()
            cgpl.execute(scenario_info)	
            del cgpl
            gc.collect()
        else:
            logger.warn("????ContourGraph for Packet Loss evaluation disabled")

        if GRAPH_EVAL_LIST.count("HistGraph") > 0:
            hg = HistGraph()
            hg.execute(scenario_info)	
            del hg
            gc.collect()
        else:
            logger.warn("????HistGraph evaluation disabled")

        if GRAPH_EVAL_LIST.count("TopologyGraph") > 0:
            if SCENARIO == "ContainerScenario":
                tog = TopologyGraph_3D()
            else:
                tog = TopologyGraph()
            tog.execute(scenario_info)	
            del tog
            gc.collect()
        else:
            logger.warn("????TopologyGraph evaluation disabled")
