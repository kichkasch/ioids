"""
All stuff involving communication for G4DS.

Grid for Digital Security (G4DS)

Protocols and Endpoints are managed in here. For each of them a Manager is available through
a Singleton interface (getXXXManager). The managers are maintaining the database backend
connections and provide functions for lists of entries or loading an entry in particular.

@author: Michael Pilgermann
@contact: mailto:mpilgerm@glam.ac.uk
@license: GPL (General Public License)

@var _protocolManager: Instance to the L{ProtocolManager} class, accessable through function L{getProtocolManager}
@type _protocolManager: L{ProtocolManager}
@var _endpointManager: Instance to the L{EndpointManager} class, accessable through function L{getEndpointManager}
@type _endpointManager: L{EndpointManager}
"""

import tools
import config
import communicationmanager_db

# ##########################################
# ##########################################
# "Singleton" stuff
_protocolManager = None
_endpointManager = None

def getProtocolManager():
    """
    Singleton - returns the instance to the protocol manager
    
    If the instance has not yet been initialised, this will be done. Finally, the
    instance is returned.
    
    @return: The only instance to a Protocol Manager
    @rtype: L{ProtocolManager}
    """
    global _protocolManager
    if _protocolManager == None:
        _protocolManager = ProtocolManager(config.dbconnected)
    return _protocolManager
    
def getEndpointManager():
    """
    Singleton - returns the instance to the endpoint manager
    
    If the instance has not yet been initialised, this will be done. Finally, the
    instance is returned.
    
    @return: The only instance to a Endpoint Manager
    @rtype: L{EndpointManager}
    """
    global _endpointManager
    if _endpointManager == None:
        _endpointManager = EndpointManager(config.dbconnected)
    return _endpointManager
# ##########################################
# ##########################################


class EndpointManager:
    """
    Maintains the list of endpoints.

    @ivar _endpoints: Dictionary, maintaining the endpoints - accessable by its id
    @type _endpoints: C{Dict} (C{String} | L{Endpoint})
    @ivar _dbconnected: Indicates, whether the manager is connected to a database; hence whether the changes 
        shall be written through
    @type _dbconnected: C{Boolean}
    @ivar _comm_db: Communication Database Connector
    @type _comm_db: L{communicationmanager_db.CommDB}
    """
    def __init__(self, loadFromDatabase = config.dbconnected):
        """
        Initialises the manager with the subjacent database.

        @param loadFromDatabase: Indicates, whether the manager shall be initialised from the database backend
        @type loadFromDatabase: C{Boolean}
        """
        self._endpoints = {}
        self._dbconnected = loadFromDatabase
        if self._dbconnected:
            self._comm_db = communicationmanager_db.CommDB()
            endpoints = self._comm_db.getEndpoints()
            
            for endpoint in endpoints:
                self.addEndpoint(endpoint, 0)

    def __str__(self):
        """
        Some basic information about the object
        """
        return "EndpointManager: %d Endpoints." %(len(self._endpoints))
        
    def addEndpoint(self, endpoint, persistent = config.dbconnected):
        """
        Add one endpoint to the manager.
        
        @param endpoint: Endpoint to be added
        @type endpoint: L{Endpoint}
        @param persistent: Indicates, whether the protocol shall be written through to the database
        @type persistent: C{Boolean}
        """
        self._endpoints[endpoint.getId()] = endpoint
        if persistent:
            self._comm_db.addEndpoint(endpoint)


    def getEndpoint(self, endpointId):
        """
        Returns the endpoint instance for the given endpoint id.
        """
        return self._endpoints[endpointId]
        
    def getEndpoints(self):
        """
        Returns a list of all saved endpoints.
        
        @return: List of all endpoints
        @rtype: C{List} of L{Endpoint}
        """
        return self._endpoints.values()

    def findEndpoint(self, memberid, communityid, protocolname, algorithmname):
        """
        There is a problem to find the correct endpoint instance for incoming message.
        
        A function inside the db connector solves this problem. All the known information is put togehter, and voila,
        we have an endpoint id.
        """
        if self._dbconnected:
            endpointid = self._comm_db.findEndpoint(memberid, communityid, protocolname, algorithmname)
            return self.getEndpoint(endpointid)
            
    def getEndpointsForMember(self, memberid, communityid = None, communityNegativeList = []):
        """
        Provides a list of endpoints for a certain member.
        
        @param memberid: ID of the member the returned endpoints belong to
        @type memberid: C{String}
        @param communityid: ID of the community that should be used; might be None
        @type communityid: C{String}
        @return: List of endpoints the requested member is owner of
        @rtype: C{List} of L{Endpoint}
        """
        returnList = []
        for endpoint in self._endpoints.values():
            if endpoint.getMemberId() == memberid:
                try:
                    communityNegativeList.index(endpoint.getCommunityId())
                except ValueError:
                    # only if the community is not in the given negative list, we may proceed here
                    if communityid:
                        if endpoint.getCommunityId() == communityid:
                            returnList.append(endpoint)
                    else:
                        returnList.append(endpoint)
                
        return returnList

    def removeEndpoint(self, endpointid):
        """
        Removes the endpoint with the given id from the manager (and the database if connected).
        """
        del self._endpoints[endpointid]
        if self._dbconnected:
            self._comm_db.removeEndpoints(endpointid)
        
    def removeEndpointsForMember(self, memberid):
        """
        Removes all endpoints from the manager (and database) for the member with the given id.
        """
        for e in self._endpoints.values():
            if e.getMemberId() == memberid:
                self.removeEndpoint(e.getId())
        
class Endpoint:
    """
    Address information about node.
    
    Provides information about how to reach a certain node through a certain community using a certain
    protocol and appropriate credentials. In fact, for each of the combinations an endpoint instance
    has to be created.

    @ivar _id: Unique id for the protocol
    @type _id: C{String}
    @ivar _memberId: ID of the member providing this endpoint
    @type _memberId: C{String}
    @ivar _communityId: ID of the community the given member uses for this endpoint
    @type _communityId: C{String}
    @ivar _protocolId: ID of the protocol used for this endpoint (SOAP, HTTP, ...)
    @type _protocolId: C{String}
    @ivar _address: Protocol specific address of the endpoint. (Like URL for SOAP, IP for SSH, ...)
    @type _address: C{String}
    @ivar _credentialId: ID of the credential connected to the endpoint
    @type _credentialId: C{String}
    """
    def __init__(self, id = None, memberId = None, communityId = None, protocolId = None,
            address = None, credentialId = None, init = 0):
        """
        Initalises the Protocol and assigns the parameters to the local variables.
        
        @param id: Unique id for the protocol
        @type id: C{String}
        @param memberId: ID of the member providing this endpoint
        @type memberId: C{String}
        @param communityId: ID of the community the given member uses for this endpoint
        @type communityId: C{String}
        @param protocolId: ID of the protocol used for this endpoint (SOAP, HTTP, ...)
        @type protocolId: C{String}
        @param address: Protocol specific address of the endpoint. (Like URL for SOAP, IP for SSH, ...)
        @type address: C{String}
        @param credentialId: ID of the credential connected to the endpoint
        @type credentialId: C{String}
        @param init: Indidates, whether this instance is created during initialises process (of the container).
        @type init: C{Boolean}
        """
        self._id = id
        self._memberId = memberId
        self._communityId = communityId
        self._protocolId = protocolId
        self._address = address
        self._credentialId = credentialId
        
        if self._id == None:
            self._id = tools.generateId(tools.TYPE_ENDPOINT)
        
    def __str__(self):
        """
        Some basic information about the object
        """
        return "Endpoint (%s): MemberID is %s. Address: %s." %(self.getId(), self.getMemberId(), self.getAddress())
        
    
    def getId(self):
        """
        GETTER
        """
        return self._id
        
    def getMemberId(self):
        """ 
        GETTER
        """
        return self._memberId
        
    def getCommunityId(self):
        """ 
        GETTER
        """
        return self._communityId
        
    def getProtocolId(self):
        """ 
        GETTER
        """
        return self._protocolId
        
    def getAddress(self):
        """ 
        GETTER
        """
        return self._address
        
    def getCredentialId(self):
        """ 
        GETTER
        """
        return self._credentialId
        
        
class ProtocolManager:
    """
    Maintains a list of protocols.

    @ivar _protocols: Dictionary, maintaining the protocols - accessable by its id
    @type _protocols: C{Dict} (C{String} | L{Protocol})
    @ivar _dbconnected: Indicates, whether the manager is connected to a database; hence whether the changes 
        shall be written through
    @type _dbconnected: C{Boolean}
    @ivar _comm_db: Communication Database Connector
    @type _comm_db: L{communicationmanager_db.CommDB}
    """
    def __init__(self, loadFromDatabase = config.dbconnected):
        """
        Initialises the manager with the subjacent database.

        @param loadFromDatabase: Indicates, whether the manager shall be initialised from the database backend
        @type loadFromDatabase: C{Boolean}
        """
        self._protocols = {}
        self._dbconnected = loadFromDatabase
        if self._dbconnected:
            self._comm_db = communicationmanager_db.CommDB()
            protocols = self._comm_db.getProtocols()
            
            for protocol in protocols:
                self.addProtocol(protocol, 0)

    def __str__(self):
        """
        Some basic information about the object
        """
        return "ProtocolManager: %d Protocols." %(len(self._protocols))
            
    def addProtocol(self, protocol, persistent = config.dbconnected):
        """
        Add one protocol to the manager.
        
        @param protocol: Protocol to be added
        @type protocol: L{Protocol}
        @param persistent: Indicates, whether the protocol shall be written through to the database
        @type persistent: C{Boolean}
        """
        self._protocols[protocol.getId()] = protocol
        if persistent:
            self._comm_db.addProtocol(protocol)


    def getProtocol(self, protocolId):
        """
        Returns the protocol instance for the given protocol id.
        """
        return self._protocols[protocolId]
        
    def getProtocols(self):
        """
        Returns a list of all saved protocols.
        
        @return: List of all protocols
        @rtype: C{List} of L{Protocol}
        """
        return self._protocols.values()
        
    def getProtocolByNameAndInsert(self, protocolname):
        """
        Returns the protocol with given protocol name. 
        
        If the protocol is not yet in the manager it will be created.
        """
        for p in self._protocols.values():
            if p.getName() == protocolname:
                return p
        p = Protocol(None, protocolname)
        self.addProtocol(p)
        return p
        
class Protocol:
    """
    Maintains the relation between protocol names and their ids.

    @ivar _id: Unique id for the protocol
    @type _id: C{String}
    @ivar _name: Name for the protocol
    @type _name: C{String}
    """
    def __init__(self, id = None, name = None, init = 0):
        """
        Initalises the Protocol and assigns the parameters to the local variables.
        
        @param id: Unique id for the protocol
        @type id: C{String}
        @param name: Name for the protocol
        @type name: C{String}
        @param init: Indidates, whether this instance is created during initialises process (of the container).
        @type init: C{Boolean}
        """
        self._id = id
        self._name = name
        
        if self._id == None:
            self._id = tools.generateId(tools.TYPE_PROTOCOL)
        
    def __str__(self):
        """
        Some basic information about the object
        """
        return "Protocol (%s): %s." %(self.getId(), self.getName())
        
    
    def getId(self):
        """
        GETTER
        """
        return self._id
        
    def getName(self):
        """ 
        GETTER
        """
        return self._name
        
