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

class Calc_Gain:
        
    def calc_gain(self, filenamebase, id, id2):
	
        pl0 = 50
        gammaX10 = 20

        # Pathloss exponent and constant for air-air
        pl0_aa = 70
        gammaX10_aa = 30

# Pathloss exponent and constant for air-top        
        pl0_at = 75
        gammaX10_at = 40

# Pathloss exponent and constant for top-top        
        pl0_tt = 85
        gammaX10_tt = 54

# Pathloss exponent and constant for top-banana
	pl0_tb = 92
        gammaX10_tb = 56

# Pathloss exponent and constant for banana-banana
        pl0_bb = 93
        gammaX10_bb = 60

# Pathloss exponent and constant for banana-air
        pl0_ba = 100
        gammaX10_ba = 80
        if SCENARIO == "ContainerScenario":
       # print "Distance between node",id,"and","node",id2,"is", self.calc_distance(id, id2)
            nodetype_dict = {} 
        
            tfile = open(filenamebase + "_nodetype.pickle","r")
            nodetype_dict = pickle.load(tfile)
            tfile.close()

            if nodetype_dict[id] == 1: 
                if nodetype_dict[id2] == 1:
                #print "air-air id:", id,id2
                    return pl0_aa + gammaX10_aa * math.log(self.calc_distance(id, id2), 10)
                elif nodetype_dict[id2] == 2:
		#print "air-top id:", id,id2
                    return pl0_at + gammaX10_at * math.log(self.calc_distance(id, id2), 10)
                elif nodetype_dict[id2] == 3:
		#print "air-banana id:", id,id2
                    return pl0_ba + gammaX10_ba * math.log(self.calc_distance(id, id2), 10)	
        
                elif nodetype_dict[id] == 2:
            	    if nodetype_dict[id2] == 1:
		#print "top-air id:", id,id2
                       return pl0_at + gammaX10_at * math.log(self.calc_distance(id, id2), 10)
                    elif nodetype_dict[id2] == 2:
		#print "top-top id:", id,id2	
                        return pl0_tt + gammaX10_tt * math.log(self.calc_distance(id, id2), 10)	
                    elif nodetype_dict[id2] == 3:
		#print "top-banana id:", id,id2	
                        return pl0_tb + gammaX10_tb * math.log(self.calc_distance(id, id2), 10)

            elif nodetype_dict[id] == 3:
                if nodetype_dict[id2] == 1:
		#print "banana-air id:", id,id2
                    return pl0_ba + gammaX10_ba * math.log(self.calc_distance(id, id2), 10)
                elif nodetype_dict[id2] == 2:
		#print "BA-top id:", id,id2
                    return pl0_tb + gammaX10_tb * math.log(self.calc_distance(id, id2), 10)	
                elif nodetype_dict[id2] == 3:
		#print "BA-BA id:", id,id2
                    return pl0_bb + gammaX10_bb * math.log(self.calc_distance(id, id2), 10)
 
        else:
	    return pl0 + gammaX10 * math.log(self.calc_distance(id, id2), 10)   

    def calc_distance(self, id, id2):
        id2xyz_dict = {} 
        ifile = open(tosroot + "/apps/UDPEcho/sim/output/id2xyz.pickle","r")
        id2xyz_dict = pickle.load(ifile)
        ifile.close()
        (x, y, z)   = id2xyz_dict[id]
        (x2, y2, z2) = id2xyz_dict[id2]
        distance = math.sqrt((x-x2)**2 + (y-y2)**2 + (z-z2)**2)
	#print "The distance between node",id, id2,"is",distance,"m"
	#print "The type of link is",nodetype_1,"-->",nodetype_2
	return distance
