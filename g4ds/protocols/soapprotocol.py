"""
SOAP communication implementation for G4DS.

Grid for Digital Security (G4DS)

Just plain text soap connections are established. Encryption should be
provided on a higher layer though.


@author: Michael Pilgermann
@contact: mailto:mpilgerm@glam.ac.uk
@license: GPL (General Public License)
"""
from protocolinterface import ProtocolInterface
import config
import SOAPpy
import thread

class ProtocolImplementation(ProtocolInterface):
    """
    Protocol implementation for G4DS for the SOAP protocol.
    
    @ivar _server: Soap server instance used for listening.
    @type _server: L{SOAPpy.SOAPServer}
    @ivar _callback: Function to call whenever a new message arrives
    @type _callback: C{Function}
    """
    
    def __init__(self):
        """
        Call super constructor and initialise with name.
        """
        ProtocolInterface.__init__(self, "soap")
        
    def listen(self, callback):
        """
        Initialises the SOAP server.
        
        Parameters are loaded from the config module.
        """
        self._callback = callback
        
        address = config.soap_local_address
        port = config.soap_local_port
        
        self._server = SOAPpy.SOAPServer((address, port))
        self._server.registerFunction(self.newMessage)
        thread.start_new_thread(self._server.serve_forever, ())
        return 1
        
    def newMessage(self, message):
        """
        Registered with the SOAP server.
        
        Sends each incoming message to the callback.
        """
        self._callback(self.getName(), message)

    def sendMessage(self, endpoint, message):
        """
        Send a message to the endpoint given.
        
        @return: Indicates, whether the message was send sucessfully
        @rtype: C{Boolean}
        """
        server = SOAPpy.SOAPProxy(endpoint)
        server.newMessage(message)
        return 1

    def shutdown(self):
        """
        Stop listening.
        """
        self._server.server_close()
