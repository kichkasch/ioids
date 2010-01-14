#!/usr/bin/python

"""
Main module for SnortDB To SoapSy logger.

SnortDB To SoapSy (SnDB2Soapsy)

@author: Michael Pilgermann
@contact: mailto:mpilgerm@glam.ac.uk
@license: GPL (General Public License)
"""

import signal, os, sys, time
from config import DAEMON_MODE
import database_action

class SnortDbSoapSy: 
    """
    Responsible for initialisation and shutdown of the whole thing.
    """

    def __init__(self):
        """
        Yet empty constructor.
        """
        signal.signal(signal.SIGTERM, self.SignalHandler)
        signal.signal(signal.SIGINT, self.SignalHandler)
        self._running = 0
        
    def startup(self):
        """
        Starts up the engine in the background.
        """
        self._running = 1
        self._dbaction = database_action.DatabaseAction()
        self._dbaction.startup()
        
    def shutdown(self):
        """
        Cleanup; shuts down the backend engine.
        """
        self._running = 0
        self._dbaction.shutdown()
        print "SnortDB2SoapSy shutdown complete."   
        sys.exit(0) 


    def SignalHandler(self, sig, id):
        """
        Called in case of receiving signals for shutting down.
        
        Calls the L{shutdown} function.
        """
        if sig == signal.SIGTERM or sig == signal.SIGINT:
            self.shutdown()        
            
            
class DummyOut:
    """
    Redirect output for daemon mode.
    """
    def __init__(self, out):
        """
        Remember a reference to the actual buffer.
        """
        self._out = out

    def write(self, msg):
        """
        Redirect message into nothing.
        """
        #self._out.write(msg)
        pass
        
    def flush(self):
        """
        Nothing.
        """
        pass
            

if __name__ == "__main__":

    import os, sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == '-d':     # daemon mode
            daemon_mode = 1
        elif sys.argv[1] == '-D':   # no daemon mode
            daemon_mode = 0
    else:
        daemon_mode = DAEMON_MODE
    
    if daemon_mode:
        try:
            pid = os.fork()
            if pid:
                os._exit(0) # kill original
        except OSError, msg:
            print "Could not start snort db to soapsy logger as deamon. Error: %s" %msg
            sys.exit(1)
        
        sys.stdout = DummyOut(sys.stdout)
        sys.stderr = DummyOut(sys.stdout)
        
    sn_soapsy = SnortDbSoapSy()
    sn_soapsy.startup()
    
