"""
Management of knowledge services

Grid for Digital Security (G4DS)


@author: Michael Pilgermann
@contact: mailto:mpilgerm@glam.ac.uk
@license: GPL (General Public License)

@var _serviceManager: Singleton - the only instance ever of the ServiceManager class
@type _serviceManager: L{ServiceManager}
"""

import config
import tools
import servicerepository_db

# ##########################################
# ##########################################
# "Singleton" stuff
_serviceManager = None

def getServiceManager():
    """
    Singleton - returns the instance to the service manager
    
    If the instance has not yet been initialised, this will be done. Finally, the
    instance is returned.
    
    @return: The only instance to a Service Manager
    @rtype: L{ServiceManager}
    """
    global _serviceManager
    if _serviceManager == None:
        _serviceManager = ServiceManager(config.dbconnected)
    return _serviceManager
    
# ##########################################
# ##########################################

class ServiceManager:
    """
    Responsible for maintaining information about Services and relations with them
    
    Connected to a database. All the data is loaded into the memory at startup time.
    Changes are written through directly.
    
    @ivar _services: Dictionary with all services (key is the id, value a Service instance)
    @type _services: C{Dict} of C{String} | L{Service}
    @ivar _dbconnected: Indicates, whether the manager is connected to a database; hence whether the changes 
        shall be written through
    @type _dbconnected: C{Boolean}
    @ivar _sr_db: Service Repository Database Connector
    @type _sr_db: L{servicerepository_db.ServDB}
    """
    
    def __init__(self, loadFromDatabase = 0):
        """
        Initialises the Service Manager
        
        Instanstiates local variables. Loads all the stuff from the database.
        
        @param loadFromDatabase: Indicates, whether the manager shall be initialised from the database backend
        @type loadFromDatabase: C{Boolean}
        """
        self._services = {}
        self._dbconnected = loadFromDatabase
        if loadFromDatabase:
            self._sr_db = servicerepository_db.ServDB()
            services = self._sr_db.getServices()
            for service in services:
                self.addService(service, persistent = 0)
                
                # also regsiter the relations for each service
                communityids = self._sr_db.getCommunitiesForService(service.getId())
                for communityid in communityids:
                    service.addCommunity(communityid, 1)
                
                memberids = self._sr_db.getMembersForService(service.getId())
                for memberid in memberids:
                    service.addMember(memberid, 1)
                    
                authorityids = self._sr_db.getAuthoritiesForService(service.getId())
                for authorityid in authorityids:
                    service.addAuthority(authorityid, 1)

    def __str__(self):
        """
        Some basic information about the object
        """
        return "ServiceManager: %d Services." %(len(self._services))
    
    def addService(self, service, persistent = config.dbconnected):
        """
        Adds a community instance to the repository
        
        @param service: Service to be inserted
        @type service: L{Service}
        @param persistent: Indicates, whether the service shall be written through to the database
        @type persistent: C{Boolean}
        """
        self._services[service.getId()] = service
        if persistent:
            self._sr_db.addService(service)
    
    def updateService(self, service, dropAuthorityRelations = 1, dropMemberRelations = 0, dropCommunityRelations = 0):
        """
        Updates the manager with the given service information.
        
        Writes information through to the database if connected.
        """
        if self._services.has_key(service.getId()):
            del self._services[service.getId()]
            self._services[service.getId()] = service
            if self._dbconnected:
                self._sr_db.updateService(service, dropAuthorityRelations, dropMemberRelations, dropCommunityRelations)     
        
            # also set the relations
            if not dropMemberRelations:
                memberids = self._sr_db.getMembersForService(service.getId())
                for memberid in memberids:
                    service.addMember(memberid, init = 1)
            
            # for the authorities
            if not dropAuthorityRelations:
                authorityids = self._sr_db.getAuthoritiesForService(service.getId())
                for authorityid in authorityids:
                    service.addAuthority(authorityid, init = 1)
        
            # for the communities
            if not dropCommunityRelations:
                communityids = self._sr_db.getCommunitiesForService(service.getId())
                for communityid in communityids:
                    service.addCommunity(communityid, init = 1)
        else:
            self.addService(service)
                
        return service
    
    def getService(self, serviceId):
        """
        Getter
        
        @param serviceId: ID of the service to return
        @type serviceId: C{String}
        @return: The service with the given id from the service repository.
        @rtype: L{Service}
        """
        return self._services[serviceId]
        
    def getServiceIds(self):
        """
        GETTER
        
        @return: The list of ids off all services
        @rtype: C{List} of C{String}
        """
        return self._services.keys()

    def registerCommunitySubscription(self, serviceid, communityid):
        """
        Passes the request to the database backend.
        """
        if self._dbconnected:
            self._sr_db.addServiceCommunity(serviceid, communityid)

    def registerMemberSubscription(self, serviceid, memberid):
        """
        Passes the request to the database backend.
        """
        if self._dbconnected:
            self._sr_db.addServiceMember(serviceid, memberid)

    def registerAuthority(self, serviceid, memberid):
        """
        Passes the request to the database backend.
        """
        if self._dbconnected:
            self._sr_db.addServiceAuthority(serviceid, memberid)

        
class Service:
    """
    Keeps data for one service.
    
    @ivar _id: Inique ID for the Service
    @type _id: C{String}
    @ivar _name: Name for the Service
    @type _name: C{String}
    @ivar _ksdl: knowledge service description in XML 
    @type _ksdl: C{String}
    @ivar _ksdlversion: Version for the XML knowledge service description
    @type _ksdlversion: C{String}
    @ivar _ksdldate: Date for the version of the XML knowledge service description
    @type _ksdldate: C{String}
    @ivar _communities: List of ids of subscribed communities
    @type _communities: C{List} of C{String}
    @ivar _members: List of ids of subscribed members
    @type _members: C{List} of C{String}
    @ivar _authorities: List of ids of members which are authorities to this service
    @type _authorities: C{List} of C{String}
    """
    
    def __init__(self, id = None, name = '', ksdl = '', ksdlversion = '', ksdldate = None):
        """
        Initialises the member instance.
        
        Parameters are assigned to local variables. If no ID is provided (or None is given)
        one will ge generated.

        @param id: Inique ID for the Member
        @type id: C{String}
        @param name: Name for the Member
        @type name: C{String}
        @param ksdl: knowledge service description in XML 
        @type ksdl: C{String}
        @param ksdlversion: Version for the XML knowledge service description
        @type ksdlversion: C{String}
        @param ksdldate: Date for the version of the XML knowledge service description
        @type ksdldate: C{String}
        """
        self._id = id
        self._name = name
        self._ksdl = ksdl
        self._ksdlversion = ksdlversion
        self._ksdldate = ksdldate
        
        self._communities = []
        self._members = []
        self._authorities = []
        
        if self._id == None:
            self._id = tools.generateId(tools.TYPE_SERVICE)
            
    def __str__(self):
        """
        Some basic information about the object
        """
        return "Service (%s): %s (%d C | %d M | %d A)." %(self._id, self._name,
            len(self._communities), len(self._members), len(self._authorities))

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
        
    def getKsdl(self):
        """
        GETTER
        
        @return: Value of the instance variable
        @rtype: C{String}
        """
        return self._ksdl
        
    def getKsdlVersion(self):
        """
        GETTER
        
        @return: Value of the instance variable
        @rtype: C{String}
        """
        return self._ksdlversion
        
    def getKsdlDate(self):
        """
        GETTER
        
        @return: Value of the instance variable
        @rtype: C{String}
        """
        return self._ksdldate

    def getMembers(self):
        """
        GETTER
        """
        return self._members

    def getCommunities(self):
        """
        GETTER
        """
        return self._communities
        
    def getAuthorities(self):
        """
        GETTER
        """
        return self._authorities
    
    def addCommunity(self, communityid, init = 0):
        """
        Mirrors the subscription of a communtiy to a service
        """
        memberalready = 0
        for c in self._communities:
            if c == communityid:
                memberalready = 1
                
        if not memberalready:
            self._communities.append(communityid)
            
            if not init:
                global getServiceManager
                getServiceManager().registerCommunitySubscription(self.getId(), communityid)
        
    def addMember(self, memberid, init = 0):
        """
        Mirrors the subscription of a member to a service
        """
        memberalready = 0
        for m in self._members:
            if m == memberid:
                memberalready = 1
                
        if not memberalready:
            self._members.append(memberid)
            
            if not init:
                global getServiceManager
                getServiceManager().registerMemberSubscription(self.getId(), memberid)
            
    def addAuthority(self, memberid, init = 0):
        """
        Mirrors the subscription of a communtiy to a service
        """
        memberalready = 0
        for m in self._authorities:
            if m == memberid:
                memberalready = 1
                
        if not memberalready:
            self._authorities.append(memberid)
            
            if not init:
                global getServiceManager
                getServiceManager().registerAuthority(self.getId(), memberid)
            
    def hasMember(self, memberid):
        """
        Checks, whether the service has a member with the given id subscribed to it.
        
        @param memberid: ID of the potential member of the service
        @type memberid: C{String}
        @return: Indicates, whether the member is member of the service
        @rtype: C{Boolean}
        """
        try:
            self._members.index(memberid)
            return 1
        except ValueError:
            pass
        return 0

    def hasAuthority(self, memberid):
        """
        Checks, whether the service has a authority with the given member id.
        
        @param memberid: member ID of the potential authority of the service
        @type memberid: C{String}
        @return: Indicates, whether the member is authority of the service
        @rtype: C{Boolean}
        """
        try:
            self._authorities.index(memberid)
            return 1
        except ValueError:
            pass
        return 0

    def hasCommunity(self, communityid):
        """
        Checks, whether the service has a community with the given id subscribed to it.
        
        @param communityid: ID of the potential community of the service
        @type communityid: C{String}
        @return: Indicates, whether the community is allowed for the service
        @rtype: C{Boolean}
        """
        try:
            self._communities.index(communityid)
            return 1
        except ValueError:
            pass
        return 0

        
