import math

from sim.scenarios.Scenario import Scenario
from sim.utils.helper import *
from sim.config import *

class DirectNeighborGridScenario(Scenario):
    def __init__(self, t, si):
        """
        """
        if math.sqrt(si.nodes) != math.ceil(math.sqrt(si.nodes)):
            raise Exception("Grid scenario required sqrt'able number of nodes")

        Scenario.__init__(self, t, si)

        self.distance = si.distance
        self.sqrt_nodes = math.sqrt(si.nodes)
        self.scen_x = si.distance*self.sqrt_nodes
        self.scen_y = si.distance*self.sqrt_nodes
	self.scen_z = 0


    def connect_neighbors(self, id):
        for id2 in range(1, self.nodes+1):
            if id == id2:
                # do not connect with the same node
                continue
            
	    if (abs(id - id2) == 1) or (abs(id - id2) == self.sqrt_nodes) \
            or (abs (id -id2) == (self.sqrt_nodes + 1)) \
            or (id - id2 == (self.sqrt_nodes -1)):
                self.connect_neighbor(id, id2)
            elif ((id2 -id) == (self.sqrt_nodes - 1)): # do not add the same link twice
                for i in range(self.sqrt_nodes, self.nodes+1, self.sqrt_nodes):
                    if id2 == i:
                        break;
                    else:
                        self.connect_neighbor(id, id2)

    def setup_radio(self):
        for id in range(1, self.nodes+1):
            # regular creation of nodes

            x = (((id-1)//math.sqrt(self.nodes)))*self.distance
            y = (((id-1)%math.sqrt(self.nodes)))*self.distance
            z = 0

            print "Location of node", id, "is", (x, y, z)

            self.id2xyz_dict[id]   = (x, y, z)
           # self.xyz2id_dict[x]    = {}
           # self.xyz2id_dict[x][y] = id

        self.setup_radio_general()
