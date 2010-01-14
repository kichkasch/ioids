# required modules
#   * m2crypto
#   * SOAPpy
#       - fpconst
#       - pyXML
#
# required software
#   * openssl
#
# for creating the keys and certificates
#
#   openssl genrsa -out ~/.sslstuff/priv_rsa_key
#   openssl req -new -x509 -key ~/.sslstuff/priv_rsa_key -out ~/.sslstuff/cacert.pem -days 1
#
from SOAPpy import SOAPServer

from M2Crypto import SSL

def greeting(s):
    return 'Hello ' + s

def echo(s):
    return s+s # repeats a string twice

ssl_context = SSL.Context()
ssl_context.load_cert('/home/michael/.sslstuff/cacert.pem', keyfile='/home/michael/.sslstuff/priv_rsa_key')

server = SOAPServer(("localhost",8443), ssl_context = ssl_context)
server.registerFunction(echo)
server.serve_forever()
