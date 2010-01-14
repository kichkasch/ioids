"""
Main Configuration file for G4DS

Grid for Digital Security (G4DS)

Modules import that module and may read the settings important to them.

Options provided here:
    1. General options (name, organisation, location, ...)
    2. Database table names


@author: Michael Pilgermann
@contact: mailto:mpilgerm@glam.ac.uk
@license: GPL (General Public License)
"""

## ########################################
##
## General options
##

# Version of G4DS - important for setup (site packages) - you should no change this
VERSION = "0.1"     

# run the G4DS listener in Daemon mode? - a new process will be started and all output will be surpressed
DAEMON_MODE = 1


# the initial path to be used for the communication with the g4ds service
FIFO_PATH_IN = '/tmp/g4ds.in.fifo'
FIFO_PATH_OUT = '/tmp/g4ds.out.fifo'


## ########################################
##
## Database table names
##
##

# dummy
dbconnected  = 1

# Settings for the Community and User database
g4ds_cudb_table_communities = 'communities'
g4ds_cudb_table_members = 'members'
g4ds_cudb_table_gateways = 'gateways'
g4ds_cudb_table_relation_communities_members = 'communities_members'
g4ds_cudb_table_relation_communities_authorities = 'communities_authorities'

# More settings for the communcation between the communities and members.
g4ds_comm_table_protocols = 'protocols'
g4ds_comm_table_endpoints = 'endpoints'
g4ds_comm_table_relation_communities_protocols = 'communities_protocols'

# Settings for secure communications
g4ds_sec_table_algorithms = 'algorithms'
g4ds_sec_table_credentials = 'credentials'
g4ds_sec_table_mycredentials ='personalcredentials'
g4ds_sec_table_relation_communities_algorithms = 'communities_algorithms'

# Settings for the Service Repository Database
g4ds_serv_table_services = 'services'
g4ds_serv_table_relation_services_communities = 'services_communities'
g4ds_serv_table_relation_services_members = 'services_members'
g4ds_serv_table_relation_services_authorities = 'services_authorities'

# Database settings for the Routing table
g4ds_rtdb_table_routingtable = 'routingtable'
