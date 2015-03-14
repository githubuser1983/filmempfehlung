library(RMySQL)
library(psych)
con <- dbConnect(MySQL(), user="orges", password="12345", dbname="empfehlung",host="localhost")
query = "
select tid,title,
      (year-m_year)/s_year as year,
      (imdbRating - m_imdbRating)/s_imdbRating as imdbRating,
      (ratingCount - m_ratingCount)/s_ratingCount as ratingCount,
      (nrOfWins - m_nrOfWins)/s_nrOfWins as nrOfWins,
      (nrOfNominations - m_nrOfNominations)/s_nrOfNominations as nrOfNominations,
      (nrOfPhotos - m_nrOfPhotos)/s_nrOfPhotos as  nrOfPhotos,
      (nrOfNewsArticles - m_nrOfNewsArticles)/s_nrOfNewsArticles as nrOfNewsArticles,
      (nrOfUserReviews - m_nrOfUserReviews)/s_nrOfUserReviews as nrOfUserReviews


from
(
select tid,title,
   year,
   imdbRating,
   ratingCount,
   nrOfWins,
   nrOfNominations,
   nrOfPhotos,
   nrOfNewsArticles,
   nrOfUserReviews
   from imdb where type='video.movie' and imdbRating > 0 and year > 0
) as i,
( select 
avg(year) m_year,sqrt(variance(year)) s_year,
avg(imdbRating) m_imdbRating,sqrt(variance(imdbRating)) s_imdbRating,
avg(ratingCount) m_ratingCount,sqrt(variance(ratingCount)) s_ratingCount,
avg(nrOfWins) m_nrOfWins,sqrt(variance(nrOfWins)) s_nrOfWins,
avg(nrOfNominations ) m_nrOfNominations , sqrt(variance(nrOfNominations )) s_nrOfNominations ,
avg(nrOfPhotos ) m_nrOfPhotos , sqrt(variance(nrOfPhotos )) s_nrOfPhotos ,
avg(nrOfNewsArticles ) m_nrOfNewsArticles , sqrt(variance(nrOfNewsArticles )) s_nrOfNewsArticles ,
avg(nrOfUserReviews ) m_nrOfUserReviews , sqrt(variance(nrOfUserReviews )) s_nrOfUserReviews 
from imdb where type='video.movie' and imdbRating > 0 and year > 0
) as stats
;"

x <- dbGetQuery(con, query)
X <- x[,3:10]
mydata <- X
#fit <- princomp(mydata, cor=TRUE)
#summary(fit) # print variance accounted for
#loadings(fit) # pc loadings
#plot(fit,type="lines") # scree plot
#fit$scores # the principal components
#biplot(fit)
fit <- factanal(mydata, 4, rotation="varimax")
load <- fit$loadings[,1:2]
plot(load,type="n")
text(load,labels=names(mydata),cex=.7)
