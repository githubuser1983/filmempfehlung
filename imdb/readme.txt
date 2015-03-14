# wget braucht ca. 0.5 sec pro Datei zum herunterladen (eigene Angabe von wget)
# 14.000 Dateien in 7 H -> 2000 Dateien/Stunde

egrep -o "/title/tt[0-9]+" imdb_top-250.html | cut -f 2,3 -d ":" | sort -n | uniq | awk '{print "http://www.imdb.com"$1}' > urls.txt

~/empfehlung/imdb$ egrep -o "/title/tt[0-9]+" tt* | cut -f 2,3 -d ":" | sort -n | uniq | awk '{print "http://www.imdb.com"$1}' > titles/urls.txt

~/imdb$ egrep -o "/title/tt[0-9]+/" titles/*html* | cut -f 2,3 -d ":" | sort -n | uniq | awk '{print "http://www.imdb.com"$1}'

wget -i urls.txt


