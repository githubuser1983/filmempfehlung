#!/usr/bin/Rscript

source("/home/orges/empfehlung/imdb/R/connectToDB.R");
library(igraph)
i <- dbGetQuery(con,"select tid from imdb order by tid");
x <- dbGetQuery(con,"select  fromTid,toTid
                      from imdbLinks where toTid in (select tid from imdb);");
g <- graph.data.frame(x,directed=T,vertices=i);
pr <- page.rank(g)$vector;
deg <- degree(g);
cl <- closeness(g);
bet <- betweenness(g,normalized=T);
tr <- transitivity(g,type='local');
ev <- evcent(g)$vector;

#print(pr$vector);
m <- matrix(c(i$tid,pr,deg,cl,bet,tr,ev),ncol=7,byrow=F);
colnames(m)<-c('tid','pr','deg','cl','bet','tr','ev');
d <- as.data.frame(m);
dbSendQuery(con,"drop table if exists tmp_imdb_igraph");
dbSendQuery(con,"drop table if exists imdb_igraph");
dbSendQuery(con,"create table imdb_igraph ( tid varchar(20) PRIMARY KEY, pr decimal(20,19),deg decimal(20,15),cl decimal(20,15),bet decimal(20,15),tr decimal(20,15),ev decimal(20,15))");
dbWriteTable(con,name="tmp_imdb_igraph",value=d);
dbSendQuery(con,"insert into imdb_igraph select tid,CAST(pr AS DECIMAL(20,19)) pr,CAST(deg AS DECIMAL(20,15)) deg,CAST(cl AS DECIMAL(20,15)) cl,CAST(bet AS DECIMAL(20,15)) bet,CAST(tr AS DECIMAL(20,15)) tr,CAST(ev AS DECIMAL(20,15)) ev  from tmp_imdb_igraph;");
dbSendQuery(con,"drop table tmp_imdb_igraph;");
