#!/usr/bin/python

import SOAPpy

from SOAPpy import SOAPProxy            
url = 'http://services.xmethods.net:80/soap/servlet/rpcrouter'
namespace = 'urn:xmethods-Temperature'  
server = SOAPProxy(url, namespace)      

##server.config.dumpSOAPOut = 1            
##server.config.dumpSOAPIn = 1
print server.getTemp('27502') 

##print SOAPpy.__version__

