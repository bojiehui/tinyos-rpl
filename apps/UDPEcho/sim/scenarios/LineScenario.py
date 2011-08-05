from sim.scenarios.Scenario import Scenario
from sim.utils.helper import *
from sim.config import *

class LineScenario(Scenario):
    def __init__(self, t, si):
        """
        """
        Scenario.__init__(self, t, si)

        self.distance = si.distance
        self.scen_x = si.distance*si.nodes
        self.scen_y = 0
        self.scen_z = 0

    def connect_neighbors(self, id):
        for id2 in range(1, self.nodes+2):
            if id == id2:
                # do not connect with the same node
                continue
           # if abs(id - id2) == 1:
            #    # only connect direct neighbor, with realistic
            #    # propagation, though
            #    self.connect_neighbor(id, id2) 
            self.connect_neighbor(id, id2)

    def setup_radio(self):
        for id in range(1, self.nodes+2):
            # regular creation of nodes

            if id == 1:
                x = 0
                y = 0
		z = 0
            else:
                #x = (((id-2)/self.size)+1)*self.distance
                #y = (((id-2)%self.size)+1)*self.distance
                x = (id-1)*self.distance
                y = 0
                z = 0
            self.id2xyz_dict[id] = (x, y, z)
            #self.xyz2id_dict[x]    = {}
            #self.xyz2id_dict[x][y][z] = id
#	    self.nodetype_dict[id] = "air"	
        self.id2xyz_dict[id] = (x, y, z)
        self.setup_radio_general()
