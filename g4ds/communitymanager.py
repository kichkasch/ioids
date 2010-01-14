"""
Management of trusting communities and Members

Grid for Digital Security (G4DS)

Both classes CommunityManager and UserManager are implemented using the Singleton Pattern.
This way, only one instance must exist. Access this instance by

L{communitymanager.getCommunityManager} for the CommunityManager, and

L{communitymanager.getMemberManager} for the MemberManager.


@author: Michael Pilgermann
@contact: mailto:mpilgerm@glam.ac.uk
@license: GPL (General Public License)

@var _communityManager: Singleton - the only instance ever of the CommunityManager class
@type _communityManager: L{CommunityManager}
@var _memberManager: Singleton - the only instance ever of the MemberManager class
@type _memberManager: L{MemberManager}
"""

import config
import tools
import communitymanager_db

# ##########################################
# ##########################################
# "Singleton" stuff
_communityManager = None
_memberManager = None

def getCommunityManager():
    """
    Singleton - returns the instance to the community manager
    
    If the instance has not yet been initialised, this will be done. Finally, the
    instance is returned.
    
    @return: The only instance to a Community Manager
    @rtype: L{CommunityManager}
    """
    global _communityManager
    if _communityManager == None:
        _communityManager = CommunityManager(config.dbconnected)
    return _communityManager
    
def getMemberManager():
    """
    Singleton - returns the instance to the member manager
    
    If the instance has not yet been initialised, this will be done. Finally, the
    instance is returned.
    
    @return: The only instance to a Member Manager
    @rtype: L{MemberManager}
    """
    global _memberManager
    if _memberManager == None:
        _memberManager = MemberManager(config.dbconnected)
    return  _memberManager
# ##########################################
# ##########################################

class CommunityManager:
    """
    Responsible for maintaining information about Communities this node is member of
    
    Connected to a database. All the data is loaded into the memory at startup time.
    Changes are written through directly.
    
    @ivar _communities: Dictionary with all communities (key is the id, value a Community instance)
    @type _communities: C{Dict} of C{String} | L{Community}
    @ivar _dbconnected: Indicates, whether the manager is connected to a database; hence whether the changes 
        shall be written through
    @type _dbconnected: C{Boolean}
    @ivar _cm_db: Community Manager Database Connector
    @type _cm_db: L{communitymanager_db.CM_DB}
    """
    
    def __init__(self, loadFromDatabase = 0):
        """
        Initialises the Community Manager
        
        Instanstiates local variables. Loads all the stuff from the database.
        
        @param loadFromDatabase: Indicates, whether the manager shall be initialised from the database backend
        @type loadFromDatabase: C{Boolean}
        """
        self._communities = {}
        self._dbconnected = loadFromDatabase
        if loadFromDatabase:
            self._cm_db = communitymanager_db.CM_DB()
            communities = self._cm_db.getCommunities()
            for community in communities:
                self.addCommunity(community, persistent = 0)
                # also set the relations
                memberids = self._cm_db.getMembersOfCommunity(community.getId())
                for memberid in memberids:
                    community.addMember(memberid, loading = 1)
                
                # for the authorities
                authorityids = self._cm_db.getAuthoritiesOfCommunity(community.getId())
                for authorityid in authorityids:
                    community.addAuthority(authorityid, loading = 1)
                    
                # and the gateways
                gateways = self._cm_db.getGateways(communityid = community.getId())
                # gateways in the cm db are not registed with communities or members - so here we go
                for gateway in gateways:
                    community.addGateway(gateway)
                    
                # and the protocols
                protocols = self._cm_db.getProtocolsForCommunity(community.getId())
                for protocol in protocols:
                    community.addProtocol(protocol, loading = 1)
                    
                # and finally the algorithms
                algorithms = self._cm_db.getAlgorithmsForCommunity(community.getId())
                for algorithm in algorithms:
                    community.addAlgorithm(algorithm, loading = 1)
                
                
        
    def __str__(self):
        """
        Some basic information about the object
        """
        return "CommunityManager: %d Communities." %(len(self._communities))
    
    def addCommunity(self, community, persistent = config.dbconnected, storeMemberRelations = 0):
        """
        Adds a community instance to the repository
        
        @param community: Community to be inserted
        @type community: L{Community}
        @param persistent: Indicates, whether the community shall be written through to the database
        @type persistent: C{Boolean}
        @param storeMemberRelations: When persistent is true, shall the relations be saved in the db too?
        @type storeMemberRelations: C{Boolean}
        """
        self._communities[community.getId()] = community
        if persistent:
            self._cm_db.addCommunity(community, storeMemberRelations)
    
    def getCommunity(self, communityId):
        """
        Getter
        
        @param communityId: ID of the community to return
        @type communityId: C{String}
        @return: The community with the given id from the community repository.
        @rtype: L{Community}
        """
        return self._communities[communityId]
        
    def getCommunityIds(self):
        """
        GETTER
        
        @return: The list of ids off all communitities
        @rtype: C{List} of C{String}
        """
        return self._communities.keys()
        
    def updateCommunity(self, community, dropAuthorityRelations = 1, dropGatewayRelations = 1, dropMemberRelations = 0,
        dropProtocols = 1, dropAlgorithms = 1):
        """
        Updates or inserts the description for one community.
        
        @param community: Reference to the community instance to be updated
        @type community: L{Community}
        @param dropAuthorityRelations: Indicates, whether all relations for authorities shall be dropped
        @type dropAuthorityRelations: C{Boolean}
        @param dropGatewayRelations: Indicates, whether all relations for gateways shall be dropped
        @type dropGatewayRelations: C{Boolean}
        @param dropMemberRelations: Indicates, whether all relations for members shall be dropped
        @type dropMemberRelations: C{Boolean}
        """
        if self._communities.has_key(community.getId()):
            del self._communities[community.getId()]
            self._communities[community.getId()] = community
            if self._dbconnected:
                self._cm_db.updateCommunity(community, dropAuthorityRelations, dropGatewayRelations, 
                    dropMemberRelations, dropProtocols, dropAlgorithms)     

                # also set the relations
                if not dropMemberRelations:
                    memberids = self._cm_db.getMembersOfCommunity(community.getId())
                    for memberid in memberids:
                        community.addMember(memberid, loading = 1)
                
                # for the authorities
                if not dropAuthorityRelations:
                    authorityids = self._cm_db.getAuthoritiesOfCommunity(community.getId())
                    for authorityid in authorityids:
                        community.addAuthority(authorityid, loading = 1)
                    
                # and the gateways
                if not dropGatewayRelations:
                    gateways = self._cm_db.getGateways(communityid = community.getId())
                    # gateways in the cm db are not registed with communities or members - so here we go
                    for gateway in gateways:
                        community.addGateway(gateway)

                # same for the protocols
                if not dropProtocols:
                    protocols = self._cm_db.getProtocolsForCommunity(community.getId())
                    for protocol in protocols:
                        community.addProtocol(protocol, loading = 1)
                        
                # and finally the algorithms
                if not dropAlgorithms:
                    algorithms = self._cm_db.getAlgorithmsForCommunity(community.getId())
                    for algorithm in algorithms:
                        community.addAlgorithm(algorithm, loading = 1)
                
        else:
            self.addCommunity(community)
        return community
        
    def registerCommunityMemberRelation(self, communityid, memberid):
        """
        Passes the request to the database backend.
        
        @param communityid: ID of the community to put into relation
        @type communityid: C{String}
        @param memberid: ID of the member to put into relation
        @type memberid: C{String}
        """
        if self._dbconnected:
            self._cm_db.addCommunityMemberRelation(communityid, memberid)
            
    def registerCommunityAuthorityRelation(self, communityid, memberid):
        """
        Passes the request to the database backend.
        
        @param communityid: ID of the community to put into relation
        @type communityid: C{String}
        @param memberid: ID of the member to put into relation as a authority for the given community
        @type memberid: C{String}
        """
        if self._dbconnected:
            self._cm_db.addCommunityAuthorityRelation(communityid, memberid)
            
    def registerCommunityProtocolRelation(self, communityid, protocolid):
        """
        Passes the request to the database backend.
        
        @param communityid: The id of the community the protocol shall be added to
        @type communityid: C{String}
        @param protocolid: The id of the protocol, which shall be added to the community
        @type protocolid: C{String}
        """
        if self._dbconnected:
            self._cm_db.addProtocolToCommunity(communityid, protocolid)
    
    def registerCommunityAlgorithmRelation(self, communityid, algorithmid):
        """
        Passes the request to the database backend.
        
        @param communityid: The id of the community the algorithm shall be added to
        @type communityid: C{String}
        @param algorithmid: The id of the algorithm, which shall be added to the community
        @type algorithmid: C{String}
        """
        if self._dbconnected:
            self._cm_db.addAlgorithmToCommunity(communityid, algorithmid)
    
class Community:
    """
    All information about one community
    
    @ivar _id: Unique ID for the Community
    @type _id: C{String}
    @ivar _name: Name of the Community
    @type _name: C{String}
    @ivar _description: Community Description
    @type _description: C{String}
    @ivar _members: List of Members of this community (their ids)
    @type _members: C{List} of C{String}
    @ivar _authorities: List of Community Authorities for this TC (their ids)
    @type _authorities: C{List} of C{String}
    @ivar _sourceGateways: List of outgoing gateways
    @type _sourceGateways: C{List} of L{CommunityGateway}
    @ivar _destinationGateways: List of incoming gateways
    @type _destinationGateways: C{List} of L{CommunityGateway}
    @ivar _tcdl: Community Description in XML format
    @type _tcdl: C{String}
    @ivar _tcdlversion: Version of the current XML Community Description
    @type _tcdlversion: C{String}
    @ivar _tcdldate: Date of the current version of the XML Community Description
    @type _tcdldate: C{String}
    @ivar _protocols: List of protocols, this community supports
    @type _protocols: C{List} of C{String}
    @ivar _algorithms: List of algorithms, this community supports
    @type _algorithms: C{List} of C{String}
    """
    
    def __init__(self, id = None, name = None, description = None, tcdl = None, tcdlversion = None, tcdldate = None):
        """
        Initialises a Community instance
        
        Assigns the parameters to the instance variables. If no id is given (or is C{None}), one
        will be calculated.

        @param id: Unique ID for the Community
        @type id: C{String}
        @param name: Name of the Community
        @type name: C{String}
        @param description: Community Description
        @type description: C{String}
        @param tcdl: Community Description in XML format
        @type tcdl: C{String}
        @param tcdlversion: Version of the current XML Community Description
        @type tcdlversion: C{String}
        @param tcdldate: Date of the current version of the XML Community Description
        @type tcdldate: C{String}
        """
        self._id = id
        self._name = name
        self._description = description
        self._tcdl = tcdl
        self._tcdlversion = tcdlversion
        self._tcdldate = tcdldate
        
        self._members = []
        self._authorities = []
        
        self._sourceGateways = []
        self._destinationGateways = []
        
        self._protocols = []
        self._algorithms = []
        
        if self._id == None:
            self._id = tools.generateId(tools.TYPE_COMMUNITY)
        
    def __str__(self):
        """
        Some basic information about the object
        """
        return "Community (%s): %s. (%d members; %d A; %d SGW, %d DGW)" %(self._id, self._name, len(self._members), 
            len(self._authorities), len(self._sourceGateways), len(self._destinationGateways))
    
    def getId(self):
        """
        GETTER
        
        @return: The id as saved in the instance variable
        rtype: C{String}
        """
        return self._id
        
    def getName(self):
        """
        GETTER

        @return: The name as saved in the instance variable
        rtype: C{String}
        """
        return self._name
        
    def getDescription(self):
        """
        GETTER

        @return: The description (comment) as saved in the instance variable
        rtype: C{String}
        """
        return self._description
        
    def getTcdl(self):
        """
        GETTER

        @return: The XML community descriptoin as saved in the instance variable
        rtype: C{String}
        """
        return self._tcdl
        
    def getTcdlVersion(self):
        """
        GETTER

        @return: The version of the tcdl as saved in the instance variable
        rtype: C{String}
        """
        return self._tcdlversion
        
    def getTcdlDate(self):
        """
        GETTER

        @return: The date of the version of the TCDL as saved in the instance variable
        rtype: C{String}
        """
        return self._tcdldate
        
    def addMember(self, memberId, isAuthority = 0, registerInMember = 0, loading = 0):
        """
        Add a member to this community.
        
        This function invokes a function in the db backend process for updating the table for the relation 
        between members and communities.
        
        @note: If your system is db backend connected, you must first add community to the community manager
        and the member to the member manager! Then you may add relations between them.
        
        @param memberId: ID of the member to be added
        @type memberId: C{String}
        @param isAuthority: Indicates, whether the given member is Community Authority for this community
        @type isAuthority: C{Boolean}
        @param registerInMember: Indicates, whether the function L{Member.addCommunity()} shall be invoked.
        @type registerInMember: C{Boolean}
        @param loading: Indicates, whether this function is called during initialisation process. No changes must be written to the db then.
        @type loading: C{Boolean}
        """
        memberalready = 0
        for m in self._members:
            if m == memberId:
                    memberalready = 1
        if not memberalready:
            self._members.append(memberId)

            if not loading:
                global getCommunityManager
                getCommunityManager().registerCommunityMemberRelation(self.getId(), memberId)
        
        if registerInMember:
            member = getMemberManager().getMember(memberId)
            member.addCommunity(self._id, registerInCommunity = 0)

        if isAuthority:
            self.addAuthority(memberId, loading, registerInMember)
        
                
    def addAuthority(self, authority_memberId, loading = 0, registerInMember = 0):
        """
        Adds the authority role for the given member to this community.
        
        @param authority_memberId: Member id of the member which is a authority for this community
        @type authority_memberId: C{String}
        @param registerInMember: Indicates, whether the function L{Member.addCommunity()} shall be invoked.
        @type registerInMember: C{Boolean}
        @param loading: Indicates, whether this function is called during initialisation process. No changes must be written to the db then.
        @type loading: C{Boolean}        
        """
        memberalready = 0
        for m in self._authorities:
            if m == authority_memberId:
                memberalready = 1

        if not memberalready:
            self._authorities.append(authority_memberId)
            
            if not loading:
                global getCommunityManager
                getCommunityManager().registerCommunityAuthorityRelation(self.getId(), authority_memberId)
                
        if registerInMember:
            member = getMemberManager().getMember(authority_memberId)
            member.addAuthorityRole(self._id)
        
    
    def getMembers(self):
        """
        GETTER
        
        Provides the list of members of this community.
        
        @return: List of IDs for the members
        @rtype: C{List} of C{String}
        """
        return self._members
        
    def hasMember(self, memberid):
        """
        Checks, whether the community has a member with the given id subscribed to it.
        
        @param memberid: ID of the potential member of the community
        @type memberid: C{String}
        @return: Indicates, whether the member is member of the community
        @rtype: C{Boolean}
        """
        try:
            self._members.index(memberid)
            return 1
        except ValueError:
            pass
        return 0
        
    def getAuthorities(self):
        """
        GETTER
        
        Provides the list of community authorities for this community.
        
        @return: List of IDs for the members, which are authorities for this community
        @rtype: C{List} of C{String}
        """
        return self._authorities
        
    def addGateway(self, gateway):
        """
        Add a community gateway to this community.
        
        It will determine itself, whether it is the source or the destination for the
        gateway.
        
        @param gateway: Community gateway to be added
        @type gateway: L{CommunityGateway}
        """
        if gateway.getSourceCommunityId() == self._id:
            self._sourceGateways.append(gateway)
        if gateway.getDestinationCommunityId() == self._id:
            self._destinationGateways.append(gateway)
    
    def getSourceGateways(self):
        """
        GETTER
        
        Provides all the gateways, this community may send through.
        
        @return: References to the gateways instances.
        @rtype: L{CommunityGateway}
        """
        return self._sourceGateways

    def getDestinationGateways(self):
        """
        GETTER
        
        Provides all the gateways, this community may receive through.
        
        @return: References to the gateways instances.
        @rtype: L{CommunityGateway}
        """
        return self._destinationGateways

        
    def addProtocol(self, protocolid, loading = 0):
        """
        Adds a protocol to the community.
        
        @param protocolid: ID of the protocol to add to the community
        @type protocolid: C{String}
        @param loading: Indicates, whether this function is called during initialisation process. No changes must be written to the db then.
        @type loading: C{Boolean}        
        """
        memberalready = 0
        for p in self._protocols:
            if p == protocolid:
                memberalready = 1
        
        if not memberalready:
            self._protocols.append(protocolid)
            
            if not loading:
                global getCommunityManager
                getCommunityManager().registerCommunityProtocolRelation(self.getId(), protocolid)
                
    def getProtocols(self):
        """
        Returns the list of protocols for this community.
        
        @return: The list of IDs for the protocols
        @rtype: C{List} of C{String}
        """
        return self._protocols
        
    def addAlgorithm(self, algorithmid, loading = 0):
        """
        Adds a algorithm to the community.
        
        @param algorithmid: ID of the algorithm to add to the community
        @type algorithmid: C{String}
        @param loading: Indicates, whether this function is called during initialisation process. No changes must be written to the db then.
        @type loading: C{Boolean}        
        """
        memberalready = 0
        for a in self._algorithms:
            if a == algorithmid:
                memberalready = 1
        
        if not memberalready:
            self._algorithms.append(algorithmid)
            
            if not loading:
                global getCommunityManager
                getCommunityManager().registerCommunityAlgorithmRelation(self.getId(), algorithmid)
                
    def getAlgorithms(self):
        """
        Returns the list of algorithms for this community.
        
        @return: The list of IDs for the algorithms
        @rtype: C{List} of C{String}
        """
        return self._algorithms
        

class CommunityGateway:
    """
    Maintains information about a Trusting Commuity Gateway.
    
    Each instance maintains only one direction, hence if a node is responsible for
    passing traffic in both directions, two instances have to be created.
    
    @ivar _memberId: ID of the node implementing this role
    @type _memberId: C{String}
    @ivar _sourceCommunityId: Community FROM which the given member may pass messages
    @type _sourceCommunityId: C{String}
    @ivar _destinationCommunityId: Community TO which the given member may pass traffic
    @type _destinationCommunityId: C{String}
    """
    
    def __init__(self, memberId, sourceCommunityId, destinationCommunityId, 
            registerInCommunities = 0, registerInMember = 0, persistent = config.dbconnected):
        """
        Initalises a community gateway.
        
        Parameters are assigned to local variables.
        
        @todo: For each gateway, a database connection is initialised. Not "too" nice.
        
        @param memberId: ID of the node implementing this role
        @type memberId: C{String}
        @param sourceCommunityId: Community FROM which the given member may pass messages
        @type sourceCommunityId: C{String}
        @param destinationCommunityId: Community TO which the given member may pass traffic
        @type destinationCommunityId: C{String}
        """
        self._memberId = memberId
        self._sourceCommunityId = sourceCommunityId
        self._destinationCommunityId = destinationCommunityId
        
        if registerInCommunities:
            source = getCommunityManager().getCommunity(sourceCommunityId)
            dest = getCommunityManager().getCommunity(destinationCommunityId)
            source.addGateway(self)
            dest.addGateway(self)
        if registerInMember:
            member = getMemberManager().getMember(memberId)
            member.addGateway(self)
        
        if persistent:
            conn = communitymanager_db.CM_DB()
            conn.addGateway(memberId, sourceCommunityId, destinationCommunityId)
            conn.shutdown()
        
    def __str__(self):
        """
        Some basic information about the object
        """
        return "Gateway. MemberID: %s. SourceID: %s. DestID: %s." \
            %(self._memberId, self._sourceCommunityId, self._destinationCommunityId)
    
    def getMemberId(self):
        """
        GETTER
        
        @return: ID of the member responsible for this gateway
        @rtype: C{String}
        """
        return self._memberId
        
    def getSourceCommunityId(self):
        """
        GETTER
        
        @return: ID of the community this gateway passes messages from
        @rtype: C{String}
        """
        return self._sourceCommunityId

    def getDestinationCommunityId(self):
        """
        GETTER
        
        @return: ID of the community this gateway passes messages to
        @rtype: C{String}
        """
        return self._destinationCommunityId

        
class MemberManager:
    """
    Managing information about members of communities
    
    Connected to a database. All the data is loaded into the memory at startup time.
    Changes are written through directly.

    @ivar _members: Dictionary with all known members (key is the id, value a Member instance)
    @type _members: C{Dict} of C{String} | L{Member}
    @ivar _dbconnected: Indicates, whether the manager is connected to a database; hence whether the changes 
        shall be written through
    @type _dbconnected: C{Boolean}
    @ivar _cm_db: Community Manager Database Connector
    @type _cm_db: L{communitymanager_db.CM_DB}
    """
    
    def __init__(self, loadFromDatabase = 0):
        """
        Initialises the member manager.
        """
        self._members = {}
        self._dbconnected = loadFromDatabase
        if loadFromDatabase:
            self._cm_db = communitymanager_db.CM_DB()
            members = self._cm_db.getMembers()
            for member in members:
                self.addMember(member, persistent = 0)
                # also load the relations with the communities
                communityIds = self._cm_db.getCommunitiesForMember(member.getId())
                for communityId in communityIds:
                    member.addCommunity(communityId)

                authorityCommunityIds = self._cm_db.getAuthorisedCommunities(member.getId())
                for communityid in authorityCommunityIds:
                    member.addAuthorityRole(communityid)
                    
                # and the gateways
                gateways = self._cm_db.getGateways(memberid = member.getId())
                # gateways in the cm db are not registed with communities or members - so here we go
                for gateway in gateways:
                    member.addGateway(gateway)

                    
    def __str__(self):
        """
        Some basic information about the object
        """
        return "MemberManager: %d Members" %(len(self._members))
    
    def addMember(self, member, persistent = config.dbconnected, storeCommunityRelations = 0):
        """
        Adds a member instance to the dictionary.
        
        @param member: Member to be added
        @type member: L{Member}
        @param persistent: Indicates, whether the member shall be written through to the database
        @type persistent: C{Boolean}
        @param storeCommunityRelations: When persistent is true, shall the relations be saved in the db too?
        @type storeCommunityRelations: C{Boolean}
        """
        self._members[member.getId()] = member
        if persistent:
            self._cm_db.addMember(member, storeCommunityRelations)
        
    def getMember(self, memberId):
        """
        Get the member with the given ID from the repository.
        
        @param memberId: ID for the member to return
        @type memberId: C{String}
        @return: Member with the given ID
        @rtype: L{Member}
        """
        return self._members[memberId]
        
    def getLocalMember(self):
        """
        Returns the member instance for the local node.

        @return: Member with the ID as provided in the config file
        @rtype: L{Member}
        """
        from config import memberid
        return self.getMember(memberid)
        
    def getMemberIds(self):
        """
        Provides a list with IDs of all members stored in the repository.
        
        return: List of IDs of all known members.
        rtype: C{List} of C{String}
        """
        return self._members.keys()
        
    def updateMember(self, member, updateCommunityRelations):
        """
        Updates the member information for the object in the member manager with the same member id.
        
        If no member with the given id is in the manager, a new member will be created. All changes are
        written through to the database if connected.
        
        @param member: Reference to the new or updated member instance
        @type member: L{Member}
        @return: Reference to the member object stored in the manager
        @rtype: L{Member}
        """
        if self._members.has_key(member.getId()):
            del self._members[member.getId()]
            self._members[member.getId()] = member
            if self._dbconnected:
                self._cm_db.updateMember(member, updateCommunityRelations)
                
        else:
            self.addMember(member, storeCommunityRelations=updateCommunityRelations)
        return member
        
class Member:
    """
    Keeps data for one member.
    
    @ivar _id: Inique ID for the Member
    @type _id: C{String}
    @ivar _name: Name for the Member
    @type _name: C{String}
    @ivar _communities: IDs of all communities, this member is member of
    @type _communities: C{List} of C{String}
    @ivar _gateways: All the gateways this node is serving
    @type _gateways: C{List} of L{CommunityGateway}
    @ivar _authorizedComunities: All the communities this node is an authority of
    @type _authorizedComunities: C{List} of C{String}
    @ivar _mdl: Member description in XML 
    @type _mdl: C{String}
    @ivar _mdlversion: Version for the XML member description
    @type _mdlversion: C{String}
    @ivar _mdldate: Date for the version of the XML member description
    @type _mdldate: C{String}
    """
    
    def __init__(self, id = None, name = None, mdl = None, mdlversion = None, mdldate = None):
        """
        Initialises the member instance.
        
        Parameters are assigned to local variables. If no ID is provided (or None is given)
        one will ge generated.

        @param id: Inique ID for the Member
        @type id: C{String}
        @param name: Name for the Member
        @type name: C{String}
        @param mdl: Member description in XML 
        @type mdl: C{String}
        @param mdlversion: Version for the XML member description
        @type mdlversion: C{String}
        @param mdldate: Date for the version of the XML member description
        @type mdldate: C{String}
        """
        self._id = id
        self._name = name
        self._mdl = mdl
        self._mdlversion = mdlversion
        self._mdldate = mdldate
        
        self._communities = []
        self._gateways = []
        self._authorizedComunities = []
        
        if self._id == None:
            self._id = tools.generateId(tools.TYPE_MEMBER)
            
    def __str__(self):
        """
        Some basic information about the object
        """
        return "Member (%s): %s. (%d communities, %d AC, %d GW)" %(self._id, self._name, 
            len(self._communities), len(self._authorizedComunities), len(self._gateways))
        
    def getId(self):
        """
        GETTER
        
        @return: Value of the instance variable
        @rtype: C{String}
        """
        return self._id
        
    def getName(self):
        """
        GETTER
        
        @return: Value of the instance variable
        @rtype: C{String}
        """
        return self._name
        
    def getMdl(self):
        """
        GETTER
        
        @return: Value of the instance variable
        @rtype: C{String}
        """
        return self._mdl
        
    def getMdlVersion(self):
        """
        GETTER
        
        @return: Value of the instance variable
        @rtype: C{String}
        """
        return self._mdlversion
        
    def getMdlDate(self):
        """
        GETTER
        
        @return: Value of the instance variable
        @rtype: C{String}
        """
        return self._mdldate
        
    def addCommunity(self, communityid, registerInCommunity = 0):
        """
        Make this node member of the given community.
        
        @note: You have to add this member also to the community. Since this relation is a n:m relation, it may
        only be set on one side (either in member.addCommunity or in community.addMember). The community
        side was chosen; this way member.addCommunity does not effect the database.
        
        @param communityid: ID of the community to join
        @type communityid: C{String}
        """
        memberalready = 0
        for c in self._communities:
            if c == communityid:
                memberalready = 1
        if not memberalready:
            self._communities.append(communityid)

        if registerInCommunity:
            community = getCommunityManager().getCommunity(communityId)
            community.addMember(self._id, registerInMember = 0)
    
    def addAuthorityRole(self, communityid):
        """
        Adds the role of an authority to the given community.
        
        @note: You have to register this node as well as an authority in the community. Only this will create
        the relation in the database.
        
        @param communityid: ID of the community this node shall be an authority for
        @type communityid: C{String}
        """
        memberalready = 0
        for c in self._authorizedComunities:
            if c == communityid:
                memberalready = 1
        if not memberalready:
            self._authorizedComunities.append(communityid)
    
    def getCommunityIds(self):
        """
        GETTER
        
        @return: List of IDs, this node is a member of
        @rtype: C{List} of C{String}
        """
        return self._communities

    def addGateway(self, gateway):
        """
        Register the gateway with this member.
        
        @param gateway: Reference to gateway instance, this node is taking care of.
        @type gateway: L{CommunityGateway}
        """
        self._gateways.append(gateway)

    def getGateways(self):
        """
        GETTER
        
        @return: List of all gateways this node is taking care of
        @rtype: C{List} of L{CommunityGateway}
        """
        return self._gateways
