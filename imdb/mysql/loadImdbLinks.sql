USE empfehlung;

DROP TABLE IF EXISTS imdbLinks;
CREATE TABLE imdbLinks(
  fromTid VARCHAR(20) NOT NULL,
  toTid VARCHAR(20) NOT NULL,
  PRIMARY KEY (fromTid,toTid)
);

LOAD DATA INFILE '/home/orges/empfehlung/imdb/imdbLinks.csv'
    INTO TABLE imdbLinks
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

