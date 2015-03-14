USE empfehlung;

DROP TABLE IF EXISTS imdb;
# ['fn', 'tid', 'title','wordsInTitle', 'url', 'imdbRating','ratingCount', 'duration', 'year','type']
CREATE TABLE imdb(
  filename varchar(10000),
  tid VARCHAR(20) PRIMARY KEY,
  title VARCHAR(256),
  wordsInTitle VARCHAR(256),
  url VARCHAR(256),
  imdbRating DOUBLE,
  ratingCount INTEGER DEFAULT 0,
  duration INTEGER DEFAULT 0,
  year INTEGER DEFAULT 0,
  type VARCHAR(30),
  nrOfWins INTEGER DEFAULT 0,
  nrOfNominations INTEGER DEFAULT 0,
  nrOfPhotos INTEGER DEFAULT 0,
  nrOfNewsArticles INTEGER DEFAULT 0,
  nrOfUserReviews INTEGER DEFAULT 0,
  nrOfGenre INTEGER DEFAULT 0,
Action INTEGER DEFAULT 0,
Adult INTEGER DEFAULT 0,
Adventure INTEGER DEFAULT 0,
Animation INTEGER DEFAULT 0,
Biography INTEGER DEFAULT 0,
Comedy INTEGER DEFAULT 0,
Crime INTEGER DEFAULT 0,
Documentary INTEGER DEFAULT 0,
Drama INTEGER DEFAULT 0,
Family INTEGER DEFAULT 0,
Fantasy INTEGER DEFAULT 0,
FilmNoir INTEGER DEFAULT 0,
GameShow INTEGER DEFAULT 0,
History INTEGER DEFAULT 0,
Horror INTEGER DEFAULT 0,
Music INTEGER DEFAULT 0,
Musical INTEGER DEFAULT 0,
Mystery INTEGER DEFAULT 0,
News INTEGER DEFAULT 0,
RealityTV INTEGER DEFAULT 0,
Romance INTEGER DEFAULT 0,
SciFi INTEGER DEFAULT 0,
Short INTEGER DEFAULT 0,
Sport INTEGER DEFAULT 0,
TalkShow INTEGER DEFAULT 0,
Thriller INTEGER DEFAULT 0,
War INTEGER DEFAULT 0,
Western INTEGER DEFAULT 0

);

LOAD DATA INFILE '/home/orges/empfehlung/imdb/imdb.csv'
    INTO TABLE imdb
    FIELDS TERMINATED BY ','
        ESCAPED BY '\\'
    LINES
        TERMINATED BY '\n'
    IGNORE 1 LINES;

#mysql> create table weight_vector(
#    ->  id int auto_increment,
#    ->  time datetime not null,
#    ->  x Decimal(20,10),
#    ->  primary key (id)
#    -> );

