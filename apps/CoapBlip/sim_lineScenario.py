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
print "Python version 2.6 required (for some reason).  You have", sys.version
if sys.version < '2.6':
     print "Python version 2.6 required (for some reason).  You have", sys.version
     sys.exit(1)

tosroot = os.environ.get("TOSROOT")

if tosroot == "":
     print "TOSROOT not set. export TOSROOT=..."
     sys.exit(1)


#building line topology
nodes =int(sys.argv[1])

LineFile = open("Linetopo" + str(sys.argv[1]) +".txt", "w")

for i in range(1, nodes +1, 1):
    for j in range(1, nodes +1, 1):
        if(i!=j):
            if((j+1)==i or (i+1==j)):
                LineFile.write("%s %s %s %s\n" % ("gain", str(i), str(j), str(-20)))
            else:
                LineFile.write("%s %s %s %s\n" % ("gain", str(i), str(j), str(-120)))
LineFile.close()



print "-"*10, "[[[[ Setting up TOSSIM ]]]]", "-"*10
print "-"*10, "Line Topology consists of " + sys.argv[1] + " nodes" "-"*10
t = Tossim([])
r = t.radio() #Radio Model

channels = ["Boot","UDPEchoP"
            #,"MsgSuccessRecv"
            #,"MsgRequests"
            ,"IPForwardingEngine-PTr"
            #,"IPForwardingEngine-Routes"
            , "Coap"
             #,"Test"
            ]
file_log = ["LogFile", "IPForwardingEngine-Routes", "MsgSuccessRecv" ,"MsgRequests" ,"IPForwardingEngine-PTr" ,"IPForwardingEngine-Routes"]

print str(nodes) + ' Nodes are used in the Simulation'

LogFile = open("BSLineScenario" + str(sys.argv[1]) +".log", "w")

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
loadLinkModel(t, 'Linetopo' + str(sys.argv[1])+ '.txt')
loadNoiseModel(t, "meyer.txt", nodes)

initializeNodes(t, nodes)

print "Simulation Running..."

eventCtr = 0
eventPresent = True

sleepDelta = 0.00001

clockStartTime = datetime.now()
simStartTime   = t.time()
# mote1 = t.getNode(1);
# print dir(r)

a = "Line Scenario of " + sys.argv[1] + " nodes"

print_gain(r, nodes)
LogFile.write("%s \n\n" % a)
print a


try:
     counter = 0
     while True:
          counter = counter +1
          clockCurrentTime = datetime.now()
          clockTimeDifference = clockCurrentTime - clockStartTime
          clockTimeDifferenceSec = (clockTimeDifference.seconds + clockTimeDifference.microseconds / float(1000000))
          simCurrentTimeSec   = t.time() / float(t.ticksPerSecond())

          sleepTime = simCurrentTimeSec - clockTimeDifferenceSec
          # node3=t.getNode(3)
          # node3.turnOff()

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
