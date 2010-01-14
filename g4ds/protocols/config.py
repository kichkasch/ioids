"""
Configuration file for protocols for G4DS

Grid for Digital Security (G4DS)

Modules import that module and may read the settings important to them.

All the commented values are populated by g4ds at boot-up time for a config file.

@author: Michael Pilgermann
@contact: mailto:mpilgerm@glam.ac.uk
@license: GPL (General Public License)
"""

import soapprotocol
import tcpsocketprotocol

# GLOBAL SETTINGS
##local_address = '193.63.148.149'                 # put DNS name or IP address of the local machine here
#local_address = '192.168.1.120'                 # put DNS name or IP address of the local machine here


# The list of protocols implemented
# 
# In form of a dictionary - key is the name and value the reference to the module
#   the module must contain a class with the name ProtocolImplementation which
#   must inherit from protocolinterface.ProtocolInterface
protocols = {}
protocols['soap'] = soapprotocol
protocols['tcpsocket'] = tcpsocketprotocol

default_protocol = 'soap'


# Settings for SOAP protocol
##soap_local_address  = local_address         # put DNS name or IP address of the local machine to be used for SOAP here
##soap_local_port = 8080                       # port to listen on for SOAP connections


# Settings for TCP sockets
##tcp_local_address = local_address
##tcp_local_port = 2000



# IMPORTANT
# the corrosponding endpoints
##endpoints = {}
##endpoints['soap'] = 'http://' + soap_local_address + ':' + str(soap_local_port)
##endpoints['tcpsocket'] = tcp_local_address + ':' + str(tcp_local_port)
