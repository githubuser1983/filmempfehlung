#!/usr/bin/python

# sudo apt-get install python-mysqldb
# sudo apt-get install python-daemon

import cgi,re,os,mimetypes,datetime,random,sys,time, datetime
import logging,sys, time, traceback
from cgi import parse_qs, escape
import httpstatus, MySQLdb, numpy as np, math
from xml.sax.saxutils import escape
from sklearn import svm
from PIL import Image
import StringIO


def init():
  global index2Tid, thisfilepath, db, cur, NUMBER_OF_REC_ITEMS
  global items, itemsX, urls, links, allKnn, itemsForXml, fieldNames, svc
  global images

  images = {}  
  svc = svm.SVC(kernel='linear')

  urls = [
  ('/img', img),
  ('/ordered', ordered),
  ('/', index),
  ]

  thisfilepath = os.path.dirname(__file__)
  logging.basicConfig(filename=os.path.join(thisfilepath,"log.txt"), level=logging.DEBUG, format = '%(asctime)s %(message)s')
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
  #cur.execute("select tid,title,year from imdb where type='video.movie' and imdbRating > 0 and year > 0;")
  #items = dict([ (row[0],(row[1:])) for row in cur.fetchall()])
  rows = cur.fetchall()
  items = dict([ (rows[i][0],i) for i in range(0,len(rows))])
  index2Tid = dict([(i,rows[i][0]) for  i in range(0,len(rows))])

  #print items
  logging.info("creating itemX..")
  print "creating itemX.."
  #itemsX = cvxopt.matrix([[float(x) for x in rows[i][1:]] for i in range(0,len(rows))]).trans()
  itemsX = np.matrix([[float(x) for x in rows[i][1:]] for i in range(0,len(rows)) ] )
  print itemsX

  print "reading itemsForXml from mysql..."
  try:
    fileQueryForItemsInXml = open(os.path.join(thisfilepath,'queryForItemsInXml.sql'),'r')
    query = fileQueryForItemsInXml.read()
    fileForQueryForItemsInXml.close()
  except Exception:
    logging.error("queryForItemsInXml.sql not found")
    queryForItemsInXml="select i.tid tid,i.title title,i.url url,replace(IFNULL(p.imageUrl,''),'https://image.tmdb.org/t/p/original/','http://www.url-to-server.com/img?imgkey=') posterPathUrl from imdb i left join imdbIdPosterPath p on i.tid = p.imdb_id;"


  #cur.execute("select tid,title,url from imdb;")
  cur.execute(queryForItemsInXml)
  fieldNames = [i[0] for i in cur.description]
  rows = cur.fetchall()
  itemsForXml = dict([ (row[0], (row[0:])) for row in rows])


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
  print "reading images and saving thumbnails to ram..."
  indir = '/home/orges/empfehlung/tmdb/requests-master/img/'
  for root, dirs, filenames in os.walk(indir):
    for f in filenames:
        imageFile = os.path.join(root, f)
        key = f.replace(".jpg","")
        size = 50,50
        print "rescaling %s " % imageFile
        try:
            im = Image.open(imageFile)
            im.thumbnail(size, Image.ANTIALIAS)
            output = StringIO.StringIO()
            im.save(output, "JPEG")
            contents = output.getvalue()
            output.close()
            images[key] = contents
            print "%s rescaled and saved" % imageFile
        except IOError:
            print "cannot create thumbnail for '%s'" % imageFile

def unicodeToHTMLEntities(text):
  text = cgi.escape(text).encode('ascii','xmlcharrefreplace')
  return text

def urlmapping(environ, start_response):
  req_url = environ['PATH_INFO']
  logging.info( environ['REMOTE_ADDR']+";"+environ['REQUEST_METHOD']+";"+req_url+";"+environ['QUERY_STRING'])
  start_app = None
  start_app_gefunden = False
  for url,app in urls:
    if not start_app_gefunden:
      reglist = re.compile(url).findall(req_url) # todo: wie kann man es vermeiden bei jedem Request re.compile auszufuehren?
      if len(reglist) > 0: #Treffer
        print reglist
        print req_url
        start_app_gefunden = True
        start_app = app
  if start_app:
    result = start_app(environ, start_response)
    return result
  else: # Fehler 404
    start_response("404 Not Found", [("Content-Type","text/plain")])
    return ["404 Not Found"]

#<?xml version="1.0" encoding="utf-8"?>
#<votes>
#  <row Id="1" PostId="2" VoteTypeId="2" CreationDate="2010-07-28T00:00:00.000" />
#  <row Id="2" PostId="1" VoteTypeId="2" CreationDate="2010-07-28T00:00:00.000" />
#  <row Id="3" PostId="4" VoteTypeId="2" CreationDate="2010-07-28T00:00:00.000" />
def genXmlFromItems(itemList):
  #cur.execute("select i.tid,title,url from imdb i, imdb_igraph g where i.tid = g.tid and i.tid in ('%s') order by pr desc, imdbRating desc;" % "','".join(itemList))
  # field_names = fn:
  #fn = [i[0] for i in cur.description]
  #rows = cur.fetchall()
  #tidToNr = dict([ (row[0],(row[0:])) for row in rows])
  xmlstr = '<?xml version="1.0" encoding="utf-8"?>\n <imdb>\n'
  # ein bisschen Werbung in eigener Sache:
  ga = '<row rank="0" tid="tt0123" title="GebrauchteApps" url="http://www.gebrauchte-apps.de/" posterPathUrl="http://www.gebrauchte-apps.de/ic_launcher.png" />'
  xmlstr += ga
  for i in range(len(itemList)):
    tid = itemList[i] # ordering is given by itemList
    #tid = rows[i][0] # ordering is given by sql query
    row = itemsForXml[tid] #tidToNr[tid] 
    #print tid, row
    rowstr = '<row rank=\"%s\" %s />\n'
    rowstr = rowstr % (i+1, " ".join(["%s=\"%s\"" % (fieldNames[j],escape(row[j], {"'":"\'"})) for j in range(len(row))]))
    xmlstr += rowstr
  xmlstr += "</imdb>"
  #print xmlstr
  return xmlstr
    
def writeOrderedItemsToDb(orderedItems):
  n = datetime.datetime.now()
  t = n.strftime('%Y-%m-%d %H:%M:%S')
  values = ",".join([str((t,tid)) for tid in orderedItems])
  query = "insert into imdb_ordered (time,tid) values %s ;" % values
  print query
  cur.execute(query)
  db.commit()


def filterRecKnownItems(recItems):
  """
    Shows only those Items which the user does not know (or at least has not ordered them yet)
  """
  cur.execute("select distinct tid from imdb_ordered;")
  knownTids = [row[0] for row in cur.fetchall()]
  return list(set(recItems).difference(knownTids))


def mergeOrderedItems(orderedItems):
  """
    Take the last 20 orderings from user.
    Sort by time desc
    Take only the first ordered item (ordered by time desc)
    merge those items with the ordered items
    return the list
  """
  # test:
  #return orderedItems
  ## idee hier: nimm die top 5( waehrend einer gewissen zeisptanne z.B. alle bewerteten filme) und die flop 5 die der user bewertet hat und "merge" sie mit der aktuellen anfrage vom user
  queryMix = """
  select * from (
 # die top 5 aller filme:
 (
  select tid, sum(score) sumscore from
  (
  select o.time, x.max-o.id + 1 score, o.tid from imdb_ordered o,
  ( select * from
    (select time,min(id) min, max(id) max, count(*) cnt from imdb_ordered group by time order by time desc ) t 
     where cnt < 20 ) x 
  where x.time = o.time 
  ) r group by tid order by sumscore desc limit 5
 )
  union distinct
 (
  # die flop 5 aller filme:
  select tid, sum(score) sumscore from
  (
  select o.time, x.max-o.id + 1 score, o.tid from imdb_ordered o,
  ( select * from
    (select time,min(id) min, max(id) max, count(*) cnt from imdb_ordered group by time order by time desc ) t
     where cnt < 20 ) x
  where x.time = o.time
  ) r group by tid order by sumscore asc limit 5
 )
  union distinct
 (
  # die aktuelle anfrage
  select tid, sum(score) sumscore from
  (
  select o.time, x.max-o.id + 1 score, o.tid from imdb_ordered o,
  ( select * from
    (select time,min(id) min, max(id) max, count(*) cnt from imdb_ordered group by time order by time desc ) t
     where cnt < 20 ) x
  where x.time = o.time
  ) r where tid in ('%s') group by tid
 )
  ) x order by sumscore desc
  ;
  """ % "','".join(orderedItems)
  
  query = """
   select tid, sum(score) sumscore from
  (
  select o.time, x.max-o.id + 1 score, o.tid from imdb_ordered o,
  ( select * from
    (select time,min(id) min, max(id) max, count(*) cnt from imdb_ordered group by time order by time desc ) t
     where cnt < 20 ) x
  where x.time = o.time
  ) r group by tid order by sumscore desc
  ;
  """
  cur.execute(query)
  tids =  [row[0] for row in cur.fetchall()]
  #tids.extend(orderedItems[1:])
  print tids
  return tids

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

def knn(orderedItems,k):
  """
  Return the k nearest neighbours of the first orderedItem
  """
  result = {}
  score = []
  for m in range(0,len(orderedItems)):
    tid = orderedItems[m]
    i = items[tid]
    X = itemsX[i,:]
    d = []
    for j in range(0,itemsX.shape[0]):
      if j != i:
        Y = itemsX[j,:]
        dist = math.sqrt(sum([(X[l]-Y[l])**2 for l in range(0,itemsX.shape[1]-1)]))
        d.append((dist,j))
    d.sort()
    print [ (dist,index2Tid[j]) for (dist,j) in d[:k-1]]
    for dist,j in d[:k-1]:
      if result.has_key(j):
        result[j].append((m,dist))
      else:
        result[j] = [(m,dist)]
    #return [ (len(orderedItems)-m,index2Tid[j]) for (dist,j) in d[:k-1]]
  print result
  for j in result.keys():
    # todo: uerberlegen was passiert, wenn ein nn zu mehreren items gehoert
    score.append((result[j],index2Tid[j]))
  score.sort()
  print score
  return [ tid for s,tid in score]

def knnLinks(orderedItems):
  """
  todo: alle links beim starten des servers in ein globales dictionary laden -> keine sql-Abfrage noetig, wenn user ein request schickt.
  """
  #cur.execute("select fromTid,toTid from imdbLinks where fromTid in ('%s') and toTid in (select tid from imdb where type='video.movie' and imdbRating > 0 and year > 0 and duration > 0 and Adult = 0);" % "','".join(orderedItems))
  #rows = cur.fetchall()
  #result = []
  #links = dict([(row[0],(row[1:])) for row in rows])
  #links = {}
  #for row in rows:
  #  tid = row[0]
  #  if links.has_key(tid):
  #    links[tid].append(row[1])
  #  else:
  #    links[tid] = [row[1]]
  result = []
  for tid in orderedItems:
    result.extend(list(links[tid]))
  return list(set(result))

def ordered(environ, start_response):
  #logging.info(environ.get('QUERY_STRING',''))
  start_time = time.time()
  parameters = parse_qs(environ.get('QUERY_STRING',''))
  if parameters.has_key("items"):
    status = httpstatus.SC_OK
    orderedItems = escape(parameters["items"][0]).split(",")
    if parameters.has_key("filterKnownItems"):
      filterKnownItems = True
    else:
      filterKnownItems = False
    #writeOrderedItemsToDb(orderedItems)
    #mergedOrderedItems = mergeOrderedItems(orderedItems)
    print orderedItems
    #print mergedOrderedItems
    #recItems = computeRecommendedItems(mergedOrderedItems, NUMBER_OF_REC_ITEMS)    
    # test: nearest neighbors of first orderedItems:
    #possibleItemsToBeSorted = knn(orderedItems,200/len(orderedItems))

    possibleItemsToBeSorted = knnPrecomputed(orderedItems, 50)
    possibleItemsToBeSorted.extend(knnLinks(orderedItems)) # take only the k-nearest neighbours of request + those which are linked to request

    #possibleItemsToBeSorted = items.keys() # take everything
    #recItems = knn(orderedItems,20).extend(knnLinks(orderedItems))
    # test: knn links:
    #knnItems = knnLinks(orderedItems)
    #filteredKnnItems = filterRecKnownItems(knnItems)
    #recItems = computeRecItems(orderedItems,filteredKnnItems)
    #if filterKnownItems:
    #  itemsToBeSorted = filterRecKnownItems(possibleItemsToBeSorted)
    #else:

    itemsToBeSorted = possibleItemsToBeSorted
    #itemsToBeSorted = items # take all items
    recItems = computeRecItemsORDERSVM(orderedItems,itemsToBeSorted,NUMBER_OF_REC_ITEMS) #filteredKnnItems,100)
    html = genXmlFromItems(recItems)
    elapsed_time = time.time() - start_time
    msg = "time to process query: %s" % elapsed_time
    print(msg)
    logging.info(msg)
    #html = genXmlFromItems(recItems)
    #html = ",".join(recItems)
  else:
    status = "404 Not Found"
    html = "404 Not Found"
  start_response(status,[('Content-Type','text/html')])
  return [html]

def computeRecItemsORDERSVM(orderedItems,filteredItems,maxNumOfRecItems):
  """
     orderedItems + SVOR -> ordering through weight vectors.
     filteredItems + ordering through weight vectors --> result
  """
  tidToNr = dict([(tid,tuple(itemsX[items[tid]].tolist()[0])) for tid in orderedItems])
  print tidToNr
  #tidToNr = dict([ (row[0],(row[1:])) for row in cur.fetchall()])
  # to be implemented:
  # do some svm computation:
  diff = []
  y = []
  orderedItemsX = []
  for i in range(len(orderedItems)):
    id = orderedItems[i]
    orderedItemsX.append(list(tidToNr[id]))
  #X = cvxopt.matrix(orderedItemsX).trans()
  X = np.matrix(orderedItemsX)
  print "X = ", X
  
  sorted = []
  score = {}
  sumw = np.matrix([[0] for i in range(0,itemsX.shape[1])])
  print "sumw.size = ", sumw.size
  #print "sumw = ", sumw
  for i in range(1,len(orderedItems)):
    y = [+1 for k in range(0,i)]
    y.extend([-1 for k in range(i,len(orderedItems))])
    print "len(y) = ", len(y)
    print "X.size = ", X.shape
    #d = cvxopt.matrix(y)
    #gamma = 2.0; kernel = 'linear'; sigma = 1.0; width = 20
    #sol1 = linearsvm.softmargin(X, d, gamma, kernel, sigma)
    sol1 = svc.fit(X,y)
    w = sol1.coef_.transpose()
    #w = sol1.coef_
    #b = sol1['b']
    print " |w| = ", np.linalg.norm(w)
    #print "w * X[1] - b -1  before = ", (w * X[1]-b)[0]-1
    #if i == 1:
    #  wX1 = ( (w * X[1]-b)[0] >= 1 )
    #if i > 1:
    #  if ((w * X[1]-b)[0] >= 1) != wX1 :
    #    w = -1 * w
    #    print "w * X[1] - b -1  after = ", (w * X[1]-b)[0]-1
    print "w.size = ", w.size
    #print "w = " , w
    sumw = sumw + w
    n = datetime.datetime.now()
    t = n.strftime('%Y-%m-%d %H:%M:%S')
    #for tid in filteredKnnItems:
    #  s = itemsX[items[tid],:]*w
    #  if s[0] > 0 :
    #    sw = 1
    #  else:
    #    sw = 0
    #  if score.has_key(tid):
    #    # bei jedem w*item>0 gibts einen punkt -> problem: mehrere filme koennen gleiche punktzahl haben :
    #    #score[tid] += sw
    #    # w*item wird als score genommen:
    #    score[tid] += s[0]
    #  else:
    #    #score[tid] = sw
    #    score[tid] = s[0]
  #print "sumw = ", sumw
  sorted =  []
  for tid in filteredItems:
    s = itemsX[items[tid],:]*sumw
    score[tid] = s[0]
  print "itemsX = " 
  #print (itemsX[items[filteredItems[0]],:].size)
  #print "sumw = %s" % sumw.size
  #print s
  #print "score = ", score
  for tid in score.keys():
    print tid, score[tid]
    sorted.append((score[tid],tid))
  sorted.sort(reverse=True)
  #print "sorted = ", sorted
  #logging.info(sol1["w"])
  return [tid for s,tid in sorted[0:maxNumOfRecItems]]


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


def computeRecommendedItems(orderedItems,numberOfRecItems):
  # read from mysql:
  #cur.execute("select tid,year,imdbRating,log(ratingCount) from imdb where tid in ('%s');" % "','".join(orderedItems))
  tidToNr = dict([(tid,tuple(itemsX[items[tid],:])) for tid in orderedItems])
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
  print(X)
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
  sortBy = itemsX*w
  k = items.keys()
  sorted = []
  for tid in items.keys():
    i = items[tid]
    s = sortBy[i]
    sorted.append((s,tid))
  sorted.sort(reverse=True)
  logging.info(sol1["w"])
  return [tid for s,tid in sorted[0:numberOfRecItems]]

def img(environ, start_response):
  # todo : hier die Posterbilder aus der DB lesen (vorher) und danach zurueckgeben
  start_time = time.time()
  parameters = parse_qs(environ.get('QUERY_STRING',''))
  if parameters.has_key("imgkey"):
    status = httpstatus.SC_OK
    imgkey = parameters["imgkey"][0].replace(".jpg","")
    try:
      data = images[imgkey]
    except KeyError:
      data = ""
  else:
    status = "404 Not Found"
    data = ""
  start_response(status,[('Content-Type','image/jpg')])
  return [data]
  

  parameters = parse_qs(environ.get('QUERY_STRING',''))
  start_response('200 OK', [('Content-Type','text/html')])
  html = ""
  for key in parameters:
    value = escape(",".join(parameters[key]))
    html += "%s : %s <br/>" % (key,value)
  return [ ""]

def index(environ, start_response):
  method = environ["REQUEST_METHOD"]
  if method == "GET":
    status = "200 OK"
    response_headers = [('Content-Type',"text/html")]
    start_response(status,response_headers)
    bytestring = """<html><body> <form action='/' method='post' accept-charset='utf-8'> 
                    <input name = 'suche' type='text'></input>
                    <input type='submit' value='Suche'></input></form></body></html>"""
    return [bytestring]
  elif method == "POST":
    status = "200 OK"
    response_headers = [('Content-Type',"text/html")]
    start_response(status, response_headers)
    input = environ['wsgi.input']
    form = cgi.FieldStorage(fp=input, environ=environ)
    if form.has_key("suche"):
      suche = form.getlist("suche").pop().split(",")[0]
      logging.info("%s;%s" % (environ["REMOTE_ADDR"], suche))
      bytestring = ""
      return [bytestring]
    else:
      status = '404 Not Found'
      response_headers = [('Content-Type','text/html')]
      start_response(status,response_headers)
      return ["Fehler, Suche fehlt."]
  else:
    status = "404 Not Found"
    response_headers = [('Content-Type', "text/html")]
    start_response(status, response_headers)
    return ["Falsche Methode %s " % method]

def main():
  init()
  #apt-get install python-cherrypy3
  from cherrypy import wsgiserver
  if len(sys.argv) == 1:
    ipadress = "192.168.178.01"
  else:
    ipadress = sys.argv[1] #"192.168.1.167"
  server = wsgiserver.CherryPyWSGIServer((ipadress,8000), urlmapping, server_name="Leka")
  #myDict = create_dict(sys.argv[1])
  itemsDict = { 'var1' : 1, 'env1' : [1,2,3]}
  #print get_results(tags,"<homework>")
  #server.environ["DICT"] = itemsDict # todo: rausfinden wie man ein environ an den server uebergibt oder schon vorhandenes environ mit einem dict $
  try:
    logging.info("Starting server")
    server.start()
  except KeyboardInterrupt:
    print "Stopping server"
    logging.info("Stopping server")
    server.stop()


if __name__ == "__main__":
  #with daemon.DaemonContext():
  try:
    main()
  except Exception,e:
    type_, value_, traceback_ = sys.exc_info()
    msg = "stopping because of Error: " +"\n".join(traceback.format_exception(type_,value_,traceback_))
    print msg
    logging.info(msg)
    sys.exit(1)
