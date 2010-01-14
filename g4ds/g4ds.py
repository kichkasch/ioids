"""
Main module for G4DS

Grid for Digital Security (G4DS)

You cannot start the application directly since it is to be used as kind of a library.

Startup the G4DS listener first. It will listen for incoming connections on fifos. Import the module
G4dsService in your application and you will be able to connect to G4DS.

Check README in the G4DS folder for more information.

@author: Michael Pilgermann
@contact: mailto:mpilgerm@glam.ac.uk
@license: GPL (General Public License)
"""

LOCATION_CONF_FILE = '/etc/g4ds.conf'

class G4DS:
    """
    Primary interface for services to communicate with G4DS.
    """

    def __init__(self):
        """
        Yet empty Constructor.
        """
        pass
        
    def __str__(self):
        """
        Some basic information about the object
        """
        return "G4DS - Grid for Digital Security"
        

## ########################################
##
## Starting up and closing down
##

    def _distributeOneConf(self, conf, section, destDict):
        for option in conf.options(section):
            value = conf.get(section, option)
            # determine type
            if value[0] == "'" or value[0] == '"': # string
                value = str(value[1:len(value)-1])
            elif value[0] == "[":   # array
                tmp = str(value[1:len(value)-1])    # get rid of the brackets
                value = []
                for x in tmp.split(","):
                    x = x.strip()
                    x = str(x[1:len(x)-1])  # only strings here
                    value.append(x)
            elif value[0] == "{":   # dict
                tmp = str(value[1:len(value)-1])
                value = {}
                for x in tmp.split(";"):
                    x = x.strip()
                    x = str(x[1:len(x)-1])
                    y, z = x.split(",")
                    y = y.strip()
                    y = str(y[1:len(y) -1 ])
                    z = z.strip()
                    z = str(z[1:len(z) - 1])
                    value[y] = z
            else:  # int - or variable .... - try variable first ...
                try:
                    value = int(value)
                except ValueError, msg:
                    value = str(value)
            
            destDict[option] = value        # all in lower case
            destDict[option.upper()] = value       # all in upper case

    def loadConfigurations(self):
        from maintainlib import _printAction, _finishActionLine, SUCESS_POS, SUCESS_NEG, SUCESS_SKIP
        _printAction(2, "Configuration file: %s" %(LOCATION_CONF_FILE))
        import ConfigParser
        import string
        
        conf = ConfigParser.ConfigParser()
        conf.read(LOCATION_CONF_FILE)

        import config
        self._distributeOneConf(conf, 'global', config.__dict__)
        
        import protocols.config
        self._distributeOneConf(conf, 'protocols', protocols.config.__dict__)

        _finishActionLine()
        
    def startup(self):
        """
        Starts up G4DS.
       
        Regarding to the settings in the configuration files the connections are established and
        the database is loaded.
        """
        from maintainlib import _printAction, _finishActionLine, SUCESS_POS, SUCESS_NEG, SUCESS_SKIP
        from errorhandling import G4dsException 
        
        print "\n" + "*" * 90
        _printAction(0, "Starting up G4DS",1)

        _printAction(1, "Loading Configuration", 1)
        self.loadConfigurations()        # initialise with their private keys from the personal credential manager
##        _finishActionLine()        

        _printAction(1, "Start G4DS logging")
        from g4dslogging import getDefaultLogger
        try:
            getDefaultLogger()
            _finishActionLine()
        except G4dsException, msg:
            _finishActionLine(SUCESS_NEG)
            _printAction(2, str(msg))
            _finishActionLine(SUCESS_NEG)
            
        _printAction(1, "Loading Keys")
        from algorithmcontroller import getAlgorithmController
        getAlgorithmController().loadKeys()        # initialise with their private keys from the personal credential manager
        _finishActionLine()        

        _printAction(1, "Start up protocols and listeners")
        from protocolcontroller import getProtocolController
        import socket 
        try:
            getProtocolController()                     # start listening on all endpoints
            _finishActionLine()
        except socket.error, msg:
            _finishActionLine(SUCESS_NEG)
            _printAction(2, str(msg))
            _finishActionLine(SUCESS_NEG)            
            
        _printAction(1, "Load up permission policies into memory")
        from authorisationcontroller import getAuthorisationController
##        getAuthorisationController()
        try:
            getAuthorisationController()                     # start listening on all endpoints
            _finishActionLine()
##        except Exception, msg:
        except KeyError, msg:
            _finishActionLine(SUCESS_NEG)
            _printAction(2, str(msg))
            _finishActionLine(SUCESS_NEG)            

        _printAction(1, "Loading routing table into memory")
        from routingtablemanager import getRoutingTableManager
        getRoutingTableManager()
        _finishActionLine()

        _printAction(1, "Enable dynamic routing")
        from dynamicrouting import getRoutingTableUpdater
        from errorhandling import G4dsRuntimeException
        try:
            getRoutingTableUpdater()
            _finishActionLine()
        except G4dsRuntimeException, msg:
            _finishActionLine(SUCESS_SKIP)
        
        _printAction(0, "G4DS running")
        _finishActionLine()
        print "*" * 90 + "\n"
                
    def shutdown(self):
        """
        Shutdown G4DS.
        
        Connections are all shutdown (especially the network servers waiting for incoming connections) and 
        eventual dynamic data is written back to the database.
        """
        from maintainlib import _printAction, _finishActionLine, SUCESS_POS, SUCESS_NEG, SUCESS_SKIP
        from errorhandling import G4dsRuntimeException
        print "\n" + "*" * 90
        _printAction (0, "Shutting down G4DS ...",1)
        
        _printAction(1, "Shutting down dynamic routing")
        from dynamicrouting import getRoutingTableUpdater
        try:
            getRoutingTableUpdater().shutdown()
            _finishActionLine()
        except G4dsRuntimeException, msg:
            _finishActionLine(SUCESS_SKIP)

        _printAction(1, "Shutting down Listeners")
        from protocolcontroller import getProtocolController
        import socket
        try:
            getProtocolController().shutdownAllListeners()
            _finishActionLine()
        except socket.error, msg:
            _finishActionLine(SUCESS_NEG)
            _printAction(2, str(msg))
            _finishActionLine(SUCESS_NEG)            
        _printAction (1,"Shutting down Logging")
        from g4dslogging import getDefaultLogger
        getDefaultLogger().closedown()
        _finishActionLine()
        _printAction(0, "Shutdown complete")
        _finishActionLine()
        print "*" * 90 + "\n"
    
## ########################################
##
## Interaction with G4ds
##
    def registerClient(self, serviceid, clientcallback):
        """
        A new client has connected through C/S facilities.
        
        Let's go and register it with the service integrator.
        """
        from serviceintegrator import getServiceIntegrator
        getServiceIntegrator().registerClient(serviceid, clientcallback)
        
    def unregisterClient(self, serviceid):
        """
        Disconnects a client from a certain service.
        """
        from serviceintegrator import getServiceIntegrator
        getServiceIntegrator().unregisterClient(serviceid)
        
    def newMessage(self, serviceid, destinationMember, destinationCommunity, message):
        """
        Sends a new message through the service integrator.
        """
        from serviceintegrator import getServiceIntegrator
        getServiceIntegrator().sendMessage(destinationMember, serviceid, 'test service', message, destinationCommunity)
        
    
## ########################################
##
## Tell them, how to integrate with g4ds
##
    
if __name__ == "__main__":
    print "\nError!\nYou can't run the G4DS standalone."
    print "You rather have to call it from you application (or so called service)"
    print "as kind of a library.\n"
    print "Start first the G4dsListener (an init script is provided)."
    print "Import the G4dsService class from g4dsservice module from the g4ds package and initialise"
    print "the G4ds. It will be running in background (new thread) then until you shut down.\n"
    print "Example:\n"
    print "\t... your app stuff ...\n"
    print "\tfrom g4ds.g4dsservice import G4dsService"
    print "\tg4dsInstance = G4dsService()"
    print "\tg4dsInstance.connect(...)     # here we connect against the backend process"
    print "\n\t... your app stuff involving G4DS ...\n"
    print "\tg4dsInstance.disconnect()      # allow the backend to clean up everything \n"
    print "Have a look into the readme file inside the G4DS directory for more information."
