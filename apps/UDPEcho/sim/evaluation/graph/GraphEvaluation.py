import gc
import logging

#from sim.evaluation.graph.packet.PacketGraph import *
from sim.evaluation.graph.sn.SN import *
#from sim.evaluation.graph.contour.ContourGraph import *
#from sim.evaluation.graph.contour.ContourGraphSentPackets import *
#from sim.evaluation.graph.hist.HistGraph import *
from sim.evaluation.graph.topology.TopologyGraph import *
from sim.evaluation.graph.topology.TopologyGraph_3D import *

from sim.utils.helper import *
from sim.config import *

logging.config.fileConfig(LOGFILENAME)
logger = logging.getLogger("evrun")

class GraphEvaluation:
    def __init__(self):
        logger.info(">"*10 + " New graph evaluation" + "<"*10)

    def execute(self,
            #    executable_info,
                scenario_info):

        logger.info("="*40)
        logger.info("Executing GraphEvaluation:" + str(GRAPH_EVAL_LIST))
        logger.info("="*40)

        # TrickleGraph shows it better
        # pg = PacketGraph()
        # pg.execute(executable_info, scenario_info)

        #
        if GRAPH_EVAL_LIST.count("SN") > 0:
            sn = SN()
            sn.execute(scenario_info)	
            del sn
            gc.collect()
        else:
            logger.warn("????SN evaluation disabled")

        if GRAPH_EVAL_LIST.count("ContourGraph") > 0:
            cg = ContourGraph()
            #cg.execute(executable_info, scenario_info)
            cg.execute(scenario_info)	
            del cg
            gc.collect()
        else:
            logger.warn("????ContourGraph evaluation disabled")

        if GRAPH_EVAL_LIST.count("ContourGraphSentPackets") > 0:
            cgsp = ContourGraphSentPackets()
            #cgsp.execute(executable_info, scenario_info)
            cgsp.execute(scenario_info)	
            del cgsp
            gc.collect()

        if GRAPH_EVAL_LIST.count("HistGraph") > 0:
            hg = HistGraph()
          #  hg.execute(executable_info, scenario_info)
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
            #tog.execute(executable_info, scenario_info)
            tog.execute(scenario_info)	
            del tog
            gc.collect()
        else:
            logger.warn("????TopologyGraph evaluation disabled")
