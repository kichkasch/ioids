"""
Connect against database backend.

Inter-Organisational Intrusion Detection System (IOIDS)

Yes, we could put something very sophisticated here in order to allow integration with
a variety of datbases; however, for reasons of simplicity I decided to just put the code 
for connecting against the XML RPC database here.

@author: Michael Pilgermann
@contact: mailto:mpilgerm@glam.ac.uk
@license: GPL (General Public License)
"""

from soapsytools.dbconnector import *
import soapsytools.dbconnector

# constant for database type
DB_CONNECTION_TYPE_XML_RPC = 'xmlrpc'

# "singleton"
_dbConnector = None
def getDBConnector():
    """
    Singleton implementation.
    """
    global _dbConnector
    if not _dbConnector:
        _dbConnector = IoidsDBConnector()
    return _dbConnector

class IoidsDBConnector(soapsytools.dbconnector.DBConnector):
    """
    Standard DB connector - work on XML RPC database.
    """

    def __init__(self):
        """
        Sets the parameters for the later db connections.
        
        Most of the settings are taken from the global config file.
        """
        from config import DATABASE_CONNECTION_TYPE, SOAP_SERVER_URL
        from errorhandling import IoidsException
            
        if DATABASE_CONNECTION_TYPE !=DB_CONNECTION_TYPE_XML_RPC:
            raise IoidsException('The database type defined in the config file is not supported by IOIDS')
            
        soapsytools.dbconnector.DBConnector.__init__(self, SOAP_SERVER_URL)
                
    def getIoidsEvents(self, conditions = []):
        """
        Collects available ioids events from the database.
        
        The result is returned in a format mixed by lists and dictionaries.
        """
        from messagewrapper import getXMLDBWrapper
        xml = getXMLDBWrapper().wrapSelect('ioids_event', 'all', conditions)
        result = self._performRequest(xml)
        no, resolved = getXMLDBWrapper().parseSelectReply(result)
        return resolved
        
    def getIoidsEventsFromEventID(self, minIoidsEventId):
        """
        Returns all ioids events with ioids event id greater then the given one.
        """
        return self.getIoidsEvents([['ioids_event_id', OPERATOR_GREATER_THEN_OR_EQUAL, str(minIoidsEventId)]])
        
        
##    def insertIoidsEvent(self, eventDict, relations = []):
    def insertIoidsEvent(self, ioidsEventEntryList):
        """
        Insert a new IOIDS event.
        
        @return: The primary key of the new event
        @rtype: C{String}
        """
        from messagewrapper import getXMLDBWrapper
##        xml = getXMLDBWrapper().wrapInsert('ioids_event', eventDict, relations)
        xml = getXMLDBWrapper().wrapInsert(ioidsEventEntryList[0], ioidsEventEntryList[1], ioidsEventEntryList[2])
        
##        print xml
        result = self._performRequest(xml)
##        print result
        decode = getXMLDBWrapper().parseInsertReply(result)
##        print "Result - primary key: %s " %(decode[0][2])
        return decode[0][2][1:len(decode[0][2])-1]
        
    def insertFullIoidsEventWithRelation(self, fullIoidsEvent):
        """
        Insert a new ioids event with its relation to further events.

        @return: The primary key of the new relation entry
        @rtype: C{String}
        """
        from messagewrapper import getXMLDBWrapper
        xml = getXMLDBWrapper().wrapInsert(fullIoidsEvent[0], fullIoidsEvent[1], fullIoidsEvent[2])
        result = self._performRequest(xml)
        
        decode = getXMLDBWrapper().parseInsertReply(result)
##        print "Result - primary key: %s " %(decode[0][2])
        return decode[0][2][1:len(decode[0][2])-1]
        
        
    ##
    ## Functions for getting all the details of events
    ##        
    def getIoidsClassification(self, classification_id, full = 1):
        from dataengine_tools import getPreXMLDictCreator
        myEntry = self._getSomething('ioids_classification', 'classification_id', classification_id)
        return getPreXMLDictCreator().createIoidsClassificationEntry(myEntry)

    def getIoidsClassificationByCode(self, classification_code, full = 1):
        from dataengine_tools import getPreXMLDictCreator
        myEntry = self._getSomething('ioids_classification', 'classification_code', classification_code)
        return getPreXMLDictCreator().createIoidsClassificationEntry(myEntry)
    
    def getIoidsPeer(self, peerId, full = 1):
        from dataengine_tools import getPreXMLDictCreator
        myEntry = self._getSomething('ioids_peer', 'ioids_peer_id', peerId)
        return getPreXMLDictCreator().createIoidsPeerEntry(myEntry)

    def getIoidsSender(self, senderId, full = 1):
        from dataengine_tools import getPreXMLDictCreator
        myEntry = self._getSomething('ioids_sender', 'ioids_sender_id', senderId)
        peer = None
        if full:
            if myEntry['ioids_peer_id'] != 'None':
                peer = self.getIoidsPeer(myEntry['ioids_peer_id'])
        return getPreXMLDictCreator().createIoidsSenderEntry(myEntry, peer)
        
    def getIoidsSource(self, sourceId, full = 1):
        from dataengine_tools import getPreXMLDictCreator
        myEntry = self._getSomething('ioids_source', 'ioids_source_id', sourceId)
        peer = None
        if full:
            if myEntry['ioids_peer_id'] != 'None':
                peer = self.getIoidsPeer(myEntry['ioids_peer_id'])
        return getPreXMLDictCreator().createIoidsSourceEntry(myEntry, peer)
    
    def getIoidsEvent(self, ioids_event_id, full = 1):
        from dataengine_tools import getPreXMLDictCreator
        myEntry = self._getSomething('ioids_event', 'ioids_event_id', ioids_event_id)

        event = None
        sender = None
        source = None
        classification = None
        if full:
            if myEntry['event_id'] != 'None':
                event = self.getEvent(myEntry['event_id'],1)
            if myEntry['ioids_sender_id'] != 'None':
                sender = self.getIoidsSender(myEntry['ioids_sender_id'],1)
            if myEntry['ioids_source_id'] != 'None':
                source = self.getIoidsSource(myEntry['ioids_source_id'],1)
            if myEntry['classification_id'] != 'None':
                classification = self.getIoidsClassification(myEntry['classification_id'],1)
            
        return getPreXMLDictCreator().createIoidsEventEntry(myEntry, event, sender, source, classification)
    
    def getIoidsRelationType(self, relation_type_id, full = 1):
        from dataengine_tools import getPreXMLDictCreator
        myEntry = self._getSomething('ioids_relation_type', 'ioids_relation_type_id', relation_type_id)
        return getPreXMLDictCreator().createIoidsRelationTypeEntry(myEntry)
    

    def getIoidsRelation(self, relationId, full =1):
        from dataengine_tools import getPreXMLDictCreator
        myEntry = self._getSomething('ioids_relation', 'ioids_relation_id', relationId)
        
        event = None
        ioids_event = None
        relationType = None
        if full:
            if myEntry['event_id'] != 'None':
                event = self.getEvent(myEntry['event_id'],1)
            if myEntry['ioids_event_id'] != 'None':
                ioids_event = self.getIoidsEvent(myEntry['ioids_event_id'],1)
            if myEntry['ioids_relation_type_id'] != 'None':
                relationType = self.getEvent(myEntry['ioids_relation_type_id'],1)
            
        return getPreXMLDictCreator().createIoidsRelationEntry(myEntry, event, ioids_event, relationType)
        
    def getRelatedEventsForIoidsEvent(self, ioidsEventId, full = 1):
        
        from messagewrapper import getXMLDBWrapper
        xml = getXMLDBWrapper().wrapSelect('ioids_relation', 'event_id', [['ioids_event_id', OPERATOR_EQUAL, str(ioidsEventId)]])
        result = self._performRequest(xml)
        #print "\n>\n%s\n<\n" %result
        no, resolved = getXMLDBWrapper().parseSelectReply(result)

        from dataengine_tools import getPreXMLDictCreator
        
        relations = []
        items = resolved[0]['relations']
        for item in items:
            aRelation = getPreXMLDictCreator().restructureEntry(item['attributes'], 'relation')
            relations.append(aRelation)
        
        for rel in relations:
            oneEvent = self.getEvent(rel[1] ['event_id'])
            rel[2].append(oneEvent)
            del rel[1]['event_id']
            oneRelType = self.getIoidsRelationType(rel[1]['ioids_relation_type_id'])
            rel[2].append(oneRelType)
            del rel[1]['ioids_relation_type_id']
        return relations
        
    def getExtensionForEvent(self, event):
        """
        Retrieves extension information from the database for an event.
        
        @param event: Event in List / Dict format.
        @return: Name of the Extension / Extension in List / Dict format (including event).
        """
##        type = self.getEventType(event[1]['event_type_id'])
##        typeName = type[1]['event_type_name']
        from messagewrapper import getIoidsMessageWrapper
        typeName  =getIoidsMessageWrapper()._getValueInTree(event, ['event_type', 'event_type_name'])
        
        eventid = self.insertEvent(event)       # it's not really an insert - but it's the only way I see to find the prim key
        extension = getDBExtensionHandler().getExtensionInformationForEventId(typeName, eventid)
        
##        print "Echo - extension - i got: %s: %s" %(typeName, extension)
        
        return typeName, extension
        
    def insertExtensionEvent(self, extensionName, data):
        return getDBExtensionHandler().insertExtensionEvent(extensionName, data)

        
# "singleton"
_dbExtensionHandler = None
def getDBExtensionHandler():
    """
    Singleton implementation.
    """
    global _dbExtensionHandler
    if not _dbExtensionHandler:
        _dbExtensionHandler = DBExtensionHandler()
    return _dbExtensionHandler
        
class DBExtensionHandler:
    """
    Provides access to information from several SoapSy extensions.
    """
    
    def __init__(self):
        """
        Yet empty constructor.
        """
        from config import SOAPSY_EXTENSIONS
        self._extensions = SOAPSY_EXTENSIONS
        
    def getExtensionInformationForEventId(self, extensionName, eventId):
        if not self._extensions.has_key(extensionName):
            return None
            
        ext_db = self._extensions[extensionName]['dbconnector']
        return ext_db().getExtensionEvent(eventId)
        
    def insertExtensionEvent(self, extensionName, data):
        """
        @return: The primary key value of the top level table of the insert action.
        """
        if not self._extensions.has_key(extensionName):
            raise ValueError('Extension unknown on this node: %s' %(extensionName))

        ext_db = self._extensions[extensionName]['dbconnector']
        return ext_db().insertExtensionEvent(data)
