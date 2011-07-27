#!/usr/bin/env python

from __future__ import division

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import scipy.stats as stats
import re

from sim.utils.helper import *
from sim.config import *

from sim.evaluation.graph.suite.SuiteEvaluationPackets import *
from sim.evaluation.graph.suite.SuiteEvaluationHist import *

class SuiteEvaluation:
    def __init__(self):
        pass

    def execute(self,
                executable_info,
                scenario_info,
                nodes_list,
                distance_list,
                iterations):

        print "="*40
        print "Executing SuiteEvaluation:"
        print "="*40

        if SUITE_EVAL_LIST.count("SuiteEvaluationPackets") > 0:
            sep = SuiteEvaluationPackets()
            sep.execute(executable_info,
                        scenario_info,
                        nodes_list,
                        distance_list,
                        iterations)
        if SUITE_EVAL_LIST.count("SuiteEvaluationHist") > 0:
            seh = SuiteEvaluationHist()
            seh.execute(executable_info,
                        scenario_info,
                        nodes_list,
                        distance_list,
                        iterations)
