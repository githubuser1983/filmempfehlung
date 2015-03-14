use empfehlung;

drop table if exists imdb_ordered;
create table imdb_ordered
(
  id INTEGER AUTO_INCREMENT,
  time DATETIME,
  tid VARCHAR(20),
  PRIMARY KEY (id)
);
