import pg
conn = pg.connect('michael','localhost',5432, None, None, 'michael', 'hd5hainer')

res = conn.query('select id, date from test_date')
list = res.getresult()

for id, timestamp in list:
	print "%s: %s" %(id, timestamp)

conn.close()
