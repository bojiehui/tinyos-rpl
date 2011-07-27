#! /usr/bin/python

import numpy as np
from optparse import OptionParser

if __name__ == "__main__":
    optparser = OptionParser()
    optparser.add_option("-f",
                         "--file",
                         help="numpy file to load and print")
    (optionsp, argsp) = optparser.parse_args()

    if optionsp.file == None:
        print "Usage: python sim/utils/load_numpy.py -f <file>"
    else:
        obj = np.load(optionsp.file, "r")
        print "Str:", obj
        print "Repr:", repr(obj)
