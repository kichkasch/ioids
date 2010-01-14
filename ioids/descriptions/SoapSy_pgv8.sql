
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
hostname text NOT NULL, 
os text, 
ip inet NOT NULL, 
mac macaddr, 
domain text, 
comp_type_id bigint, 
PRIMARY KEY (comp_id), 
FOREIGN KEY (comp_type_id) REFERENCES comp_type (comp_type_id)
);
GRANT ALL ON TABLE computer TO uioids;
CREATE UNIQUE INDEX hostname_idx ON computer (hostname); 
CREATE UNIQUE INDEX ip_idx ON computer (ip); 
CREATE UNIQUE INDEX domain_idx ON computer (domain); 
GRANT ALL ON TABLE computer_computer_id_seq TO uioids;

CREATE TABLE agent
( 
agent_id bigserial NOT NULL, 
agent_name text NOT NULL, 
agent_class_id bigint NOT NULL, 
comp_id bigint NOT NULL, 
PRIMARY KEY (agent_id), 
FOREIGN KEY (agent_class_id) REFERENCES agent_class (agent_class_id), 
FOREIGN KEY (comp_id) REFERENCES computer (comp_id)
);
GRANT ALL ON TABLE agent TO uioids;
CREATE UNIQUE INDEX agent_name_idx ON agent (agent_name); 
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
CREATE UNIQUE INDEX obsrv_name_idx ON observer (obsrv_name); 
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
CREATE UNIQUE INDEX rprt_name_idx ON reporter (rprt_name); 
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
CREATE UNIQUE INDEX src_name_idx ON source (src_name); 
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
CREATE UNIQUE INDEX dstn_name_idx ON destination (dstn_name); 
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
CREATE UNIQUE INDEX timestmp_idx ON event (timestmp); 
GRANT ALL ON TABLE event_event_id_seq TO uioids;

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
comp_id bigint NOT NULL, 
usr_id bigint, 
PRIMARY KEY (prcss_id), 
FOREIGN KEY (prcss_name_id) REFERENCES prcss_name (prcss_name_id), 
FOREIGN KEY (prcss_type_id) REFERENCES prcss_type (prcss_type_id), 
FOREIGN KEY (comp_id) REFERENCES computer (comp_id), 
FOREIGN KEY (usr_id) REFERENCES usr (usr_id)
);
GRANT ALL ON TABLE process TO uioids;
GRANT ALL ON TABLE process_process_id_seq TO uioids;
