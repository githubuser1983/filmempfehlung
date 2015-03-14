#!/usr/bin/python

# sudo apt-get install python-mysqldb
# sudo apt-get install python-daemon

import os,random,sys,time, datetime
import logging,sys, daemon
#rom cgi import parse_qs, escape
#import cvxopt, linearsvm
import MySQLdb, numpy as np, math
from pyflann import *
#from xml.sax.saxutils import escape


def init():
  global thisfilepath
  global db
  global cur
  global NUMBER_OF_KNN
  global items
  global itemsX
  global links

  thisfilepath = os.path.dirname(__file__)
  logging.basicConfig(filename=os.path.join(thisfilepath,"knn-log.txt"), level=logging.DEBUG, format = '%(asctime)s %(message)s')
  sys.path.append(thisfilepath)
  mysqlNotConnected = True
  waitAtMost30Sec = True
  secWaited = 0
  maxSecWait = 30
  while mysqlNotConnected and waitAtMost30Sec:
    try:
      db = MySQLdb.connect(host="localhost", user="orges", passwd="12345",db="empfehlung")
      cur = db.cursor()
      mysqlNotConnected = False
    except MySQLdb.Error, e:
      time.sleep(1)
      secWaited += 1
      if secWaited > maxSecWait:
        waitAtMost30Sec = False
      msg = "Error: Cant connect to Mysql, waited %s/%s second(s) ..." % (secWaited,maxSecWait)
      print msg
      logging.info(msg)
  if not waitAtMost30Sec and mysqlNotConnected:
    msg = "Error: Cant connect to Mysql, stopping"
    print msg
    logging.info(msg)
    sys.exit(1)
  #>>> cur.execute("select tid,imdbRating,ratingCount,duration,year from imdb limit 10;")

  NUMBER_OF_KNN = 50
  try:
    fileForQuery = open(os.path.join(thisfilepath,'../server/fileForQuery.sql'),'r')
    query = fileForQuery.read()
    fileForQuery.close()
  except Error:
    log.error("fileForQuery.sql not found")
    query="""
      select tid,title,
        year,
        imdbRating,
        ratingCount,
        nrOfWins
    from imdb where type='video.movie' and imdbRating > 0 and year > 0
    ;
    """

  cur.execute(query)
  #cur.execute("select tid,title,year from imdb where type='video.movie' and imdbRating > 0 and year > 0;")
  #items = dict([ (row[0],(row[1:])) for row in cur.fetchall()])
  rows = cur.fetchall()
  items = dict([ (rows[i][0],i) for i in range(0,len(rows))])
  index2Tid = dict([(i,rows[i][0]) for  i in range(0,len(rows))])
  #print items
  logging.info("creating itemX..")
  print "creating itemX.."
  itemsX = np.matrix([[float(x) for x in rows[i][1:]] for i in range(0,len(rows))])
  #print(itemsX.size)
  # rescale, mean = 0, sd = 1, if sd=0 -> sd = 1:
  msg = "rescaling itemsX, mean = 0, sd = 1, if sd = 0 -> sd = 1"
  logging.info(msg)
  print msg
  print itemsX.shape[1]
  dim = itemsX.shape[1]
  print itemsX[:,4]
  #sd = np.std(itemsX,axis=0)
  for d in range(0,dim):
    msg = "d = %s " % d
    logging.info(msg)
    print msg

    sd = np.sqrt(np.var(itemsX[:,d]))
    msg = "sd = %s " % sd
    logging.info(msg)
    print msg
    msg = "mean = %s " % np.mean(itemsX[:,d])
    logging.info(msg)
    print msg
    if abs(sd) < 0.0000001:
      msg = "new sd=1 (previously sd=0) at dim = %s" % d
      logging.info(msg)
      print(msg)  
      sd = 1
    itemsX[:,d] = (itemsX[:,d] - np.mean(itemsX[:,d]))/sd
    msg = "new mean = %s " % np.mean(itemsX[:,d])
    logging.info(msg)
    print(msg)
    msg = "new var = %s" % np.var(itemsX[:,d])
    logging.info(msg)
    print(msg)
    
  # compute knn:
  flann = FLANN()
  result,dists = flann.nn(itemsX,itemsX,NUMBER_OF_KNN,algorithm="kmeans", branching=32,iterations=7,checks=16);
  
  print result.shape
  # write knn to db:
  query = "drop table if exists imdb_knn;"
  cur.execute(query)
  db.commit()    
  query = """
    create table imdb_knn (
      tid VARCHAR(20),
      nTid VARCHAR(20),
      dist DECIMAL(20,10),
      PRIMARY KEY(tid,nTid)
    );
  """
  cur.execute(query)
  db.commit()
  for i in range(result.shape[0]):
    tuplelist = [(index2Tid[result[i,0]],index2Tid[result[i,j]],dists[i,j]) for j in range(1,result.shape[1])]
    query = "insert into imdb_knn values %s;" % ",".join([str(t) for t in tuplelist])
    cur.execute(query)
  db.commit()
    #print tuplelist

    
def main():
  #apt-get install python-cherrypy3
  try:
    logging.info("Starting computation of knn")
    init()
  except KeyboardInterrupt:
    print "Stopping computation of knn because of KeyboarInterrupt"
    logging.info("Stopping computation of knn because of KeyboarInterrupt")


if __name__ == "__main__":
  #with daemon.DaemonContext():
  try:
    main()
  except Exception,e:
    msg = "stopping because of Error: " + str(e) 
    print msg
    logging.info(msg)
    sys.exit(1)
