use empfehlung;


drop view imdbIdPosterPath;

drop table if exists imdbIdPosterPath;

create table imdbIdPosterPath AS 
select imdb_id, 
    IF(length(poster_path)>0,concat('https://image.tmdb.org/t/p/original',poster_path),
        IF(length(backdrop_path)>0,concat('https://image.tmdb.org/t/p/original',backdrop_path),'')) as imageUrl 
    from tmdb where length(poster_path)>0 or length(backdrop_path)>0;

create or replace view imdbIdTmdbId AS
select imdb_id as imdbId, id as tmdbId
from tmdb;
