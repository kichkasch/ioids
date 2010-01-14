-- SQL File for creating required tables in the community database
--
-- Grid for Digital Security (G4DS)
-- Michael Pilgermann
-- mpilgerm@glam.ac.uk

--
-- Sections in here:
--  1. Communities / members
--  2. Relations for communities / members
--  3. Security stuff
--  4. Communication stuff
--  5. Services
--  6. Routing
--


--
-- 1st Section
--             Tables for communities and members
--
CREATE TABLE MEMBERS 
(
    ID VARCHAR(100) PRIMARY KEY,
    NAME VARCHAR(100),
    MDL VARCHAR(100000),   -- the member description in XML
    MDLVERSION VARCHAR(30),
    MDLDATE DATE
);

CREATE TABLE COMMUNITIES
(
    ID VARCHAR(100)  PRIMARY KEY,
    NAME VARCHAR(100),
    DESCRIPTION VARCHAR(500),
    TCDL VARCHAR(100000),   -- the tc description in XML
    TCDLVERSION VARCHAR(30),
    TCDLDATE DATE
);

--
-- 2nd Section
--             Tables for relations between communities and members
--
CREATE TABLE GATEWAYS
(
    MEMBER_ID VARCHAR(100) REFERENCES MEMBERS(ID),
    SOURCE_COMMUNITY_ID VARCHAR(100) REFERENCES COMMUNITIES(ID),
    DEST_COMMUNITY_ID VARCHAR(100) REFERENCES COMMUNITIES(ID)
);

CREATE TABLE COMMUNITIES_MEMBERS
(
    MEMBERID VARCHAR(100) REFERENCES MEMBERS(ID),
    COMMUNITYID VARCHAR(100) REFERENCES COMMUNITIES(ID)
);

CREATE TABLE COMMUNITIES_AUTHORITIES
(
    MEMBERID VARCHAR(100) REFERENCES MEMBERS(ID),
    COMMUNITYID VARCHAR(100) REFERENCES COMMUNITIES(ID)
);

--
-- 3rd Section
--             Tables for security stuff
--

CREATE TABLE ALGORITHMS
(
    ID VARCHAR(100) PRIMARY KEY,
    NAME VARCHAR(50)        -- NAME such as DSA, RSA, ...
);

CREATE TABLE CREDENTIALS
(
    ID VARCHAR(100) PRIMARY KEY,
    ALGORITHMID VARCHAR(50) REFERENCES ALGORITHMS(ID),
    USERNAME VARCHAR(50),   -- user name; optional depending on algorithm
    KEY VARCHAR(10000),      -- public key
    MEMBERID VARCHAR(100) REFERENCES MEMBERS(ID)
);

-- for each algorithm "I" support, i have to provide the credentials
CREATE TABLE PERSONALCREDENTIALS
(
    ID VARCHAR(100) PRIMARY KEY,
    NAME VARCHAR(50),
    ALGORITHMID VARCHAR(100) REFERENCES ALGORITHMS(ID),
    KEY_PRIVATE VARCHAR(10000),
    KEY_PUBLIC VARCHAR(10000),
    USERNAME VARCHAR(50)   -- user name; optional depending on algorithm    
);

CREATE TABLE COMMUNITIES_ALGORITHMS -- which algorithms are supported by which communtiy
(
    COMMUNITYID VARCHAR(100) REFERENCES COMMUNITIES(ID),
    ALGORITHMID VARCHAR(100) REFERENCES ALGORITHMS(ID)
);

--
-- 4th Section
--             Tables for communication
--
CREATE TABLE PROTOCOLS
(
    ID VARCHAR(100) PRIMARY KEY,
    NAME VARCHAR(50)       -- NAME such as SOAP, HTTP, SSH
);

CREATE TABLE ENDPOINTS      -- each endpoint is defined for a certain member within a certain community using a certain protocol with its specific key
(
    ID VARCHAR(100) PRIMARY KEY,
    MEMBERID VARCHAR(100) REFERENCES MEMBERS(ID),
    COMMUNITYID VARCHAR(100) REFERENCES COMMUNITIES(ID),
    PROTOCOLID VARCHAR(100) REFERENCES PROTOCOLS(ID),
    ADDRESS VARCHAR(500),   -- protocol specific address (e.g. URL for SOAP or IP/PORT for SSH)
    CREDENTIALID VARCHAR(100) REFERENCES CREDENTIALS(ID)
);

CREATE TABLE COMMUNITIES_PROTOCOLS  -- which protocols are supported by which community
(
    COMMUNITYID VARCHAR(100) REFERENCES COMMUNITIES(ID),
    PROTOCOLID VARCHAR(100) REFERENCES PROTOCOLS(ID)
);

--
-- 5th Section
--             Tables for Services and their relations
--
CREATE TABLE SERVICES
(
    ID VARCHAR(100) PRIMARY KEY,
    NAME VARCHAR(50),
    KSDL VARCHAR(100000),        -- Service description in Knowledge Service Description language
    KSDLVERSION VARCHAR(30),
    KSDLDATE DATE       -- Date of this version of the KSD
--    WSDL VARCHAR(10000),        -- Service description in Web Service Description Language
--    WSDLVERSION VARCHAR(30), -- Version of the file, not the WSDL version itself!
--    WSDLDATE DATE       -- Date of this version of teh WSD
);

CREATE TABLE SERVICES_COMMUNITIES
(
    SERVICEID VARCHAR(100) REFERENCES SERVICES(ID),
    COMMUNITYID VARCHAR(100) REFERENCES COMMUNITIES(ID)
);

CREATE TABLE SERVICES_MEMBERS
(
    SERVICEID VARCHAR(100) REFERENCES SERVICES(ID),
    MEMBERID VARCHAR(100) REFERENCES MEMBERS(ID)
);

CREATE TABLE SERVICES_AUTHORITIES
(
    SERVICEID VARCHAR(100) REFERENCES SERVICES(ID),
    MEMBERID VARCHAR(100) REFERENCES MEMBERS(ID)
);

--
-- 6th Section
--             Tables for routing
--
CREATE TABLE ROUTINGTABLE
(
    ID VARCHAR(100) PRIMARY KEY,
    SOURCE_COMMUNITY VARCHAR(100) REFERENCES COMMUNITIES(ID),
    DESTINATION_COMMUNITY VARCHAR(100) REFERENCES COMMUNITIES(ID),
    GATEWAY_MEMBER_ID VARCHAR(100) REFERENCES MEMBERS(ID),
    GATEWAY_COMMUNITY_ID VARCHAR(100) REFERENCES COMMUNITIES(ID),
    COSTS INT
);
