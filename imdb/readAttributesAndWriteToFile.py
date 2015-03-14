#!/usr/bin/python

import re, sys, os, HTMLParser,math
from genres_names import D

def getWordsInTitle(txt):
  title = getTitle(txt).lower()
  return " ".join(re.compile("[a-z]+").findall(title))

def compStat(listOfInt):
  X = listOfInt
  if len(X) == 0:
    return 0,0.0,0.0,0,0
  mean = 1.0/len(X) * sum([x for x in X])
  sd = math.sqrt(1.0/len(X) * sum([(x-mean)**2 for x in X]))
  Max = max(X)
  Min = min(X)
  return len(X),mean,sd,Min,Max

def getGenres(txt):
  l = re.compile('itemprop="genre">[a-zA-Z\-]+</span>').findall(txt)
  return [x.replace('itemprop="genre">','').replace('</span>','').replace('-','') for x in l]

def getDuration(txt):
  try:
    dString = re.compile('<time itemprop="duration" datetime="[PTM0-9\,\.]+').findall(txt)[0]
    dString = dString.replace(',','')
    minDuration = float(dString.split('PT')[1][:-1])
    return "%s" % (int(round(minDuration * 60)))
  except IndexError:
    return ""

def getTitle(txt):
  htmlTitle = re.compile('property=\'og:title\' content=\".*\"').findall(txt)[0].split("content=\"")[1][:-1]
  return HTMLParser.HTMLParser().unescape(htmlTitle.decode('utf-8')).encode('utf-8')

def sortByOcc(list,reverse=False):
  sorted = [(list.count(x),x) for x in set(list) ]
  sorted.sort(reverse=reverse)
  return sorted

def getTid(txt):
  titles = re.compile('tt[0-9]{3,70}').findall(txt)
  return sortByOcc(titles,reverse=True)[0][1] # Take the title which occurs most


def getUrl(txt):
  tid = getTid(txt)
  return "http://www.imdb.com/title/%s/" % tid


def getImdbRating(txt):
  try:
    return re.compile('itemprop=\"ratingValue\">[0-9\.]+<\/span>').findall(txt)[0].split(">")[1].split("<")[0]
  except IndexError:
    return ''

def getYear(txt):
  try:
    return re.compile('year/[0-9]{4}').findall(txt)[0].split("/")[1]
  except IndexError:
    try:
      years = re.compile('[1-2]{1}[0,9]{1}[0-9]{2}').findall(getTitle(txt))
      # 1989 is average year -> take the year which is nearer to 1989:
      s = [(abs(int(y)-1989),y) for y in years]
      s.sort()
      return str(int(s[0][1]))
    except IndexError: # take first occurrance (might have more than once) of 'datePublished'
      try:
        return re.compile('itemprop=\"datePublished\" content=\"[0-9]{4}').findall(txt)[0].split("content=\"")[1]
      except IndexError:
        return ''

def getType(txt):
  return re.compile("meta property='og:type' content=\"[a-z\.]+").findall(txt)[0].split('content="')[1]

def getRatingCount(txt):
  try:
    return re.compile("<span itemprop=\"ratingCount\">[0-9\,]+").findall(txt)[0].split('ratingCount">')[1].replace(",","")
  except IndexError:
    return ''

def getNrOfWins(txt):
  try:
    return re.compile("<span itemprop=\"awards\">\d+ win").findall(txt)[0].split(' win')[0].split(">")[1]
  except IndexError:
    try:
      # <span itemprop="awards">Another 86 win
      return re.compile("<span itemprop=\"awards\">Another \d+ win").findall(txt)[0].split(' win')[0].split(">Another ")[1]
    except IndexError:
      return '0'

def getNrOfNominations(txt):
  try:
    return re.compile("<span itemprop=\"awards\">.+? \d+ nomination").findall(txt)[0].split(' ')[-2]
  except IndexError:
    return '0'

def getNrOfPhotos(txt):
  try:
    return re.compile("<a href=\"/title/tt\d+/mediaindex\?ref_=tt_pv_mi_sm\" >\d+ photos</a>").findall(txt)[0].split(" ")[-2][1:]
  except IndexError:
    return '0'

def getNrOfNewsArticles(txt):
  try:
    return re.compile("<a href=\"/title/tt\d+/news\?ref_=tt_pv_nw_sm\" >\d+ news articles</a>").findall(txt)[0].split(' ')[-3][1:]
  except IndexError:
    return '0'

def getNrOfUserReviews(txt):
  try:
    return re.compile("<a href=\"reviews\?ref_=tt_ov_rt\" title=\"\d+ IMDb user reviews").findall(txt)[0].split('="')[-1].split(' ')[0]
  except IndexError:
    try:
      return re.compile('\d+[\,]*\d+').findall(re.compile('See all \d+[\,]*\d+ user reviews').findall(txt)[0])[0].replace(',','')
    except IndexError:
      return '0'


if __name__ == "__main__":
  # usage:
  # ~/empfehlung/imdb$ ./readAttributesAndWriteToFile.py test.csv titles/*html*
  removeDuplicateFiles = True
  fileToWrite = open(sys.argv[1],"w")
  filesToReadAttributes = sys.argv[2:]
  attributeNames = ['fn', 'tid', 'title','wordsInTitle', 'url', 'imdbRating',
                    'ratingCount', 'duration', 'year','type','nrOfWins','nrOfNominations','nrOfPhotos',
                    'nrOfNewsArticles','nrOfUserReviews',
                    'nrOfGenre'
                    #,'meanGenre','sdGenre','minGenre','maxGenre'
                   ]
  genres = D['genres'].keys()
  # sort genres alphabetically
  genres.sort()
  # add genres to Attributes:
  for g in genres:
    attributeNames.append(g)

  idsAlreadySeen = set([])
  delim = ','
  fileToWrite.write(delim.join(attributeNames)+"\n")
  for fn in filesToReadAttributes:
    lineDict = {}
    f = open(fn,'r')
    txt = f.read()
    lineDict['fn'] = fn
    print fn
    # read Attributes:
    nrOfGenre, meanGenre, sdGenre, minGenre, maxGenre = compStat([ D['genres'][g] for g in getGenres(txt)])
    lineDict['title'] = getTitle(txt)
    lineDict['tid'] = getTid(txt)
    lineDict['url'] = getUrl(txt)
    lineDict['imdbRating'] = getImdbRating(txt)
    lineDict['year'] = getYear(txt)
    lineDict['duration'] = getDuration(txt)
    lineDict['ratingCount'] = getRatingCount(txt)
    lineDict['wordsInTitle'] = getWordsInTitle(txt)
    lineDict['type'] = getType(txt)
    lineDict['nrOfWins']=getNrOfWins(txt)
    lineDict['nrOfNominations'] = getNrOfNominations(txt)
    lineDict['nrOfPhotos'] = getNrOfPhotos(txt)
    lineDict['nrOfNewsArticles'] = getNrOfNewsArticles(txt)
    lineDict['nrOfUserReviews'] = getNrOfUserReviews(txt)
    lineDict['nrOfGenre'] = str(nrOfGenre)
    #lineDict['meanGenre'] = str(meanGenre)
    #lineDict['sdGenre'] = str(sdGenre)
    #lineDict['minGenre'] = str(minGenre)
    #lineDict['maxGenre'] = str(maxGenre)
    # iterate over genres:
    genresOfMovie = getGenres(txt)
    for g in genres:
      #print "%s INTEGER DEFAULT 0," % g
      if g in genresOfMovie:
        lineDict[g] = '1'
      else:
        lineDict[g] = '0'
    if not lineDict['tid'] in idsAlreadySeen: # Take only those which we have not already seen:
      # print Attributes to file in order given by attributeNames:
      line = ''
      for attribute in attributeNames:
        line += lineDict[attribute].replace(delim,"\\"+delim)+delim
      line = line[0:( len(line) - len(delim) )] + "\n"
      fileToWrite.write(line)
      idsAlreadySeen.add(lineDict['tid'])
      f.close()
    elif removeDuplicateFiles: # if file is duplicate and we want to remove it, delete it:
      f.close()
      os.remove(fn)
    
