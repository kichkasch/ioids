"""
Configuration file for XML names for G4DS

Grid for Digital Security (G4DS)

Modules import that module and may read the settings important to them.


@author: Michael Pilgermann
@contact: mailto:mpilgerm@glam.ac.uk
@license: GPL (General Public License)
"""

# root element
g4ds_root_node = 'g4ds'

# plain root element
g4ds_plain_root = 'g4dsplain'
g4ds_plain_messageid = 'messageid'
g4ds_plain_senderid = 'senderid'
g4ds_plain_referenceid = 'referenceid'
g4ds_plain_data = 'data'

# control messages
g4ds_control_node = 'control'
g4ds_control_ssid = 'subsystemid'
g4ds_control_ssname = 'subsystemname'
g4ds_control_data = 'data'

# service messages
g4ds_service_node = 'service'
g4ds_service_sid = 'serviceid'
g4ds_service_name = 'servicename'
g4ds_service_data = 'data'

# encrypted G4DS message chunks
g4ds_encryption_node = 'enc'
g4ds_encryption_algorithm = 'algorithm'
g4ds_encryption_data = 'data'

# G4DS signature chunks
g4ds_signature_node = 'signed'
g4ds_signature_algorithm = 'algorithm'
g4ds_signature_senderid = "senderid"
g4ds_signature_communityid = "communityid"
g4ds_signature_data = 'data'
g4ds_signature_signature = 'signature'


#
# control messages - control subsystem tags
#
g4ds_control_ss_member = 'ss-member'
g4ds_control_ss_community = 'ss-community'
g4ds_control_ss_routing = 'ss-routing'
g4ds_control_ss_service = 'ss-service'
g4ds_control_ss_action = 'action'
g4ds_control_ss_sucess = 'sucess'
g4ds_control_ss_arguments = 'arguments'
g4ds_control_ss_data = 'data'

#
# Member Description Language Tags
#
mdl_node = 'mdl'
mdl_id = 'id'
mdl_version = 'version'
mdl_name = 'name'
mdl_creationdate = 'creationdate'

mdl_description = 'description'
mdl_description_fullname = 'fullname'
mdl_description_organisation = 'organisation'
mdl_description_location = 'location'
mdl_description_location_country = 'country'
mdl_description_location_country_code = 'code'
mdl_description_location_country_name = 'name'
mdl_description_location_city = 'city'

mdl_credentials = 'credentials'
mdl_credentials_credential = 'credential'
mdl_credentials_credential_docid = 'docid'
mdl_credentials_credential_username = 'username'
mdl_credentials_credential_publickey = 'publickey'
mdl_credentials_credential_publickey_algorithm = 'algorithm'
mdl_credentials_credential_publickey_algorithm_name = 'name'
mdl_credentials_credential_publickey_value = 'value'

mdl_communities = 'communities'
mdl_communities_community = 'community'
mdl_communities_community_id = 'id'
mdl_communities_community_endpoints = 'endpoints'
mdl_communities_community_endpoints_endpoint = 'endpoint'
mdl_communities_community_endpoints_endpoint_protocol = 'protocol'
mdl_communities_community_endpoints_endpoint_address = 'address'
mdl_communities_community_endpoints_endpoint_credential = 'credential'
mdl_communities_community_endpoints_endpoint_credential_docid = 'docid'

#
# Community Description Language Tags
#
tcdl_node = 'tcdl'
tcdl_id = 'id'
tcdl_version = 'version'
tcdl_name = 'name'
tcdl_creationdate = 'creationdate'

tcdl_description = 'description'
tcdl_description_fullname = 'fullname'
tcdl_description_organisation = 'organisation'
tcdl_description_location = 'location'
tcdl_description_location_country = 'country'
tcdl_description_location_country_code = 'code'
tcdl_description_location_country_name = 'name'
tcdl_description_location_city = 'city'

tcdl_communication = 'communication'
tcdl_communication_protocols = 'protocols'
tcdl_communication_protocols_protocol = 'protocol'
tcdl_communication_protocols_protocol_name = 'name'
tcdl_communication_protocols_protocol_comment = 'comment'
tcdl_communication_algorithms = 'algorithms'
tcdl_communication_algorithms_algorithm = 'algorithm'
tcdl_communication_algorithms_algorithm_name = 'name'
tcdl_communication_algorithms_algorithm_comment = 'comment'

tcdl_authorities = 'authorities'
tcdl_authorities_authority = 'authority'
tcdl_authorities_authority_id = 'memberid'
tcdl_authorities_authority_endpoint = 'endpoint'
tcdl_authorities_authority_endpoint_protocol = 'protocol'
tcdl_authorities_authority_endpoint_address = 'address'
tcdl_authorities_authority_endpoint_credential = 'credential'
tcdl_authorities_authority_endpoint_credential_algorithm = 'algorithm'
tcdl_authorities_authority_endpoint_credential_publickey = 'publickey'

tcdl_routing = 'routing'
tcdl_routing_gateways = 'gateways'
tcdl_routing_gateways_incoming = 'incoming'
tcdl_routing_gateways_incoming_gateway = 'gateway'
tcdl_routing_gateways_incoming_gateway_memberid = 'memberid'
tcdl_routing_gateways_incoming_gateway_source = 'source'
tcdl_routing_gateways_incoming_gateway_source_communityid = 'communityid'
tcdl_routing_gateways_outgoing = 'outgoing'
tcdl_routing_gateways_outgoing_gateway = 'gateway'
tcdl_routing_gateways_outgoing_gateway_memberid = 'memberid'
tcdl_routing_gateways_outgoing_gateway_destination = 'destination'
tcdl_routing_gateways_outgoing_gateway_destination_communityid = 'communityid'

tcdl_policy = 'policy'
tcdl_policy_browsalbe = 'browsable'     # may a list of members be requested from the CAs


#
# Service Description Language Tags
#
ksdl_node = 'ksdl'
ksdl_id = 'id'
ksdl_version = 'version'
ksdl_name = 'name'
ksdl_creationdate = 'creationdate'
ksdl_lastupdate = 'lastupdate'

ksdl_description = 'description'
ksdl_description_fullname = 'fullname'
ksdl_description_contacts = 'contacts'
ksdl_description_contacts_contact = 'contact'
ksdl_description_contacts_contact_name = 'name'
ksdl_description_contacts_contact_organisation = 'organisation'
ksdl_description_contacts_contact_email = 'email'

ksdl_communication = 'communication'
ksdl_communication_communities = 'communities'
ksdl_communication_communities_community = 'community'
ksdl_communication_communities_community_id = 'id'
ksdl_communication_messageformats = 'messageformats'
ksdl_communication_messageformats_messageformat = 'messageformat'
ksdl_communication_messageformats_messageformat_id = 'id'
ksdl_communication_messageformats_messageformat_name = 'name'
ksdl_communication_messageformats_messageformat_definition = 'definition'

ksdl_authorities = 'authorities'
ksdl_authorities_authority = 'authority'
ksdl_authorities_authority_memberid = 'memberid'

#
# Tags for generic wrapper
#
gen_action = 'action'
gen_data = 'data'


#
# Tags for routing table wrapper
#
rtbl_routing_table = 'routingtable'
rtbl_routing_table_entries = 'routingtableentries'
rtbl_routing_table_entries_entry = 'routingtableentry'
rtbl_routing_table_entries_entry_source = 'source'
rtbl_routing_table_entries_entry_destination = 'destination'
rtbl_routing_table_entries_entry_gatewaytc = 'gateway_community'
rtbl_routing_table_entries_entry_gatewaymember = 'gateway_member'
rtbl_routing_table_entries_entry_costs = 'costs'


#
# Tags for policy files
#
pol_policy = 'g4dspolicy'

pol_policy_roles = 'roles'
pol_policy_roles_roleset = 'roleset'
pol_policy_roles_roleset_type = 'type'
pol_policy_roles_roleset_role = 'role'
pol_policy_roles_roleset_role_name = 'name'
pol_policy_roles_roleset_role_description = 'description'

pol_policy_groups = 'groups'
pol_policy_groups_group = 'group'
pol_policy_groups_group_rolename = 'rolename'
pol_policy_groups_group_representatives = 'representatives'
pol_policy_groups_group_representatives_representative = 'representative'
pol_policy_groups_group_representatives_representative_type = 'type'
pol_policy_groups_group_exceptions = 'exceptions'
pol_policy_groups_group_exceptions_representative = 'representative'
pol_policy_groups_group_exceptions_representative_type = 'type'

pol_policy_rules = 'rules'
pol_policy_rules_ruleset = 'ruleset'
pol_policy_rules_ruleset_id = 'id'
pol_policy_rules_ruleset_name = 'name'
pol_policy_rules_ruleset_rule = 'rule'
pol_policy_rules_ruleset_rule_id = 'id'
pol_policy_rules_ruleset_rule_comment = 'comment'
pol_policy_rules_ruleset_rule_actor = 'actor'
pol_policy_rules_ruleset_rule_actor_type = 'type'
pol_policy_rules_ruleset_rule_action = 'action'
pol_policy_rules_ruleset_rule_action_type = 'type'
pol_policy_rules_ruleset_rule_target = 'target'
pol_policy_rules_ruleset_rule_target_type = 'type'
pol_policy_rules_ruleset_rule_reaction = 'reaction'
pol_policy_rules_ruleset_rule_reaction_type = 'type'
