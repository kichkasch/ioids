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
import thread
from socket import *

class ProtocolImplementation(ProtocolInterface):
    """
    Protocol implementation for G4DS for simple TCP socket connections.
    
    @ivar _server: TCP server instance used for listening.
    @type _server: L{socket.socket}
    @ivar _callback: Function to call whenever a new message arrives
    @type _callback: C{Function}
    """
    
    def __init__(self):
        """
        Call super constructor and initialise with name.
        """
        ProtocolInterface.__init__(self, "tcpsocket")
        
    def listen(self, callback):
        """
        Initialises the TCP socket.
        
        Parameters are loaded from the config module.
        """
        self._callback = callback
        
        address = config.tcp_local_address
        port = config.tcp_local_port
        
        self._server = socket(AF_INET, SOCK_STREAM)    # create a TCP socket
        self._server.bind((address, port))                          # bind it to the server port
        self._server.listen(0)
           
        self._alive = 1
        thread.start_new_thread(self._waitForMessages, ())
        
        return 1
        
    def _waitForMessages(self):
        """
        Sends each incoming message to the callback.
        """
        while self._alive:
            # wait for next client to connect
            connection, address = self._server.accept() # connection is a new socket
            alldata = ""
            while 1:
                data = connection.recv(1024) # receive up to 1K bytes
                if data:
                    alldata += data
                else:
                    break
            connection.close()
            self._callback(self.getName(), alldata)

    def sendMessage(self, endpoint, message):
        """
        Send a message to the endpoint given.
        
        @return: Indicates, whether the message was send sucessfully
        @rtype: C{Boolean}
        """
        addresses = endpoint.split(":")
        host = addresses[0]
        port = int(addresses[1])
        s = socket(AF_INET, SOCK_STREAM)
        s.connect((host, port)) # connect to server on the port
        sendbytes = 0
        while sendbytes < len(message):
            sendbytes += s.send(message[sendbytes:])
        return 1

    def shutdown(self):
        """
        Stop listening.
        """
        self._alive = 0
