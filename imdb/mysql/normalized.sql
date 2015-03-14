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
;
