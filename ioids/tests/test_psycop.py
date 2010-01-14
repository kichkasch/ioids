import psycopg

conn = psycopg.connect('dbname=michael user=michael password=hd5hainer host=localhost')
cu = conn.cursor()
cu.execute('select id, date from test_date')

res = cu.fetchall()
conn.close()

for id, date in res:
	print "%s: %s" %(id, date)

