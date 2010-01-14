from SOAPpy import SOAPProxy

url = 'https://localhost:8443'
server = SOAPProxy(url)
print server.echo("hello world")
s = raw_input("Your name: ")
print server.echo(s)
