"""
Some additional information for XML database.

Inter-Organisational Intrusion Detection System (IOIDS)

@author: Michael Pilgermann
@contact: mailto:mpilgerm@glam.ac.uk
@license: GPL (General Public License)
"""

##
## In the XML RPC database, we have to provide the datatype for each column whenever
## we want to perfrom an insert. However, we cannot know about them a priori; consequently
## for each column in each table used, the datatype has to be defined here. Use the
## following syntax:
##
## DATATYPES['$TABLENAME.$COLUMN_NAME'] = '$DATATYPE_NAME'
##
import soapsytools.xmldb_infos
DATATYPES = soapsytools.xmldb_infos.DATATYPES

DATATYPES['ioids_event.ioids_event_id'] = 'bigserial'
DATATYPES['ioids_event.classification_id'] = 'bigint'
DATATYPES['ioids_event.ioids_sender_id'] = 'varchar(100)'
DATATYPES['ioids_event.event_id'] = 'bigint'
DATATYPES['ioids_event.timestamp_received'] = 'timestamp'
DATATYPES['ioids_event.community_id'] = 'varchar(100)'
DATATYPES['ioids_event.ioids_source_id'] = 'varchar(100)'

DATATYPES['ioids_peer.ioids_peer_id']  ='bigserial'
DATATYPES['ioids_peer.peer_memberid']  ='varchar(100)'

DATATYPES['ioids_sender.ioids_sender_id'] = 'bigserial'
DATATYPES['ioids_sender.ioids_peer_id'] = 'bigint'

DATATYPES['ioids_source.ioids_source_id'] = 'bigserial'
DATATYPES['ioids_source.ioids_peer_id'] = 'bigint'

DATATYPES['ioids_classification.classification_id'] = 'bigint'
DATATYPES['ioids_classification.classification_code'] = 'int'
DATATYPES['ioids_classification.classification_name'] = 'text'

DATATYPES['ioids_relation.ioids_relation_id'] = 'bigserial'
DATATYPES['ioids_relation.ioids_event_id'] = 'bigint'
DATATYPES['ioids_relation.event_id'] = 'bigint'
DATATYPES['ioids_relation.ioids_relation_type_id'] = 'bigint'

DATATYPES['ioids_relation_type.ioids_relation_type_id'] = 'bigserial'
DATATYPES['ioids_relation_type.ioids_relation_type_name'] = 'text'

