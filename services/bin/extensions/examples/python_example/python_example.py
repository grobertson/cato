""" Not a python tutorial, just a simple example of a python Cato command extension. """

import sys

if (len(sys.argv) > 1):
    print "Hello %s!" % (sys.argv[1])
