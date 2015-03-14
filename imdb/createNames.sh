egrep -rio "/name/nm[0-9]+" titles*/* | cut -f 2 -d ":" | cut -f 3 -d "/" | sort -n | uniq -c | sort -nr > names.txt
