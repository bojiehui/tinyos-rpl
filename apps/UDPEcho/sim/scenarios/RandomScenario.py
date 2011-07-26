from sim.scenarios.Scenario import Scenario
from sim.utils.helper import *
from sim.config import *

import random

class RandomScenario(Scenario):
    def __init__(self, t, si):
        """
        """
        Scenario.__init__(self, t, si)
  
        self.scen_x = si.distance*math.sqrt(si.nodes)
        self.scen_y = si.distance*math.sqrt(si.nodes)

    def connect_neighbors(self, id):
        for id2 in range(1, self.nodes+2):
            if id == id2:
                # do not connect with the same node
                continue
            self.connect_neighbor(id, id2)

    def setup_radio(self):
        #CHECK: if network is randomized
        if RANDOMIZE_TOPOLOGY == "True":
            pass
        else:
            random.seed(0)

        self.id2xyz_dict[1]    = (0, 0, 0)
        #self.xy2id_dict[0]    = {}
        #self.xy2id_dict[0][0] = 1

        for id in range(2, self.nodes+2):
            # randomly create nodes

            x = random.uniform(0, self.scen_x)
            y = random.uniform(0, self.scen_y)
            z = 0
           
            self.id2xyz_dict[id]   = (x, y, z)
            #self.xy2id_dict[x]    = {}
            #self.xy2id_dict[x][y] = id

        self.setup_radio_general()
