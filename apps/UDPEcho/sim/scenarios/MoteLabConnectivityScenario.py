import cPickle
import numpy as np

from sim.scenarios.Scenario import Scenario
from sim.utils.helper import *
from sim.config import *

class MoteLabConnectivityScenario(Scenario):
    def __init__(self, t, ei, si):
        """
        """
        Scenario.__init__(self, t, ei, si)
        self.mlc = cPickle.load(open(SCENARIOFILE, 'rb'))

    def setup_radio(self):
        self.motelabnodes = self.mlc.getAllNodes()
        for sender in self.mlc.links.keys():
            if sender not in self.motelabnodes:
                continue
            for receiver in self.mlc.links[sender].keys():
                if receiver not in self.motelabnodes:
                    continue
                self.r.add(sender, receiver, self.mlc.RSSI[sender][receiver])
        for node in self.mlc.noise.keys():
            if node not in self.motelabnodes:
                continue
            for noise in self.mlc.noise[node]:
                self.t.getNode(node).addNoiseTraceReading(int(noise))
                self.t.getNode(node).createNoiseModel()

        for node in self.motelabnodes:
            self.id2xy_dict[node]   = (None, None)
            #self.xy2id_dict[x]    = {}
            #self.xy2id_dict[x][y] = id

        # TODO: use real neighbor values
        neighbors_min  = np.zeros(self.nodes+2)
        neighbors_mean = np.zeros(self.nodes+2)
        neighbors_max  = np.zeros(self.nodes+2)

        np.save(self.filenamebase+"_neighbors_min.npy", neighbors_min)
        np.save(self.filenamebase+"_neighbors_mean.npy", neighbors_mean)
        np.save(self.filenamebase+"_neighbors_max.npy", neighbors_max)
