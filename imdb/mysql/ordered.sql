
select i.title, s.* from (
select tid, sum(score) sumscore from 
(
select o.time, x.max-o.id + 1 score, o.tid from imdb_ordered o,
( select * from 
    (select time,min(id) min, max(id) max, count(*) cnt from imdb_ordered group by time order by time desc limit 10) t 
     where cnt < 20 ) x 
  where x.time = o.time 
) r group by tid order by sumscore desc
) s, imdb i where s.tid = i.tid order by sumscore desc;
