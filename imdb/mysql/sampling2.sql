use empfehlung;

drop table if exists toBeSampled;
create table toBeSampled AS
select tid,
round(imdbRating) AS iR,
round(year/10)*10 as y,
round(log(ratingCount+1)) as rC 
from imdb 
Where 
(year REGEXP '[0-9]{4}') 
AND imdbRating > 0.0 
AND type = 'video.movie'
;


drop function if exists rI;
delimiter //
create function rI(n integer) returns integer
begin
  return n;
end//
delimiter ;


drop procedure if exists sample;
delimiter //
create procedure sample(n integer)
begin
  declare vIR,vY,vRC, vNi,vNi10  integer;
  declare var_done integer default 0;
  declare c cursor for select iR,y,rC,ni from withNi where ni > 0;
  declare continue handler for not found set var_done = 1;

  drop table if exists inGroups;
  create table inGroups AS
  select iR, y, rC,
  count(*) as cnt,
  count(*) / ( select count(*) As s from toBeSampled ) as pr
  from toBeSampled
  group by iR,y,rC;


  drop table if exists withNi;
  create table withNi AS
  select *, round(pr*rI(n)) as ni from inGroups order by pr desc;

  set @diff = 0;
  # there might be differences...: sum(ni) = 16 as opposed to expected n=20:
  select rI(n)-sum(ni) from withNi into @diff;

  set @sql=concat('update withNi set ni = ni+1 order by ',n,'*pr-ni desc limit ', @diff);
  prepare stmt from @sql;
  execute stmt;



  drop table if exists sampled;
  create table sampled as select * from toBeSampled limit 0;
  
  open c;
  fetch c into vIR, vY,vRC, vNi;
  select 10*vNi into vNi10;
  while var_done=0 do
    set @sql = concat( 'insert into sampled 
                        select * from (
                        select s.* from imdb, toBeSampled as s where iR = ',viR,' and y = ', vY,' and rC=',vRC,' and imdb.tid = s.tid 
                        order by ratingCount desc, imdbRating desc, year desc limit ', vNi10 ,'
                        ) as t order by rand() limit ',vNi
                        );
    prepare stmt from @sql;
    execute stmt;
    fetch c into vIR, vY, vRC, vNi;
  end while;
  close c;
  
end//
delimiter ;

call sample(30);



select 'imdb' into @tableName;
select '/tmp/sample.csv' into @outputFile;
select 'select imdb.* from imdb,sampled where imdb.tid=sampled.tid order by imdb.ratingCount desc, imdb.imdbRating desc, imdb.year desc' into @myQuery;

# 2. get the column names in a format that will fit the query

select group_concat(concat("'",column_name, "'")) into @columnNames from information_schema.columns
where table_name=@tableName and table_schema='empfehlung';

# 3. build the query

SET @query = CONCAT(
"select * from
((SELECT ",@columnNames,")
UNION
(",@myQuery,")) as a
INTO OUTFILE '", @outputFile, "'
Fields terminated by ','
lines terminated by '\n'
");

# 4. execute the query

PREPARE stmt FROM @query;
EXECUTE stmt;
