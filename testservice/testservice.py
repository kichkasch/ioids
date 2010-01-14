"""
Simple Test Service for G4DS

Grid for Digital Security (G4DS)

All it does is waiting for user input and sending it to the requested destination member.

@author: Michael Pilgermann
@contact: mailto:mpilgerm@glam.ac.uk
@license: GPL (General Public License)
"""

import g4ds.g4dsservice
from g4ds.errorhandling import G4dsException

class TestService:
    """
    Class, which holds the callback for incoming messages and the functions user input for processing
    messages to be passed on to the g4ds system.
    """
    
    def __init__(self, serviceid = 'S177696'):
        """
        Connects against G4ds backend.
        """
        self._gs = g4ds.g4dsservice.G4dsService()
        try:
            self._gs.connect(serviceid, None, 'key', callback = self.callback)
            self.userInput()
        except G4dsException, msg:
            print "Could not connect against G4DS: %s" %msg
        
    def callback(self, msg):
        """
        Callback for incoming messages  from g4ds.
        
        Just prints the msg to std out.
        """
        print "\n\tReceived: %s" %(msg)
        
    
    def userInput(self):
        """
        Request user input and send it over.
        """
        
        while 1:
            msg = raw_input('Message (q to quit): ')
            if msg == 'q':
                self._gs.disconnect()
                break
            receiver = raw_input('Member ID of receiver: ')
            try:
                self._gs.sendMessage(receiver, None, msg, actionstring='chat.send.message')
            except G4dsException, msg:
                print "\nSomething went wrong here - error message from G4DS: %s"
                
                
if __name__ == "__main__":
    import sys      # this way you can specify a service id on the prompt - testing several services
    if len(sys.argv) > 1:
        ts = TestService(sys.argv[1])
    else:
        ts = TestService()
