#!/usr/bin/python

import pg

dbname = 'test'
host = 'j4-itrl-12.comp.glam.ac.uk'
port = 5432
options = None
tty = None
user = 'michael'
password = 'hd5hainer'

c = pg.connect(dbname, host, port, options, tty, user, password)
result = c.query('select name, firstname from person')

print result.getresult()

c.close()
