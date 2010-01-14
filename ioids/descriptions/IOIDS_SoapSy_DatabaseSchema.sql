
CREATE TABLE agent_class
( 
agent_class_id serial NOT NULL, 
agent_class_name varchar(3) NOT NULL, 
agent_class_dscr text NOT NULL, 
PRIMARY KEY (agent_class_id)
);
GRANT ALL ON TABLE agent_class TO uioids;
CREATE UNIQUE INDEX agent_class_name_idx ON agent_class (agent_class_name); 
GRANT ALL ON TABLE agent_class_agent_class_id_seq TO uioids;
INSERT INTO agent_class (agent_class_name, agent_class_dscr) VALUES ('000', 'Unknown Agent Class'); 
INSERT INTO agent_class (agent_class_name, agent_class_dscr) VALUES ('c00', 'computer'); 
INSERT INTO agent_class (agent_class_name, agent_class_dscr) VALUES ('cp0', 'process runnning on computer'); 
INSERT INTO agent_class (agent_class_name, agent_class_dscr) VALUES ('cpu', 'user logged and running process on computer'); 

CREATE TABLE comp_type
( 
comp_type_id serial NOT NULL, 
comp_type_name text, 
PRIMARY KEY (comp_type_id)
);
GRANT ALL ON TABLE comp_type TO uioids;
CREATE UNIQUE INDEX comp_type_name_idx ON comp_type (comp_type_name); 
GRANT ALL ON TABLE comp_type_comp_type_id_seq TO uioids;

CREATE TABLE computer
( 
comp_id bigserial NOT NULL, 
hostname text, 
os text, 
ip inet, 
mac macaddr, 
domain text, 
comp_type_id bigint, 
PRIMARY KEY (comp_id), 
FOREIGN KEY (comp_type_id) REFERENCES comp_type (comp_type_id)
);
GRANT ALL ON TABLE computer TO uioids;
GRANT ALL ON TABLE computer_computer_id_seq TO uioids;

CREATE TABLE prcss_name
( 
prcss_name_id bigserial NOT NULL, 
process_name text, 
PRIMARY KEY (prcss_name_id)
);
GRANT ALL ON TABLE prcss_name TO uioids;
CREATE UNIQUE INDEX process_name_idx ON prcss_name (process_name); 
GRANT ALL ON TABLE prcss_name_prcss_name_id_seq TO uioids;

CREATE TABLE prcss_type
( 
prcss_type_id serial NOT NULL, 
prcss_type_name text, 
PRIMARY KEY (prcss_type_id)
);
GRANT ALL ON TABLE prcss_type TO uioids;
GRANT ALL ON TABLE prcss_type_prcss_type_id_seq TO uioids;
INSERT INTO prcss_type (prcss_type_name) VALUES ('user'); 
INSERT INTO prcss_type (prcss_type_name) VALUES ('system'); 
INSERT INTO prcss_type (prcss_type_name) VALUES ('zombie'); 
INSERT INTO prcss_type (prcss_type_name) VALUES ('Unknown'); 

CREATE TABLE usr_group
( 
usr_group_id serial NOT NULL, 
usr_group_name text, 
usr_group_domain text, 
PRIMARY KEY (usr_group_id)
);
GRANT ALL ON TABLE usr_group TO uioids;
CREATE UNIQUE INDEX usr_group_name_idx ON usr_group (usr_group_name); 
GRANT ALL ON TABLE usr_group_usr_group_id_seq TO uioids;

CREATE TABLE usr
( 
usr_id bigserial NOT NULL, 
usr_name text, 
usr_group_id bigint, 
PRIMARY KEY (usr_id), 
FOREIGN KEY (usr_group_id) REFERENCES usr_group (usr_group_id)
);
GRANT ALL ON TABLE usr TO uioids;
CREATE UNIQUE INDEX usr_name_idx ON usr (usr_name); 
GRANT ALL ON TABLE usr_usr_id_seq TO uioids;

CREATE TABLE process
( 
prcss_id bigserial NOT NULL, 
prcss_pid bigint, 
prcss_name_id bigint NOT NULL, 
prcss_type_id bigint, 
usr_id bigint, 
PRIMARY KEY (prcss_id), 
FOREIGN KEY (prcss_name_id) REFERENCES prcss_name (prcss_name_id), 
FOREIGN KEY (prcss_type_id) REFERENCES prcss_type (prcss_type_id), 
FOREIGN KEY (usr_id) REFERENCES usr (usr_id)
);
GRANT ALL ON TABLE process TO uioids;
GRANT ALL ON TABLE process_process_id_seq TO uioids;

CREATE TABLE agent
( 
agent_id bigserial NOT NULL, 
agent_name text NOT NULL, 
agent_class_id bigint NOT NULL, 
comp_id bigint NOT NULL, 
prcss_id bigint, 
PRIMARY KEY (agent_id), 
FOREIGN KEY (agent_class_id) REFERENCES agent_class (agent_class_id), 
FOREIGN KEY (comp_id) REFERENCES computer (comp_id), 
FOREIGN KEY (prcss_id) REFERENCES process (prcss_id)
);
GRANT ALL ON TABLE agent TO uioids;
GRANT ALL ON TABLE agent_agent_id_seq TO uioids;

CREATE TABLE observer
( 
obsrv_id bigserial NOT NULL, 
obsrv_name text, 
agent_id bigint NOT NULL, 
PRIMARY KEY (obsrv_id), 
FOREIGN KEY (agent_id) REFERENCES agent (agent_id)
);
GRANT ALL ON TABLE observer TO uioids;
GRANT ALL ON TABLE observer_observer_id_seq TO uioids;

CREATE TABLE reporter
( 
rprt_id bigserial NOT NULL, 
rprt_name text, 
agent_id bigint NOT NULL, 
PRIMARY KEY (rprt_id), 
FOREIGN KEY (agent_id) REFERENCES agent (agent_id)
);
GRANT ALL ON TABLE reporter TO uioids;
GRANT ALL ON TABLE reporter_reporter_id_seq TO uioids;

CREATE TABLE source
( 
src_id bigserial NOT NULL, 
src_name text, 
agent_id bigint NOT NULL, 
PRIMARY KEY (src_id), 
FOREIGN KEY (agent_id) REFERENCES agent (agent_id)
);
GRANT ALL ON TABLE source TO uioids;
GRANT ALL ON TABLE source_source_id_seq TO uioids;

CREATE TABLE destination
( 
dstn_id bigserial NOT NULL, 
dstn_name text NOT NULL, 
agent_id bigint NOT NULL, 
PRIMARY KEY (dstn_id), 
FOREIGN KEY (agent_id) REFERENCES agent (agent_id)
);
GRANT ALL ON TABLE destination TO uioids;
GRANT ALL ON TABLE destination_destination_id_seq TO uioids;

CREATE TABLE event_type
( 
event_type_id bigserial NOT NULL, 
event_type_name text, 
PRIMARY KEY (event_type_id)
);
GRANT ALL ON TABLE event_type TO uioids;
CREATE UNIQUE INDEX event_type_name_idx ON event_type (event_type_name); 
GRANT ALL ON TABLE event_type_event_type_id_seq TO uioids;
INSERT INTO event_type (event_type_name) VALUES ('generic'); 

CREATE TABLE encoding
( 
encoding_id bigserial NOT NULL, 
encoding_type varchar(8), 
PRIMARY KEY (encoding_id)
);
GRANT ALL ON TABLE encoding TO uioids;
CREATE UNIQUE INDEX encoding_type_idx ON encoding (encoding_type); 
GRANT ALL ON TABLE encoding_encoding_id_seq TO uioids;
INSERT INTO encoding (encoding_type) VALUES ('ASCII'); 
INSERT INTO encoding (encoding_type) VALUES ('HEX'); 
INSERT INTO encoding (encoding_type) VALUES ('OCT'); 
INSERT INTO encoding (encoding_type) VALUES ('NOT'); 

CREATE TABLE data
( 
data_id serial NOT NULL, 
data_text text, 
encoding_id bigint, 
PRIMARY KEY (data_id), 
FOREIGN KEY (encoding_id) REFERENCES encoding (encoding_id)
);
GRANT ALL ON TABLE data TO uioids;
GRANT ALL ON TABLE data_data_id_seq TO uioids;

CREATE TABLE event
( 
event_id bigserial NOT NULL, 
timestmp timestamp NOT NULL, 
obsrv_id bigint NOT NULL, 
rprt_id bigint NOT NULL, 
src_id bigint NOT NULL, 
dstn_id bigint NOT NULL, 
event_type_id bigint NOT NULL, 
data_id bigint, 
PRIMARY KEY (event_id), 
FOREIGN KEY (obsrv_id) REFERENCES observer (obsrv_id), 
FOREIGN KEY (rprt_id) REFERENCES reporter (rprt_id), 
FOREIGN KEY (src_id) REFERENCES source (src_id), 
FOREIGN KEY (dstn_id) REFERENCES destination (dstn_id), 
FOREIGN KEY (event_type_id) REFERENCES event_type (event_type_id), 
FOREIGN KEY (data_id) REFERENCES data (data_id)
);
GRANT ALL ON TABLE event TO uioids;
GRANT ALL ON TABLE event_event_id_seq TO uioids;

CREATE TABLE ioids_classification
( 
classification_id bigserial NOT NULL, 
classification_code int, 
classification_name text, 
PRIMARY KEY (classification_id)
);
GRANT ALL ON TABLE ioids_classification TO uioids;
CREATE UNIQUE INDEX classification_code_idx ON ioids_classification (classification_code); 
CREATE UNIQUE INDEX classification_name_idx ON ioids_classification (classification_name); 
GRANT ALL ON TABLE ioids_classification_ioids_classification_id_seq TO uioids;
INSERT INTO ioids_classification (classification_code, classification_name) VALUES (0, 'confidential'); 
INSERT INTO ioids_classification (classification_code, classification_name) VALUES (10, 'public'); 

CREATE TABLE ioids_peer
( 
ioids_peer_id bigserial NOT NULL, 
peer_memberid varchar(100), 
PRIMARY KEY (ioids_peer_id)
);
GRANT ALL ON TABLE ioids_peer TO uioids;
GRANT ALL ON TABLE ioids_peer_ioids_peer_id_seq TO uioids;

CREATE TABLE ioids_sender
( 
ioids_sender_id bigserial NOT NULL, 
ioids_peer_id bigint, 
PRIMARY KEY (ioids_sender_id), 
FOREIGN KEY (ioids_peer_id) REFERENCES ioids_peer (ioids_peer_id)
);
GRANT ALL ON TABLE ioids_sender TO uioids;
GRANT ALL ON TABLE ioids_sender_ioids_sender_id_seq TO uioids;

CREATE TABLE ioids_source
( 
ioids_source_id bigserial NOT NULL, 
ioids_peer_id bigint, 
PRIMARY KEY (ioids_source_id), 
FOREIGN KEY (ioids_peer_id) REFERENCES ioids_peer (ioids_peer_id)
);
GRANT ALL ON TABLE ioids_source TO uioids;
GRANT ALL ON TABLE ioids_source_ioids_source_id_seq TO uioids;

CREATE TABLE ioids_event
( 
ioids_event_id bigserial NOT NULL, 
event_id bigint, 
ioids_sender_id varchar(100), 
ioids_source_id varchar(100), 
timestamp_received timestamp NOT NULL, 
community_id varchar(100), 
classification_id bigint, 
ioids_message_id varchar(100), 
PRIMARY KEY (ioids_event_id), 
FOREIGN KEY (event_id) REFERENCES event (event_id), 
FOREIGN KEY (ioids_sender_id) REFERENCES ioids_sender (ioids_sender_id), 
FOREIGN KEY (ioids_source_id) REFERENCES ioids_source (ioids_source_id), 
FOREIGN KEY (classification_id) REFERENCES ioids_classification (classification_id)
);
GRANT ALL ON TABLE ioids_event TO uioids;
CREATE UNIQUE INDEX timestamp_received_idx ON ioids_event (timestamp_received); 
GRANT ALL ON TABLE ioids_event_ioids_event_id_seq TO uioids;

CREATE TABLE ioids_relation_type
( 
ioids_relation_type_id bigserial NOT NULL, 
ioids_relation_type_name text, 
PRIMARY KEY (ioids_relation_type_id)
);
GRANT ALL ON TABLE ioids_relation_type TO uioids;
CREATE UNIQUE INDEX ioids_relation_type_name_idx ON ioids_relation_type (ioids_relation_type_name); 
GRANT ALL ON TABLE ioids_relation_type_ioids_relation_type_id_seq TO uioids;
INSERT INTO ioids_relation_type (ioids_relation_type_name) VALUES ('parent'); 
INSERT INTO ioids_relation_type (ioids_relation_type_name) VALUES ('reference'); 

CREATE TABLE ioids_relation
( 
ioids_relation_id bigserial NOT NULL, 
ioids_event_id bigint, 
event_id bigint, 
ioids_relation_type_id bigint, 
PRIMARY KEY (ioids_relation_id), 
FOREIGN KEY (ioids_event_id) REFERENCES ioids_event (ioids_event_id), 
FOREIGN KEY (event_id) REFERENCES event (event_id), 
FOREIGN KEY (ioids_relation_type_id) REFERENCES ioids_relation_type (ioids_relation_type_id)
);

CREATE TABLE snortdb_signature
( 
signature_id bigserial NOT NULL, 
name varchar(255), 
class varchar(60), 
priority bigint, 
revision bigint, 
internal_id bigint, 
PRIMARY KEY (signature_id)
);
GRANT ALL ON TABLE snortdb_signature TO uioids;
GRANT ALL ON TABLE snortdb_signature_snortdb_signature_id_seq TO uioids;

CREATE TABLE snortdb_sensor
( 
sensor_id bigserial NOT NULL, 
hostname text, 
interface text, 
filter text, 
encoding text, 
detail text, 
PRIMARY KEY (sensor_id)
);
GRANT ALL ON TABLE snortdb_sensor TO uioids;
GRANT ALL ON TABLE snortdb_sensor_snortdb_sensor_id_seq TO uioids;

CREATE TABLE snortdb_tcp_header
( 
tcp_header_id bigserial NOT NULL, 
source_port int, 
destination_port int, 
seq bigint, 
ack bigint, 
offst int, 
reserved int, 
flags int, 
window int, 
checksum int, 
urgent int, 
PRIMARY KEY (tcp_header_id)
);
GRANT ALL ON TABLE snortdb_tcp_header TO uioids;
GRANT ALL ON TABLE snortdb_tcp_header_snortdb_tcp_header_id_seq TO uioids;

CREATE TABLE snortdb_udp_header
( 
udp_header_id bigserial NOT NULL, 
source_port int, 
destination_port int, 
length int, 
checksum int, 
PRIMARY KEY (udp_header_id)
);
GRANT ALL ON TABLE snortdb_udp_header TO uioids;
GRANT ALL ON TABLE snortdb_udp_header_snortdb_udp_header_id_seq TO uioids;

CREATE TABLE snortdb_icmp_header
( 
icmp_header_id bigserial NOT NULL, 
type int, 
code int, 
checksum int, 
icmp_id int, 
seq int, 
PRIMARY KEY (icmp_header_id)
);
GRANT ALL ON TABLE snortdb_icmp_header TO uioids;
GRANT ALL ON TABLE snortdb_icmp_header_snortdb_icmp_header_id_seq TO uioids;

CREATE TABLE snortdb_ip_header
( 
ip_header_id bigserial NOT NULL, 
source_ip bigint, 
destination_ip bigint, 
version int, 
header_length int, 
tos int, 
datagram_length int, 
ip_id int, 
flags int, 
offst int, 
ttl int, 
protocol int, 
checksum int, 
tcp_header_id bigint, 
udp_header_id bigint, 
icmp_header_id bigint, 
PRIMARY KEY (ip_header_id), 
FOREIGN KEY (tcp_header_id) REFERENCES snortdb_tcp_header (tcp_header_id), 
FOREIGN KEY (udp_header_id) REFERENCES snortdb_udp_header (udp_header_id), 
FOREIGN KEY (icmp_header_id) REFERENCES snortdb_icmp_header (icmp_header_id)
);
GRANT ALL ON TABLE snortdb_ip_header TO uioids;
GRANT ALL ON TABLE snortdb_ip_header_snortdb_ip_header_id_seq TO uioids;

CREATE TABLE snortdb_payload
( 
payload_id bigserial NOT NULL, 
data text, 
PRIMARY KEY (payload_id)
);
GRANT ALL ON TABLE snortdb_payload TO uioids;
GRANT ALL ON TABLE snortdb_payload_snortdb_payload_id_seq TO uioids;

CREATE TABLE snortdb_event
( 
snortdb_event_id bigserial NOT NULL, 
event_id bigint, 
timestamp timestamp NOT NULL, 
sid varchar(100), 
cid varchar(100), 
ip_header_id bigint, 
signature_id bigint, 
sensor_id bigint, 
payload_id bigint, 
PRIMARY KEY (snortdb_event_id), 
FOREIGN KEY (event_id) REFERENCES event (event_id), 
FOREIGN KEY (ip_header_id) REFERENCES snortdb_ip_header (ip_header_id), 
FOREIGN KEY (signature_id) REFERENCES snortdb_signature (signature_id), 
FOREIGN KEY (sensor_id) REFERENCES snortdb_sensor (sensor_id), 
FOREIGN KEY (payload_id) REFERENCES snortdb_payload (payload_id)
);
GRANT ALL ON TABLE snortdb_event TO uioids;
GRANT ALL ON TABLE snortdb_event_snortdb_event_id_seq TO uioids;
