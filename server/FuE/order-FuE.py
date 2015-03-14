#!/usr/bin/python

# sudo apt-get install python-mysqldb
# sudo apt-get install python-daemon

import cgi,re,os,mimetypes,datetime,random,sys,time, datetime
import logging,sys, time, traceback
import MySQLdb, numpy as np, math
from sklearn import svm
import re


def init():
  global index2Tid, thisfilepath, db, cur, NUMBER_OF_REC_ITEMS
  global tidReg, items, itemsX, urls, links, allKnn, fieldNames, svc
  global outfile

  
  svc = svm.SVC(kernel='linear')
  
  outfile = open("outfile.tsv", "w")

  tidReg = re.compile("tt[0-9]+")

  thisfilepath = os.path.dirname(__file__)
  logging.basicConfig(filename=os.path.join(thisfilepath,"log-FuE.txt"), level=logging.DEBUG, format = '%(asctime)s %(message)s')
  sys.path.append(thisfilepath)
  mysqlNotConnected = True
  waitAtMost30Sec = True
  secWaited = 0
  maxSecWait = 30
  while mysqlNotConnected and waitAtMost30Sec:
    try:
      db = MySQLdb.connect(host="192.168.178.01", user="orges", passwd="12345",db="empfehlung")
      #db = MySQLdb.connect(host="localhost", user="orges", passwd="12345",db="empfehlung")
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

  NUMBER_OF_REC_ITEMS = 50
  try:
    fileForQuery = open(os.path.join(thisfilepath,'fileForQuery.sql'),'r')
    query = fileForQuery.read()
    fileForQuery.close()
  except Exception:
    logging.error("fileForQuery.sql not found")
    query="""
      select tid,title,
        year,
        imdbRating,
        ratingCount,
        nrOfWins
    from imdb where type='video.movie' and imdbRating > 0 and year > 0
    ;
    """
  print "reading items from mysql..."
  # items
  cur.execute(query)
  rows = cur.fetchall()
  items = dict([ (rows[i][0],i) for i in range(0,len(rows))])
  index2Tid = dict([(i,rows[i][0]) for  i in range(0,len(rows))])

  #print items
  logging.info("creating itemX..")
  print "creating itemX.."
  #itemsX = cvxopt.matrix([[float(x) for x in rows[i][1:]] for i in range(0,len(rows))]).trans()
  itemsX = np.matrix([[float(x) for x in rows[i][1:]] for i in range(0,len(rows)) ] )
  print itemsX

  # rescale, mean = 0, sd = 1, if sd=0 -> sd = 1:
  msg = "rescaling itemsX, mean = 0, sd = 1, if sd = 0 -> sd = 1"
  logging.info(msg)
  print msg
  dim = itemsX.shape[1]
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
    
  #get all links:
  logging.info("reading all links...")
  print "reading all links..."
  links = getAllLinks()
  print "all links read."
  print "reading all knn from db...."
  allKnn = getAllKnn()
  #for tid in items.keys():
  #  print tid
  #  for x in items[tid][1:]:
  #    try:
  #      float(x)
  #    except TypeError:
  #      print x
  #      sys.exit(1)
  print "all knn read."

def getAllKnn():
  """
    Return a dictionary with knn:
       tid:[(tid1,dist1),(tid2,dist2),...]
  """
  #cur.execute("SET GLOBAL group_concat_max_len=1000000;")
  #db.commit()

  query = """
  select tid, nTid, dist from imdb_knn order by tid asc, dist asc;
  """
  cur.execute(query)
  rows = cur.fetchall()
  result = {}
  for row in rows:
    tid = row[0]
    nTid = row[1]
    dist = row[2]
    if result.has_key(tid):
      result[tid].append((nTid,dist))
    else:
      result[tid] = [(nTid,dist)]
  return result

def getAllLinks():
  """
  Return all links to "all" items, as dictionary
  """
  cur.execute("select fromTid,toTid from imdbLinks where toTid in (select tid from imdb where type='video.movie' and imdbRating > 0 and year > 0 and duration > 0 and Adult = 0);")
  rows = cur.fetchall()
  result = []
  #links = dict([(row[0],(row[1:])) for row in rows])
  links = {}
  for row in rows:
    tid = row[0]
    if links.has_key(tid):
      links[tid].append(row[1])
    else:
      links[tid] = [row[1]]
  return links

def knnPrecomputed(orderedItems,k):
  """
  Return the k nearest neighbours of the first orderedItem
  """
  result = []
  for tid in orderedItems:
    result.extend([ tid for tid,dist in allKnn[tid][0:k]])
  return list(set(result))

def knnLinks(orderedItems):
  """
  todo: alle links beim starten des servers in ein globales dictionary laden -> keine sql-Abfrage noetig, wenn user ein request schickt.
  """
  result = []
  for tid in orderedItems:
    result.extend(list(links[tid]))
  return list(set(result))

def ordered(orderedItems):
  #logging.info(environ.get('QUERY_STRING',''))
  start_time = time.time()
  #parameters = parse_qs(environ.get('QUERY_STRING',''))
  orderedItems = orderedItems.split(",")
  possibleItemsToBeSorted = knnPrecomputed(orderedItems, 50)
  possibleItemsToBeSorted.extend(knnLinks(orderedItems)) # take only the k-nearest neighbours of request + those which are linked to request
  itemsToBeSorted = possibleItemsToBeSorted
  result = computeRecItemsORDERSVM(orderedItems,itemsToBeSorted,NUMBER_OF_REC_ITEMS) #filteredKnnItems,100)
  recItems = result["recItems"]
  #line = "%s\t%s\t%s\t%s\n" % (result["query"],result["wS"],result["sumW"],result["scoresSorted"])
  #outfile.write(line)
  elapsed_time = time.time() - start_time
  msg = "time to process query: %s" % elapsed_time
  print(msg)
  logging.info(msg)
  return result

def computeRecItemsORDERSVM(orderedItems,filteredItems,maxNumOfRecItems):
  """
     orderedItems + SVOR -> ordering through weight vectors.
     filteredItems + ordering through weight vectors --> result
  """
  result = {}
  tidToNr = dict([(tid,tuple(itemsX[items[tid]].tolist()[0])) for tid in orderedItems])
  print tidToNr
  diff = []
  y = []
  orderedItemsX = []
  for i in range(len(orderedItems)):
    id = orderedItems[i]
    orderedItemsX.append(list(tidToNr[id]))
  X = np.matrix(orderedItemsX)
  print "X = ", X
  
  sorted = []
  score = {}
  wS = []
  sumw = np.matrix([[0] for i in range(0,itemsX.shape[1])])
  print "sumw.size = ", sumw.size
  for i in range(1,len(orderedItems)):
    y = [+1 for k in range(0,i)]
    y.extend([-1 for k in range(i,len(orderedItems))])
    print "len(y) = ", len(y)
    print "X.size = ", X.shape
    sol1 = svc.fit(X,y)
    w = sol1.coef_.transpose()
    wS.append(w)
    print " |w| = ", np.linalg.norm(w)
    print "w.size = ", w.size
    sumw = sumw + w
    n = datetime.datetime.now()
    t = n.strftime('%Y-%m-%d %H:%M:%S')
  sorted =  []
  for tid in filteredItems:
    s = itemsX[items[tid],:]*sumw
    score[tid] = s[0]
  print "itemsX = " 
  for tid in score.keys():
    print tid, score[tid]
    sorted.append((score[tid],tid))
  sorted.sort(reverse=True)
  result["query"] = orderedItems
  result["sumW"] = sumw
  result["wS"] = wS
  result["scoresSorted"] = sorted
  result["recItems"] = "%s" % [tid for s,tid in sorted[0:maxNumOfRecItems]]
  return result



def computeRecItems(orderedItems,filteredKnnItems):
  """
     orderedItems + SVOR -> ordering through weight vector.
     filteredKnnItems + ordering through weight vector --> result
  """
  tidToNr = dict([(tid,tuple(itemsX[items[tid]].tolist()[0])) for tid in orderedItems])
  print tidToNr
  #tidToNr = dict([ (row[0],(row[1:])) for row in cur.fetchall()])
  # to be implemented:
  # do some svm computation:
  diff = []
  y = []
  for i in range(len(orderedItems)):
    for j in range(i+1,len(orderedItems)):
      id1 = orderedItems[i]
      id2 = orderedItems[j]
      x1 = tidToNr[id1]
      x2 = tidToNr[id2]
      # herbrich, ranksvm: (minimizes kendalls tau):
      d12 = [float(x1[k] - x2[k]) for k in range(len(x1))]
      # minimize spearmans footroole ?:
      #d12 = [float(x1[k] - x2[k])*abs(i-j) for k in range(len(x1))]
      d21 = [-d for d in d12]
      diff.append(d12)
      diff.append(d21)
      y.append(+1)
      y.append(-1)

  m = 20
  #X = 2.0*cvxopt.uniform(m,2)-1.0
  #X = cvxopt.matrix(diff).trans()
  X = np.matrix(diff)
  #print(X)
  #d = cvxopt.matrix([2*int(v>=0)-1 for v in cvxopt.mul(X[:,0],X[:,1])],(m,1))
  #d = cvxopt.matrix(y)
  d = np.matrix(y).transpose()
  #print(d)
  gamma = 2.0; kernel = 'linear'; sigma = 1.0; width = 20
  sol1 = linearsvm.softmargin(X, d, gamma, kernel, sigma)
  print "w = "
  w = sol1['w']
  print w
  n = datetime.datetime.now()
  t = n.strftime('%Y-%m-%d %H:%M:%S')
  values = ",".join([str((t,w[i])) for i in range(len(w))])
  query = "insert into weight_vector (time,x) values %s ;" % values
  print query
  cur.execute(query)
  db.commit()
  #
  sorted = []
  for tid in filteredKnnItems:
    s = itemsX[items[tid],:]*w
    print s
    sorted.append((s[0],tid))
  sorted.sort(reverse=True)
  #logging.info(sol1["w"])
  return [tid for s,tid in sorted]


def main():
  init()
  f = open("requests",'r')
  nrOfQuery = 0
  outfile.write("nrOfQuery;type;tid;nrOfweight;score;imdbRating;year\n")
  for line in f:
    query = line.replace("\n","")
    query = ",".join(tidReg.findall(query))
    result = ordered(query)
    for tid in result["query"]:
       vector = itemsX[items[tid],:].tolist()[0]
       vectorStr = ";".join(str(x) for x in vector)
       outfile.write( "%s;query;%s;NULL;NULL;%s\n" % (nrOfQuery,tid,vectorStr))
    nrOfWeight = 1
    for weight in result["wS"]:
      vector = weight.tolist()
      vectorStr = ";".join(str(x[0]) for x in vector)
      outfile.write("%s;weight;NULL;%s;NULL;%s\n" % (nrOfQuery,nrOfWeight,vectorStr))
      nrOfWeight += 1
    for score,tid in result["scoresSorted"]:
       vector = itemsX[items[tid],:].tolist()[0]
       vectorStr = ";".join(str(x) for x in vector)
       score = score.tolist()[0][0]
       outfile.write( "%s;score;%s;NULL;%s;%s\n" % (nrOfQuery,tid,score,vectorStr))
    nrOfQuery += 1
  f.close()

if __name__ == "__main__":
  #with daemon.DaemonContext():
  try:
    main()
    outfile.close()
  except Exception,e:
    type_, value_, traceback_ = sys.exc_info()
    msg = "stopping because of Error: " +"\n".join(traceback.format_exception(type_,value_,traceback_))
    print msg
    logging.info(msg)
    outfile.close()
    sys.exit(1)
