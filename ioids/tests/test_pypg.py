from pyPgSQL import PgSQL
conn = PgSQL.connect(host='localhost', user='michael', password='hd5hainer', database='michael',
	client_encoding = 'utf-8', unicode_results = '1')

cu = conn.cursor()
cu.execute('select id,date from test_date')

results = cu.fetchall()
conn.close()

for id, date in results:
	#print "%s: %s" %(id, date.strftime())
	print "%s: %s" %(id, date)

