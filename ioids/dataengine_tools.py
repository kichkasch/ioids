"""
Some supportive functions for the data engine.

Inter-Organisational Intrusion Detection System (IOIDS)

@author: Michael Pilgermann
@contact: mailto:mpilgerm@glam.ac.uk
@license: GPL (General Public License)
"""

import soapsytools.dataengine_tools

# "singleton"
_preXMLDictCreator = None
def getPreXMLDictCreator():
    """
    Singleton implementation.
    
    @return: The instance for the data engine
    @rtype: L{DataEngine}
    """
    global _preXMLDictCreator
    if not _preXMLDictCreator:
        _preXMLDictCreator = IoidsPreXMLDictCreator()
    return _preXMLDictCreator

class IoidsPreXMLDictCreator(soapsytools.dataengine_tools.PreXMLDictCreator):

    def createNewIoidsPeerEntry(self, memberid):
        dict_peer = {}
        self._evalValue(dict_peer, 'peer_memberid', memberid)
        return ['ioids_peer', dict_peer, []]
    
    def createNewIoidsSourceEntry(self, memberid):
        """
        Creates the nested list for preparing for XML creation of an IOIDS Source.
        """
        return ['ioids_source', {}, [self.createNewIoidsPeerEntry(memberid)]]
        
    def createNewIoidsSenderEntry(self, memberid):
        """
        Creates the nested list for preparing for XML creation of an IOIDS Source.
        """
        return ['ioids_sender', {}, [self.createNewIoidsPeerEntry(memberid)]]
        
    def createNewIoidsClassificationEntry(self, classificationCode, classificationName):
        """
        Creates the nested list for preparing for XML creation of an IOIDS Classification.
        """
        dict_class = {}
        self._evalValue(dict_class, 'classification_code', classificationCode)
        self._evalValue(dict_class, 'classification_name', classificationName)
        return ['ioids_classification', dict_class, []]

    def createNewIoidsEventEntry(self, community_id, timestamp_received, relations = [], event_id = None):
        dict = {}
        self._evalValue(dict, 'event_id', event_id)
        self._evalValue(dict, 'community_id', community_id)
        self._evalValue(dict, 'timestamp_received', timestamp_received)
        return ['ioids_event', dict, relations]

    def createNewIoidsRelationTypeEntry(self, typeName, relations = []):
        dict = {}
        self._evalValue(dict, 'ioids_relation_type_name', typeName)
        return ['ioids_relation_type', dict, relations]

    def createNewIoidsRelationEntry(self, relations = [], ioidsEventId = None, eventId = None, relationTypeId = None, relationTypeName = None):
        dict = {}
        self._evalValue(dict, 'ioids_event_id', ioidsEventId)
        self._evalValue(dict, 'event_id', eventId)
        self._evalValue(dict, 'ioids_relation_type_id', relationTypeId)
        if relationTypeName:
            relations.append(self.createNewIoidsRelationTypeEntry(relationTypeName))
        return ['ioids_relation', dict, relations]
        
    # here we go with the known events
    
    def createIoidsClassificationEntry(self, dictRaw):
        dict = {}
        rels = []
##        self._evalValue(dict, 'classification_id', dictRaw['classification_id'])
        self._evalValue(dict, 'classification_code', dictRaw['classification_code'])
        self._evalValue(dict, 'classification_name', dictRaw['classification_name'])
        return ['ioids_classification', dict, rels]
        
    def createIoidsPeerEntry(self, dictRaw):
        dict = {}
        rels = []
##        self._evalValue(dict, 'ioids_peer_id', dictRaw['ioids_peer_id'])
        self._evalValue(dict, 'peer_memberid', dictRaw['peer_memberid'])
        return ['ioids_peer', dict, rels]
        
    def createIoidsSenderEntry(self, dictRaw, peerRelation):
        dict = {}
        rels = []
##        self._evalValue(dict, 'ioids_sender_id', dictRaw['ioids_sender_id'])
        if not peerRelation:
            self._evalValue(dict, 'ioids_peer_id', dictRaw['ioids_peer_id'])
        else:
            rels.append(peerRelation)
        return ['ioids_sender', dict, rels]

    def createIoidsSourceEntry(self, dictRaw, peerRelation):
        dict = {}
        rels = []
##        self._evalValue(dict, 'ioids_source_id', dictRaw['ioids_source_id'])
        if not peerRelation:
            self._evalValue(dict, 'ioids_peer_id', dictRaw['ioids_peer_id'])
        else:
            rels.append(peerRelation)
        return ['ioids_source', dict, rels]
        
    def createIoidsEventEntry(self, dictRaw, eventRelation, ioidsSenderRelation, ioidsSourceRelation, ioidsClassificationRelation):
        dict = {}
        rels = []
##        self._evalValue(dict, 'ioids_event_id', dictRaw['ioids_event_id'])
        self._evalValue(dict, 'timestamp_received', dictRaw['timestamp_received'])
        self._evalValue(dict, 'community_id', dictRaw['community_id'])
        if not eventRelation:
            self._evalValue(dict, 'event_id', dictRaw['event_id'])
        else:
            rels.append(eventRelation)
        if not ioidsSenderRelation:
            self._evalValue(dict, 'ioids_sender_id', dictRaw['ioids_sender_id'])
        else:
            rels.append(ioidsSenderRelation)
        if not ioidsSourceRelation:
            self._evalValue(dict, 'ioids_source_id', dictRaw['ioids_source_id'])
        else:
            rels.append(ioidsSourceRelation)
        if not ioidsClassificationRelation:
            self._evalValue(dict, 'classification_id', dictRaw['classification_id'])
        else:
            rels.append(ioidsClassificationRelation)
        return ['ioids_event', dict, rels]
 
    def createIoidsRelationTypeEntry(self, dictRaw):
        dict = {}
        self._evalValue(dict, 'ioids_relation_type_name', dictRaw['ioids_relation_type_name'])
        return ['ioids_relation_type', dict, []]        
 
    def createIoidsRelationEntry(self, dictRaw, eventRelation, ioidsEventRelation, relationTypeRelation):
        dict = {}
        rels = []
        if not eventRelation:
            self._evalValue(dict, 'event_id', dictRaw['event_id'])
        else:
            rels.append(eventRelation)
        if not ioidsEventRelation:
            self._evalValue(dict, 'ioids_event_id', dictRaw['ioids_event_id'])
        else:
            rels.append(ioidsEventRelation)
        if not relationTypeRelation:
            self._evalValue(dict, 'ioids_relation_type_id', dictRaw['ioids_relation_type_id'])
        else:
            rels.append(relationTypeRelation)
        return ['ioids_relation', dict, rels]
 
    
    def restructureEntry(self, normalDict, relationName):
        attributes = {}
        relations = []
        
        for key in normalDict:
            self._evalValue(attributes, key, normalDict[key])
        
        return [relationName, attributes, relations]  # todo: something her
 
    def restructureIoidsEventEntry(self, normalDict):
        return self.restructureEntry(normalDict, 'ioids_event')
##        attributes = {}
##        relations = []
##        
##        for key in normalDict:
##            self._evalValue(attributes, key, normalDict[key])
##        
##        return ['ioids_event', attributes, relations]  # todo: something here

        
        
        
