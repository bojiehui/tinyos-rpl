
##################################################
BASESTATION_ID    = 1     # NEEDS TO BE SETTED IN Makefile/TrickleSim.h AS WELL

#TURNOFF_NODE_TIME   = 100 # DISABLED
#TURNOFF_NODE_TIME   = SEC_BEFORE_INJECT + (SEC_AFTER_INJECT/10)
#TURNOFF_NODE_TIME   = 120

NODES_LIST = [4]	#Number of nodes
#NODES_LIST = [2, 4]
#NODES_LIST = [2, 3, 4, 5, 6, 7, 8, 9, 10, 16, 25]
#NODES_LIST = [2, 3, 4, 5, 6, 7, 8, 9]
#NODES_LIST = [4, 9, 16, 25, 36, 49, 64, 81, 100, 225, 400]
#NODES_LIST = [4, 9, 16, 25, 36, 49, 64, 81, 100, 225]

#NODES_LIST = [32] # FOR MOTELAB

#SQR_NODES_LIST    = [2, 3, 4, 5, 6, 7, 8, 9, 10, 15, 20]

#DISTANCE_LIST      [70, 80]
#DISTANCE_LIST     = [40]
#DISTANCE_LIST     = [20, 40]
#DISTANCE_LIST     = [20, 40, 60, 80, 100]
#DISTANCE_LIST     = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
#DISTANCE_LIST     = [ 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100]
#DISTANCE_LIST     = [30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130, 140]
#DISTANCE_LIST     = [30, 50, 70, 90, 110, 130]
#DISTANCE_LIST     = [10, 50, 60, 70, 80, 90, 100, 110, 120, 130, 140]

#DISTANCE_LIST     = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130, 140]

DISTANCE_LIST     = [80] # FOR MOTELAB

#MONTE_CARLO_ITERATIONS = 2
#MONTE_CARLO_ITERATIONS = 300
MONTE_CARLO_ITERATIONS = 1

#RANDOMIZE_BOOT      = True
RANDOMIZE_BOOT      = False

# this is Python only, if you need randomness in the app, check TrickleSimAppC
RANDOMIZE_SEED      = True
#RANDOMIZE_SEED      = False

#RANDOMIZE_TOPOLOGY  = True
RANDOMIZE_TOPOLOGY  = False

#SCENARIO = "GridScenario"
#SCENARIO = "RandomScenario"
SCENARIO = "LineScenario"
#SCENARIO = "TestingContainerScenario"
#SCENARIO = "ContainerScenario"
#SCENARIO = "DirectNeighborLineScenario"
#SCENARIO = "MoteLabConnectivityScenario"
#SCENARIOFILE = "sim/scenarios/MoteLabConnectivity.pickle"


MIN_DISTANCE = 130
MEAN_DISTANCE = 143
MAX_DISTANCE = 153

SIM_REALTIME = False
SIM_TIME = 50

# debug channels:
stdout_channels = [
    #"TrickleSimC"
    #"Trickle", sys
    #"TrickleTimes"
    #"Boot"
    "MsgSuccessRecv"
    ,"MsgRequests"
    ,"UDPEchoP"
    ,"IPForwardingEngine-PTr"
    # ,"IPForwardingEngine-Routes"
    ]

file_channels = [
    "Boot",
    #"CpmModelC,SNRLoss",
    #"CpmModelC,SNR",
    #"ICMPResponder", "mab",
    #"CpmModelC","ICMPPing", "base",
    "MsgExchange",
    "MsgRequests",
    "MsgSuccessRecv",
    #"TossimPacketModelC",

    # "Packet",
    # "Drops",
    # "IPDispatchP",
    # "IPDispatch",
    # "IP",
    # "IPRouting",
    # "Install",
    # "Table",
    # "ICMPResponder",
    # "6LoWPAN"
    ]

#METRIC_EVAL = True
METRIC_EVAL = False

GRAPH_EVAL = True
#GRAPH_EVAL = False
GRAPH_EVAL_LIST = [
    "SN",
#    "ContourGraph",
#    "HistGraph",
#    "TopologyGraph",
    ]

#MONTECARLO_EVAL = True
MONTECARLO_EVAL = False
MONTECARLO_EVAL_LIST = [
#    "MonteCarloContourGraph",
    "MonteCarloHistGraph",
    ]

#SUITE_EVAL = True
SUITE_EVAL = False
SUITE_EVAL_LIST = [
#    "SuiteEvaluationPackets",
    "SuiteEvaluationHist",
    ]

EVAL_LOW_TIME  = -.2
#EVAL_HIGH_TIME = 120
EVAL_HIGH_TIME = 10
#EVAL_BINS      = (EVAL_HIGH_TIME - EVAL_LOW_TIME) * 10000
EVAL_BINS      = (EVAL_HIGH_TIME - EVAL_LOW_TIME) * 60000

if RANDOMIZE_TOPOLOGY == True and SCENARIO != "RandomScenario":
    raise Exception("Cannot randomize non random scenario topology. Check config.py")

if RANDOMIZE_TOPOLOGY == True and MONTECARLO_EVAL_LIST.count("MonteCarloContourGraph") > 0:
    raise Exception("Cannot create contour graph for randomized topology. Check config.py")

#########

#SMTP_SERVER = 'localhost'
#SMTP_SERVER = 'bugs.comnets.uni-bremen.de'

#MAIL_SENDER = 'mab@comnets.uni-bremen.de'
#MAIL_RECEIVERS = ['mab@comnets.uni-bremen.de']

#MAIL_TEMPLATE = """From: Markus Becker <mab@comnets.uni-bremen.de>
#To: Markus Becker <mab@comnets.uni-bremen.de>
#Subject: Simulation/Evaluation finished

#The simulation/evaluation has finished:
#"""

#########

LOGFILENAME = "sim/logging.conf"
