"""
Main Configuration file for IOIDS

Inter-Organisational Intrusion Detection System (IOIDS)

Modules import that module and may read the settings important to them.

Options provided here:
    1. General options (name, organisation, location, ...)
    2. Data processing options
    3. Logging options
    4. G4DS Connection parameters
    5. Database connection parameters
    6. Database extension information

@author: Michael Pilgermann
@contact: mailto:mpilgerm@glam.ac.uk
@license: GPL (General Public License)
"""

## ########################################
##
## General options
##

# Version of IOIDS - important for setup (site packages) - you should not change this
VERSION = "0.1"

# put your local address information to be inserted into the database for events
LOCAL_ADDRESS = '192.168.1.120'
LOCAL_HOSTNAME = 'pchome.kichkasch.co.uk'
LOCAL_MAC = None
LOCAL_OS = 'Gentoo Linux'
LOCAL_DOMAIN = None
LOCAL_COMPUTER_TYPE = 'pc x86'

## ########################################
##
## Data processing options
##

# interval between two queue checkings of the data engine
DATA_ENGINE_PROCESSING_INTERVAL = 5     # seconds

# path of file(s) containing ioids policy rules
LOCATION_POLICY_FILES = ['descriptions/ioids_policy.xml']

## ########################################
##
## Logging options
##
## Configure log level
##  0 - Critical errors only
##  1 - 
##  2 - 
##  3 - 
##  4 -
##  5 - All messages
##

# 1) ioids internal logging
#
# Logfile location
#LOGGING_FILENAME = '/var/log/ioids.log'        # common system log directory (requires root priveleges usually)
LOGGING_FILENAME = './ioids.log'                      # current directory
# Logging level (0 critical logs - 5 all logs)
LOGGING_LEVEL = 4

# 2) Logging into syslog
ENABLE_SYSLOG = 0
SYSLOG_IDENTIFIER = 'ioids'

## ########################################
##
## G4DS Connection options
##

# ID for this service within G4DS as it is given in the G4DS IOIDS service description
G4DS_SERVICE_ID = 'S07112005ioids001'

# location of private key for connection against G4DS
LOCATION_PRIVATE_KEY = './g4dskey'

# your member id in G4DS
G4DS_MEMBER_ID = 'M111'

## ########################################
##
## Database connection options
##

# type of connection
#   currently supported: 'xmlrpc' - XML encoded database requests
DATABASE_CONNECTION_TYPE = 'xmlrpc'

# address and port of the Database SOAP Server
SOAP_DB_ADDRESS = 'localhost'
SOAP_DB_PORT = '9900'
SOAP_SERVER_URL = 'http://' + SOAP_DB_ADDRESS + ':' + SOAP_DB_PORT

# how often shall the IOIDS core check for new events on the local database
# specify time interval between two polls in seconds
DB_POLL_INTERVAL = 60   # ones in a minute
DB_POLL_INTERVAL = 5   # 5 seconds - testing purposes

# location for status file in file system - needed for remembering the latest event ids for trigger mechanism
LOCATION_EVENT_ID_STATUS_FILE = './event_status.dat'

# Datatype of the connected database (connected to the XML RPC interface)
DB_DATA_TYPE = 'Postgresv8.0'

# IOIDS Event type
IOIDS_EVENT_TYPE = 'ioids'

## ########################################
##
## Database extension information
##
SOAPSY_EXTENSIONS = {}

# snortdb extension
import snortdb_extension
snortdb = {}
snortdb['dbconnector'] = snortdb_extension.getDBConnector
snortdb['messagewrapper'] = snortdb_extension.getMessageWrapper

import ioids_extension
db_ioids = {}
db_ioids['dbconnector'] = ioids_extension.getDBConnector
db_ioids['messagewrapper'] = ioids_extension.getMessageWrapper

SOAPSY_EXTENSIONS['snortdb'] = snortdb
SOAPSY_EXTENSIONS['ioids'] = db_ioids

