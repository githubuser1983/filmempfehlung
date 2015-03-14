#!/usr/bin/Rscript
source("connectToDB.R");
query = "
select t.*, k.sumscore from
( select i.tid,
   score,
   pr,
   deg,
   #cl,
   bet,
   #tr,
   ev, 
   # Adult’ and ‘Documentary’ and ‘FilmNoir’ and ‘GameShow’ and ‘Musical’ and ‘News’ and ‘RealityTV’ and ‘Short’ and ‘TalkShow’
   year,imdbRating,ratingCount,duration,nrOfWins,nrOfNominations,nrOfPhotos,nrOfNewsArticles,nrOfUserReviews,nrOfGenre,
   Action,Adventure,Animation,Biography,Comedy,Crime,Drama,Family,Fantasy,History,Horror,Music,Mystery,Romance,SciFi,Sport,Thriller,War,Western
   from imdb i, imdb_qsp q, imdb_igraph g where i.type='video.movie' 
   and i.imdbRating > 0 and i.year > 0 and i.duration > 0 
   and i.tid = q.tid and i.tid=g.tid ) t,
(
 select tid, sum(score) sumscore from  ( 
            select o.time, x.max-o.id + 1 score, o.tid from imdb_ordered o, ( 
                  select * from      (select time,min(id) min, max(id) max, count(*) cnt from imdb_ordered group by time order by time desc ) t       where cnt < 20 ) x    where x.time = o.time  ) r group by tid order by sumscore desc 
) k
where t.tid = k.tid order by sumscore desc
;
";
x <- dbGetQuery(con,query);
X <- scale(x[,2:(dim(x)[2])]);
library(e1071)
s <- svm(sumscore ~ score+pr+deg+bet+ev+year+imdbRating+ratingCount+duration+nrOfWins+nrOfNominations+nrOfPhotos+nrOfNewsArticles+nrOfUserReviews+nrOfGenre+Action+Adventure
         +Animation+Biography+Comedy+Crime+Drama+Family+Fantasy+History+Horror+Music+Mystery+Romance+SciFi+Sport+Thriller+War+Western
         , data=X)
p <- predict(s,X)
ps <- sort(p)
#print(x[ps,1])
