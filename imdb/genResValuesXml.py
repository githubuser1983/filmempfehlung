#!/usr/bin/python

import csv,sys
from xml.dom.minidom import Text, Element

#t = Text()
#e = Element('item')

#t.data = '<bar><a/><baz spam="eggs"> & blabla &entity;</>'
#e.appendChild(t)

#Then you will get nicely escaped XML string:

#>>> e.toxml()

if __name__ == "__main__":
  csvfile = open(sys.argv[1],'r')
  reader = csv.DictReader(csvfile,delimiter=',',strict=True,escapechar='\\')
  attributeNames = ['title','tid', 'url', 'year']
  fieldValues = dict([(fn,[]) for fn in attributeNames])
  for row in reader:
    for fn in attributeNames:
      fieldValues[fn].append(row[fn])
  csvfile.close()
  xmlfile = open('/home/orges/empfehlung/app/res/values/imdb.xml','w')
  xmlfile.write('<?xml version="1.0" encoding="utf-8"?>\n')
  xmlfile.write('<resources>\n')
  for fn in attributeNames:
    xmlfile.write('  <string-array name="%s">\n' % fn)
    for item in fieldValues[fn]:
      t = Text()
      e = Element('item')
      item = item.replace("'","\\'") #hack
      t.data = item
      e.appendChild(t)
      xmlfile.write(e.toxml()+'\n')
    xmlfile.write('</string-array>\n')
  xmlfile.write('</resources>\n')
  xmlfile.close()
