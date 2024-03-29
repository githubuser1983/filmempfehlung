#!/usr/bin/Rscript

source("/home/orges/empfehlung/imdb/R/connectToDB.R");
library(spoutlier)
i <- dbGetQuery(con,"select tid from imdb order by tid");
x <- dbGetQuery(con,"select 
                       #pr,deg,cl,bet,tr,ev,
                       imdbRating,ratingCount,duration, year, nrOfWins, nrOfNominations, nrOfPhotos, nrOfNewsArticles, nrOfUserReviews, nrOfGenre, 
                       Action,Adult,Adventure,Animation,Biography,Comedy,Crime,Documentary,Drama,Family,Fantasy,FilmNoir,GameShow,History,Horror,Music,Musical,Mystery,News,RealityTV,Romance,SciFi,Short,Sport,TalkShow,Thriller,War,Western
                      from imdb i, imdb_igraph g where g.tid = i.tid order by i.tid;");
#print(scale(x));
score <- qsp(scale(x));
m <- matrix(c(i$tid,score),ncol=2,byrow=F);
colnames(m)<-c('tid','score');
d <- as.data.frame(m);
print(head(m));
print(head(d));
dbSendQuery(con,"drop table if exists tmp_imdb_qsp");
dbSendQuery(con,"drop table if exists imdb_qsp");
dbSendQuery(con,"create table imdb_qsp ( tid varchar(20) PRIMARY KEY, score decimal(10,5))");
dbWriteTable(con,name="tmp_imdb_qsp",value=d);
dbSendQuery(con,"insert into imdb_qsp select tid,CAST(score AS DECIMAL(10,5)) score from tmp_imdb_qsp;");
dbSendQuery(con,"drop table tmp_imdb_qsp;");
