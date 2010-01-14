"""
Handles both, incoming at outgoing messages in the first place.

Grid for Digital Security (G4DS)

For incoming messages a class L{GlobalOutoingMessageHandler} is provided. Only the instance
provided by the function L{getGlobalOutgoingMessageHandler} should be used for accessing it. (Singleton).
It provides functions for sending both service and control messages.

For outgoing messages there is the class called GlobalMessageDispatcher. Whenever a new message
arrives, it should be passed to the function L{GlobalDispatcher.dispatch} inside it.

@author: Michael Pilgermann
@contact: mailto:mpilgerm@glam.ac.uk
@license: GPL (General Public License)

@var _globalOutgoingMessageHandler: Singleton - the only instance ever of the GlobalOutoingMessageHandler class
@type _globalOutgoingMessageHandler: L{GlobalOutoingMessageHandler}
@var _globalDispatcher: Singleton - the only instance ever of the GlobalDispatcher class
@type _globalDispatcher: L{GlobalDispatcher}
"""

from g4dsconfigurationcontroller import getControlMessageDispatcher
from securitycontroller import getSecurityController
from serviceintegrator import getServiceIntegrator
from securitymanager import getAlgorithmManager
from messagewrapper import getMessageWrapper
from protocolcontroller import getProtocolController
import xmlconfig
import messagewrapper
import g4dsconfigurationcontroller
import securitycontroller

import xml.dom
from xml.dom import Node
import xml.dom.ext.reader.Sax2
from StringIO import StringIO
import xml.dom.ext


# "singleton"
_globalOutgoingMessageHandler = None
def getGlobalOutgoingMessageHandler():
    """
    Singleton implementation.
    
    @return: The instance for the global outgoing message handler class
    @rtype: L{GlobalOutoingMessageHandler}
    """
    global _globalOutgoingMessageHandler
    if not _globalOutgoingMessageHandler:
        _globalOutgoingMessageHandler = GlobalOutoingMessageHandler()
    return _globalOutgoingMessageHandler
    

class GlobalOutoingMessageHandler:
    """
    Handler for outgoing messages.
    
    Two kinds of messages are distinguished; namely service messages and control messages. Service
    messages are messages traveling from the connected service (application) on this node to the 
    same service on another node. Control message, however, are G4DS internal message for the purposes
    of configuring the G4DS parameters and keep data up-to-date on all sides.
    
    Both kinds of messages service and control are finally wrapped into G4DS messages.
    
    If you want to send a service message, use L{sendServiceMessage}.
    
    If you want to send a control message, use L{sendControlMessage}.
    
    L{sendG4dsMessage} should normally not be used from the outside, it is used from the above two
    functions instead.
    """
    def __init__(self):
        """
        Yet empty Constructor.
        """
        pass
    
    def sendServiceMessage(self, endpointid, serviceid, servicename, message, refid = None):
        """
        Assembles a G4DS service message with the given content and sends it off.
        
        In fact, the L{messagewrapper.MessageWrapper} is used for wrapping the given message
        into a valid G4DS control message. Afterwards, the message is passed on to the
        function L{sendG4dsMessage} for final delivery.
        
        @param endpointid: Id of the Endpoint for this message. Passed to L{sendG4dsMessage}
        @type endpointid: C{String}
        @param serviceid: The G4DS wide unique identifier of the service for this message
        @type serviceid: C{String}
        @param servicename: The name of the service used for this message 
        @type servicename: C{String}
        @param message: The message itself (as passed from the service). May (but does does not necessarily
            need to be in XML format. Other format are processed too
        @type message: C{String}
        @param refid: An id of a previous message which shall be referenced here - passed on to L{sendG4dsMessage}
        @type refid: C{String}
        @return: Return value of L{sendG4dsMessage} - should be the message id of the sent message
        @rtype: C{String}
        """
        wrapped = getMessageWrapper().wrapServiceMessage(serviceid, servicename, message)
        return self.sendG4dsMessage(endpointid, wrapped, refid)
        
    def sendControlMessage(self, endpointid, subsystemid, subsystemname, message, refid = None):
        """
        Assembles a G4DS control message with the given content and sends it off.
        
        In fact, the L{messagewrapper.MessageWrapper} is used for wrapping the given message
        into a valid G4DS service message. Afterwards, the message is passed on to the
        function L{sendG4dsMessage} for final delivery.
        
        @param endpointid: Id of the Endpoint for this message. Passed to L{sendG4dsMessage}
        @type endpointid: C{String}
        @param subsystemid: The id of the control sub system for this message
        @type subsystemid: C{String}
        @param subsystemname: The name of the control sub system used for this message 
        @type subsystemname: C{String}
        @param message: The message itself (as passed from the control handler)
        @type message: C{String}
        @param refid: An id of a previous message which shall be referenced here - passed on to L{sendG4dsMessage}
        @type refid: C{String}
        @return: Return value of L{sendG4dsMessage} - should be the message id of the sent message
        @rtype: C{String}
        """
        wrapped = getMessageWrapper().wrapControlMessage(subsystemid, subsystemname, message)
        return self.sendG4dsMessage(endpointid, wrapped, refid)
        
        
    def sendG4dsMessage(self, endpointid, message, refid = None):
        """
        Send a message using the given protocol.
        
        The message is encyrpted first of all using the algorithm with the requested id. (In fact, for this
        matter the message is passed to the private function L{_handleSigningAndEncryption}, which will thereupon
        pass the request to the SecurityController and return the result. The encrypted result is wrapped into
        a valid G4DS message using the L{messagewrapper.MessageWrapper.wrapG4dsMessage} function.
        Finally, the result is passed to the routing engine, which will send it off using the requested
        protocol.
        
        @param endpointid: Id of the endpoint for this message. 
        @type endpointid: C{String}
        @param message: Message to be send via G4DS. Should "actually" be a service or control message
        @type message: C{String} (XML)
        @param refid: An id of a previous message which shall be referenced here
        @type refid: C{String}
        @return: ID of the message
        @rtype: C{String}
        """
        from communicationmanager import getEndpointManager
        endpoint = getEndpointManager().getEndpoint(endpointid)

        from tools import generateId, TYPE_MESSAGE
        mid = generateId(TYPE_MESSAGE)
        from config import memberid
        message, doc = getMessageWrapper().wrapG4dsPlain(message, mid, memberid, refid)
        
        message, tree, rootnode = self._handleSigningAndEncryption(message, endpoint)
        xmltext, domtree = getMessageWrapper().wrapG4dsMessage(rootnode)
        
        from routingcontroller import getRoutingEngine
##        import thread
##        thread.start_new_thread(getRoutingEngine().sendMessage, (xmltext, endpoint))
    
        getRoutingEngine().sendMessage(xmltext, endpoint)
        return mid
        
    def _handleSigningAndEncryption(self, message, endpoint):
        """
        Helper function for supporting the encryption of a message.
        
        The algorithm name is gained for the given algorithm id (from the AlgorithmManager inside
        the securitymanager module) and the message is encrypted using the SecurityController class
        in the securitycontroller module (of course using the given algorithm name). Afterwards,
        the message is passed on to the L{messagewrapper.MessageWrapper.wrapForEncryption} to make
        it a valid piece of encrypted information.
        
        @param message: Message to be encrypted and wrapped
        @type message: C{String}
        @param endpoint: Endpoint instance holding all information required about the destination
        @type endpoint: L{communicationmanager.Endpoint}
        """
        from securitymanager import getCredentialManager
        credential = getCredentialManager().getCredential(endpoint.getCredentialId())
        algName = getAlgorithmManager().getAlgorithm(credential.getAlgorithmId()).getName()
        
        from config import memberid
        communityid = endpoint.getCommunityId()
        signature = getSecurityController().signMessage(message, algName)  # let's just use the same algorithm as we used for encryption
        sigXmlString, doc, node = getMessageWrapper().wrapForSigning(message, signature, algName, memberid, communityid)
        
        ciphered = getSecurityController().encrypt(sigXmlString, credential.getKey(), algName)
        xmlString = getMessageWrapper().wrapForEncryption(ciphered, algName)
        return xmlString

# "singleton"
_globalDispatcher = None
def getGlobalDispatcher():
    """
    Singleton implementation.
    
    @return: The instance for the global dispatcher class
    @rtype: L{GlobalDispatcher}
    """
    global _globalDispatcher
    if not _globalDispatcher:
        _globalDispatcher = GlobalDispatcher()
    return _globalDispatcher

class GlobalDispatcher:
    """
    First instance for dispatching messages.
    
    Checks, whether a messae is a G4DS control message or an application message. If G4DS control message,
    it will be passed on to the ControlMessageDispatcher, in the latter case passed to the serviceintegrator.
    """
    def __init__(self):
        """
        Yet empty Constructor.
        """
        pass

    def dispatch(self, protocol, message, inbackground = 1):
        """
        Receives the raw messages from the protocol implementations and passes them
        somewhere depending on the type.
        
        Message is passed to the L{messagewrapper.MessageWrapper.unwrapG4dsMessage} function for removing
        the g4ds-"header" and gain the actual information. Afterwards, in case of an encrypted message
        it is passed to the private function L{_handleDecryptionAndValidation} which will thereupon unwrap and decrypt
        the message. Then, the message is passed and it is identified, whether there is a service or a
        control message contained. Depending on this, the content is either passed to the 
        L{g4dsconfigurationcontroller.ControlMessageDispatcher.dispatch} or to the 
        L{serviceintegrator.ServiceIntegrator.dispatch}.
        
        @param protocol: Protocol as identified for the incoming message
        @type protocol: C{String}
        @param message: String representation of the XML message
        @type message: C{String}
        """
        if inbackground:
            import thread
            thread.start_new_thread(self.dispatch,(protocol, message, 0))
            return
        
        from errorhandling import G4dsException
        try:
            from g4dslogging import getDefaultLogger, COMMUNICATION_INCOMING_MSG, COMMUNICATION_INCOMING_MSG_DETAILS
            getDefaultLogger().newMessage(COMMUNICATION_INCOMING_MSG, 'New incoming message')
            firstmessage = message
            message, rootnode = getMessageWrapper().unwrapG4dsMessage(message)
            
            message, senderidDec, communityid = self._handleDecryptionAndValidation(message, protocol)
            
            message, mid, senderid, refid = getMessageWrapper().unwrapG4dsPlain(message)
            getDefaultLogger().newMessage(COMMUNICATION_INCOMING_MSG_DETAILS, '-- MSG ID %s | SENDER %s' %(mid, senderid))
            getDefaultLogger().newMessage(COMMUNICATION_INCOMING_MSG_DETAILS, '-- Size of msg (brutto | netto): %d | %d Bytes' %(len(firstmessage), len(message)))
            getMessageContextController().addMessage(mid)
            getMessageContextController().addValue(mid, 'refid', refid)
            getMessageContextController().addValue(mid, 'senderid', senderid)
            getMessageContextController().addValue(mid, 'communityid', communityid)
            
            root = xml.dom.ext.reader.Sax2.FromXml(message)
    
            childnode = root.childNodes[1]
            if childnode.nodeType == Node.ELEMENT_NODE:
                stio = StringIO()
                xml.dom.ext.PrettyPrint(childnode, stio)
                xmlSubTreeString = stio.getvalue()
                stio.close()
                
                if childnode.nodeName == xmlconfig.g4ds_control_node:
                    id, name, data = getMessageWrapper().unwrapControlMessage(xmlSubTreeString)
                    getControlMessageDispatcher().dispatch(childnode, id, name, data, mid)
                    
                if childnode.nodeName == xmlconfig.g4ds_service_node:
                    id, name, data = getMessageWrapper().unwrapServiceMessage(xmlSubTreeString)
                    getServiceIntegrator().dispatch(id, name, data, mid)
        except G4dsException, msg:
            from g4dslogging import getDefaultLogger, COMMUNICATION_INCOMING_ERROR
            getDefaultLogger().newMessage(COMMUNICATION_INCOMING_ERROR, msg)
        except Exception, msg:
            from g4dslogging import getDefaultLogger, COMMUNICATION_INCOMING_ERROR
            getDefaultLogger().newMessage(COMMUNICATION_INCOMING_ERROR, 'Global dispatching - unknown Error: %s' %(msg))

    def _handleDecryptionAndValidation(self, message, protocolname):
        """
        Helper function for supporting the decryption of the message.
        
        The passed message is passed to the L{messagewrapper.MessageWrapper.unwrapForDecryption}
        for removing the encryption "header" and gaining the name of the algorithm and the 
        cipher text. Afterwards, the function decrypt in the securitycontroller is invoked
        and the result is returned.
        
        @return: Result of the L{securitycontroller.SecurityController.decrypt}
        @rtype: C{String}
        """
        alg, data = getMessageWrapper().unwrapForDecryption(message)
        data = getSecurityController().decrypt(data, alg)
        algName, memberid, communityid, data, signature = getMessageWrapper().unwrapForValidation(data)
        
        from communicationmanager import getEndpointManager
        from errorhandling import G4dsDependencyException, G4dsCommunicationException
        from g4dslogging import getDefaultLogger, COMMUNICATION_INCOMING_NO_ENDPOINT
        from securitymanager import getCredentialManager, getAlgorithmManager

        try:
            endpoint = getEndpointManager().findEndpoint(memberid, communityid, protocolname, algName)
            credential = getCredentialManager().getCredential(endpoint.getCredentialId())
            if not credential:
                getDefaultLogger().newMessage(COMMUNICATION_INCOMING_NO_ENDPOINT, 'No credential found for the sender of the incoming message - validation aborted.')
                raise G4dsCommunicationException('No credential found for the sender of the incoming message - validation aborted.')
            key = credential.getKey()
            
            if not getSecurityController().validate(data, signature, key, algName):
                raise G4dsCommunicationException('Signature not valid for this message.')
            return data, memberid, communityid
        except G4dsDependencyException, msg:
            getDefaultLogger().newMessage(COMMUNICATION_INCOMING_NO_ENDPOINT, 'Src Enpoint Detemination: %s - attempt key determination' %(msg))
            # we have to carry on here - if the message is routed; the end-to-end message integrity must still be ensured; however - both members are not in the 
            # same community; hence - the receiver might not know about the endpoints of the sender; however, for this approach it's compulsary, that the public
            # key is known
            creds = getCredentialManager().getCredentialsForMember(memberid)
            for cred in creds:
                # well, problem here - the sender might have several keys of the same algorithm - no chance to get around checking them all here
                if getAlgorithmManager().getAlgorithm(cred.getAlgorithmId()).getName() == algName:
                    key = cred.getKey()
                    if getSecurityController().validate(data, signature, key, algName):
                        return data, memberid, communityid
            # ohoh - looks like this message is not valied :(
            getDefaultLogger().newMessage(COMMUNICATION_INCOMING_NO_ENDPOINT, 'Src Enpoint Detemination: manual key search not sucessful.')
            raise G4dsCommunicationException('Signature not valid for the incoming message.')
        

# "singleton"
_messageContextController = None
def getMessageContextController():
    """
    Singleton implementation.
    
    @return: The instance for the message context controller
    @rtype: L{MessageContextController}
    """
    global _messageContextController
    if not _messageContextController:
        _messageContextController = MessageContextController()
    return _messageContextController
        
class MessageContextController:
    """
    Stores all information about incoming messages.
    
    Incoming messages are unwrapped at many several locations within the G4DS module tree. In order to
    avoid passing this information from one function to another, a message context may be created for this
    message. The key is always the message id - this way, only the message id needs to be passed and all
    remaining information may be accessed using the id.
    """
    def __init__(self):
        """
        Initialises the dictionary for messages.
        """
        self._messages = {}
        
    def addMessage(self, messageid):
        """
        Initialises a new context for a certain message.
        """
        self._messages[messageid] = {}
        self._messages[messageid]['senderid'] = None
        self._messages[messageid]['refid'] = None
        
    def addValue(self, messageid, key, value):
        """
        Adds a value to the context of the message with the given id.
        
        @param messageid: Id of the message in the first place
        @type messageid: C{String}
        @param key: Key for this value (must be used for requesting the content later on)
        @type key: C{String}
        @param value: The value to be stored in the context for this message behind the given key
        @type value: any
        """
        self._messages[messageid][key] = value
        
    def getValue(self, messageid, key):
        """
        Requests a value for a certain message stored behind a certain key.
        
        @param messageid: Id of the message in the first place
        @type messageid: C{String}
        @param key: Key for the requested value 
        @type key: C{String}
        @return: The value behind the key
        @rtype: any
        
        @note: If there is no value behind the given key, an KeyError will be produced.
        """
        return self._messages[messageid][key]
        
    def deleteMessage(self, messageid):
        """
        Deletes the context for the given message id.
        
        @param messageid: ID of the message in the first place.
        @type messageid: C{String}
        """
        del self._messages[messageid]
