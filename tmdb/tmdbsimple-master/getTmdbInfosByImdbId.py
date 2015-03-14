#!/usr/bin/python

# sudo apt-get install python-mysqldb
# sudo apt-get install python-daemon

import os,random,sys,time, datetime
import logging,sys
#rom cgi import parse_qs, escape
#import cvxopt, linearsvm
import MySQLdb, traceback
#from xml.sax.saxutils import escape


import tmdbsimple as tmdb

tmdb.API_KEY = '12345'

urlForImagePrefix = 'https://image.tmdb.org/t/p/original'

id = 'tt0266543' # findet nemo
#id = 'tt123' # falsche id zum testen
external_source = 'imdb_id'


#find = tmdb.Find(id)
#response = find.info(external_source=external_source)
#if len(find.movie_results) == 0: #nichts gefunden
#  pass
#else:
#  print find.movie_results
#  print urlForImagePrefix + find.movie_results[0]['poster_path']

def init():
  global thisfilepath
  global db
  global cur
  global items

  thisfilepath = os.path.dirname(__file__)
  logging.basicConfig(filename=os.path.join(thisfilepath,"tmdb-log.txt"), level=logging.DEBUG, format = '%(asctime)s %(message)s')
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

  try:
    fileForQuery = open(os.path.join(thisfilepath,'../../server/fileForQuery.sql'),'r')
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

  #[{u'poster_path': u'/zjqInUwldOBa0q07fOyohYCWxWX.jpg', u'title': u'Finding Nemo', u'release_date': u'2003-05-30', u'popularity': 4.58358991579472, 
  #u'original_title': u'Finding Nemo', u'backdrop_path': u'/n2vIGWw4ezslXjlP0VNxkp9wqwU.jpg', u'vote_count': 1984, u'adult': False, u'vote_average': 7.0, u'id': 12}]
    
  # write tmdb to db:
  query = "drop table if exists tmdb;"
  cur.execute(query)
  db.commit()    
  query = """
    create table tmdb (
      id INT,
      imdb_id VARCHAR(20),
      poster_path VARCHAR(50),
      title VARCHAR(100),
      release_date DATE,
      original_title VARCHAR(100),
      backdrop_path VARCHAR(100),
      vote_count INT,
      adult BOOLEAN,
      vote_average DECIMAL(4,2),
      popularity DECIMAL(20,10),
      PRIMARY KEY(id)
    );
  """
  cur.execute(query)
  db.commit()
  for i in range(len(items.keys())):
    imdb_id = items.keys()[i]
    print "imdb_id = %s, %s / %s" % (imdb_id, str(i+1), str(len(items.keys())))
    find = tmdb.Find(imdb_id)
    response = find.info(external_source='imdb_id')
    if len(find.movie_results) == 0: #nichts gefunden
      msg = "imdb_id = %s not found at tmdb." % imdb_id
      print msg
      logging.info(msg)
    elif len(find.movie_results) == 1: # genau ein Treffer gefunden:
      myDict = find.movie_results[0]
      myDict['imdb_id'] = imdb_id
      myDict['adult'] = 0+(myDict['adult'] == 'True')
      # todo: rausfinden wie man das mit dem scheiss unicode macht! jetzige lsg: wenns nicht klappt nimm leeren string!
      try:
        myDict['original_title'] = db.escape_string(myDict['original_title']) #.decode('utf-8')
      except UnicodeEncodeError:
        myDict['original_title'] = ''
      try:
        myDict['title'] = db.escape_string(myDict['title']) #.encode('utf-8').decode('utf-8'))
      except UnicodeEncodeError:
        myDict['title'] = ''

      for x in ['adult', 'release_date', 'vote_count','vote_average','popularity','id']:
        myDict[x] = str(myDict[x])
      for (x,y) in myDict.items():
        if y is None:
          myDict[x] = ''

      print myDict
      # aus stackoverflow (http://stackoverflow.com/questions/9336270/using-a-python-dict-for-a-sql-insert-statement) :
      query = "insert into tmdb (`%s`) values ('%s')" % ("` , `".join(myDict.keys()),"' , '".join(myDict.values()))
      #query = db.escape_string(query)
      print query
      cur.execute(query)
    else: # mehrere Treffer gefunden
      msg = "imdb_id = %s found %s tims at tmdb." % (imdb_id, str(len(find.movie_results)))
      print msg
      logging.info(msg)
      
  db.commit()
    #print tuplelist

    
def main():
  #apt-get install python-cherrypy3
  try:
    logging.info("Starting of tmdb-download info")
    init()
  except KeyboardInterrupt:
    print "Stopping tmdb-download because of KeyboarInterrupt"
    logging.info("Stopping tmdb-download because of KeyboarInterrupt")


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
