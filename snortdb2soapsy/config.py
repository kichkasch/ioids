"""
Configuration file for SnDB2Soapsy

SnortDB To SoapSy (SnDB2Soapsy)

Modules import that module and may read the settings important to them.

Options provided here:
    1. General options (name, organisation, location, ...)
    2. Database options
    3. SoapSy naming options


@author: Michael Pilgermann
@contact: mailto:mpilgerm@glam.ac.uk
@license: GPL (General Public License)
"""

## ########################################
##
## General options
##

# Version of SnDB2Soapsy - important for setup (site packages) - you should no change this
VERSION = "0.1"     

# run SnDB2Soapsy in Daemon mode? - a new process will be started and all output will be surpressed
DAEMON_MODE = 0

# where to store the OID of the latest processed snort event
EVENT_STATUS_LOCATION = './event_status.dat'

# how many seconds to wait between two event polls from the snort db
DB_POLL_INTERVAL = 5

## ########################################
##
## Database options
##
## for the Snort source database
##

# Settings for the Community and User database
DB_HOST = 'localhost'
DB_PORT = 5432
DB_DATABASENAME = 'snort'
DB_USERNAME = 'snort'
DB_PASSWORD = 'pwsnort'

## ########################################
##
## XML RPC Database options
##
## for the destination database
##

# address and port of the Database SOAP Server
SOAP_DB_ADDRESS = 'localhost'
SOAP_DB_PORT = '9900'
SOAP_SERVER_URL = 'http://' + SOAP_DB_ADDRESS + ':' + SOAP_DB_PORT

# Datatype of the connected database (connected to the XML RPC interface)
DB_DATA_TYPE = 'Postgresv8.0'

## ########################################
##
## SoapSy naming options
##
## depending on this information, the entries are inserted into  the SoapSy database.

SOAPSY_LOCAL_NAME = 'pchome.kichkasch.co.uk'
SOAPSY_LOCAL_IP = '192.168.1.120'
SOAPSY_LOCAL_OS = 'Linux'
SOAPSY_LOCAL_MAC = None
SOAPSY_LOCAL_DOMAIN = None
SOAPSY_LOCAL_AGENT_NAME = 'snortdb2soapsy agent'
SOAPSY_LOCAL_REPORTER_NAME = 'snortdb2soapsy reporter'
SOAPSY_EVENT_TYPE_NAME = 'snortdb'

SOAPSY_OBSERVER_NAME = 'snort observer'
SOAPSY_OBSERVER_AGENT_NAME = 'snort agent'

SOAPSY_SOURCE_NAME = 'unknown source'
SOAPSY_SOURCE_AGENT_NAME = 'unknown source agent'
SOAPSY_DESTINATION_NAME = 'unknown destination'
SOAPSY_DESTINATION_AGENT_NAME = 'unknown destination agent'
