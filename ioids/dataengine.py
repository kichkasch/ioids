"""
The heart of IOIDS - processing incoming data and takes appropriate actions.

Inter-Organisational Intrusion Detection System (IOIDS)

@author: Michael Pilgermann
@contact: mailto:mpilgerm@glam.ac.uk
@license: GPL (General Public License)
"""

# "singleton"
_dataEngine = None
def getDataEngine():
    """
    Singleton implementation.
    
    @return: The instance for the data engine
    @rtype: L{DataEngine}
    """
    global _dataEngine
    if not _dataEngine:
        _dataEngine = DataEngine()
    return _dataEngine

class DataEngine:

    def __init__(self):
        """
        Sets up the queues for incoming messages.
        """
        self._localEvents = []
        self._localIoidsEvents =[]
        self._remoteEvents = []
        self._running = 0
    
    def startup(self):
        """
        Start up the data engine in its background thread.
        """
        from config import DATA_ENGINE_PROCESSING_INTERVAL
        self._interval = DATA_ENGINE_PROCESSING_INTERVAL
        self._running = 1
        import thread
        thread.start_new_thread(self.runUntilShutdown, ())
##        self.runUntilShutdown()
        
        from ioidslogging import DATAENGINE_STATUS, getDefaultLogger
        getDefaultLogger().newMessage(DATAENGINE_STATUS, 'Data engine process started')
        
        
    def runUntilShutdown(self):
        """
        In here, all the queues are checked frequently and appropriate actions are undertaken.
        """
        from ioidslogging import DATAENGINE_PROCESSING_DETAILS, getDefaultLogger, DATAENGINE_ERROR_GENERIC
        
        import time
        time.sleep(self._interval)
        while self._running:
            try:
                getDefaultLogger().newMessage(DATAENGINE_PROCESSING_DETAILS, 'Data engine details: check my lists')
                counter = 0
                while len(self._localEvents):
                    self._processEventFromLocal(self._localEvents[0])
                    del self._localEvents[0]
                    counter += 1
                getDefaultLogger().newMessage(DATAENGINE_PROCESSING_DETAILS, '-- Data engine details: Processed %d local events.' %(counter))
                counter = 0
                while len(self._localIoidsEvents):
                    self._processIoidsEventFromLocal(self._localIoidsEvents[0])
                    del self._localIoidsEvents[0]
                    counter += 1
                getDefaultLogger().newMessage(DATAENGINE_PROCESSING_DETAILS, '-- Data engine details: Processed %d local ioids events.' %(counter))
##            except Exception, msg:
            except ValueError, msg:
                getDefaultLogger().newMessage(DATAENGINE_ERROR_GENERIC, 'Data engine ERROR: %s' %(msg))
            time.sleep(self._interval)
        
    def shutdown(self):
        """
        Shutdown the data engine thread.
        """
        self._running = 0
        from ioidslogging import DATAENGINE_STATUS, getDefaultLogger
        getDefaultLogger().newMessage(DATAENGINE_STATUS, 'Data engine process stopped')

    def _executeOneReaction(self, event, reaction):
        """
        Performs all operations as defined by the reaction part of an ioids rule.
        """
        from config import G4DS_MEMBER_ID
        from dbconnector import getDBConnector
        from errorhandling import IoidsDependencyException

        ioidsSource = G4DS_MEMBER_ID
        ioidsSender = G4DS_MEMBER_ID
        if reaction['parameters'].has_key('community'):
            if reaction['parameters']['community'] == 'Auto':
                ioidsCommunity = 'C001'     # we will do this properly soon :) TODO
            else:
                ioidsCommunity = reaction['parameters']['community']
        else:
            raise IoidsDependencyException('Community can not be determined for new local event. Looks like a mistake in ioids policy.')
        
        if reaction['parameters'].has_key('classification'):
            if reaction['parameters']['classification'] == 'Auto':
                ioidsClassificationCode = '10'     # we will do this properly soon :) TODO
            else:
                ioidsClassificationCode = reaction['parameters']['classification']
        else:
            raise IoidsDependencyException('Community can not be determined for new local event. Looks like a mistake in ioids policy.')

        ioidsTimestamp = 'now'

        
        if reaction['type'] == 'NewLocalEvent':
            if event[1].has_key('event_id'):        # we must get rid off the id - otherwise it will insert a new event again and again
                del event[1]['event_id']
            
            # create relations        
            from dataengine_tools import getPreXMLDictCreator
            from config import IOIDS_EVENT_TYPE, LOCAL_ADDRESS, LOCAL_HOSTNAME, LOCAL_MAC, LOCAL_OS, LOCAL_DOMAIN, LOCAL_COMPUTER_TYPE
            from messagewrapper import getXMLDBWrapper
            import binascii as hex
            creator = getPreXMLDictCreator()
            
            # here we create the actual event
            newEncoding = creator.createNewEncodingEntry('XML HEX')
            eventXML = getXMLDBWrapper().wrapInsert(event[0], event[1], event[2])
            encoded = hex.hexlify(eventXML)
            newData = creator.createNewDataEntry(encoded, [newEncoding])  # todo: put whole event description here
            
            newComputer = creator.createNewComputerEntry(LOCAL_HOSTNAME, LOCAL_OS, LOCAL_ADDRESS, LOCAL_MAC, LOCAL_DOMAIN, [], None, LOCAL_COMPUTER_TYPE)
            newAgent = creator.createNewAgentEntry('IOIDS', [newComputer], '2')
            newReporter = creator.createNewReporterEntry('IOIDS reporter', [newAgent])
            
            newEventType = creator.createNewEventTypeEntry(IOIDS_EVENT_TYPE)
            
            # reporter is me
            # observer is the reporter from our event
            oldEventReporterId = event[1]['rprt_id']
            fullReporter = getDBConnector().getReporter(oldEventReporterId)
            if fullReporter[1].has_key('rprt_name'):
                repName = fullReporter[1]['rprt_name']
            else:
                repName = None
            newObserver = creator.createNewObserverEntry(repName, fullReporter[2])
            # source and destination are the same than of the actual event
            newEvent = creator.createNewEventEntry('now', [newData, newEventType, newReporter, newObserver], None, None, 
                event[1]['src_id'], event[1]['dstn_id'])
            ioidsEventEntry = creator.createNewIoidsEventEntry(ioidsCommunity, ioidsTimestamp, [
                creator.createNewIoidsSourceEntry(ioidsSource),
                creator.createNewIoidsSenderEntry(ioidsSender),
                getDBConnector().getIoidsClassificationByCode(ioidsClassificationCode),
##                creator.createNewIoidsClassificationEntry(ioidsClassificationCode, ioidsClassificationName), 
                newEvent     # our event should be in the proper format already
                ])
    ##            creator.createIoidsClassificationEntry(ioidsClassification)], event['event_id'])
            
            # and finally the relations
            newRelationEntry = creator.createNewIoidsRelationEntry([ioidsEventEntry, event], relationTypeName = 'parent')
            
            # testing purposes
    ##        import support.dictviewer
    ##        support.dictviewer.showNow(newRelationEntry)
            # ####
            
            primKeyRel = getDBConnector().insertFullIoidsEventWithRelation(newRelationEntry)
##            ioidsEventId = getDBConnector().getIoidsRelation(primKeyRel,0)[1]['ioids_event_id']
##    ##        primKey = getDBConnector().insertIoidsEvent(ioidsEventEntry)
##            eventId = getDBConnector().getIoidsEvent(ioidsEventId, 0)[1]['event_id']
##            self._remoteEvents.append(eventId)
            print "\t-- Inserted event with id: %s" %(primKeyRel)

            # now let's go and check whether this is to be distributed
            if reaction['parameters'].has_key('distribute'):
                print "\t--Now I would even send it off to %s." %(reaction['parameters']['distribute']['domain'])
                # but that's for tomorrow ;)
        
    def _processEventFromLocal(self, event):
        """
        Processes one item from the local event list.
        """
        from config import G4DS_MEMBER_ID
        from dbconnector import getDBConnector
        
##        
##  real dataengine started here
##
        
        event1 = getDBConnector().getEvent(event[1]['event_id'])
        subsystem = None
        for rel in event1[2]:
            if rel[0] == 'event_type':
                subsystem = rel[1]['event_type_name']
        print "Local event - subsystem determination: %s" %(subsystem)
        
        # that's all we need here - let's ask for the corrospondig policies
        from policyengine import getPolicyEngine
        params = {}
        params['origin'] = 'local'
        if subsystem:
            params['subsystem'] = subsystem
        reactions = getPolicyEngine().lookup(params)
        
        # let's carry out the reactions then
        for reaction in reactions:
            print "\t-- Carry out reaction # %s: %s" %(reaction['id'], reaction['type'])
            self._executeOneReaction(event, reaction)

        return 
    
    


        
    def _processIoidsEventFromLocal(self, event):
        from dbconnector import getDBConnector
        ioidsevent = getDBConnector().getIoidsEvent(event[1]['ioids_event_id'])
##        print ioidsevent
        from messagewrapper import getXMLDBWrapper, getIoidsMessageWrapper
        x = getXMLDBWrapper().wrapInsert(ioidsevent[0], ioidsevent[1], ioidsevent[2])
##        print "***** SENT:\n", x
        from g4dsconnector import getG4dsConnector
##        getG4dsConnector().sendMessage(ioidsevent)
        
        relatedEvents = getDBConnector().getRelatedEventsForIoidsEvent(event[1]['ioids_event_id'])
        # determine the extension information for each related event
        for relEvent in relatedEvents:
            relEventEvent = getIoidsMessageWrapper()._getRelationInTree(relEvent, ['event'])
            extName, extValue = getDBConnector().getExtensionForEvent(relEventEvent)
            dict = {}
            dict['extension_name'] = extName
            relEvent[2].append(['extension',dict, [extValue]])
        
        from messagewrapper import getIoidsMessageWrapper
        xml = getIoidsMessageWrapper().assembleIoidsMessage(ioidsevent, relatedEvents)
##        print "Sending:\n%s" %xml
        
        getG4dsConnector().sendEventUpdate(xml)
        print "*** processed (and sent) IOIDS event %s" %(event[1]['ioids_event_id'])
        
        #
        #
        # testing
        #
##        print "*" * 40, 'TEST', "*"  * 40
##        xmlNew = getIoidsMessageWrapper().wrapKnowledgeReplyMessage([(ioidsevent, relatedEvents)])
##        print xmlNew
##        print "*" * 40, 'TEST', "*"  * 40
##        newInDict = getIoidsMessageWrapper().parseKnowledgeReplyMessage(xmlNew)
##        print "%s\n%s" %(newInDict[0][0], newInDict[0][1])
##        print "*" * 40, 'TEST', "*"  * 40
        
    def newEventFromLocal(self, event):
        """
        Processes the occurence of a new event in the local database.
        
        Should be called from the ioids event trigger.
        """
        print "Received event (local) with id: %s - put it into event queue." %(event[1]['event_id'])
        self._localEvents.append(event)
        
    def newIoidsEventFromLocal(self, ioidsevent):
        """
        Processes the occurence of a new ioids event in the local database.
        
        Should be called from the ioids event trigger.
        """
        print "Received ioids event (local) with id: %s - put into ioids event queue." %(ioidsevent[1]['ioids_event_id'])
        self._localIoidsEvents.append(ioidsevent)
        
    def newIoidsEventFromRemote(self, ioidsevent, relations = []):
        from dbconnector import getDBConnector
##        print "I received from remote:\nEvent: %s\nRelations: %s" %(event, relations)
        print "I received from remote Event with Relations"
        primKey = getDBConnector().insertIoidsEvent(ioidsevent)
        eventId = getDBConnector().getIoidsEvent(primKey, 0)[1]['event_id']
        self._remoteEvents.append(eventId)      # our trigger must not pick up this event

        from dataengine_tools import getPreXMLDictCreator
        for relation in relations:
            print "New Relation:"
            plainEvent = None
            extensionEvent = None
            relationType = relation[1]['type']
            extensionType = None
            for entry in relation[2]:
                if entry[0] == 'plainevent':
                    plainEvent = entry[2][0]
                elif entry[0] == 'extension':
                    try:
                        extensionEvent = entry[2][0]
                        extensionType = entry[1]['type']
                    except IndexError, msg:
                        pass        # no prob, that only means, that the sender could not handle the extension
            
            
            relType = getPreXMLDictCreator().createNewIoidsRelationTypeEntry(relationType)
            relEntry = getPreXMLDictCreator().createNewIoidsRelationEntry([ioidsevent, plainEvent, relType])
            
            # testing purposes
##            import support.dictviewer
##            support.dictviewer.showNowAscii(relEntry)
####            support.dictviewer.showNow(relEntry)
            # ####
            primKey = getDBConnector().insertFullIoidsEventWithRelation(relEntry)
            print "-- Primary key for remote ioids event (relation): %s" %(primKey)
            
            print "-- Event for Extension: %s" %(extensionType)
##            support.dictviewer.showNowAscii(extensionEvent)
            try:
                primKey = getDBConnector().insertExtensionEvent(extensionType, extensionEvent)
                print "-- Primary key for extension event: %s" %(primKey)
            except ValueError, msg:
                print "-- Extension is unknown: %s" %(extensionType)
                pass        # that's fine again - only means that I myself do not understand the extension here.

                
