"""
Manages the implementations for the different protocols.

Grid for Digital Security (G4DS)

Responsible for invoking the communcations and making the network
servers listening and so on.


@author: Michael Pilgermann
@contact: mailto:mpilgerm@glam.ac.uk
@license: GPL (General Public License)

@var _protocolController: For singleton implementation
@type _protocolController: L{ProtocolController}
"""

import protocols.config
import protocols.protocolinterface

# "singleton"
_protocolController = None
def getProtocolController():
    """
    Singleton Implementation.
    
    Returns the instance to the ProtocolController class.
    """
    global _protocolController
    if not _protocolController:
        _protocolController = ProtocolController()
    return _protocolController
    
class ProtocolController:
    """
    Maintains a dictionary with all available protocols.
    
    @ivar _protocols: Dictionary of protocols implemented and available on this node
    @type _protocols: C{Dict} of {ProtocolImplementationModules}
    @ivar _openprotocols: Protocols, which are currently in use; hence, which ones are listening
    @type _openprotocols: C{Dict} of {ProtocolImplementations}
    @ivar _defaultprotocol: Name of the protocol to be used whenever none is defined
    @type _defaultprotocol: C{String}
    """
    def __init__(self, positiveList = None, negativeList = None, defaultProtocol = protocols.config.default_protocol):
        """
        Initialises the Protocol controller. 
        
        The list of protocols is loaded from the config file for protocols. 
        
        If L{positiveList} is given, only the protocols defined in there will be used. If not positiveList
        is given, the negativeList will be checked. Protocols given in there will be skipped when intialising
        the protocols. If neither of the two lists is given, all protocols defined in the config file
        for protocols will be initialised and activated.
        
        @param positiveList: List of names of protocols to initialise
        @type positiveList: C{List} of C{String}
        @param negativeList: List of names of protocols to skip for initialisation
        @type negativeList: C{List} of C{String}
        @param defaultProtocol: Name of protocol to use if none is specified
        @type defaultProtocol: C{String}
        """
        self._protocols = protocols.config.protocols
        self._openprotocols = {}
        self._defaultprotocol = defaultProtocol
        if positiveList:
            for protocolName in positiveList:
                protocolModule = self._protocols[protocolName]
                instance = protocolModule.ProtocolImplementation()
                self._openprotocols[instance.getName()] = instance
                instance.listen(Dispatcher().dispatch)
        else:
            if not negativeList:
                negativeList = []
            for protocolName in self._protocols.keys():
                try:
                    negativeList.index(protocolName)
                except ValueError:
                    # here we go if the protocolName is not in the negativeList
                    protocolModule = self._protocols[protocolName]
                    instance = protocolModule.ProtocolImplementation()
                    self._openprotocols[instance.getName()] = instance
                    instance.listen(Dispatcher().dispatch)

    def __str__(self):
        """
        Some basic information about the object
        """
        return "Protocolcontroller. %d|%d Protocols." %(len(self._openprotocols), len(self._protocols))
                    
        
    def getAvailableProtocols(self):
        """
        Returns a list of names of available protocols.
        
        @return: List of names of protocols
        @rtype: C{List} of C{String}
        """
        return self._protocols.keys()
        
    def getOpenProtocols(self):
        """
        Returns a list of names of protocols, which are currently initialised on this node.

        @return: List of names of protocols
        @rtype: C{List} of C{String}
        """
        return self._openprotocols.keys()
        
    def getOpenProtocol(self, name):
        """
        Provides an instance of the protocol with the name requested.
        
        @return: Reference to protocol implementation with the given name
        @rtype: L{protocols.protocolinterface.ProtocolInterface}
        """
        return self._openprotocols[name]

    def shutdownAllListeners(self):
        for x in self.getOpenProtocols():
            prot = self.getOpenProtocol(x)
            prot.shutdown()
        
class Dispatcher:
    """
    Dispatcher so be registered with the protocols.
    
    Only in charge to pass any incoming message to the global Dispatcher.
    """
    
    def __init__(self):
        """
        Yet empty Constructor.
        """
        pass
        
    def dispatch(self, protocol, message):
        """
        Passes messages to the GlobalDispatcher in the messagehandler module.
        
        @param protocol: Name of the protocol, which has been identified as carrier for the message
        @type protocol: C{String}
        @param message: Message itself
        @type message: C{String}
        """
        from messagehandler import getGlobalDispatcher

        getGlobalDispatcher().dispatch(protocol, message)
