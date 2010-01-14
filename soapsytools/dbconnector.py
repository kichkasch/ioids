"""
Connect against database backend.

Tools for SoapSy

Yes, we could put something very sophisticated here in order to allow integration with
a variety of datbases; however, for reasons of simplicity I decided to just put the code 
for connecting against the XML RPC database here.

@author: Michael Pilgermann
@contact: mailto:mpilgerm@glam.ac.uk
@license: GPL (General Public License)
"""

from SOAPpy import *

# constants for db operator strings
OPERATOR_LESS_THEN = 'lt'
OPERATOR_LESS_THEN_OR_EQUAL = 'ltq'
OPERATOR_GREATER_THEN = 'gt'
OPERATOR_GREATER_THEN_OR_EQUAL = 'gtq'
OPERATOR_EQUAL = 'eq'
OPERATOR_NOT_EQUAL = 'neq'
OPERATOR_LIKE = 'lk'
OPERATOR_STARTING_LIKE = 'slk'
OPERATOR_ENDING_LIKE = 'elk'
OPERATOR_NOT_LIKE = 'nlk'
OPERATOR_NOT_STARTING_LIKE = 'nslk'
OPERATOR_NOT_ENDING_LIKE = 'nelk'

class DBConnector:
    """
    Standard DB connector - work on XML RPC database.
    """

    def __init__(self, soapServerUrl):
        """
        Sets the parameters for the later db connections.
        
        Most of the settings are taken from the global config file.
        """
        from errorhandling import SoapsyToolsException
                        
        self._serverUrl = soapServerUrl
        self._server = None
        
    def connect(self):
        """
        Establishes the connection to the XML SOAP RPC database.
        """
        from errorhandling import SoapsyToolsException
        
        try:
            self._server = SOAPProxy(self._serverUrl)
        except Exception, msg:
            raise SoapsyToolsException('XML RPC database not available - error: %s' %(msg))
            
    def disconnect(self):
        """
        Disconnects from the XML RPC database.
        """
        self._server = None
            
    def _performRequest(self, xmlRequest):
        """
        Performs the final request to the XML RPC database.
        """
        from errorhandling import SoapsyToolsException

        # had to take this off since it is causing funny errors
##        if self._server:
##            raise SoapsyToolsException('Connection to XML RPC database not established. Please connect first!')
            
        reply = self._server.getDocument(xmlRequest)
        return reply
        
    def testConnection(self):
        """
        Checks XML RPC database connectivity.
        """
        from errorhandling import SoapsyToolsException
        import socket
        
        # just any can go here - we should just make sure that the given relation is really available in the database
        request = "<RELATIONS command='SELECT'><REL name='computer' val='all'/></RELATIONS>"
        try:
            reply = self._performRequest(request)
        except socket.error, msg:
            raise SoapsyToolsException("Connection not available: %s" %(msg))

            
    def getEvents(self, conditions = []):
        """
        Collects available events from the database.
        
        The result is returned in a format mixed by lists and dictionaries.
        """
        from messagewrapper import getXMLDBWrapper
        xml = getXMLDBWrapper().wrapSelect('event', 'all', conditions)
        result = self._performRequest(xml)
        #print "\n>\n%s\n<\n" %result
        no, resolved = getXMLDBWrapper().parseSelectReply(result)
        return resolved
        
    def getEventsFromEventID(self, minEventId):
        """
        Returns all events with event id greater then the given one.
        """
        return self.getEvents([['event_id', OPERATOR_GREATER_THEN_OR_EQUAL, str(minEventId)]])
                
    def insertEvent(self, event):
        """
        Insert a new event.
        """
        from messagewrapper import getXMLDBWrapper
        xml = getXMLDBWrapper().wrapInsert(event[0], event[1], event[2])
        result = self._performRequest(xml)
##        print result
        decode = getXMLDBWrapper().parseInsertReply(result)
##        print "Result - primary key: %s " %(decode[0][2])
        return decode[0][2][1:len(decode[0][2])-1]  # don't ask  -hehe - it's removing the apostrophes ;) nice, isn't it??? 

        
    ##
    ## Functions for getting all the details of events
    ##
    def _getSomething(self, relationName, primKeyName, primKey):
        from dataengine_tools import getPreXMLDictCreator
        from messagewrapper import getXMLDBWrapper
        xml = getXMLDBWrapper().wrapSelect(relationName, 'all', [[primKeyName, OPERATOR_EQUAL, primKey]])
        result = self._performRequest(xml)
        no, resolved = getXMLDBWrapper().parseSelectReply(result)
        myEntry = resolved[0]['relations'][0]['attributes']
        return myEntry
    

    def getComputerType(self, computer_type_id, full =1):
        from dataengine_tools import getPreXMLDictCreator
        myEntry = self._getSomething('comp_type', 'comp_type_id', computer_type_id)
        return getPreXMLDictCreator().createComputerTypeEntry(myEntry)
        
    def getComputer(self, computer_id, full  = 1):
        from dataengine_tools import getPreXMLDictCreator
        myEntry = self._getSomething('computer', 'comp_id', computer_id)
        
        if full and myEntry['comp_type_id'] != 'None':
            computerType = self.getComputerType(myEntry['comp_type_id'], 1)
        else:
            computerType = None
        return getPreXMLDictCreator().createComputerEntry(myEntry, computerType)
    
    def getUserGroup(self, user_group_id, full = 1):
        from dataengine_tools import getPreXMLDictCreator
        myEntry = self._getSomething('usr_group', 'usr_group_id', user_group_id)
        return getPreXMLDictCreator().createUserGroupEntry(myEntry)

    def getUser(self, user_id, full  = 1):
        from dataengine_tools import getPreXMLDictCreator
        myEntry = self._getSomething('usr', 'usr_id', user_id)
        
        if full and myEntry['usr_group_id'] != 'None':
            userGroup = self.getUserGroup(myEntry['usr_group_id'], 1)
        else:
            userGroup = None
        return getPreXMLDictCreator().createUserEntry(myEntry, userGroup)

    def getProcessType(self, process_type_id, full =1):
        from dataengine_tools import getPreXMLDictCreator
        myEntry = self._getSomething('prcss_type', 'prcss_type_id', process_type_id)
        return getPreXMLDictCreator().createProcessTypeEntry(myEntry)

    def getProcessName(self, process_name_id, full =1):
        from dataengine_tools import getPreXMLDictCreator
        myEntry = self._getSomething('prcss_name', 'prcss_name_id', process_name_id)
        return getPreXMLDictCreator().createProcessNameEntry(myEntry)

    def getProcess(self, process_id, full  = 1):
        from dataengine_tools import getPreXMLDictCreator
        myEntry = self._getSomething('process', 'prcss_id', process_id)
        
        user = None
        processType = None
        processName = None
        if full:
            if myEntry['usr_id'] != 'None':
                user = self.getUser(myEntry['usr_id'], 1)
            if myEntry['prcss_type_id'] != 'None':
                processType = self.getProcessType(myEntry['prcss_type_id'],1)
            if myEntry['prcss_name_id'] != 'None':
                processName = self.getProcessName(myEntry['prcss_name_id'],1)
        return getPreXMLDictCreator().createProcessEntry(myEntry, processType, processName, user)
    
    def getAgentClass(self, agent_class_id, full =1):
        from dataengine_tools import getPreXMLDictCreator
        myEntry = self._getSomething('agent_class', 'agent_class_id', agent_class_id)
        return getPreXMLDictCreator().createAgentClassEntry(myEntry)

    def getAgent(self, agent_id, full  = 1):
        from dataengine_tools import getPreXMLDictCreator
        myEntry = self._getSomething('agent', 'agent_id', agent_id)
        
        agentClass = None
        computer = None
        process = None
        if full:
            if myEntry['agent_class_id'] != 'None':
                agentClass = self.getAgentClass(myEntry['agent_class_id'], 1)
            if myEntry['comp_id'] != 'None':
                computer = self.getComputer(myEntry['comp_id'],1)
            if myEntry['prcss_id'] != 'None':
                process = self.getProcess(myEntry['prcss_id'],1)
        return getPreXMLDictCreator().createAgentEntry(myEntry, agentClass, computer, process)
 
    def getObserver(self, observer_id, full = 1):
        from dataengine_tools import getPreXMLDictCreator
        myEntry = self._getSomething('observer', 'obsrv_id', observer_id)
        
        agent = None
        if full:
            if myEntry['agent_id'] != 'None':
                agent = self.getAgent(myEntry['agent_id'],1)
        return getPreXMLDictCreator().createObserverEntry(myEntry, agent)

    def getReporter(self, reporter_id, full = 1):
        from dataengine_tools import getPreXMLDictCreator
        myEntry = self._getSomething('reporter', 'rprt_id', reporter_id)
        
        agent = None
        if full:
            if myEntry['agent_id'] != 'None':
                agent = self.getAgent(myEntry['agent_id'],1)
        return getPreXMLDictCreator().createReporterEntry(myEntry, agent)
    
    def getSource(self, source_id, full = 1):
        from dataengine_tools import getPreXMLDictCreator
        myEntry = self._getSomething('source', 'src_id', source_id)
        
        agent = None
        if full:
            if myEntry['agent_id'] != 'None':
                agent = self.getAgent(myEntry['agent_id'],1)
        return getPreXMLDictCreator().createSourceEntry(myEntry, agent)

    def getDestination(self, destination_id, full = 1):
        from dataengine_tools import getPreXMLDictCreator
        myEntry = self._getSomething('destination', 'dstn_id', destination_id)
        
        agent = None
        if full:
            if myEntry['agent_id'] != 'None':
                agent = self.getAgent(myEntry['agent_id'],1)
        return getPreXMLDictCreator().createDestinationEntry(myEntry, agent)
    
    def getEncoding(self, encoding_id, full = 1):
        from dataengine_tools import getPreXMLDictCreator
        myEntry = self._getSomething('encoding', 'encoding_id', encoding_id)
        return getPreXMLDictCreator().createEncodingEntry(myEntry)
        
    def getData(self, data_id, full = 1):
        from dataengine_tools import getPreXMLDictCreator
        myEntry = self._getSomething('data', 'data_id', data_id)
        
        encoding = None
        if full:
            if myEntry['encoding_id'] != 'None':
                encoding = self.getEncoding(myEntry['encoding_id'],1)
        return getPreXMLDictCreator().createDataEntry(myEntry, encoding)
    
    def getEventType(self, event_type_id, full = 1):
        from dataengine_tools import getPreXMLDictCreator
        myEntry = self._getSomething('event_type', 'event_type_id', event_type_id)
        return getPreXMLDictCreator().createEventTypeEntry(myEntry)
        
    def getEvent(self, event_id, full = 1):
        from dataengine_tools import getPreXMLDictCreator
        myEntry = self._getSomething('event', 'event_id', event_id)
        
        observer = None
        reporter = None
        source = None
        destination = None
        data = None
        eventType = None
        if full:
            if myEntry['obsrv_id'] != 'None':
                observer = self.getObserver(myEntry['obsrv_id'],1)
            if myEntry['rprt_id'] != 'None':
                reporter = self.getReporter(myEntry['rprt_id'],1)
            if myEntry['src_id'] != 'None':
                source = self.getSource(myEntry['src_id'],1)
            if myEntry['dstn_id'] != 'None':
                destination = self.getDestination(myEntry['dstn_id'],1)
            if myEntry['data_id'] != 'None':
                data = self.getData(myEntry['data_id'],1)
            if myEntry['event_type_id'] != 'None':
                eventType = self.getEventType(myEntry['event_type_id'])
            
        return getPreXMLDictCreator().createEventEntry(myEntry, observer, reporter, source, destination, data, eventType)
        
        
