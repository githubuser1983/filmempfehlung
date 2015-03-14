#!/usr/bin/python

import os,sys

sql = """SELECT tid,title FROM imdb 
WHERE tid IN ('%s')
ORDER BY CASE tid
"""
tids = sys.argv[1].split(',')

for i in range(len(tids)):
  tid = tids[i]
  sql += ( "when '%s' then %s \n" % (tid,i))

sql += 'end;'

print sql % "','".join(tids)  
