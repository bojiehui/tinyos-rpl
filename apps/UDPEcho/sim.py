#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import time
import os
import shlex
import traceback
from datetime import datetime
from tinyos.tossim.TossimHelp import *
from TOSSIM import *

sys.path.append("..")
#print "Python version 2.6 required (for some reason).  You have", sys.version
#if sys.version < '2.6':
#     print "Python version 2.6 required (for some reason).  You have", sys.version
#     sys.exit(1)

tosroot = os.environ.get("TOSROOT")

if tosroot == "":
     print "TOSROOT not set. export TOSROOT=..."
     sys.exit(1)



print "-"*10, "[[[[ Setting up TOSSIM ]]]]", "-"*10

t = Tossim([])
# r = t.radio()

channels = [#"Boot",
             "UDPEchoP",
            # "CpmModelC",
            # "Bo-RoutingEngine",
            # "Driver.debug",
            # "Bo-Csma",
            # "Bo-SoftwareAck",
            # "Bo-Collision",
            # "Bo-MessageBuffer",
            # "Bo-Unique",
            # "Bo-LPL",
            # "Bo-PLink",
            # "Bo-Network",
            # "Bo-AM",
            # "Bo-154Message",
            # "Bo-AutoResource",
             "MsgSuccessRecv",
             "MsgRequests",
             "MsgExchange",
            # "IPND",
            "IPForwardingEngine-Routes",
            # "Ping",
            "IPForwardingEngine-PTr",
             "UDPEchoP",
            # "IPProtocols",
            # "ICMPCore",
            # "RPLDAORoutingEngine",
            # "OF00",
            # "OF0"
            ]
file_log = ["LogFile"]

nodes = 4
print str(nodes) + 'Nodes are used in the Simulation'

LogFile = open("BS.log", "w")

for log in file_log:
     print "File Logging", log, "enabled"
     t.addChannel(log,LogFile)

for chan in channels:
      print "Channel", chan, "enabled"
      t.addChannel(chan, sys.stdout)

print "Setting up TOSSIM topology..."
if(len(sys.argv)==1):
     print "Specify Topology!"
     sys.exit(1)

#Load different Models for Topology and Radio Link
loadLinkModel(t, 'topo' + str(sys.argv[1])+ '.txt')
loadNoiseModel(t, "meyer.txt", nodes)

initializeNodes(t, nodes)

print "Simulation Running..."

eventCtr = 0
eventPresent = True

sleepDelta = 0.00001

clockStartTime = datetime.now()
simStartTime   = t.time()

try:
     counter = 0
     while True:
          counter = counter +1
          clockCurrentTime = datetime.now()
          clockTimeDifference = clockCurrentTime - clockStartTime
          clockTimeDifferenceSec = (clockTimeDifference.seconds + clockTimeDifference.microseconds / float(1000000))
          simCurrentTimeSec   = t.time() / float(t.ticksPerSecond())
          
          sleepTime = simCurrentTimeSec - clockTimeDifferenceSec

          while sleepTime > 0:
               time.sleep(sleepDelta)
               sleepTime -= sleepDelta
          eventPresent = t.runNextEvent()
          eventCtr = eventCtr + 1
    
          



except KeyboardInterrupt:
     print ">>> Ctrl-C"

except:
     traceback.print_exc()
     print ">>> Exception while simulating."

finally:
     #throttle.finalize()
     #throttle.printStatistics()
     pass
