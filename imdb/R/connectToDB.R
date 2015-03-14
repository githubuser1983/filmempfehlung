#!/usr/bin/Rscript

library(RMySQL)
con <- dbConnect(MySQL(), user="orges", password="12345", dbname="empfehlung",host="localhost")
example <- 'x <- dbGetQuery(con, "select tid, imdbRating, ratingCount from imdb limit 10;")'

print(example);
