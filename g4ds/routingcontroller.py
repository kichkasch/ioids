"""
All issues concerning routing are implemented in here.

Grid for Digital Security (G4DS)


@author: Michael Pilgermann
@contact: mailto:mpilgerm@glam.ac.uk
@license: GPL (General Public License)

"""

from routingtablemanager import getRoutingTableManager

# "singleton"
_routingController = None
def getRoutingController():
    """
    Singleton
    """
    global _routingController
    if not _routingController:
        _routingController = RoutingController()
    return _routingController

class RoutingController:
    """
    The decisioin maker for routing.
    """
    
    def __init__(self):
        """
        Yet empty constructor.
        """
        pass
        

    def findBestEndpointForMember(self, memberid, communityid = None, allowDefaultCommunity = 0, allowRouting =1):
        """
        Picks the most approriate endpoint for the given member.
        
        Per default, the default community is disabled here. 
        
        Currently, simply the first one is taken.
        """
        from config import default_tc_id
        from communicationmanager import getEndpointManager
        from communitymanager import getMemberManager
        
        negCommunityList = []
        if not allowDefaultCommunity:
            negCommunityList.append(default_tc_id)
            
        endpoints = getEndpointManager().getEndpointsForMember(memberid, communityid, negCommunityList)
        
        # if no routing allowed, remove the entries where the TC is not one, we are subscribed to
        routingless_endpoints = []
        local = getMemberManager().getLocalMember()
        for e in endpoints:
            try:
                local.getCommunityIds().index(e.getCommunityId())
                routingless_endpoints.append(e)
            except ValueError, msg:
                pass
        if not allowRouting:
            endpoints = routingless_endpoints
        
        if not allowDefaultCommunity:
            new_endpoints = []
            from config import default_tc_id 
            for e in endpoints:
                if e.getCommunityId() != default_tc_id:
                    new_endpoints.append(e)
            endpoints = new_endpoints

            new_routingless_endpoints = []
            for e in routingless_endpoints:
                if e.getCommunityId() != default_tc_id:
                    new_routingless_endpoints.append(e)
            routingless_endpoints = new_routingless_endpoints
        
        # well, if we can deliver directly, let's do it
        if len(routingless_endpoints):
            endpoints = routingless_endpoints
        
        if not len(endpoints):
            from errorhandling import G4dsCommunicationException
            raise G4dsCommunicationException('No Endpoint found for Member with id ' + memberid + '.')
        return endpoints[0]
        
# "singleton"
_routingEngine = None
def getRoutingEngine():
    """
    Singleton
    """
    global _routingEngine
    if not _routingEngine:
        _routingEngine = RoutingEngine()
    return _routingEngine

class RoutingEngine:
    """
    Handles all outgoing messages.
    """
    
    def __init__(self):
        """
        Yet empty constructor.
        """
        pass
    
    def sendMessage(self, message, endpoint):
        """
        Tries to deliver a message directly, if impossible via wrapping into routing message.
        
        All messages should be passed here and not be sent from anywhere else. The routing engine 
        looks, whether the given endpoint may be reached directly from the local node. If this
        is possible, the message is sent off directly. If, however, this is not possible, the 
        message is wrapped into a routing message and gateways are tried to identify for passing
        the message through the topology.
        """
        
        # check, whether I am in the community of the given endpoint, if not - we need to attempt to route this message
        tc = endpoint.getCommunityId()
        from communitymanager import getMemberManager
        local = getMemberManager().getLocalMember()
##        try:
##            local.getCommunityIds().index(tc)
        from communicationmanager import getProtocolManager, getEndpointManager

        if len(getEndpointManager().getEndpointsForMember(local.getId(), tc)):

            from g4dslogging import getDefaultLogger, COMMUNICATION_OUTGOING_MSG, COMMUNICATION_OUTGOING_MSG_DETAILS
            getDefaultLogger().newMessage(COMMUNICATION_OUTGOING_MSG, 'New outgoing message - direct delivery (%s | %s)' %(endpoint.getMemberId(), tc))
            getDefaultLogger().newMessage(COMMUNICATION_OUTGOING_MSG_DETAILS, '-- Endpoint %s' %(str(endpoint)))
            getDefaultLogger().newMessage(COMMUNICATION_OUTGOING_MSG_DETAILS, '-- Size of Data %d chars' %(len(message)))

            protocol = getProtocolManager().getProtocol(endpoint.getProtocolId())
            
            from protocolcontroller import getProtocolController
            protocol = getProtocolController().getOpenProtocol(protocol.getName())
    
            from socket import error
            from errorhandling import G4dsCommunicationException
            try:
                protocol.sendMessage(endpoint.getAddress(), message)
            except error, msg:
                raise G4dsCommunicationException('Sending Message: %s' %(msg))
##        except ValueError, msg:
        else:
            # ok, not in there - let's route then
            from g4dslogging import getDefaultLogger, COMMUNICATION_OUTGOING_MSG_ROUTED
            getDefaultLogger().newMessage(COMMUNICATION_OUTGOING_MSG_ROUTED, 'New outgoing message - routed (%s | %s)' %(endpoint.getMemberId(), tc))

            self._assembleRoutingMessage(message, endpoint)
        
    def _assembleRoutingMessage(self, message, endpoint):
        
        final_destination = endpoint.getMemberId()
        community = endpoint.getCommunityId()
        from communicationmanager import getProtocolManager
        protocolname = getProtocolManager().getProtocol(endpoint.getProtocolId()).getName()
        gateway_member_id, peercommunity, hops = getRoutingTableManager().getNexthopForCommunity(endpoint.getCommunityId())
        args = {}
        args['destination'] = final_destination
        args['protocol'] = protocolname
        args['community'] = community
        from messagewrapper import getControlMessageWrapper
        wrapped, tmp, tmp1 = getControlMessageWrapper().wrapSSRoutingMessage('1', args = args, data = message)

        from g4dslogging import getDefaultLogger, COMMUNICATION_OUTGOING_MSG_DETAILS
        getDefaultLogger().newMessage(COMMUNICATION_OUTGOING_MSG_DETAILS, '-- Routing details: Gateway (%s | %s)' %(gateway_member_id, peercommunity))
        getDefaultLogger().newMessage(COMMUNICATION_OUTGOING_MSG_DETAILS, '-- Size of Data %d chars' %(len(message)))

        from g4dsconfigurationcontroller import getOutgoingControlMessagesHandler, CONTROL_ROUTER
        getOutgoingControlMessagesHandler().sendMessage(gateway_member_id, CONTROL_ROUTER, "Routing message", wrapped, communityid = peercommunity)
        
        
        
# "singleton"
_routingMessageDispatcher = None
def getRoutingMessageDispatcher():
    """
    Singleton
    """
    global _routingMessageDispatcher
    if not _routingMessageDispatcher:
        _routingMessageDispatcher = RoutingMessageDispatcher()
    return _routingMessageDispatcher

class RoutingMessageDispatcher:
    """
    Dispatcher for incoming Routing messages (special kind of control messages).
    
    Routing messages are one kind of control messages. They encapsulate the data inside them.
    Whenever the dispatcher for control messages recognises a routing message, it should be passed
    to this class for further processing.
    """
    
    def __init__(self):
        """
        Yet empty constructor.
        """
        pass

    def dispatch(self, message, incomingmessageid):
        """
        Unwrappes the message and tries to deliver directly, or if not possible through another routing hop.
        """
##        print "\tRouting Dispatcher: Received something to pass on."
        from g4dslogging import getDefaultLogger, COMMUNICATION_INCOMING_MSG_DETAILS
        getDefaultLogger().newMessage(COMMUNICATION_INCOMING_MSG_DETAILS, '-- Control Msg - SS: Routing Engine')

        from messagewrapper import getControlMessageWrapper
        action, sucess, args, unwrapped = getControlMessageWrapper().unwrapSSRoutingMessage(message)
        destination = args['destination']
        protocol = args['protocol']
        community = args['community']

        from authorisationcontroller import getAuthorisationController
        from messagehandler import getMessageContextController
        sourceCommunity = getMessageContextController().getValue(incomingmessageid, 'communityid')
##        # let's check, whether the sender of this message is allowed to route into the community
##        if not getAuthorisationController().validate(getMessageContextController().getValue(incomingmessageid, 'senderid'), 
##            sourceCommunity, 'g4ds.routing.route'):
##            return
        
        from communitymanager import getMemberManager
        # check first, whether we are the final receipient
        if getMemberManager().getLocalMember().getId() == destination:
            # great stuff - pass it to the global dispatcher
            from messagehandler import getGlobalDispatcher
            getGlobalDispatcher().dispatch(protocol, unwrapped)
        else:
            args = {}
            args['destination'] = destination
            args['protocol'] = protocol
            args['community'] = community
            from messagewrapper import getControlMessageWrapper
            wrapped, doc, element = getControlMessageWrapper().wrapSSRoutingMessage('1', args = args, data = unwrapped)
            from g4dsconfigurationcontroller import getOutgoingControlMessagesHandler, CONTROL_ROUTER
            # check, whether we can reach the dest community directly
            try:
                getMemberManager().getLocalMember().getCommunityIds().index(community)
                # great to know; but are we allowed this action?
                if not getAuthorisationController().validate(getMemberManager().getLocalMember().getId(), community, 'g4ds.routing.route'):
                    raise ValueError('I am in the dest community; but I am not allowed to route into it. Let us try to find somebody else.')
                # unfortunately, we can only check the dest tc with the access control - let's check for scr / dest combination additionally
                for gw in getMemberManager().getLocalMember().getGateways():
                    if gw.getSourceCommunityId() == sourceCommunity and gw.getDestinationCommunityId() == community:
                        getOutgoingControlMessagesHandler().sendMessage(destination, CONTROL_ROUTER, "Routing message", wrapped, communityid = community)
                raise ValueError('I am in the dest community; but I am not allowed to route into it. Let us try to find somebody else.')
            except ValueError, msg:
                # ok - looks like we can only pass it on to the next hop
                gateway_member_id, peercommunity, hops = getRoutingTableManager().getNexthopForCommunity(community)
                # are we allowed this action then?
                if not getAuthorisationController().validate(getMemberManager().getLocalMember().getId(), peercommunity, 'g4ds.routing.route'):
                    return
                # ah, fair enough - is it also allowed for the combination src TC / dst TC?
                for gw in getMemberManager().getLocalMember().getGateways():
                    if gw.getSourceCommunityId() == sourceCommunity and gw.getDestinationCommunityId() == peercommunity:
                        getOutgoingControlMessagesHandler().sendMessage(gateway_member_id, CONTROL_ROUTER, "Routing message", wrapped, communityid = peercommunity)
                
            
            
