"""
Some additional information for XML database.

Tools for SoapSy

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
DATATYPES = {}

DATATYPES['event_type.event_type_id'] = 'bigserial'
DATATYPES['event_type.event_type_name'] = 'text'

DATATYPES['event.event_id'] = 'bigserial'
DATATYPES['event.timestmp'] = 'timestamp'
DATATYPES['event.obsrv_id'] = 'bigint'
DATATYPES['event.rprt_id'] = 'bigint'
DATATYPES['event.src_id'] = 'bigint'
DATATYPES['event.dstn_id'] = 'bigint'
DATATYPES['event.event_type_id'] = 'bigint'
DATATYPES['event.data_id'] = 'bigint'

DATATYPES['comp_type.comp_type_id'] = 'serial'
DATATYPES['comp_type.comp_type_name'] = 'text'

DATATYPES['computer.comp_id'] = 'bigserial'
DATATYPES['computer.hostname'] = 'text'
DATATYPES['computer.os'] = 'text'
DATATYPES['computer.ip'] = 'inet'
DATATYPES['computer.mac'] = 'macaddr'
DATATYPES['computer.domain'] = 'text'
DATATYPES['computer.comp_type_id'] = 'bigint'

DATATYPES['agent_class.agent_class_id'] = 'serial'
DATATYPES['agent_class.agent_class_name'] = 'varchar(3)'
DATATYPES['agent_class.agent_class_dscr'] = 'text'

DATATYPES['agent.agent_id'] = 'bigserial'
DATATYPES['agent.agent_name'] = 'text'
DATATYPES['agent.agent_class_id'] = 'bigint'
DATATYPES['agent.comp_id'] = 'bigint'

DATATYPES['observer.obsrv_id'] = 'bigserial'
DATATYPES['observer.obsrv_name'] = 'text'
DATATYPES['observer.agent_id'] = 'bigint'

DATATYPES['reporter.rprt_id'] = 'bigserial'
DATATYPES['reporter.rprt_name'] = 'text'
DATATYPES['reporter.agent_id'] = 'bigint'

DATATYPES['source.src_id'] = 'bigserial'
DATATYPES['source.src_name'] = 'text'
DATATYPES['source.agent_id'] = 'bigint'

DATATYPES['destination.dstn_id'] = 'bigserial'
DATATYPES['destination.dstn_name'] = 'text'
DATATYPES['destination.agent_id'] = 'bigint'

DATATYPES['process.prcss_id'] = 'bigserial'
DATATYPES['process.prcss_pid'] = 'biginit'
DATATYPES['process.prcss_name_id'] = 'biginit'
DATATYPES['process.prcss_type_id'] = 'biginit'
DATATYPES['process.usr_id'] = 'biginit'

DATATYPES['prcss_name.prcss_name_id'] = 'bigserial'
DATATYPES['prcss_name.process_name'] = 'text'

DATATYPES['prcss_type.prcss_type_id'] = 'bigserial'
DATATYPES['prcss_type.prcss_type_name'] = 'text'

DATATYPES['usr.usr_id'] = 'bigserial'
DATATYPES['usr.usr_name'] = 'text'
DATATYPES['usr.usr_group_id'] = 'bigint'

DATATYPES['usr_group.usr_group_id'] = 'bigserial'
DATATYPES['usr_group.usr_group_name'] = 'text'
DATATYPES['usr_group.usr_group_domain'] = 'text'

DATATYPES['data.data_id'] = 'bigserial'
DATATYPES['data.data_text'] = 'text'
DATATYPES['data.encoding_id'] = 'bigint'

DATATYPES['encoding.encoding_id'] = 'bigserial'
DATATYPES['encoding.encoding_type'] = 'varchar(8)'
