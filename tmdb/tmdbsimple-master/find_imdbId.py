#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
test_find.py
~~~~~~~~~~~~

This test suite checks the methods of the Find class of tmdbsimple.

Created by Celia Oakley on 2013-11-05

:copyright: (c) 2013-2014 by Celia Oakley.
:license: GPLv3, see LICENSE for more details.
"""

# limit: 30 requests in 10 seq.

import tmdbsimple as tmdb

tmdb.API_KEY = '12345'

urlForImagePrefix = 'https://image.tmdb.org/t/p/original'

"""
Constants
"""
id = 'tt0266543' # findet nemo
#id = 'tt123' # falsche id zum testen
external_source = 'imdb_id'


find = tmdb.Find(id)
response = find.info(external_source=external_source)
if len(find.movie_results) == 0: #nichts gefunden
  pass
else:
  print find.movie_results
  print urlForImagePrefix + find.movie_results[0]['poster_path']
