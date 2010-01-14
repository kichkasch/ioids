"""
All configurations are applied in here.

Grid for Digital Security (G4DS)

There are 3 controller subsystems:
    - Member controller subsystem
    - Community controller subsystem
    - Routing controller subsystem
    
Additionally, we have the routing messages as well, which are also encapsulated in G4DS control messages.

This way, messages with ID L{CONTROL_ROUTER} are encapsulated routing messages; messages with ID
L{CONTROL_SUBSYSTEM_ROUTING} in contrast are control messages for the routing control sub system; hence,
for controlling the routing.

@author: Michael Pilgermann
@contact: mailto:mpilgerm@glam.ac.uk
@license: GPL (General Public License)

@var _controlMessageDispatcher: Singleton - the only instance ever of the ControlMessageDispatcher class
@type _controlMessageDispatcher: L{ControlMessageDispatcher}
"""

CONTROL_ROUTER = 'ROUTING-MESSAGE'
CONTROL_SUBSYSTEM_MEMBERS   = 'SS-MEMBER'
CONTROL_SUBSYSTEM_COMMUNITIES = 'SS-COMMUNITY'    
CONTROL_SUBSYSTEM_SERVICES = 'SS-SERVICE'
CONTROL_SUBSYSTEM_ROUTING = 'SS-ROUTING'


# "singleton"
_controlMessageDispatcher = None
def getControlMessageDispatcher():
    global _controlMessageDispatcher
    if not _controlMessageDispatcher:
        _controlMessageDispatcher = ControlMessageDispatcher()
    return _controlMessageDispatcher

class ControlMessageDispatcher:
    """
    Handles incoming G4DS control messages.
    """
    
    def __init__(self):
        """
        Yet empty Constructor.
        """
        pass
        
    def dispatch(self, node, subsystemid, subsystemname, message, incomingmessageid):
        """
        Checks for the type within the control message and passes on to the appropriate function
        within this class.
        
        @param node: Data of the message as DOM tree
        @type node: L{xml.dom.Node}
        @param subsystemid: ID of the g4ds control subsystem
        @type subsystemid: C{String}
        @param subsystemname: Name of the g4ds control subsystem
        @type subsystemname: C{String}
        @param message: XML Message in String representation
        @type message: C{String}
        """
        ##print "ControlMessageDispatcher: Received a message - subsystem (%s): %s" %(subsystemid, subsystemname)
        if subsystemid == CONTROL_SUBSYSTEM_MEMBERS:
            getMemberController().dispatch(node, message, incomingmessageid)
        elif subsystemid == CONTROL_SUBSYSTEM_COMMUNITIES:
            getCommunityController().dispatch(node, message, incomingmessageid)
        elif subsystemid == CONTROL_SUBSYSTEM_ROUTING:
            getRoutingController().dispatch(node, message, incomingmessageid)
        elif subsystemid == CONTROL_SUBSYSTEM_SERVICES:
            getServiceController().dispatch(node, message, incomingmessageid)
        elif subsystemid == CONTROL_ROUTER:
            from routingcontroller import getRoutingMessageDispatcher
            getRoutingMessageDispatcher().dispatch(message, incomingmessageid)
        else:
            from g4dslogging import getDefaultLogger, COMMUNICATION_INCOMING_ERROR
            getDefaultLogger().newMessage(COMMUNICATION_INCOMING_ERROR, 'Unknown subsystem for G4DS Configuration Controller: %s' %(subsystemid))

# "singleton"
_outgoingControlMessagesHandler = None
def getOutgoingControlMessagesHandler():
    global _outgoingControlMessagesHandler
    if not _outgoingControlMessagesHandler:
        _outgoingControlMessagesHandler = OutgoingControlMessagesHandler()
    return _outgoingControlMessagesHandler

class OutgoingControlMessagesHandler:
    """
    Handles outgoing G4DS control messages.
    """
    def __init__(self):
        """
        Yet empty Constructor.
        """
        pass
        
    def sendMessage(self, dest_memberid, subsystemid, subsystemname, message, messagereference = None, communityid = None):
        """
        Any subsystem controller should use this function to connect to the outside world.
        
        The appropriate functions inside the global message controller are invoked.
        
        @param communityid: Which community to use for sending this message, give None and the most appropriate will be applied
        @type communityid: C{String}
        """
        from g4dslogging import getDefaultLogger, COMMUNICATION_OUTGOING_ERROR, COMMUNICATION_OUTGOING_MSG_CTRL
        getDefaultLogger().newMessage(COMMUNICATION_OUTGOING_MSG_CTRL, 'Sending control message')
        from errorhandling import G4dsCommunicationException

        from routingcontroller import getRoutingController
##        try:
##            # try first without default community
##            endpoint = getRoutingController().findBestEndpointForMember(dest_memberid, communityid, 0, 1)
##        except G4dsCommunicationException, msg:
            # if this is not working - OK; let's go
        endpoint = getRoutingController().findBestEndpointForMember(dest_memberid, communityid, 1, 1)
        endpointid = endpoint.getId()
        from messagehandler import getGlobalOutgoingMessageHandler
        return getGlobalOutgoingMessageHandler().sendControlMessage(endpointid, subsystemid, subsystemname, message, messagereference)

        
COMMUNITY_ACTION_REQUEST_TCDL = '0'
COMMUNITY_ACTION_UPDATE_TCDL = '1'
COMMUNITY_ACTION_GET_MEMBERS = '2'
COMMUNITY_ACTION_UPDATE_MEMBERS = '3'
COMMUNITY_ACTION_GENERIC_REPLY = '4'
COMMUNITY_ADMIN_SUBSCRIBE = '5'

COMMUNITY_SUCESS_NO_ERROR = '0'
COMMUNITY_SUCESS_TCDL_NOT_FOUND = '1'
COMMUNITY_SUCESS_COMMUNITY_NOT_FOUND = '2'
COMMUNITY_SUCESS_MEMBER_ALREADY = '3'
COMMUNITY_SUCESS_MEMBER_UNKNOWN = '4'
        
# "singleton"
_communityController = None
def getCommunityController():
    global _communityController
    if not _communityController:
        _communityController = CommunityController()
    return _communityController
        
class CommunityController:        
    """
    Handles controlling of communities.
    """
    def __init__(self):
        """
        Yet empty Constructor.
        """
        pass
        
    def dispatch(self, node, message, incomingmessageid):
        """
        Handles incoming messages.

        @param node: Data of the message as DOM tree
        @type node: L{xml.dom.Node}
        @param message: XML Message in String representation
        @type message: C{String}
        """
        from g4dslogging import getDefaultLogger, COMMUNICATION_INCOMING_MSG_DETAILS
        getDefaultLogger().newMessage(COMMUNICATION_INCOMING_MSG_DETAILS, '-- Control Msg - SS: Community Controller')

        from messagewrapper import getControlMessageWrapper
        action, sucess, args, data = getControlMessageWrapper().unwrapSSCommunityMessage(message)
        ##print "\tRequesed action: %s" %(action)
        from messagehandler import getMessageContextController
        messagereference = getMessageContextController().getValue(incomingmessageid, 'refid')
        from authorisationcontroller import getAuthorisationController
        if messagereference:
            ##print "\n\tAttempt to resume Job %s" %(messagereference)
            from runtimecontroller import getJobDispatcher
            args['sucess'] = sucess
            if getAuthorisationController().validate(getMessageContextController().getValue(incomingmessageid, 'senderid'), args['communityid'], 'g4ds.control.community.reply'):
                getJobDispatcher().resumeJob(messagereference, data, args)
        else:
            if action == COMMUNITY_ACTION_REQUEST_TCDL:
                if getAuthorisationController().validate(getMessageContextController().getValue(incomingmessageid, 'senderid'), args['communityid'], 'g4ds.control.community.read.requesttcdl'):
                    self.replyToRequestCommunityDescription(args['communityid'], incomingmessageid)
            elif action == COMMUNITY_ACTION_GET_MEMBERS:
                if getAuthorisationController().validate(getMessageContextController().getValue(incomingmessageid, 'senderid'), args['communityid'], 'g4ds.control.community.read.requestmemberlist'):
                    self.replyToRequestMemberList(args['communityid'], incomingmessageid)
            elif action == COMMUNITY_ADMIN_SUBSCRIBE:
                if getAuthorisationController().validate(getMessageContextController().getValue(incomingmessageid, 'senderid'), args['communityid'], 'g4ds.control.community.read.requestsubscription'):
                    self.replyToRequestMemberSubscription(args['newmemberid'], args['communityid'], incomingmessageid)
            else:
                from errorhandling import G4dsCommunicationException
                raise G4dsCommunicationException('Unknown action for CommunityController in ControllerManager.')

    def sendCommunityControllerMessage(self, destination, action, args, data = None, messagereference = None, sucess = COMMUNITY_SUCESS_NO_ERROR):
        """
        Any community message should be send through this interface.
        
        @param action: Action to perform - check constants in this module
        @type action: C{String}
        @param args: Arguments to pass in form of dictionary - name | value
        @type args: C{dict}
        @param data: Any additional data which does not fit into the args
        @type data: C{String}
        @return: The ID of the message
        @rtype: C{String}
        """
        from messagewrapper import getControlMessageWrapper
        wrapped, doc, node = getControlMessageWrapper().wrapSSCommunityMessage(action, sucess, args, data)
        return getOutgoingControlMessagesHandler().sendMessage(destination, CONTROL_SUBSYSTEM_COMMUNITIES, "Control Sub-System Communities", wrapped, messagereference)                
                
    def requestCommunityDescription(self, communityid, destinationMemberId):
        """
        Requests the community description for communityid from destinationMemberId.
        
        Note: Is does not wait for the reply. You have to register yourself with the JobScheduler in order to
        await the reply to the message!
        
        @param communityid: ID of the community, the description shall be downloaded for
        @type communityid: C{String}
        @param destinationMemberId: ID of the member, the description shall be requested from
        @type destinationMemberId: C{String}
        @return: The ID of the message
        @rtype: C{String}
        """
        args = {}
        args['communityid'] = communityid
        return self.sendCommunityControllerMessage(destinationMemberId, COMMUNITY_ACTION_REQUEST_TCDL, args)
        
    def replyToRequestCommunityDescription(self, communityid, messageid):
        """
        Looks for the requested community description and replies appropriately.
        
        @param communityid: ID of the community the description was requested for
        @type communityid: C{String}
        @param messageid: ID of the incoming message
        @type messageid: C{String}
        """
        ##print "Will give community description - community %s; ref %s" %(communityid, messageid)
        from communitymanager import getCommunityManager
        from messagehandler import getMessageContextController
        receiver = getMessageContextController().getValue(messageid, 'senderid')
        args = {}
        args['communityid'] = communityid
        try:
            community = getCommunityManager().getCommunity(communityid)
            tcdl = community.getTcdl()
            self.sendCommunityControllerMessage(receiver, COMMUNITY_ACTION_UPDATE_TCDL, args, tcdl, messageid)
            ##print "\n\tSENT TCDL SUCESSFULLY"
        except KeyError:
            self.sendCommunityControllerMessage(receiver, COMMUNITY_ACTION_UPDATE_TCDL, args, None, messageid, COMMUNITY_SUCESS_TCDL_NOT_FOUND)
            ##print "\n\tSENT ERROR FOR TCDL - community not found."
            
    def requestMemberList(self, communityid, destinationMemberId):
        """
        Requests a list of members subscriped to the community with the given community id.
        
        @param communityid: ID of the community, the list of members shall be requested for
        @type communityid: C{String}
        @param destinationMemberId: ID of the member the list shall be requested from
        @type destinationMemberId: C{String}
        @return: ID of the sent message
        @rtype: C{String}
        """
        args = {}
        args['communityid'] = communityid
        return self.sendCommunityControllerMessage(destinationMemberId, COMMUNITY_ACTION_GET_MEMBERS, args)
        
    def replyToRequestMemberList(self, communityid, messageid):
        """
        Looks for the members of the requested community - if available and allowed, a list of member ids is sent.
        
        @param communityid: ID of the community the member list was requested for
        @type communityid: C{String}
        @param messageid: ID of the incoming message
        @type messageid: C{String}
        """
        ##print "Will give member list for community %s" %(communityid)
        from communitymanager import getCommunityManager
        from messagehandler import getMessageContextController
        receiver = getMessageContextController().getValue(messageid, 'senderid')
        args = {}
        args['communityid'] = communityid
        try:
            community = getCommunityManager().getCommunity(communityid)
            members = community.getMembers()
            for x in range(1, len(members)+1):
                args['member' + str(x)] = members[x-1]
            self.sendCommunityControllerMessage(receiver, COMMUNITY_ACTION_UPDATE_MEMBERS, args, None, messageid)
            ##print "\nMEMBER LIST SENT SUCESSFULLY."
        except KeyError:
            self.sendCommunityControllerMessage(receiver, COMMUNITY_ACTION_UPDATE_MEMBERS, args, None, messageid, COMMUNITY_SUCESS_COMMUNITY_NOT_FOUND)
            ##print "\nSENT ERROR FOR COMMUNITY MEMBER LIST - COMMUNITY NOT AVAILABLE."
            
    def requestMemberSubscription(self, communityid, newmemberid, destinationmemberid):
        """
        Send a message to a CA in order to subscribe to a community.
        """
        args = {}
        args['newmemberid'] = newmemberid
        args['communityid'] = communityid
        return self.sendCommunityControllerMessage(destinationmemberid, COMMUNITY_ADMIN_SUBSCRIBE, args)
        
    def replyToRequestMemberSubscription(self, newmemberid, communityid, messageid):
        """
        Generates the reply to L{requestMemberSubscription}
        """
        from communitymanager import getCommunityManager, getMemberManager
        from messagehandler import getMessageContextController
        receiver = getMessageContextController().getValue(messageid, 'senderid')

        args = {}
        args['communityid'] = communityid
        try:
            member = getMemberManager().getMember(newmemberid)
        except KeyError:
            # here is something wrong - we can't add a member unless it's well known to us  
            self.sendCommunityControllerMessage(receiver, COMMUNITY_ACTION_GENERIC_REPLY, args, None, messageid, COMMUNITY_SUCESS_MEMBER_UNKNOWN)
            return
        try:
            community = getCommunityManager().getCommunity(communityid)
            members = community.getMembers()
            try:
                members.index(newmemberid)
                # he is a member already
                self.sendCommunityControllerMessage(receiver, COMMUNITY_ACTION_GENERIC_REPLY, args, None, messageid, COMMUNITY_SUCESS_MEMBER_ALREADY)
            except ValueError:
                # that's great - he is not a member yet
                community.addMember(newmemberid)
                member.addCommunity(communityid)
                self.sendCommunityControllerMessage(receiver, COMMUNITY_ACTION_GENERIC_REPLY, args, None, messageid)
        except KeyError:
            self.sendCommunityControllerMessage(receiver, COMMUNITY_ACTION_GENERIC_REPLY, args, None, messageid, COMMUNITY_SUCESS_COMMUNITY_NOT_FOUND)
        
MEMBER_ACTION_GENERIC_REPLY = '0'
MEMBER_ACTION_REQUEST_MDL = '1'
MEMBER_ACTION_UPDATE_MDL = '2'

MEMBER_SUCESS_NO_ERROR = '0'
MEMBER_SUCESS_GENERIC_ERROR = '1'
MEMBER_SUCESS_MDL_NOT_FOUND = '2'
MEMBER_SUCESS_PERMISSION_DENIED = '3'
        
# "singleton"
_memberController = None
def getMemberController():
    global _memberController
    if not _memberController:
        _memberController = MemberController()
    return _memberController
        
class MemberController:
    """
    Handles controlling of members.
    """
    def __init__(self):
        """
        Yet empty Constructor.
        """
        pass
        
    def dispatch(self, node, message, incomingmessageid):
        """
        Handles incoming messages.

        @param node: Data of the message as DOM tree
        @type node: L{xml.dom.Node}
        @param message: XML Message in String representation
        @type message: C{String}
        """
        from g4dslogging import getDefaultLogger, COMMUNICATION_INCOMING_MSG_DETAILS
        getDefaultLogger().newMessage(COMMUNICATION_INCOMING_MSG_DETAILS, '-- Control Msg - SS: Member Controller')

        from messagewrapper import getControlMessageWrapper
        action, sucess, args, data = getControlMessageWrapper().unwrapSSMemberMessage(message)
        from messagehandler import getMessageContextController
        from authorisationcontroller import getAuthorisationController
        messagereference = getMessageContextController().getValue(incomingmessageid, 'refid')
        if messagereference:
            from runtimecontroller import getJobDispatcher
            args['sucess'] = sucess
            if getAuthorisationController().validate(getMessageContextController().getValue(incomingmessageid, 'senderid'), args['memberid'], 'g4ds.control.member.reply'):
                getJobDispatcher().resumeJob(messagereference, data, args)
        else:
            if action == MEMBER_ACTION_REQUEST_MDL:
                if getAuthorisationController().validate(getMessageContextController().getValue(incomingmessageid, 'senderid'), args['memberid'], 'g4ds.control.member.read.requestmdl'):
                    self.replyToRequestMemberDescription(args['memberid'], incomingmessageid)
            if action == MEMBER_ACTION_UPDATE_MDL:
                if getAuthorisationController().validate(getMessageContextController().getValue(incomingmessageid, 'senderid'), args['memberid'], 'g4ds.control.member.write.updatemdl'):
                    self.processUpdateMdl(args['memberid'], 0, args['ackrequested'], data, incomingmessageid)
            else:
                from errorhandling import G4dsCommunicationException
                raise G4dsCommunicationException('Unknown action for MemberController in ControllerManager.')

    def sendMemberControllerMessage(self, destination, action, args, data = None, messagereference = None, sucess = MEMBER_SUCESS_NO_ERROR):
        """
        Any member message should be send through this interface.
        
        @param action: Action to perform - check constants in this module
        @type action: C{String}
        @param args: Arguments to pass in form of dictionary - name | value
        @type args: C{dict}
        @param data: Any additional data which does not fit into the args
        @type data: C{String}
        @return: The ID of the message
        @rtype: C{String}
        """
        from messagewrapper import getControlMessageWrapper
        wrapped, doc, node = getControlMessageWrapper().wrapSSMemberMessage(action, sucess, args, data)
        return getOutgoingControlMessagesHandler().sendMessage(destination, CONTROL_SUBSYSTEM_MEMBERS, "Control Sub-System Members", wrapped, messagereference)
        
        
    def requestMemberDescription(self, memberid, destinationMemberId):
        """
        Requests the member description for memberid from destinationMemberId.
        
        Note: Is does not wait for the reply. You have to register yourself with the JobScheduler in order to
        await the reply to the message!
        
        @return: The ID of the message
        @rtype: C{String}
        """
        args = {}
        args['memberid'] = memberid
        return self.sendMemberControllerMessage(destinationMemberId, MEMBER_ACTION_REQUEST_MDL, args)
        
    def replyToRequestMemberDescription(self, memberid, messageid):
        """
        Looks for the requested member description and replies appropriately.
        """
        from communitymanager import getMemberManager
        from messagehandler import getMessageContextController
        receiver = getMessageContextController().getValue(messageid, 'senderid')
        args = {}
        args['memberid'] = memberid
        try:
            member = getMemberManager().getMember(memberid)
            mdl = member.getMdl()
            self.sendMemberControllerMessage(receiver, MEMBER_ACTION_UPDATE_MDL, args, mdl, messageid)
        except KeyError:
            self.sendMemberControllerMessage(receiver, MEMBER_ACTION_UPDATE_MDL, args, None, messageid, MEMBER_SUCESS_MDL_NOT_FOUND)

    def requestPushMdl(self, destination, memberid, distribute, mdl, ackrequested = 0):
        """
        Push the member description to the given member.
        
        From the outside use L{uploadMdlToMembers} instead - it's waiting for replies and so on.
        """
        args = {}
        args['memberid'] = memberid
        args['distribute'] = str(distribute)
        args['ackrequested'] = str(ackrequested)
        return self.sendMemberControllerMessage(destination, MEMBER_ACTION_UPDATE_MDL, args, mdl)
    
    def processUpdateMdl(self, memberid, distribute, ackrequested, data, messageid, timeout = 120):
        """
        Processes a request for applying a new version of a member description.
        """
        from descriptionprocessor import getMemberDescriptionProcessor
        from messagehandler import getMessageContextController

        mdl = data
        ackrequested = int(ackrequested)
        distribute = int(distribute)
        
        status = getMemberDescriptionProcessor().applyMdl(mdl, 1)
        receiver = getMessageContextController().getValue(messageid, 'senderid')
        args = {}
        from communitymanager import getMemberManager
        args['memberid'] = getMemberManager().getLocalMember().getId()
        elapsed = 0
        timeover = 0
        secs = timeout
        import time
        from runtimecontroller import JOB_FINISHED, JOB_ABORTED
        while 1:
            time.sleep(1)
            elapsed += 1
            if status.getStatus() == JOB_FINISHED or status.getStatus() == JOB_ABORTED:
                break
            if elapsed > secs:
                timeover = 1
                break
        if status.getStatus() == JOB_ABORTED:
            if ackrequested:
                code, msg = status.getError()
                if code != None:    
                    args['errorcode'] = str(code)
                if msg != None:
                    args['errormessage'] = msg
                self.sendMemberControllerMessage(receiver, MEMBER_ACTION_GENERIC_REPLY, args, None, messageid, MEMBER_SUCESS_GENERIC_ERROR)
            return
        if timeover:
            if ackrequested:
                args['errorcode'] = '12'
                args['errormessage'] = 'Action timed out'                
                self.sendMemberControllerMessage(receiver, MEMBER_ACTION_GENERIC_REPLY, args, None, messageid, MEMBER_SUCESS_GENERIC_ERROR)
            return
        
        if ackrequested:
            self.sendMemberControllerMessage(receiver, MEMBER_ACTION_GENERIC_REPLY, args, None, messageid, MEMBER_SUCESS_NO_ERROR)
            
    def _subUploadOne(self, memberid, mdl, communityid, destination, distribute, inbackground = 1, status = None):
        if not status:
            from runtimecontroller import JobStatus
            status = JobStatus()

        if inbackground:
            import thread
            thread.start_new_thread(self._subUploadOne, (memberid, mdl, communityid, destination, distribute, 0, status))
            return status
            
        from runtimecontroller import getJobDispatcher, JobLocker, JOB_FINISHED, JOB_ABORTED, JOB_FINISHED_WITH_ERROR, JOB_INITIALISED
        from errorhandling import G4dsException, G4dsRuntimeException
        status.setStatus(JOB_INITIALISED)

        try:
            msgId = self.requestPushMdl(destination, memberid, distribute, mdl, 1)
            jl = JobLocker()
            getJobDispatcher().addJob(msgId, jl)
            
        except G4dsException, msg:
            status.setError(21,'Error for Tcdl download: ' + str(msg))
            status.setStatus(JOB_ABORTED)
            return
            
        from runtimecontroller import getJobDispatcher
        msg, args = getJobDispatcher().getMessage(msgId)
        sucess = args['sucess'] 
        if sucess == MEMBER_SUCESS_NO_ERROR:
            status.setStatus(JOB_FINISHED)
        else:
            try:
                code = args['errorcode']
                msg = args['errormessage']
                status.setError(code, msg)
            except KeyError, msg:
                status.setError(21,'Error for Tcdl download: ' + str(msg))
            status.setStatus(JOB_FINISHED_WITH_ERROR)
    
    def uploadMdlToMembers(self, memberid, mdl, communityid = None, destinations = [], timeout = 60, distribute = 0):
        """
        Uploads a mdl to a collection of members.
        
        Supports some job features - chcking for replies...
        
        @param memberid: ID of the member described in the mdl
        @type memberid: C{String}
        @param mdl: Description in xml format
        @type mdl: C{String}
        @param communityid: ID of the community to use for this transaction - None for any
        @type communityid: C{String}
        @param destinations: List of IDs for members to upload to
        @type destinations: C{List} of C{String}
        @param timeout: Time to wait for EACH transaction to finish.
        @type timeout: C{int}
        @return: List of sucessful member ids and list of unsucessful member ids
        @rtype: C{List} of C{String} / C{List} of C{String}
        """
        positive = []
        negative = []
        errors = {}
        secs = timeout
        for dest in destinations:

            status = self._subUploadOne(memberid, mdl, communityid, dest, distribute)
            elapsed = 0
            timeover = 0
            import time
            from runtimecontroller import JOB_FINISHED, JOB_ABORTED, JOB_FINISHED_WITH_ERROR
            while 1:
                time.sleep(1)
                elapsed += 1
                if status.getStatus() == JOB_FINISHED or status.getStatus() == JOB_ABORTED or status.getStatus() == JOB_FINISHED_WITH_ERROR:
                    break
                if elapsed > secs:
                    timeover = 1
                    break
            if status.getStatus() == JOB_ABORTED or status.getStatus() == JOB_FINISHED_WITH_ERROR:
                negative.append(dest)
            elif timeover:
                negative.append(dest)
                errors[dest] = (0, 'timeout')
            else:
                positive.append(dest)
            if status.getError() != (None, None):
                errors[dest] = status.getError()

        return positive, negative, errors


        
ROUTING_ACTION_GENERIC_REPLY = '0'
ROUTING_ACTION_REQUEST_ROUTING_TABLE = '1'
ROUTING_ACTION_UPDATE_ROUTING_TABLE = '2'

ROUTING_SUCESS_NO_ERROR = '0'
ROUTING_SUCESS_GENERIC_ERROR = '1'
ROUTING_SUCESS_PERMISSION_DENIED = '2'
        
# "singleton"
_routingController = None
def getRoutingController():
    global _routingController
    if not _routingController:
        _routingController = RoutingController()
    return _routingController
        
class RoutingController:
    """
    Handles controlling of routing.
    """
    def __init__(self):
        """
        Yet empty Constructor.
        """
        pass
        
    def dispatch(self, node, message, incomingmessageid):
        """
        Handles incoming messages.

        @param node: Data of the message as DOM tree
        @type node: L{xml.dom.Node}
        @param message: XML Message in String representation
        @type message: C{String}
        """
        from g4dslogging import getDefaultLogger, COMMUNICATION_INCOMING_MSG_DETAILS
        getDefaultLogger().newMessage(COMMUNICATION_INCOMING_MSG_DETAILS, '-- Control Msg - SS: Routing Controller')

        from messagewrapper import getControlMessageWrapper
        action, sucess, args, data = getControlMessageWrapper().unwrapSSRoutingMessage(message)
        from messagehandler import getMessageContextController
        messagereference = getMessageContextController().getValue(incomingmessageid, 'refid')
        from authorisationcontroller import getAuthorisationController        
        senderid = getMessageContextController().getValue(incomingmessageid, 'senderid')
        senderId = getMessageContextController().getValue(incomingmessageid, 'senderid')
        if messagereference:
            from runtimecontroller import getJobDispatcher
            args['sucess'] = sucess
            if getAuthorisationController().validate(senderId, senderId, 'g4ds.control.routing.reply'):
                getJobDispatcher().resumeJob(messagereference, data, args)
        else:
            if action == ROUTING_ACTION_REQUEST_ROUTING_TABLE:
                if getAuthorisationController().validate(senderId, senderId, 'g4ds.control.routing.read.requestroutingtable'):
                    self.replyToDownloadRoutingTable(senderid, None, incomingmessageid)
            elif action == ROUTING_ACTION_UPDATE_ROUTING_TABLE:
                if getAuthorisationController().validate(senderId, senderId, 'g4ds.control.routing.write.pushroutingtable'):
                    self.processIncomingRoutingUpdate(senderid, data, incomingmessageid)
            else:
                from errorhandling import G4dsCommunicationException
                raise G4dsCommunicationException('Unknown action for RoutingController in ControllerManager.')

    def sendRoutingControllerMessage(self, destination, action, args, data = None, messagereference = None, sucess = ROUTING_SUCESS_NO_ERROR):
        """
        Any routing controller message should be send through this interface.
        
        @param action: Action to perform - check constants in this module
        @type action: C{String}
        @param args: Arguments to pass in form of dictionary - name | value
        @type args: C{dict}
        @param data: Any additional data which does not fit into the args
        @type data: C{String}
        @return: The ID of the message
        @rtype: C{String}
        """
        from messagewrapper import getControlMessageWrapper
        wrapped, doc, node = getControlMessageWrapper().wrapSSRoutingMessage(action, sucess, args, data)
        return getOutgoingControlMessagesHandler().sendMessage(destination, CONTROL_SUBSYSTEM_ROUTING, "Control Sub-System Routing", wrapped, messagereference)

    def _uploadRoutingTableToOneNode(self, destination, destinationcommunity, inbackground =1, status = None, messageid = None, requestReply = 1):
        """
        Job function for routing table upload.
        """
        if not status:
            from runtimecontroller import JobStatus
            status = JobStatus()
            
        if inbackground:
            import thread
            thread.start_new_thread(self._uploadRoutingTableToOneNode, (destination, destinationcommunity, 0, status, messageid, requestReply))
            return status
            
        from runtimecontroller import getJobDispatcher, JobLocker, JOB_FINISHED, JOB_ABORTED, JOB_FINISHED_WITH_ERROR, JOB_INITIALISED
        from errorhandling import G4dsException, G4dsRuntimeException
        status.setStatus(JOB_INITIALISED)

        try:
            args = {}
            from routingtablemanager import getRoutingTableManager
            data = getRoutingTableManager().getRoutingTableXML()
            msgid = self.sendRoutingControllerMessage(destination, ROUTING_ACTION_UPDATE_ROUTING_TABLE, args, data, messageid)
        except G4dsException, msg:
            status.setError(30, 'Error for routing table upload to member %s' %(destination))
            status.setStatus(JOB_ABORTED)
            return
        
        if not requestReply:
            status.setStatus(JOB_FINISHED)
            return
        
        from runtimecontroller import getJobDispatcher
        msg, args = getJobDispatcher().getMessage(msgid)
        sucess = args['sucess']
        if sucess ==ROUTING_SUCESS_NO_ERROR:
            status.setStatus(JOB_FINISHED)
            status.setMessage(msg)
        else:
            try:
                code = args['errorcode']
                msg = args['errormessage']
                status.setError(code, msg)
            except KeyError, msg:
                status.setError(31, 'Error for routing table download - remote peer id is %s.' %(destination))
            status.setStatus(JOB_FINISHED_WITH_ERROR)
        
    def sendRoutingTable(self, destination, destinationcommunity = None, timeout = 120, msgid = None, requestReply = 1):
        """
        Sends the local routing table xml encoded to one peer.
        """
        status = self._uploadRoutingTableToOneNode(destination, destinationcommunity, messageid = msgid, requestReply = requestReply)
        
        elapsed = 0
        timeover = 0
        import time
        from runtimecontroller import JOB_FINISHED, JOB_ABORTED, JOB_FINISHED_WITH_ERROR
        
        while 1:
            time.sleep(1)
            elapsed += 1
            if status.getStatus() == JOB_FINISHED  or status.getStatus() == JOB_ABORTED or status.getStatus() == JOB_FINISHED_WITH_ERROR:
                break
            if elapsed > timeout:
                timeover = 1
                break
            
        if status.getStatus() == JOB_ABORTED or status.getStatus() == JOB_FINISHED_WITH_ERROR or timeover:
            if status.getError() != (None, None):
                errormsg = 'Error - routing table upload to peer %s: %s' %(destination, str(list(status.getError())))
            elif timeover:
                errormsg = 'Timeout of transaction for uploading routing table to peer %s.' %(destination)
            else:
                errormsg = 'Unknown error for uploading routing table to %s.' %(destination)
            from errorhandling import G4dsDependencyException
            raise G4dsDependencyException(errormsg)
        
        return 0
        
    def replyToDownloadRoutingTable(self, destination, destinationcommunity, messageid):
        """
        Reply to the request of routing table.
        """
        from messagehandler import getMessageContextController
        receiver = getMessageContextController().getValue(messageid, 'senderid')
        try:
            self.sendRoutingTable(receiver, destinationcommunity, msgid =  messageid, requestReply = 0)
        except Exception, msg:
            args = {}
            args['errorcode'] = '0'
            args['errormessage'] = 'Unknown error - low level message: %s' %(msg)
            self.sendRoutingControllerMessage(receiver, ROUTING_ACTION_UPDATE_ROUTING_TABLE, args, None, messageid, ROUTING_SUCESS_GENERIC_ERROR)
        
    def _downloadRoutingTableFromOneNode(self, destination, destinationcommunity, inbackground =1, status = None):
        """
        Starts a job to download the routing table from one node.
        """
        if not status:
            from runtimecontroller import JobStatus
            status = JobStatus()
            
        if inbackground:
            import thread
            thread.start_new_thread(self._downloadRoutingTableFromOneNode, (destination, destinationcommunity, 0, status))
            return status
            
        from runtimecontroller import getJobDispatcher, JobLocker, JOB_FINISHED, JOB_ABORTED, JOB_FINISHED_WITH_ERROR, JOB_INITIALISED
        from errorhandling import G4dsException, G4dsRuntimeException
        status.setStatus(JOB_INITIALISED)

        try:
            args = {}
            msgid = self.sendRoutingControllerMessage(destination, ROUTING_ACTION_REQUEST_ROUTING_TABLE, args)
            jl = JobLocker()
            getJobDispatcher().addJob(msgid, jl)
        except G4dsException, msg:
            status.setError(30, 'Error for routing table download from member %s' %(destination))
            status.setStatus(JOB_ABORTED)
            return
        
        from runtimecontroller import getJobDispatcher
        msg, args = getJobDispatcher().getMessage(msgid)
        sucess = args['sucess']
        if sucess ==ROUTING_SUCESS_NO_ERROR:
            status.setStatus(JOB_FINISHED)
            status.setMessage(msg)
        else:
            try:
                code = args['errorcode']
                msg = args['errormessage']
                status.setError(code, msg)
            except KeyError, msg:
                status.setError(31, 'Error for routing table download - remote peer id is %s.' %(destination))
            status.setStatus(JOB_FINISHED_WITH_ERROR)
            
    def downloadRoutingTable(self, destination, destinationcommunity = None, timeout = 120):
        """
        Download routing table from one peer.
        """
        status = self._downloadRoutingTableFromOneNode(destination, destinationcommunity)
        
        elapsed = 0
        timeover = 0
        import time
        from runtimecontroller import JOB_FINISHED, JOB_ABORTED, JOB_FINISHED_WITH_ERROR
        
        while 1:
            time.sleep(1)
            elapsed += 1
            if status.getStatus() == JOB_FINISHED  or status.getStatus() == JOB_ABORTED or status.getStatus() == JOB_FINISHED_WITH_ERROR:
                break
            if elapsed > timeout:
                timeover = 1
                break
            
        if status.getStatus() == JOB_ABORTED or status.getStatus() == JOB_FINISHED_WITH_ERROR or timeover:
            if status.getError() != (None, None):
                errormsg = 'Error - routing table download from peer %s: %s' %(destination, str(list(status.getError())))
            elif timeover:
                errormsg = 'Timeout of transaction for downloading routing table from peer %s.' %(destination)
            else:
                errormsg = 'Unknown error for downloading routing table from %s.' %(destination)
            from errorhandling import G4dsDependencyException
            raise G4dsDependencyException(errormsg)
        
        return status.getMessage()
        
    def processIncomingRoutingUpdate(self, destination, data, messageid):
        """
        Applies an incoming routing table update to the local routing table manager.
        """
        from routingtablemanager import getRoutingTableManager
        from g4dslogging import getDefaultLogger, ROUTING_TABLE_UPDATED_PUHSHED, ROUTING_TABLE_UPDATED_ERROR
        try:
            getRoutingTableManager().applyRoutingTableFromNode(destination, data)
            getDefaultLogger().newMessage(ROUTING_TABLE_UPDATED_PUHSHED, 
                "Processed pushed routing table from peer %s" %(destination))
        except Exception, msg:
            getDefaultLogger().newMessage(ROUTING_TABLE_UPDATED_ERROR, 
                "Error when processing pushed routing table from peer %s - error: %s" %(destination, msg))
        

SERVICE_ACTION_REQUEST_KSDL = '0'
SERVICE_ACTION_UPDATE_KSDL = '1'
SERVICE_ACTION_GET_MEMBERS = '2'
SERVICE_ACTION_UPDATE_MEMBERS = '3'
SERVICE_ACTION_GENERIC_REPLY = '4'
SERVICE_ADMIN_SUBSCRIBE = '5'

SERVICE_SUCESS_NO_ERROR = '0'
SERVICE_SUCESS_KSDL_NOT_FOUND = '1'
SERVICE_SUCESS_SERVICE_NOT_FOUND = '2'
SERVICE_SUCESS_MEMBER_ALREADY = '3'
SERVICE_SUCESS_MEMBER_UNKNOWN = '4'
SERVICE_SUCESS_GENERIC_ERROR = '5'

        
# "singleton"
_serviceController = None
def getServiceController():
    global _serviceController
    if not _serviceController:
        _serviceController = ServiceController()
    return _serviceController
        
class ServiceController:        
    """
    Handles controlling of services.
    """
    def __init__(self):
        """
        Yet empty Constructor.
        """
        pass
        
    def dispatch(self, node, message, incomingmessageid):
        """
        Handles incoming services control messages.

        @param node: Data of the message as DOM tree
        @type node: L{xml.dom.Node}
        @param message: XML Message in String representation
        @type message: C{String}
        """
        from g4dslogging import getDefaultLogger, COMMUNICATION_INCOMING_MSG_DETAILS
        getDefaultLogger().newMessage(COMMUNICATION_INCOMING_MSG_DETAILS, '-- Control Msg - SS: Service Controller')

        from messagewrapper import getControlMessageWrapper
        action, sucess, args, data = getControlMessageWrapper().unwrapSSServiceMessage(message)
        ##print "\tRequesed action: %s" %(action)
        from messagehandler import getMessageContextController
        messagereference = getMessageContextController().getValue(incomingmessageid, 'refid')
        from authorisationcontroller import getAuthorisationController
        if messagereference:
            ##print "\n\tAttempt to resume Job %s" %(messagereference)
            from runtimecontroller import getJobDispatcher
            args['sucess'] = sucess
            if getAuthorisationController().validate(getMessageContextController().getValue(incomingmessageid, 'senderid'), args['serviceid'], 'g4ds.control.service.reply'):
                getJobDispatcher().resumeJob(messagereference, data, args)
        else:
            if action == SERVICE_ACTION_REQUEST_KSDL:
                if getAuthorisationController().validate(getMessageContextController().getValue(incomingmessageid, 'senderid'), args['serviceid'], 'g4ds.control.service.read.requestksdl'):
                    self.replyToRequestServiceDescription(args['serviceid'], incomingmessageid)
            elif action == SERVICE_ACTION_UPDATE_KSDL:
                if getAuthorisationController().validate(getMessageContextController().getValue(incomingmessageid, 'senderid'), args['serviceid'], 'g4ds.control.service.write.updateksdl'):
                    self.replyToUploadKsdlToMember(args['serviceid'], args['ackrequested'], data, incomingmessageid)
            elif action == SERVICE_ACTION_GET_MEMBERS:
                if getAuthorisationController().validate(getMessageContextController().getValue(incomingmessageid, 'senderid'), args['serviceid'], 'g4ds.control.service.read.requestmemberlist'):
                    self.replyToRequestMemberList(args['serviceid'], incomingmessageid)
            elif action == SERVICE_ADMIN_SUBSCRIBE:
                if getAuthorisationController().validate(getMessageContextController().getValue(incomingmessageid, 'senderid'), args['serviceid'], 'g4ds.control.service.read.requestsubscription'):
                    self.replyToRequestMemberSubscription(args['newmemberid'], args['serviceid'], incomingmessageid)
            else:
                from errorhandling import G4dsCommunicationException
                raise G4dsCommunicationException('Unknown action for ServiceController in ControllerManager.')
    
    def sendServiceControllerMessage(self, destination, action, args, data = None, messagereference = None, sucess = SERVICE_SUCESS_NO_ERROR):
        """
        Any service control message should be send through this interface.
        
        @param action: Action to perform - check constants in this module
        @type action: C{String}
        @param args: Arguments to pass in form of dictionary - name | value
        @type args: C{dict}
        @param data: Any additional data which does not fit into the args
        @type data: C{String}
        @return: The ID of the message
        @rtype: C{String}
        """
        from messagewrapper import getControlMessageWrapper
        wrapped, doc, node = getControlMessageWrapper().wrapSSServiceMessage(action, sucess, args, data)
        return getOutgoingControlMessagesHandler().sendMessage(destination, CONTROL_SUBSYSTEM_SERVICES, "Control Sub-System Services", wrapped, messagereference)
    
    def replyToRequestServiceDescription(self, serviceid, messageid):
        """
        Looks for the requested service description and replies appropriately.
        
        @param serviceid: ID of the service the description was requested for
        @type serviceid: C{String}
        @param messageid: ID of the incoming message
        @type messageid: C{String}
        """
        ##print "Will give community description - community %s; ref %s" %(communityid, messageid)
        from servicerepository import getServiceManager
        from messagehandler import getMessageContextController
        receiver = getMessageContextController().getValue(messageid, 'senderid')
        args = {}
        args['serviceid'] = serviceid
        try:
            service = getServiceManager().getService(serviceid)
            ksdl = service.getKsdl()
            self.sendServiceControllerMessage(receiver, SERVICE_ACTION_UPDATE_MEMBERS, args, ksdl, messageid)
            ##print "\n\tSENT TCDL SUCESSFULLY"
        except KeyError:
            self.sendServiceControllerMessage(receiver, SERVICE_ACTION_UPDATE_MEMBERS, args, None, messageid, SERVICE_SUCESS_SERVICE_NOT_FOUND)

    def requestServiceDescription(self, serviceid, destinationMemberId):
        """
        Requests the community description for serviceid from destinationMemberId.
        
        Note: Is does not wait for the reply. You have to register yourself with the JobScheduler in order to
        await the reply to the message!
        
        @param serviceid: ID of the service, the description shall be downloaded for
        @type serviceid: C{String}
        @param destinationMemberId: ID of the member, the description shall be requested from
        @type destinationMemberId: C{String}
        @return: The ID of the message
        @rtype: C{String}
        """
        args = {}
        args['serviceid'] = serviceid
        return self.sendServiceControllerMessage(destinationMemberId, SERVICE_ACTION_REQUEST_KSDL, args)

    def downloadServiceDescriptionJob(self, serviceid, memberid, inbackground = 0, status = None):
        """
        Job function for downloading a ksdl from a remote host.
        
        Supports job functionality.
        """
        from runtimecontroller import JobStatus, JOB_UNINITIALISED, JOB_INITIALISED, JOB_FINISHED, JOB_ABORTED
        from errorhandling import G4dsDependencyException, G4dsException
        if not status:
            status = JobStatus()
    
        if inbackground:
            import thread
            thread.start_new_thread(self.downloadServiceDescriptionJob,(serviceid, memberid, 0, status))
            return status
        
        status.setStatus(JOB_INITIALISED)
        from runtimecontroller import getJobDispatcher, JobLocker
        try:
            msgId = self.requestServiceDescription(serviceid, memberid)
        except G4dsException, msg:
            status.setError(21,'Error for ksdl download: ' + str(msg))
            status.setStatus(JOB_ABORTED)
            return
            
        jl = JobLocker()
        getJobDispatcher().addJob(msgId, jl)
        # wait and wait and wait
        # and go
        message, args = getJobDispatcher().getMessage(msgId)
        if not message or args['sucess'] == SERVICE_SUCESS_SERVICE_NOT_FOUND:
            status.setError(4,'The required KSDL (' + serviceid + ') could not be downloaded. You have to download it manually.')
            status.setStatus(JOB_ABORTED)
            return
        status.setMessage(message)
        status.setStatus(JOB_FINISHED)


    def requestPushKsdl(self, destination, serviceid, ksdl, ackrequested = 0):
        """
        Push service description to given member.
        """
        args = {}
        args['serviceid'] = serviceid
        args['ackrequested'] = str(ackrequested)
        return self.sendServiceControllerMessage(destination, SERVICE_ACTION_UPDATE_KSDL, args, ksdl)
        
    def uploadKsdlToMember(self, serviceid, ksdl, destination, communityid = None, inbackground = 1, status = None):
        if not status:
            from runtimecontroller import JobStatus
            status = JobStatus()

        if inbackground:
            import thread
            thread.start_new_thread(self.uploadKsdlToMember, (serviceid, ksdl, destination, communityid, 0, status))
            return status
            
        from runtimecontroller import getJobDispatcher, JobLocker, JOB_FINISHED, JOB_ABORTED, JOB_INITIALISED
        from errorhandling import G4dsException, G4dsRuntimeException
        status.setStatus(JOB_INITIALISED)

        try:
            msgId = self.requestPushKsdl(destination, serviceid, ksdl, 1)
            jl = JobLocker()
            getJobDispatcher().addJob(msgId, jl)
            
        except G4dsException, msg:
            status.setError(21,'Error for Ksdl upload: ' + str(msg))
            status.setStatus(JOB_ABORTED)
            return
            
        from runtimecontroller import getJobDispatcher
        msg, args = getJobDispatcher().getMessage(msgId)
        sucess = args['sucess'] 
        if sucess == SERVICE_SUCESS_NO_ERROR:
            status.setStatus(JOB_FINISHED)
        else:
            try:
                code = args['errorcode']
                msg = args['errormessage']
                status.setError(code, msg)
            except KeyError, msg:
                status.setError(21,'Error for ksdl upload: ' + str(msg))
            status.setStatus(JOB_ABORTED)

    def uploadKsdlToMemberJob(self, serviceid, ksdl, destination, community = None, timeout = 60):
        """
        Uploads the service description to the given member.
        
        Function supports job functionality.
        """
        from errorhandling import G4dsCommunicationException
        
        status = self.uploadKsdlToMember(serviceid, ksdl, destination, community, 1)
       
        elapsed = 0
        timeover = 0
        import time
        from runtimecontroller import JOB_FINISHED, JOB_ABORTED, JOB_FINISHED_WITH_ERROR
        while 1:
            time.sleep(1)
            elapsed += 1
            if status.getStatus() == JOB_FINISHED or status.getStatus() == JOB_ABORTED:
                break
            if elapsed > timeout:
                timeover = 1
                break
        if status.getStatus() == JOB_ABORTED:
            if status.getError() != (None, None):
                raise G4dsCommunicationException('KSDL upload error: %s' %(status.getError()))
        elif timeover:
            raise G4dsCommunicationException('KSDL upload error: Action was timed out')
        else:
            return 1
            
    def replyToUploadKsdlToMember(self, serviceid, ackrequested, data, messageid, timeout = 120):
        """
        Processes a request for applying a new version of a service description.
        """
        from descriptionprocessor import getServiceDescriptionProcessor
        from messagehandler import getMessageContextController

        ksdl = data
        ackrequested = int(ackrequested)
        
        status = getServiceDescriptionProcessor().applyKsdl(ksdl, 1, 1)
        receiver = getMessageContextController().getValue(messageid, 'senderid')
        args = {}
        
        args['serviceid'] = serviceid
        elapsed = 0
        timeover = 0
        secs = timeout
        import time
        from runtimecontroller import JOB_FINISHED, JOB_ABORTED
        while 1:
            time.sleep(1)
            elapsed += 1
            if status.getStatus() == JOB_FINISHED or status.getStatus() == JOB_ABORTED:
                break
            if elapsed > secs:
                timeover = 1
                break
        if status.getStatus() == JOB_ABORTED:
            if ackrequested:
                code, msg = status.getError()
                if code != None:    
                    args['errorcode'] = str(code)
                if msg != None:
                    args['errormessage'] = msg
                self.sendServiceControllerMessage(receiver, SERVICE_ACTION_GENERIC_REPLY, args, None, messageid, SERVICE_SUCESS_GENERIC_ERROR)
            return
        if timeover:
            if ackrequested:
                args['errorcode'] = '12'
                args['errormessage'] = 'Action timed out'                
                self.sendServiceControllerMessage(receiver, SERVICE_ACTION_GENERIC_REPLY, args, None, messageid, SERVICE_SUCESS_GENERIC_ERROR)
            return
        
        if ackrequested:
            self.sendServiceControllerMessage(receiver, SERVICE_ACTION_GENERIC_REPLY, args, None, messageid, SERVICE_SUCESS_NO_ERROR)

    def requestMemberList(self, serviceid, destinationMemberId):
        """
        Requests a list of members subscriped to the service with the given service id.
        
        @param serviceid: ID of the service, the list of members shall be requested for
        @type serviceid: C{String}
        @param destinationMemberId: ID of the member the list shall be requested from
        @type destinationMemberId: C{String}
        @return: ID of the sent message
        @rtype: C{String}
        """
        args = {}
        args['serviceid'] = serviceid
        return self.sendCommunityControllerMessage(destinationMemberId, SERVICE_ACTION_GET_MEMBERS, args)
        
    def replyToRequestMemberList(self, serviceid, messageid):
        """
        Looks for the members of the requested service - if available and allowed, a list of member ids is sent.
        
        @param serviceid: ID of the service the member list was requested for
        @type serviceid: C{String}
        @param messageid: ID of the incoming message
        @type messageid: C{String}
        """
        from servicerepository import getServiceManager
        from messagehandler import getMessageContextController
        receiver = getMessageContextController().getValue(messageid, 'senderid')
        args = {}
        args['serviceid'] = serviceid
        try:
            service = getServiceManager().getService(serviceid)
            members = service.getMembers()
            for x in range(1, len(members)+1):
                args['member' + str(x)] = members[x-1]
            self.sendServiceControllerMessage(receiver, SERVICE_ACTION_UPDATE_MEMBERS, args, None, messageid)
            ##print "\nMEMBER LIST SENT SUCESSFULLY."
        except KeyError:
            self.sendCommunityControllerMessage(receiver, SERVICE_ACTION_UPDATE_MEMBERS, args, None, messageid, SERVICE_SUCESS_SERVICE_NOT_FOUND)
            ##print "\nSENT ERROR FOR SERVICE MEMBER LIST - CO

    def requestMemberSubscription(self, serviceid, newmemberid, destinationmemberid):
        """
        Send a message to a service authority in order to subscribe to a service.
        """
        args = {}
        args['newmemberid'] = newmemberid
        args['serviceid'] = serviceid
        return self.sendServiceControllerMessage(destinationmemberid, SERVICE_ADMIN_SUBSCRIBE, args)

    def replyToRequestMemberSubscription(self, newmemberid, serviceid, messageid):
        """
        Generates the reply to L{requestMemberSubscription}.
        """
        from communitymanager import getMemberManager
        from servicerepository import getServiceManager
        from messagehandler import getMessageContextController
        receiver = getMessageContextController().getValue(messageid, 'senderid')

        from g4dslogging import getDefaultLogger, CONTROL_SYSTEM_DETAILS, CONTROL_SYSTEM_ERROR
        
        args = {}
        args['serviceid'] = serviceid
        try:
            member = getMemberManager().getMember(newmemberid)
        except KeyError:
            # here is something wrong - we can't add a member unless it's well known to us  
            self.sendServiceControllerMessage(receiver, SERVICE_ACTION_GENERIC_REPLY, args, None, messageid, SERVICE_SUCESS_MEMBER_UNKNOWN)
            return
        try:
            service = getServiceManager().getService(serviceid)
            members = service.getMembers()
            try:
                members.index(newmemberid)
                # he is a member already
                self.sendServiceControllerMessage(receiver, SERVICE_ACTION_GENERIC_REPLY, args, None, messageid, SERVICE_SUCESS_MEMBER_ALREADY)
            except ValueError:
                # that's great - he is not a member yet
                service.addMember(newmemberid)
                self.sendServiceControllerMessage(receiver, SERVICE_ACTION_GENERIC_REPLY, args, None, messageid)
                getDefaultLogger().newMessage(CONTROL_SYSTEM_DETAILS, 'G4DS Control - SS Service: Added member (%s) to service (%s).' %(newmemberid, serviceid))
        except KeyError:
            self.sendServiceControllerMessage(receiver, SERVICE_ACTION_GENERIC_REPLY, args, None, messageid, SERVICE_SUCESS_SERVICE_NOT_FOUND)

    def _requestSubscriptionThread(self, serviceid, memberid, destination, inbackground = 0, status = None):
        """
        Supporter function for subsribing a member to a service.
        
        Supports job functionality.
        """
        from runtimecontroller import JobStatus, JOB_UNINITIALISED, JOB_INITIALISED, JOB_FINISHED, JOB_ABORTED
        from errorhandling import G4dsDependencyException, G4dsException
        if not status:
            status = JobStatus()
    
        if inbackground:
            import thread
            thread.start_new_thread(self._requestSubscriptionThread,(serviceid, memberid, destination, 0, status))
            return status
        
        status.setStatus(JOB_INITIALISED)
        from runtimecontroller import getJobDispatcher, JobLocker
        try:
            msgId = self.requestMemberSubscription(serviceid, memberid, destination)
        except G4dsException, msg:
            status.setError(21,'Error for member subscription: ' + str(msg))
            status.setStatus(JOB_ABORTED)
            return
            
        jl = JobLocker()
        getJobDispatcher().addJob(msgId, jl)
        # wait and wait and wait
        # and go
        message, args = getJobDispatcher().getMessage(msgId)
        if args['sucess'] != SERVICE_SUCESS_NO_ERROR and args['sucess'] != SERVICE_SUCESS_MEMBER_ALREADY:
            status.setError(4,'The subscription could not be performed. Error Code is %s' %args['sucess'])
            status.setStatus(JOB_ABORTED)
            return
        status.setMessage(message)
        status.setStatus(JOB_FINISHED)
    
                
    def requestSubscriptionJob(self, serviceid, newmemberid, destination, secs):
        """
        Supporter function for member subscription process.
        """
        from errorhandling import G4dsRuntimeException
        status = self._requestSubscriptionThread(serviceid, newmemberid, destination, 1)
        elapsed = 0
        timeover = 0
        import time
        from runtimecontroller import JOB_FINISHED, JOB_ABORTED
        while 1:
            time.sleep(1)
            elapsed += 1
            if status.getStatus() == JOB_FINISHED or status.getStatus() == JOB_ABORTED:
                break
            if elapsed > secs:
                timeover = 1
                break
        if status.getStatus() == JOB_ABORTED:
            if status.getError() != (None, None):
                raise G4dsRuntimeException('Error for subscription: (%d) (%s)' % status.getError())
            else:
                raise G4dsRuntimeException('Unknown error when performing subscription.')
        if timeover:
            raise G4dsRuntimeException('The requested action has been timed out.')
