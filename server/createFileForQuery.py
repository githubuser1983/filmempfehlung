#!/usr/bin/python


ffqTempl = """
select i.tid,
   #score,
   pr,
   deg,
   #cl,
   bet,
   #tr,
   ev, 
   %s
   from imdb i, imdb_qsp q, imdb_igraph g where i.type='video.movie' 
   and i.imdbRating > 0 and i.year > 0 and i.duration > 0 
   and i.tid = q.tid and i.tid=g.tid and i.Adult = 0
   #and i.tid not in (select distinct tid from imdb_ordered)
;
"""

ffqTemplPca = """
select i.tid,
     %s 
    from imdb_pca p, imdb i where i.type='video.movie' and i.tid = p.V1
;
"""

if __name__ == '__main__':
  l  = [   
   'year',
   'imdbRating',
   'ratingCount',
   'duration',
   'nrOfWins',
   'nrOfNominations',
   'nrOfPhotos',
   'nrOfNewsArticles',
   'nrOfUserReviews',
   'nrOfGenre',
   #'meanGenre',
   #'sdGenre',
   #'minGenre',
   #'maxGenre',
   'Action','Adult','Adventure','Animation','Biography','Comedy','Crime','Documentary','Drama','Family','Fantasy','FilmNoir','GameShow','History','Horror','Music','Musical','Mystery','News','RealityTV','Romance','SciFi','Short','Sport','TalkShow','Thriller','War','Western'
  ]

  normalized = ",\n".join(["(%s-m_%s)/s_%s as %s" % (x,x,x,x) for x in l])
  li = ",".join(l)
  avg_sd = ",\n".join(["avg(%s) m_%s,if(sqrt(variance(%s))=0,1,sqrt(variance(%s))) s_%s" % (x,x,x,x,x) for x in l])
  # if(sqrt(variance(News))=0,1,sqrt(variance(News)))

  ffq = ffqTempl % li #(normalized,li,avg_sd)
  ffqPca = ffqTemplPca % ",".join(["p.V%s" % i for i in range(2,43+1)])

  with open("fileForQuery.sql","w") as f:
    f.write(ffq)
    #f.write(ffqPca)

