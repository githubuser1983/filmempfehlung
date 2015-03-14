use empfehlung;

select 'select * from (
  select imdb.* 
  from imdb   
  where 
  type = "video.movie" 
  order by 
  round(log(ratingCount+1)*0.5)* round(imdbRating*2)/2 *  10*round(year/10) 
  desc limit 1000
) as t 
#order by rand() limit 20
' into @myQuery;

select 'imdb' into @tableName;
select '/tmp/sample.csv' into @outputFile;

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

