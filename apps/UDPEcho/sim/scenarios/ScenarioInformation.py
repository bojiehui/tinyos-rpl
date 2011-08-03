
FILENAMEBASE = "sim/output/"

from sim.config import *
from sim.scenarios.Scenario import *

class ScenarioInformation:
    def __init__(self,
                 startdate,
                 run,
                 nodes,
                 distance,
                # sec_after_inject,
                # turnoff_node_time,
                 randomize_boot,
                 randomize_seed):

        self.startdate = startdate
        self.run = run
        self.nodes = nodes
        self.distance = distance
        #self.distance = get_distance(distance, sqr_nodes)

       # self.sec_after_inject = sec_after_inject
       # self.turnoff_node_time = turnoff_node_time

        self.randomize_boot = randomize_boot # CHECK: OK here?
        self.randomize_seed = randomize_seed # CHECK: OK here?

    def get_suite_dir(self):
        return "suite_" + str(self.startdate) + "/"

    def get_run_dir(self):
        return "run_" + str(self.run) + "/"

    def get_topo_dir(self):
        return "topo_" + str(self.nodes) + "/"

    def get_dist_dir(self):
        return "dist_" + str(self.distance) + "/"

    def get_full_dir(self):
        return FILENAMEBASE + \
            self.get_suite_dir() + \
            self.get_topo_dir() + \
            self.get_dist_dir() + \
            self.get_run_dir()

    def get_montecarlo_full_dir(self):
        return FILENAMEBASE + \
            self.get_suite_dir() + \
            self.get_topo_dir() + \
            self.get_dist_dir()

    def get_topo_full_dir(self):
        return FILENAMEBASE + \
            self.get_suite_dir() + \
            self.get_topo_dir()

    def get_suite_full_dir(self):
        return FILENAMEBASE + \
            self.get_suite_dir()

    def createfilenamebase(self):
        return self.get_full_dir() \
            + "file_suite" + str(self.startdate) + "_" \
            + "topo" + str(self.nodes) + "_" \
            + "dist" + str(self.distance) + "_" \
            + "run" + str(self.run) # + "_"

#            + "turnoff" + str(self.turnoff_node_time)

    def create_montecarlo_filenamebase(self):
        return self.get_montecarlo_full_dir() \
            + "file_suite" + str(self.startdate) + "_" \
            + "topo" + str(self.nodes) + "_" \
            + "dist" + str(self.distance)

    def create_topo_filenamebase(self):
        return self.get_topo_full_dir() \
            + "file_suite" + str(self.startdate) + "_" \
            + "topo" + str(self.nodes)

    def create_suite_filenamebase(self):
        return self.get_suite_full_dir() \
            + "file_suite" + str(self.startdate)

    def __str__(self):
        return "="*40 + "\n" \
            "Start:\t\t\t" + str(self.startdate) \
            + "\nnodes\t\t\t" + str(self.nodes) \
            + "\ndistance\t\t" + str(self.distance) \
            + "\nrun\t\t\t" + str(self.run) \
            + "\nrandomize_boot\t\t" + str(self.randomize_boot) \
            + "\nlogfilename\t\t" + self.createfilenamebase() \
            + "\n" + "="*40
