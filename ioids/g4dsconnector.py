"""
Handles communication with G4DS communication plattform.

Inter-Organisational Intrusion Detection System (IOIDS)

@author: Michael Pilgermann
@contact: mailto:mpilgerm@glam.ac.uk
@license: GPL (General Public License)
"""

# "singleton"
_g4dsConnector = None
def getG4dsConnector():
    """
    Singleton implementation.
    """
    global _g4dsConnector
    if not _g4dsConnector:
        _g4dsConnector = G4dsConnector()
    return _g4dsConnector

class G4dsConnector:

    def __init__(self):
        """
        Initialises local variables.
        
        Perform the connection with L{connect}. Please shut down properly the connection with
        L{disconnect}.
        """
        from config import LOCATION_PRIVATE_KEY
        self._locationKey = LOCATION_PRIVATE_KEY
        
        
    def connect(self):
        """
        Establishes the connection to the G4DS backend.
        """
        from g4ds import g4dsservice
        from config import G4DS_SERVICE_ID
        from errorhandling import IoidsException
        
        self._g4ds = g4dsservice.G4dsService()
        try:
            self._g4ds.connect(G4DS_SERVICE_ID, None, self._locationKey, callback = self._incomingMessageCallback)
        except Exception, msg:
            raise IoidsException('G4DS connection failed: %s' %(msg))
        
    def disconnect(self):
        """
        Shuts down connection to G4DS.
        """
        try:
            self._g4ds.disconnect()
        except Exception, msg:
            from errorhandling import IoidsException
            raise IoidsException('G4DS connection shutdown failed: %s' %(msg))
        
    def _incomingMessageCallback(self, data, metadata):
        """
        Callback function for G4DS to receive messages from it.
        """
        from g4ds import g4dsservice
##        import cPickle as pickle
##        from StringIO import StringIO
##        st = StringIO(data)
##        data = pickle.load(st)
####        print "Received (%s): %s" %(metadata[g4dsservice.METADATA_SENDERID], data)

        print "Received sth from %s" %(metadata[g4dsservice.METADATA_SENDERID])
        getDispatcher().dispatch(data, metadata)
        
    def sendEventUpdate(self, data, receiver = None):
        self.sendMessage(data, 'ioids.write.newevent', receiver)
            
    def sendKnowledgeRequest(self, conditions, receiver):
        """
        @param conditions: List of conditions; each item a list itself (attribute name | operator indicator | value)
        @type conditions: C{List} of C{List}
        """
        condXml = None  # here we go
        self.sendMessage(condXml, 'ioids.read.events', receiver)
            
    def sendMessage(self, data, action, receiver = None):
        """
        Testing - send it off to everybody in the service :)
        """
        if not receiver:
            from config import G4DS_SERVICE_ID
            receiver = G4DS_SERVICE_ID
            
        self._g4ds.sendMessage(receiver, None, data, action)
        from ioidslogging import getDefaultLogger, G4DS_CONNECTOR_OUTGOING_MSG, G4DS_CONNECTOR_OUTGOING_MSG_DETAILS
        getDefaultLogger().newMessage(G4DS_CONNECTOR_OUTGOING_MSG, 'G4DS Outgoing message: Passed new message to %s' %(receiver))
        getDefaultLogger().newMessage(G4DS_CONNECTOR_OUTGOING_MSG_DETAILS, '-- Outgoing message details: action is %s' %(action))
        getDefaultLogger().newMessage(G4DS_CONNECTOR_OUTGOING_MSG_DETAILS, '-- Outgoing message details: data size is %s' %(len(data)))
        
        
# "singleton"
_dispatcher = None
def getDispatcher():
    """
    Singleton implementation.
    
    @return: The instance for the Dispatcher
    @rtype: L{Dispatcher}
    """
    global _dispatcher 
    if not _dispatcher:
        _dispatcher  = Dispatcher()
    return _dispatcher 
        
class Dispatcher:

    def __init__(self):
        """
        Yet empty constructor.
        """
        pass
        
    def dispatch(self, data, metadata):
        """
        First instance for incoming messages.
        """
##        print "My meta data: %s" %metadata
        from ioidslogging import getDefaultLogger, G4DS_CONNECTOR_INCOMING_MSG, G4DS_CONNECTOR_INCOMING_MSG_DETAILS
        getDefaultLogger().newMessage(G4DS_CONNECTOR_INCOMING_MSG, 'G4DS Incoming message: Received data from %s | %s' %(metadata['senderid'], metadata['communityid']))
        getDefaultLogger().newMessage(G4DS_CONNECTOR_INCOMING_MSG_DETAILS, '-- G4DS Incoming message details: action is %s ' %(metadata['actionstring']))
        getDefaultLogger().newMessage(G4DS_CONNECTOR_INCOMING_MSG_DETAILS, '-- G4DS Incoming message details: data size is %s ' %(len(data)))
        if metadata['actionstring'] == 'ioids.write.newevent':
            self._incomingMessageNewIoidsEvent(data)
        elif metadata['actionstring'] == 'ioids.read.events':
            sender = metadata['senderid']
            community = metadata['communityid']
            self._replyToKnowledgeRequest(sender, community, data)
        
        
    def _incomingMessageNewIoidsEvent(self, data):
        ioidsevent = None
        relations = []
        
        from messagewrapper import getIoidsMessageWrapper
        ioidsevent, relations = getIoidsMessageWrapper().unwrapFullIoidsEventMessage(data)
        from dataengine import getDataEngine 
        getDataEngine().newIoidsEventFromRemote(ioidsevent , relations)

        
    def _replyToKnowledgeRequest(self, sender, community, data):
        """
        @param data: XML encoded conditions
        @type data: C{String} xml encoded
        """
        pass
        
        
