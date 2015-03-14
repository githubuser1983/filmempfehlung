#!/bin/bash

echo "reading attributes..."
./readAttributesAndWriteToFile.py imdb.csv titles01/tt* titles0*/*html*
echo "attributes read and written in imdb.csv"

echo "creating links.."
./getRecMovieLinks.py imdbLinks.csv titles01/tt* titles0*/*html*
echo "links created"

echo "loading table to mysql..."
mysql -u "orges" "-p12345" < "mysql/loadImdbTable.sql"
mysql -u "orges" "-p12345" < "mysql/loadImdbLinks.sql"
rm /tmp/sample.csv
echo "table loaded in mysql"
echo "computing outliers..."
./R/spoutlier.R
echo "outliers computed and written to db"
echo "sampling from mysql..."
mysql -u "orges" "-p12345" < "mysql/sampling.sql"
cp /tmp/sample.csv .
echo "generating Resource Values Xml for app from file sample.csv..."
./genResValuesXml.py sample.csv
echo "resource xml generated."
