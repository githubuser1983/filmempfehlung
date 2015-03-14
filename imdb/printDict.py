#!/usr/bin/python

import sys

if __name__ == '__main__':
  D = {}
  for fn in sys.argv[1:]:
    name = fn.split('.txt')[0]
    file = open(fn,'r')
    lines = file.readlines()
    file.close()
    d = {}
    for line in lines:
      val,key = line.strip().split(' ')
      d[key] = int(val)
    D[name] = d
  print "D = %s" % D

