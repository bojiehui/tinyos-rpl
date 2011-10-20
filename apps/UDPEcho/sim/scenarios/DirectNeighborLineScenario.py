from sim.scenarios.Scenario import Scenario
from sim.utils.helper import *
from sim.config import *

class DirectNeighborLineScenario(Scenario):
    def __init__(self, t, si):
        """
        """
        Scenario.__init__(self, t, si)

        self.distance = si.distance
        self.scen_x = si.distance*si.nodes
        self.scen_y = 0
        self.scen_z =0

    def connect_neighbors(self, id):
        for id2 in range(1, self.nodes+1):
            if id == id2:
                # do not connect with the same node
                continue
            if abs(id - id2) == 1:
            #    # only connect direct neighbor, with realistic
            #    # propagation, though
                self.connect_neighbor(id, id2)

    def setup_radio(self):
        for id in range(1, self.nodes+1):
            # regular creation of nodes

            if id == 1:
                x = 0
                y = 0
                z = 0
            else:
                x = (id-1)*self.distance
                y = 0
                z = 0
            self.id2xyz_dict[id]   = (x, y, z)
            #self.xy2id_dict[x]    = {}
            #self.xy2id_dict[x][y] = id

        self.setup_radio_general()
