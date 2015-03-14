#!/usr/bin/python


# 1. read urls of images to be downloaded form mysql db
# 2. for each image-url:
# 3.   download image (with requests)
# 4.   scale the image down to 50x50 (maybe different image sizes)
# 5.   if table posterPathImg exists it will be deleted and created new: posterPathImg( tmdbId intger, img blob, img50x50 blob)
# 5.   write the original image and the scaled down images to db, table: posterPathImmg


#import cgi,re,os,mimetypes,datetime,random,sys,time, datetime
import logging,sys, time, traceback, os
#from cgi import parse_qs, escape
import MySQLdb, requests, shutil


def main():
  global items, itemsX, urls, links, allKnn, itemsForXml, fieldNames, svc

  #thisfilepath = os.getcwd()
  #thisfile = os.path.basename(__file__)

  thisfile = file = os.path.join(os.getcwd(), os.listdir(os.getcwd())[0])
  thisfilepath = os.path.dirname(file) ## directory of file

  print thisfilepath, thisfile
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

  print "connected to DB"

  try:
    fileQueryForItemsInXml = open(os.path.join(thisfilepath,'../../server/queryForItemsInXml.sql'),'r')
    query = fileQueryForItemsInXml.read()
    fileForQueryForItemsInXml.close()
  except Exception:
    logging.error("queryForItemsInXml.sql not found")
    print("queryForItemsInXml.sql not found, use internal query...")
    queryForItemsInXml="select i.tid tid,i.title title,i.url url,IFNULL(p.imageUrl,'') posterPathUrl from imdb i, imdbIdPosterPath p where i.tid = p.imdb_id;"

  print "read queryForItemsInXml"

  cur.execute(queryForItemsInXml)
  fieldNames = [i[0] for i in cur.description]
  print "fieldNames = %s" % fieldNames
  print "fetching all rows..."
  rows = cur.fetchall()
  print "creating itemsForXml - Dictionary ..."
  itemsForXml = dict([ (row[0], (row[0:])) for row in rows])

  print "loaded posterPathUrls..."

  for tid, row in itemsForXml.items():
    #url = 'https://image.tmdb.org/t/p/original/wpKBLDjNRddmH6N32ni4bASogt8.jpg'
    tid, title,url,posterPathUrl = row
    print "downloading %s,%s,%s ..." % (title,url,posterPathUrl)
    response = requests.get(posterPathUrl, stream=True)
    # todo:...
    fn = '/home/orges/empfehlung/tmdb/requests-master/img/%s' % posterPathUrl.split('/')[-1]
    print fn
    with open(fn, 'wb') as out_file:
      print tid,title,posterPathUrl
      shutil.copyfileobj(response.raw, out_file)
    del response 


if __name__ == '__main__':
  main()
