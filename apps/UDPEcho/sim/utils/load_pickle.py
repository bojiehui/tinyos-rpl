#! /usr/bin/python

import pickle
from optparse import OptionParser

if __name__ == "__main__":
    optparser = OptionParser()
    optparser.add_option("-f",
                         "--file",
                         help="pickle file to load and print")
    (optionsp, argsp) = optparser.parse_args()

    if optionsp.file == None:
        print "Usage: python sim/utils/loac_pickle.py -f <file>"
    else:
        obj = pickle.load(open(optionsp.file, 'rb'))
        print obj
