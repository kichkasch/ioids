"""
Some additional information for XML database.

SnortDB To SoapSy (SnDB2Soapsy)

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

DATATYPES['snortdb_event.snortdb_event_id'] = 'bigserial'
DATATYPES['snortdb_event.event_id'] = 'bigint'
DATATYPES['snortdb_event.timestamp'] = 'timestamp'
DATATYPES['snortdb_event.sid'] = 'varchar(100)'
DATATYPES['snortdb_event.cid'] = 'varchar(100)'
DATATYPES['snortdb_event.ip_header_id'] = 'bigint'
DATATYPES['snortdb_event.signature_id'] = 'bigint'
DATATYPES['snortdb_event.sensor_id'] = 'bigint'

DATATYPES['snortdb_payload.payload_id'] = 'bigserial'
DATATYPES['snortdb_payload.data'] = 'text'

DATATYPES['snortdb_signature.signature_id'] = 'bigserial'
DATATYPES['snortdb_signature.name'] = 'varchar(255)'
DATATYPES['snortdb_signature.class'] = 'varchar(60)'
DATATYPES['snortdb_signature.priority'] = 'bigint'
DATATYPES['snortdb_signature.revision'] = 'bigint'
DATATYPES['snortdb_signature.internal_id'] = 'bigint'

DATATYPES['snortdb_sensor.sensor_id'] = 'bigserial'
DATATYPES['snortdb_sensor.hostname'] = 'text'
DATATYPES['snortdb_sensor.interface'] = 'text'
DATATYPES['snortdb_sensor.filter'] = 'text'
DATATYPES['snortdb_sensor.detail'] = 'text'
DATATYPES['snortdb_sensor.encoding'] = 'text'

DATATYPES['snortdb_ip_header.ip_header_id'] = 'bigserial'
DATATYPES['snortdb_ip_header.source_ip'] = 'bigint'
DATATYPES['snortdb_ip_header.destination_ip'] = 'bigint'
DATATYPES['snortdb_ip_header.version'] = 'int'
DATATYPES['snortdb_ip_header.header_length'] = 'int'
DATATYPES['snortdb_ip_header.tos'] = 'int'
DATATYPES['snortdb_ip_header.datagram_length'] = 'int'
DATATYPES['snortdb_ip_header.ip_id'] = 'int'
DATATYPES['snortdb_ip_header.flags'] = 'int'
DATATYPES['snortdb_ip_header.offst'] = 'int'
DATATYPES['snortdb_ip_header.ttl'] = 'int'
DATATYPES['snortdb_ip_header.protocol'] = 'int'
DATATYPES['snortdb_ip_header.checksum'] = 'int'
DATATYPES['snortdb_ip_header.tcp_header_id'] = 'bigint'
DATATYPES['snortdb_ip_header.udp_header_id'] = 'bigint'
DATATYPES['snortdb_ip_header.icmp_header_id'] = 'bigint'

DATATYPES['snortdb_tcp_header.tcp_header_id'] = 'bigserial'
DATATYPES['snortdb_tcp_header.source_port'] = 'int'
DATATYPES['snortdb_tcp_header.destination_port'] = 'int'
DATATYPES['snortdb_tcp_header.seq'] = 'bigint'
DATATYPES['snortdb_tcp_header.ack'] = 'bigint'
DATATYPES['snortdb_tcp_header.offst'] = 'int'
DATATYPES['snortdb_tcp_header.reserved'] = 'int'
DATATYPES['snortdb_tcp_header.flags'] = 'int'
DATATYPES['snortdb_tcp_header.window'] = 'int'
DATATYPES['snortdb_tcp_header.checksum'] = 'int'
DATATYPES['snortdb_tcp_header.urgent'] = 'int'

DATATYPES['snortdb_udp_header.udp_header_id'] = 'bigserial'
DATATYPES['snortdb_udp_header.source_port'] = 'int'
DATATYPES['snortdb_udp_header.destination_port'] = 'int'
DATATYPES['snortdb_udp_header.length'] = 'int'
DATATYPES['snortdb_udp_header.checksum'] = 'int'

DATATYPES['snortdb_icmp_header.icmp_header_id'] = 'bigserial'
DATATYPES['snortdb_icmp_header.type'] = 'int'
DATATYPES['snortdb_icmp_header.code'] = 'int'
DATATYPES['snortdb_icmp_header.checksum'] = 'int'
DATATYPES['snortdb_icmp_header.icmp_id'] = 'int'
DATATYPES['snortdb_icmp_header.seq'] = 'int'


