#!/usr/bin/Rscript

source("connectToDB.R");
library(DMwR)
i <- dbGetQuery(con,"select tid from imdb order by tid");
x <- dbGetQuery(con,"select imdbRating,ratingCount,duration, year, nrOfWins, nrOfNominations, nrOfPhotos, nrOfNewsArticles, nrOfUserReviews from imdb order by tid;");
lof <- lofactor(scale(x),k=40);
m <- matrix(c(i$tid,lof),ncol=2,byrow=F);
colnames(m)<-c('tid','score');
d <- as.data.frame(m);
print(head(m));
print(head(d));
dbSendQuery(con,"drop table if exists tmp_imdb_lof");
dbSendQuery(con,"drop table if exists imdb_lof");
dbSendQuery(con,"create table imdb_lof ( tid varchar(20), score decimal(10,5))");
dbWriteTable(con,name="tmp_imdb_lof",value=d);
dbSendQuery(con,"insert into imdb_lof select tid,CAST(score AS DECIMAL(10,5)) score from tmp_imdb_lof;");
dbSendQuery(con,"drop table tmp_imdb_lof;");

