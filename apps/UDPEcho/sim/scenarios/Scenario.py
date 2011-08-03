import numpy as np
import pickle
import math
import random

from sim.config import *

class Scenario():
#    def __init__(self, t, ei, si):
    def __init__(self, t, si):
        """
        """
        self.t = t
        self.si = si
        self.nodes = si.nodes
        self.r = self.t.radio()

        self.pl0 = 50
        self.gammaX10 = 20

        self.filenamebase = si.createfilenamebase()

        self.id2xyz_dict = {}
	self.xyz2id_dict = {}

    def id2xyz(id):
        return self.id2xyz_dict[id]

    def xyz2id(x, y):
        return self.xyz2id_dict[x][y][z]

    def connect_neighbor(self, id, id2):
	gain = self.calc_gain(id, id2)
        print "gain = ",gain
        self.r.add(id, id2,
                  0 - gain)# negative gain
    
    def calc_gain(self, id, id2):
        #print "Distance between node",id,"and","node",id2,"is", self.calc_distance(id, id2)
    
        return self.pl0 + self.gammaX10 * math.log(self.calc_distance(id, id2), 10)

    def calc_distance(self, id, id2):
        (x, y, z)   = self.id2xyz_dict[id]
        (x2, y2, z2) = self.id2xyz_dict[id2]
        return math.sqrt((x-x2)**2 + (y-y2)**2 + (z-z2)**2)

    def calc_neighbors(self, id, cutoff_distance):
        neigh = 0
        for id2 in range(2, self.nodes+1):
            if id == id2:
                # do not count the same node
                continue

            if (self.calc_distance(id, id2) <= cutoff_distance):
               # print "node",id,"and node",id2,"are neighbors"
                neigh += 1

        return neigh

    def get_scenario_size():
        return self.scen_x, self.scen_y

    def setup_radio(self):
        raise Exception("Pure virtual function")

    def setup_boot(self, randomize=False, randomseed=False):
        for id in range(1, self.nodes+1):
            if randomize == False:
                boottime = 1*self.t.ticksPerSecond() \
                    + id*10
            else:
                if randomseed:
                    random.seed()

                boottime = 1*self.t.ticksPerSecond() \
                    + int(9*random.random()*self.t.ticksPerSecond())

            print "Setting boot time for", \
                id, boottime
            n = self.t.getNode(id)

            # set the boottime
#            if id == self.ei.defines["INJECT_NODE"]:
#                n.bootAtTime(0)
#            elif id == BASESTATION_ID:
            if id == BASESTATION_ID:
                n.bootAtTime(0) #BASESTATION
            else:
                n.bootAtTime(boottime)
                print "Boot",id,"now"

    def setup_radio_general(self):
        of = open(self.filenamebase+"_id2xyz.pickle", "w")
        pickle.dump(self.id2xyz_dict, of)
        of.close()

        for id in range(1, self.nodes+1):
            self.connect_neighbors(id)

        for id in range(1, self.nodes+1):
            for i in range(0, 10000):
                self.t.getNode(id).addNoiseTraceReading(-98)

        for id in range(1, self.nodes+1):
            self.t.getNode(id).createNoiseModel()

        neighbors_min  = np.zeros(self.nodes+1)
        neighbors_mean = np.zeros(self.nodes+1)
        neighbors_max  = np.zeros(self.nodes+1)


        for id in range(1, self.nodes+1):
            neighbors_min [id] = self.calc_neighbors(id, MIN_DISTANCE)
            neighbors_mean[id] = self.calc_neighbors(id, MEAN_DISTANCE)
            neighbors_max [id] = self.calc_neighbors(id, MAX_DISTANCE)

      #  print "Neighbors(", MIN_DISTANCE,  "):", neighbors_min
      #  print "Neighbors(", MEAN_DISTANCE, "):", neighbors_mean
      #  print "Neighbors(", MAX_DISTANCE,  "):", neighbors_max

        np.save(self.filenamebase+"_neighbors_min.npy", neighbors_min)
        np.save(self.filenamebase+"_neighbors_mean.npy", neighbors_mean)
        np.save(self.filenamebase+"_neighbors_max.npy", neighbors_max)
