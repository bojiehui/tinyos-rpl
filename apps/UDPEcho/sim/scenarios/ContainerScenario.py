import pickle
import numpy as np
from sim.scenarios.Scenario import Scenario
from sim.utils.helper import *
from sim.config import *
import os

tosroot = os.environ.get("TOSROOT")

SURROUNDING_MATERIAL_AIR    = 1
SURROUNDING_MATERIAL_TOP    = 2
SURROUNDING_MATERIAL_BANANA = 3

class ContainerScenario(Scenario):
    def __init__(self, t, si):
        """
        """
        Scenario.__init__(self, t, si)
        self.t = t
        self.si    = si
        self.nodes = si.nodes
        self.r = self.t.radio()

        self.scen_x = si.distance*math.sqrt(si.nodes)
        self.scen_y = si.distance*math.sqrt(si.nodes)

# Pathloss exponent and constant for air-air
        self.pl0_aa = 50
        self.gammaX10_aa = 20

# Pathloss exponent and constant for air-top        
        self.pl0_at = 75
        self.gammaX10_at = 30

# Pathloss exponent and constant for top-top        
        self.pl0_tt = 85
        self.gammaX10_tt = 40

# Pathloss exponent and constant for top-banana
	self.pl0_tb = 100
        self.gammaX10_tb = 60

# Pathloss exponent and constant for banana-banana
        self.pl0_bb = 110
        self.gammaX10_bb = 70

        self.filenamebase = si.createfilenamebase()

        self.id2xyz_dict = {}
	self.xyz2id_dict = {}
	self.nodetype_dict = {}	

    def connect_neighbors(self, id, id2):
        for id2 in range(1, self.nodes+1):
            if id == id2:
                # do not connect with the same node
                continue
            gain = self.calc_gain(id, id2)
            # print "gain between", id, id2, "=",gain,"db"
            if not gain:	
           # print id,"and",id2,"are not neighbours."
                pass	  
            else:
                self.r.add(id, id2, 0 - gain)# negative gain
        
    def calc_gain(self, id, id2):
       # print "Distance between node",id,"and","node",id2,"is", self.calc_distance(id, id2)

        if self.nodetype_dict[id] == 1: 
            if self.nodetype_dict[id2] == 1:
                #print "air-air id:", id,id2
                return self.pl0_aa + self.gammaX10_aa * math.log(self.calc_distance(id, id2), 10)
            elif self.nodetype_dict[id2] == 2:
		#print "air-top id:", id,id2
                return self.pl0_at + self.gammaX10_at * math.log(self.calc_distance(id, id2), 10)	
        
        elif self.nodetype_dict[id] == 2:
            if self.nodetype_dict[id2] == 1:
		#print "top-air id:", id,id2
                return self.pl0_at + self.gammaX10_at * math.log(self.calc_distance(id, id2), 10)
            elif self.nodetype_dict[id2] == 2:
		#print "top-top id:", id,id2	
                return self.pl0_tt + self.gammaX10_tt * math.log(self.calc_distance(id, id2), 10)	
            elif self.nodetype_dict[id2] == 3:
		#print "top-banana id:", id,id2	
                return self.pl0_tb + self.gammaX10_tb * math.log(self.calc_distance(id, id2), 10)

        elif self.nodetype_dict[id] == 3:
            if self.nodetype_dict[id2] == 2:
		#print "BA-top id:", id,id2
                return self.pl0_tb + self.gammaX10_tb * math.log(self.calc_distance(id, id2), 10)	
            elif self.nodetype_dict[id2] == 3:
		#print "BA-BA id:", id,id2
                return self.pl0_bb + self.gammaX10_bb * math.log(self.calc_distance(id, id2), 10)

    def calc_distance(self, id, id2):
        (x, y, z)   = self.id2xyz_dict[id]
        (x2, y2, z2) = self.id2xyz_dict[id2]
        distance = math.sqrt((x-x2)**2 + (y-y2)**2 + (z-z2)**2)
	#print "The distance between node",id, id2,"is",distance,"m"
	return distance


    def setup_radio_container(self):
        of = open(self.filenamebase+"_id2xyz.pickle", "w")
        pickle.dump(self.id2xyz_dict, of)
        of.close()

        tf = open(self.filenamebase+"_nodetype.pickle", "w")
        pickle.dump(self.nodetype_dict, tf)
        tf.close()

        for id in range(1, self.nodes+1):
            for id2 in range(1, self.nodes+1):
                if id == id2:
                    continue
                self.connect_neighbors(id, id2)

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

        #print "Neighbors(", MIN_DISTANCE,  "):", neighbors_min
        #print "Neighbors(", MEAN_DISTANCE, "):", neighbors_mean
        #print "Neighbors(", MAX_DISTANCE,  "):", neighbors_max

        np.save(self.filenamebase+"_neighbors_min.npy", neighbors_min)
        np.save(self.filenamebase+"_neighbors_mean.npy", neighbors_mean)
        np.save(self.filenamebase+"_neighbors_max.npy", neighbors_max)

    def setup_radio(self):

	n = [
	((0.01, 1.15, 1.2),  1),
	((0.70, 2.05, 1.05), 3),
	((0.70, 2.05, 1.45), 3),
	((0.70, 2.05, 1.85), 3),
	((0.70, 2.05, 2.25), 3),
	((0.70, 1.05, 1.05), 3), 
	((0.70, 1.05, 1.45), 3), 
	((0.70, 1.05, 1.85), 3), 
	((0.70, 1.05, 2.25), 2), 
	((2.20, 2.05, 2.30), 1), 
	((3.00, 0.50, 2.30), 1), 
	((6.15, 2.05, 2.30), 1), 
	((6.15, 0.50, 2.30), 1), 
	((6.15, 1.05, 0.25), 3), 
	((6.15, 1.05, 1.05), 3), 
	((6.15, 1.05, 1.65), 3), 
	((6.15, 1.05, 2.25), 2), 
	((6.15, 0.50, 0.25), 3), 
	((6.15, 0.50, 1.05), 3), 
	((6.15, 0.50, 1.65), 3), 
	((6.15, 0.50, 2.25), 2), 
	((7.60, 2.05, 2.30), 1), 
	((7.60, 0.50, 2.30), 1), 
	((10.0, 2.05, 2.30), 1), 
	((10.0, 2.05, 0.25), 3), 
	((10.0, 2.05, 1.45), 3), 
	((10.0, 2.05, 1.85), 3), 
	((10.0, 2.05, 2.25), 2), 
	((10.8, 2.05, 0.25), 3), 
	((10.8, 2.05, 1.45), 3), 
	((10.8, 2.05, 1.85), 3), 
	((10.8, 2.05, 2.25), 2),
	((10.8, 0.50, 2.30), 1)
	]
        

        for id in range(1, self.nodes+1):
            x = n[id-1][0][0]
	    y = n[id-1][0][1]
	    z = n[id-1][0][2]

            self.id2xyz_dict[id]   = (x, y, z)
	    self.nodetype_dict[id] = n[id-1][1]
        print self.id2xyz_dict
        self.setup_radio_container()

 
