#!/usr/bin/python

import re, sys, os, HTMLParser,math
from genres_names import D

def sortByOcc(list,reverse=False):
  sorted = [(list.count(x),x) for x in set(list) ]
  sorted.sort(reverse=reverse)
  return sorted

def getFromTid(txt):
  titles = re.compile('tt[0-9]{3,70}').findall(txt)
  return sortByOcc(titles,reverse=True)[0][1] # Take the title which occurs most

def getToTids(txt):
  return [re.compile('tt[0-9]+').findall(x)[0] for x in set(re.compile('/title/tt[0-9]+/\?ref_=tt_rec_tti').findall(txt))]


if __name__ == "__main__":
  # usage:
  # ~/empfehlung/imdb$ ./readAttributesAndWriteToFile.py test.csv titles/*html*
  removeDuplicateFiles = True
  fileToWrite = open(sys.argv[1],"w")
  filesToReadAttributes = sys.argv[2:]
  attributeNames = ['fromTid', 'toTid']
                    #,'meanGenre','sdGenre','minGenre','maxGenre'
  idsAlreadySeen = set([])
  delim = ','
  fileToWrite.write(delim.join(attributeNames)+"\n")
  for fn in filesToReadAttributes:
    lineDict = {}
    f = open(fn,'r')
    txt = f.read()
    print fn
    # read Attributes:
    lineDict['fromTid'] = getFromTid(txt)
    toTids = getToTids(txt)
    if not lineDict['fromTid'] in idsAlreadySeen: # Take only those which we have not already seen:
      for toTid in toTids:
        # print Attributes to file in order given by attributeNames:
        line = ''
        lineDict['toTid'] = toTid
        for attribute in attributeNames:
          line += lineDict[attribute].replace(delim,"\\"+delim)+delim
        line = line[0:( len(line) - len(delim) )] + "\n"
        fileToWrite.write(line)
      idsAlreadySeen.add(lineDict['fromTid'])
      f.close()
    elif removeDuplicateFiles: # if file is duplicate and we want to remove it, delete it:
      f.close()
      os.remove(fn)
    
