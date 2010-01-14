-- SQL File for totally cleaning up the community database.
--
-- Grid for Digital Security (G4DS)
-- Michael Pilgermann
-- mpilgerm@glam.ac.uk
--
-- Note: Objects in here are deleted the opposite order than
-- created in createtables.sql. This is by purpose and due to
-- relations.

-- Tables for Routing
DROP TABLE ROUTINGTABLE;

-- Tables for Services
DROP TABLE SERVICES_AUTHORITIES;
DROP TABLE SERVICES_MEMBERS;
DROP TABLE SERVICES_COMMUNITIES;
DROP TABLE SERVICES;

-- Tables for communication
DROP TABLE COMMUNITIES_PROTOCOLS;
DROP TABLE ENDPOINTS;
DROP TABLE PROTOCOLS;

-- Tables for security stuff
DROP TABLE COMMUNTIES_ALGORITHMS;
DROP TABLE PERSONALCREDENTIALS;
DROP TABLE CREDENTIALS;
DROP TABLE ALGORITHMS;

-- Tables for relations between communities and members
DROP TABLE GATEWAYS;
DROP TABLE COMMUNITIES_MEMBERS;
DROP TABLE COMMUNITIES_AUTHORITIES;

-- Tables for communities and members
DROP TABLE MEMBERS CASCADE;
DROP TABLE COMMUNITIES CASCADE;
