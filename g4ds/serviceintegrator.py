"""
Connection to services.

Grid for Digital Security (G4DS)

Handles all issues directly related to connectivity to services. A calss ServiceIntegrator with its function
L{ServiceIntegrator.dispatch} is provided for dispatching incoming service messages to the 
appropriate service.

@author: Michael Pilgermann
@contact: mailto:mpilgerm@glam.ac.uk
@license: GPL (General Public License)
"""

# "singleton"
_serviceIntegrator = None
def getServiceIntegrator():
    global _serviceIntegrator
    if not _serviceIntegrator:
        _serviceIntegrator = ServiceIntegrator()
    return _serviceIntegrator
    
class ServiceIntegrator:
    """
    All issues for communication to connected services.
    """
    
    def __init__(self):
        """
        Create the dictionary for connected clients.
        """
        self._clients = {}
        
    def dispatch(self, serviceid, servicename, data, messageid):   
        """
        Passing the incoming message to the appropriate service.
        """
        from messagehandler import getMessageContextController
        from authorisationcontroller import getAuthorisationController

        from g4dslogging import getDefaultLogger, COMMUNICATION_INCOMING_MSG_DETAILS
        getDefaultLogger().newMessage(COMMUNICATION_INCOMING_MSG_DETAILS, '-- Service Msg - Service %s (%s)' %(servicename, serviceid))
        
        # the action string for service is: g4ds.service.$ACTION_ID - let's check whether to pass
        actionString = "g4ds.service." + serviceid
        if not getAuthorisationController().validate(getMessageContextController().getValue(messageid, 'senderid'), serviceid, actionString):
            return
        
        if self._clients.has_key(serviceid):
            self._clients[serviceid](data, getMessageContextController().getValue(messageid, 'senderid'), serviceid, getMessageContextController().getValue(messageid, 'communityid'), messageid)      # this invokes the provided callback function of the connected client
            getDefaultLogger().newMessage(COMMUNICATION_INCOMING_MSG_DETAILS, '-- Service Msg - passed message to connected client.')
        else:
            getDefaultLogger().newMessage(COMMUNICATION_INCOMING_MSG_DETAILS, '-- Service Msg - no client connected for this service.')

    def sendMessage(self, dest_memberid, serviceid, servicename, message, communityid = None, messagereference = None):
        """
        Any service message should be sent using this function to connect to the outside world.
        
        The appropriate functions inside the global message controller are invoked.
        
        For destination (L{dest_memberid}) several place holders are allowed in order to allow some kind of broadcasting messages.
        This way, you may either provide a single member id for it (one destination), a single community id (all members of this
        community) or a service id (all members of the service).
        """
        from g4dslogging import getDefaultLogger, COMMUNICATION_OUTGOING_MSG_SERVICE_DETAILS, COMMUNICATION_OUTGOING_ERROR_SERVICE
        
        destinations = []
        # ok - here we do the magic resolving of the destination 
        if dest_memberid[0] == 'S':
            # this message is sent to all members of the given service
            from servicerepository import getServiceManager
            try:
                service = getServiceManager().getService(dest_memberid)
                for memberid in service.getMembers():
                    destinations.append(memberid)
            except KeyError, msg:
                getDefaultLogger().newMessage(COMMUNICATION_OUTGOING_ERROR_SERVICE, 'Outgoing service message - destination (service) unknown here: %s' %(dest_memberid))
        elif dest_memberid[0] == 'C':
            # this message is sent to all members of the given community
            from communitymanager import getCommunityManager
            try:
                community = getCommunityManager().getCommunity(dest_memberid)
                for memberid in community.getMembers():
                    destinations.append(memberid)
            except KeyError, msg:
                getDefaultLogger().newMessage(COMMUNICATION_OUTGOING_ERROR_SERVICE, 'Outgoing service message - destination (community) unknown here: %s' %(dest_memberid))
        elif dest_memberid[0] == 'M':
            # this is for a single member
            destinations.append(dest_memberid)
        else:
            # that should not happen
            getDefaultLogger().newMessage(COMMUNICATION_OUTGOING_ERROR_SERVICE, 'Outgoing service message - unkown destination string for service %s: %s' %(serviceid, dest_memberid))
        getDefaultLogger().newMessage(COMMUNICATION_OUTGOING_MSG_SERVICE_DETAILS, 'Outgoing service message - resolved destination string (%s): %s' %(dest_memberid, destinations))
            
        from routingcontroller import getRoutingController
        for dest_memberid in destinations:
            endpoint = getRoutingController().findBestEndpointForMember(dest_memberid, communityid)
            endpointid = endpoint.getId()
            from messagehandler import getGlobalOutgoingMessageHandler
            getGlobalOutgoingMessageHandler().sendServiceMessage(endpointid, serviceid, servicename, message, messagereference)
    
    
    def registerClient(self, serviceid, callback):
        """
        Puts the client into the dictionary of clients.
        """
        from g4dslogging import getDefaultLogger, SERVICES_CLIENT_CONNECT, SERVICES_CLIENT_DISCONNECT
        
        if self._clients.has_key(serviceid):
            from errorhandling import G4dsDependencyException
            raise G4dsDependencyException('There is another client connected to service %s already.' %(serviceid))
            
        self._clients[serviceid] = callback
        getDefaultLogger().newMessage(SERVICES_CLIENT_CONNECT, 'Client connected for service %s.' %(serviceid))
        
    def unregisterClient(self, serviceid):
        """
        Disconnect the client from the given service id.
        """
        from g4dslogging import getDefaultLogger, SERVICES_CLIENT_CONNECT, SERVICES_CLIENT_DISCONNECT
        
        if not self._clients.has_key(serviceid):
            from errorhandling import G4dsDependencyException
            raise G4dsDependencyException('Client is not registered with service %s.' %(serviceid))
            
        del self._clients[serviceid]
        getDefaultLogger().newMessage(SERVICES_CLIENT_DISCONNECT, 'Client disconnected for service %s.' %(serviceid))
        
