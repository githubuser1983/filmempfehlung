
select i.tid,
   #score,
   pr,
   deg,
   #cl,
   bet,
   #tr,
   ev, 
   year,imdbRating,ratingCount,duration,nrOfWins,nrOfNominations,nrOfPhotos,nrOfNewsArticles,nrOfUserReviews,nrOfGenre,Action,Adult,Adventure,Animation,Biography,Comedy,Crime,Documentary,Drama,Family,Fantasy,FilmNoir,GameShow,History,Horror,Music,Musical,Mystery,News,RealityTV,Romance,SciFi,Short,Sport,TalkShow,Thriller,War,Western
   from imdb i, imdb_qsp q, imdb_igraph g where i.type='video.movie' 
   and i.imdbRating > 0 and i.year > 0 and i.duration > 0 
   and i.tid = q.tid and i.tid=g.tid and i.Adult = 0
   #and i.tid not in (select distinct tid from imdb_ordered)
;
