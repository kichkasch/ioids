"""
Provides the interface, each protocol implementation must implement to work with G4DS.

Grid for Digital Security (G4DS)


@author: Michael Pilgermann
@contact: mailto:mpilgerm@glam.ac.uk
@license: GPL (General Public License)
"""

class ProtocolInterface:
    """
    Provides a common interface for all implementations for protocols.
    
    @ivar _name: Name of the Implementation
    @type _name: C{String}
    """

    def __init__(self, name):
        """
        Just ot set up the name of the implementation.
        """
        self._name = name
        
    def getName(self):
        """
        GETTER
        """
        return self._name
    
    def listen(self, callback):
        """
        The implementation should listen to a certain port here.
        
        Parameters for address and the like are not required here since the implementations should load their
        settings from the config module.
        
        Any implementation must run its listener in its own thread, otherwise it
        will block the entire application / library.
        
        @param callback: Function to call whenever a new message arrives
        @type callback: Function
        @return: Indicates, whether the server was established sucessfully
        @rtype: C{Boolean}
        """
        return 0
    
    def shutdown(self):
        """
        The implementation should shut down the listener.
        
        @return: Indicates, whether the shutdown was sucessful.
        @rtype: C{Boolean}
        """
        return 0
    
    def sendMessage(self, endpoint, message):
        """
        The implementation should send the message to the endpoint.
        
        @return: Indicates, whether the message was send sucessfully
        @rtype: C{Boolean}
        """
        return 0
        
