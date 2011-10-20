
##################################################
BASESTATION_ID    = 1     # NEEDS TO BE SETTED IN Makefile/TrickleSim.h AS WELL

NODES_LIST        = [9]	#Number of nodes

DISTANCE_LIST     = [10, 50, 100]
#DISTANCE_LIST     = [100]
NUM_PING          = 100

MONTE_CARLO_ITERATIONS = 100

#RANDOMIZE_BOOT      = True
RANDOMIZE_BOOT      = False

# this is Python only, if you need randomness in the app, check TrickleSimAppC
RANDOMIZE_SEED      = True
#RANDOMIZE_SEED      = False

#RANDOMIZE_TOPOLOGY  = True
RANDOMIZE_TOPOLOGY  = False

#SCENARIO = "GridScenario"
#SCENARIO = "DirectNeighborGridScenario"
#SCENARIO = "RandomScenario"
SCENARIO = "LineScenario"
#SCENARIO = "ContainerScenario"
#SCENARIO = "DirectNeighborLineScenario"
#SCENARIO = "MoteLabConnectivityScenario"
#SCENARIOFILE = "sim/scenarios/MoteLabConnectivity.pickle"


MIN_DISTANCE = 130
MEAN_DISTANCE = 143
MAX_DISTANCE = 153

#SIM_REALTIME = True
SIM_REALTIME = False
SIM_TIME = 100000000

# debug channels:
stdout_channels = [
    #"TrickleSimC"
    #"Trickle", sys
    #"TrickleTimes"
    #"Boot",
    #"CpmModelC",
    #"Csma",
    #"MessageBuffer",
    #"driver.debug",
    #"Collision",
    #"PacketLink",
    #"MsgExchange",
    #"MsgSuccessRecv",
    #"MsgRequests",
    #"UDPEchoP",
    #"IPForwardingEngine-PTr",
    #"IPForwardingEngine-DefaultRoute",
    #"ICMPCore"
   # "IPForwardingEngine-Routes",
    ]

file_channels = [
    "Boot",
   # "TrickleTimer",
    #"Gain",
   # "CpmModelC,SNRLoss",
   # "CpmModelC,SNR",
    #"ICMPResponder", "mab",
   # "CpmModelC",
    # "Bo-154Message",
    # "Bo-154Packet",
    # "Bo-Network",
    # "Bo-Unique",
    # "PLink",
    # "MessageBuffer",
    # "Retry",
    # "Collision",
    # "SoftwareAck",
    # "Csma",
    # "Driver.debug",
    # "Driver.error",
    # "Driver.trace",
    "MsgExchange",
    "MsgRequests",
    "MsgSuccessRecv",
    "UDPEchoP",
    "IPForwardingEngine-DefaultRoute",
    "IPForwardingEngine-PTr",
    "ICMPCore",
    #"RPLRoutingEngine",
    # "RPLDAORoutingEngine",
    #"IPForwardingEngine-Routes",
    # "IPForwardingEngine",
    # "MRHOF",
    # "RPLRank",
    # "OF0",
    # "DAORouting",
    # "Test",
    #"CCA",
    #"SameNode"
    ]

METRIC_EVAL = True
#METRIC_EVAL = False

#GRAPH_EVAL = True
GRAPH_EVAL = False
GRAPH_EVAL_LIST = [
#    "SN",
#    "ContourGraph",
#    "ContourGraphPacketLoss",
#    "ContourGraphSentICMP",
     "HistGraph",
#   "TopologyGraph",
#   "TopologyGraphBare",
    ]

MONTECARLO_EVAL = True
#MONTECARLO_EVAL = False
MONTECARLO_EVAL_LIST = [
 #   "MonteCarloContourGraph",
 #   "MonteCarloContourGraphPacketLoss",
 #  "MonteCarloContourGraphSentICMP",
   "MonteCarloHistGraph",
    ]

#SUITE_EVAL = True
SUITE_EVAL = False
SUITE_EVAL_LIST = [
#    "SuiteEvaluationPackets",
    "SuiteEvaluationHist",
    ]

EVAL_LOW_TIME  = 0
EVAL_HIGH_TIME = 2000
EVAL_BINS      = (EVAL_HIGH_TIME - EVAL_LOW_TIME) * 6

if RANDOMIZE_TOPOLOGY == True and SCENARIO != "RandomScenario":
    raise Exception("Cannot randomize non random scenario topology. Check config.py")

if RANDOMIZE_TOPOLOGY == True and MONTECARLO_EVAL_LIST.count("MonteCarloContourGraph") > 0:
    raise Exception("Cannot create contour graph for randomized topology. Check config.py")

LOGFILENAME = "sim/logging.conf"
