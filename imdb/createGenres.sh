#!/bin/bash
egrep -rin ".*/genre/[A-Za-z\-]+" titles*/* | cut -f 3 -d ":" | egrep -io "/genre/[A-Za-z\-]+" | cut -f 3 -d "/" | sort -n | uniq -c | sort -nr > genres.txt
