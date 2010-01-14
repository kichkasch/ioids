"""
Main module for IOIDS

Inter-Organisational Intrusion Detection System (IOIDS)

Check README in the IOIDS folder for more information.

@author: Michael Pilgermann
@contact: mailto:mpilgerm@glam.ac.uk
@license: GPL (General Public License)
"""

class IOIDS:

    def __init__(self):
        """
        Registers closing down signals.
        """
        pass
            
    def __str__(self):
        """
        Some basic information about the object.
        """
        return "IOIDS - Inter-Organisational Intrusion Detection System"

        
    def startup(self):
        """
        Start required listeners and services.
        
        Also connects against G4DS.
        """
        from tools import printAction, finishActionLine, SUCESS_POS, SUCESS_NEG, SUCESS_SKIP
        from errorhandling import IoidsException
        
        print "\n" + "*" * 90
        printAction(0, "Starting up IOIDS",1)
        
        printAction(1, "Start IOIDS logging")
        from ioidslogging import getDefaultLogger
        try:
            getDefaultLogger()
            finishActionLine()
        except IoidsException, msg:
            finishActionLine(SUCESS_NEG)
            printAction(2, str(msg))
            finishActionLine(SUCESS_NEG)
            
        printAction(1, "Loading G4DS Key")
        try:
            from config import LOCATION_PRIVATE_KEY
            file = open(LOCATION_PRIVATE_KEY)
            file.close()
            finishActionLine()       
        except IOError, msg:
            finishActionLine(SUCESS_NEG)
            printAction(2, "Reported error: %s" %(msg), 1)
            raise IoidsException("Could not load key for G4DS connection.")
            
        printAction(1, "Connect against database backend")
        try:
            from dbconnector import getDBConnector
            getDBConnector().connect()
            finishActionLine()       
            printAction(2, "Testing connection")
            getDBConnector().testConnection()
            finishActionLine()
        except Exception, msg:
            finishActionLine(SUCESS_NEG)
            printAction(2, str(msg))
            finishActionLine(SUCESS_NEG)
            raise IoidsException("Could not establish connection to database backend.")

        printAction(1, "Connect against G4DS")
        try:
            from g4dsconnector import getG4dsConnector
            getG4dsConnector().connect()
            finishActionLine()       
        except IoidsException, msg:
            finishActionLine(SUCESS_NEG)
            printAction(2, str(msg))
            finishActionLine(SUCESS_NEG)
            raise IoidsException("Could not establish G4DS connection.")
            
        printAction(1, "Loading policies into memory")
        try:
            from policyengine import getPolicyEngine
            getPolicyEngine().startup()
            finishActionLine()
        except Exception, msg:
            finishActionLine(SUCESS_NEG)
            printAction(2, str(msg))
            finishActionLine(SUCESS_NEG)
            raise IoidsException("Could not load ioids policies.")
            
        printAction(1, "Initialise event trigger")
        try:
            from eventtrigger import EventTrigger
            self._trigger = EventTrigger()
            self._trigger.startup()
            finishActionLine()
        except IoidsException, msg:
            finishActionLine(SUCESS_NEG)
            printAction(2, str(msg))
            finishActionLine(SUCESS_NEG)
            raise IoidsException("Could not initialise Event trigger.")

        printAction(1, "Initialise data engine")
        try:
            from dataengine import getDataEngine
            getDataEngine().startup()
            finishActionLine()
        except IoidsException, msg:
            finishActionLine(SUCESS_NEG)
            printAction(2, str(msg))
            finishActionLine(SUCESS_NEG)
            raise IoidsException("Could not initialise data engine.")

        printAction(0, "IOIDS running")
        finishActionLine()
        print "*" * 90 + "\n"

        
    def shutdown(self):
        """
        Shutdown connected listeners and services.
        """
        from tools import printAction, finishActionLine, SUCESS_POS, SUCESS_NEG, SUCESS_SKIP
        from errorhandling import IoidsException
        
        print "\n" + "*" * 90
        printAction(0, "Shutting down IOIDS",1)
        
        printAction(1, "Shutting down event trigger")
        try:
            self._trigger.shutdown()
            finishActionLine()
        except IoidsException, msg:
            finishActionLine(SUCESS_NEG)
            printAction(2, str(msg))
            finishActionLine(SUCESS_NEG)
            raise IoidsException("Could not shutdown Event trigger.")

        printAction(1, "Shutting down data engine")
        try:
            from dataengine import getDataEngine
            getDataEngine().shutdown()
            finishActionLine()
        except IoidsException, msg:
            finishActionLine(SUCESS_NEG)
            printAction(2, str(msg))
            finishActionLine(SUCESS_NEG)
            raise IoidsException("Could not shutdown data engine.")
            
        printAction(1, "Closing down connection to G4DS")
        try:
            from g4dsconnector import getG4dsConnector
            getG4dsConnector().disconnect()
            finishActionLine()
        except IoidsException, msg:
            finishActionLine(SUCESS_NEG)
            printAction(2, str(msg))
            finishActionLine(SUCESS_NEG)
        
        printAction(1, "Closing down connection to database backend")
        try:
            from dbconnector import getDBConnector
            getDBConnector().disconnect()
            finishActionLine()       
        except IoidsException, msg:
            finishActionLine(SUCESS_NEG)
            printAction(2, str(msg))
            finishActionLine(SUCESS_NEG)        
        
        printAction (1,"Shutting down Logging")
        from ioidslogging import getDefaultLogger
        getDefaultLogger().closedown()
        finishActionLine()
        
        printAction(0, "Shutdown complete")
        finishActionLine()
        print "*" * 90 + "\n"


def SignalHandler(sig, id):
    import signal
    global ioidsInst
    if sig == signal.SIGTERM or sig == signal.SIGINT:
        ioidsInst.shutdown()
        import sys
        sys.exit(1)
        
    
if __name__ == "__main__":
    """
    Let's startup a IOIDS instance here.
    """
    global ioidsInst
    from errorhandling import IoidsException
    
    ioidsInst = IOIDS()
    try:
        ioidsInst.startup()
    except IoidsException, msg:
        print "\nIOIDS could not be started - error message:\n\t%s" %(msg)
        import sys
        sys.exit(1)
    
    import signal
    signal.signal(signal.SIGTERM, SignalHandler)
    signal.signal(signal.SIGINT, SignalHandler)

    while 1:
        raw_input()             # to stop ioids, you may use CTRL-C (SIGINT); so this only runs indefinite
