"""
Some supportive functions for the data engine.

Tools for SoapSy

@author: Michael Pilgermann
@contact: mailto:mpilgerm@glam.ac.uk
@license: GPL (General Public License)
"""
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
        _preXMLDictCreator = PreXMLDictCreator()
    return _preXMLDictCreator
    
class PreXMLDictCreator:
        
    def createNewEventEntry(self, timestamp, relations = [], observerId = None, reporterId = None, 
        sourceId = None, destinationId = None, eventTypeId = None, dataId = None):
        dict = {}
        self._evalValue(dict, 'timestmp', timestamp)
        self._evalValue(dict, 'obsrv_id', observerId)
        self._evalValue(dict, 'rprt_id', reporterId)
        self._evalValue(dict, 'src_id', sourceId)
        self._evalValue(dict, 'dstn_id', destinationId)
        self._evalValue(dict, 'event_type_id', eventTypeId)
        self._evalValue(dict, 'data_id', dataId)
        return ['event', dict, relations]
        
    def createNewEncodingEntry(self, encodingValue, relations = []):
        dict = {}
        self._evalValue(dict, 'encoding_type', encodingValue)
        return ['encoding', dict, relations]
        
    def createNewDataEntry(self, data, relations = [], encodingId = None):
        dict = {}
        self._evalValue(dict, 'data_text', data)
        self._evalValue(dict, 'encoding_id', encodingId)
        return ['data', dict, relations]
        
    def createNewEventTypeEntry(self, eventTypeName, relations = []):
        dict = {}
        self._evalValue(dict, 'event_type_name', eventTypeName)
        return ['event_type', dict, relations]
        
    def createNewAgentEntry(self, agentName, relations = [], agentClassId = None, computerId = None, processId = None):
        dict = {}
        self._evalValue(dict, 'agent_name', agentName)
        self._evalValue(dict, 'agent_class_id', agentClassId)
        self._evalValue(dict, 'comp_id', computerId)
        self._evalValue(dict, 'prcss_id', processId)
        return ['agent', dict, relations]
        
    def createNewAgentClassEntry(self, agentClassName, agentClassDescription, relations = []):
        dict = {}
        self._evalValue(dict, 'agent_class_name', agentClassName)
        self._evalValue(dict, 'agent_class_dscr', agentClassDescription)
        return ['agent_class', dict, relations]
        
    def createNewObserverEntry(self, observerName, relations = [], agentId = None):
        dict = {}
        self._evalValue(dict, 'obsrv_name', observerName)
        self._evalValue(dict, 'agent_id', agentId)
        return ['observer', dict, relations]

    def createNewReporterEntry(self, reporterName, relations = [], agentId = None):
        dict = {}
        self._evalValue(dict, 'rprt_name', reporterName)
        self._evalValue(dict, 'agent_id', agentId)
        return ['reporter', dict, relations]
        
    def createNewSourceEntry(self, sourceName, relations = [], agentId = None):
        dict = {}
        self._evalValue(dict, 'src_name', sourceName)
        self._evalValue(dict, 'agent_id', agentId)
        return ['source', dict, relations]
        
    def createNewDestinationEntry(self, destinationName, relations = [], agentId = None):
        dict = {}
        self._evalValue(dict, 'dstn_name', destinationName)
        self._evalValue(dict, 'agent_id', agentId)
        return ['destination', dict, relations]
        
    def createNewComputerTypeEntry(self, computerTypeName, relations = []):
        dict = {}
        self._evalValue(dict, 'comp_type_name', computerTypeName)
        return ['comp_type', dict, relations]        
        
    def createNewComputerEntry(self, hostname, os, ip, mac, domain, relations = [], computerTypeId = None, computerTypeName = None):
        dict = {}
        self._evalValue(dict, 'hostname', hostname)
        self._evalValue(dict, 'os', os)
        self._evalValue(dict, 'ip', ip)
        self._evalValue(dict, 'mac', mac)
        self._evalValue(dict, 'domain', domain)
        self._evalValue(dict, 'comp_type', computerTypeId)
        if computerTypeName:
            relations.append(self.createNewComputerTypeEntry(computerTypeName))
        return ['computer', dict, relations]
                
    # here we go with the known events
    
    def _evalValue(self, dict, key, value):
        if value and value != 'None':
##            dict[key] = "'" + value + "'"     - the XML DB RPC server is doing this for us now
            dict[key] = value
        
    def createComputerTypeEntry(self, dictRaw):
        dict = {}
##        self._evalValue(dict, 'comp_type_id', dictRaw['comp_type_id'])
        self._evalValue(dict, 'comp_type_name', dictRaw['comp_type_name'])
        return ['comp_type', dict, []]
        
    def createComputerEntry(self, dictRaw, computerTypeRelation = None):
        dict = {}
##        self._evalValue(dict, 'comp_id', dictRaw['comp_id'])
        self._evalValue(dict, 'hostname', dictRaw['hostname'])
        self._evalValue(dict, 'os', dictRaw['os'])
        self._evalValue(dict, 'ip', dictRaw['ip'])
        self._evalValue(dict, 'mac', dictRaw['mac'])
        self._evalValue(dict, 'domain', dictRaw['domain'])
        if not computerTypeRelation:
            self._evalValue(dict, 'comp_type_id', dictRaw['comp_type_id'])
            return ['computer', dict, []]
        return ['computer', dict, [computerTypeRelation]]
        
    def createUserGroupEntry(self, dictRaw):
        dict = {}
##        self._evalValue(dict, 'usr_group_id', dictRaw['usr_group_id'])
        self._evalValue(dict, 'usr_group_name', dictRaw['usr_group_name'])
        self._evalValue(dict, 'usr_group_domain', dictRaw['usr_group_domain'])
        return ['usr_group', dict, []]
        
    def createUserEntry(self, dictRaw, userGroupRelation = None):
        dict = {}
##        self._evalValue(dict, 'usr_id', dictRaw['usr_id'])
        self._evalValue(dict, 'usr_name', dictRaw['usr_name'])
        if not userGroupRelation:
            self._evalValue(dict, 'usr_group', dictRaw['usr_group'])
            return ['usr', dict, []]
        return ['usr', dict, [computerTypeRelation]]
    
    def createProcessTypeEntry(self, dictRaw):
        dict = {}
##        self._evalValue(dict, 'prcss_type_id', dictRaw['prcss_type_id'])
        self._evalValue(dict, 'prcss_type_name', dictRaw['prcss_type_name'])
        return ['prcss_type', dict, []]

    def createProcessNameEntry(self, dictRaw):
        dict = {}
##        self._evalValue(dict, 'prcss_name_id', dictRaw['prcss_name_id'])
        self._evalValue(dict, 'process_name', dictRaw['process_name'])
        return ['prcss_name', dict, []]
        
    def createProcessEntry(self, dictRaw, processTypeRelation = None, processNameRelation = None, userRelation = None):
        dict = {}
        rels = []
##        self._evalValue(dict, 'prcss_id', dictRaw['prcss_id'])
        self._evalValue(dict, 'prcss_pid', dictRaw['prcss_pid'])
        if not processTypeRelation:
            self._evalValue(dict, 'prcss_type_id', dictRaw['prcss_type_id'])
        else:
            rels.append(processTypeRelation)
        if not processNameRelation:
            self._evalValue(dict, 'prcss_name_id', dictRaw['prcss_name_id'])
        else:
            rels.append(processNameRelation)
        if not userRelation:
            self._evalValue(dict, 'usr_id', dictRaw['usr_id'])
        else:
            rels.append(userRelation)
        return ['process', dict, rels]
    
    def createAgentClassEntry(self, dictRaw):
        dict = {}
##        self._evalValue(dict, 'agent_class_id', dictRaw['agent_class_id'])
        self._evalValue(dict, 'agent_class_name', dictRaw['agent_class_name'])
        self._evalValue(dict, 'agent_class_dscr', dictRaw['agent_class_dscr'])
        return ['agent_class', dict, []]        
        
    def createAgentEntry(self, dictRaw, agentClassRelation = None, computerRelation = None, processRelation = None):
        dict = {}
        rels = []
##        self._evalValue(dict, 'agent_id', dictRaw['agent_id'])
        self._evalValue(dict, 'agent_name', dictRaw['agent_name'])
        if not agentClassRelation:
            self._evalValue(dict, 'agent_class_id', dictRaw['agent_class_id'])
        else:
            rels.append(agentClassRelation)
        if not computerRelation:
            self._evalValue(dict, 'comp_id', dictRaw['comp_id'])
        else:
            rels.append(computerRelation)
        if not processRelation:
            self._evalValue(dict, 'prcss_id', dictRaw['prcss_id'])
        else:
            rels.append(processRelation)
        return ['agent', dict, rels]
        
    def createObserverEntry(self, dictRaw, agentRelation):
        dict = {}
        rels = []
##        self._evalValue(dict, 'obsrv_id', dictRaw['obsrv_id'])
        self._evalValue(dict, 'obsrv_name', dictRaw['obsrv_name'])
        if not agentRelation:
            self._evalValue(dict, 'agent_id', dictRaw['agent_id'])
        else:
            rels.append(agentRelation)
        return ['observer', dict, rels]

    def createReporterEntry(self, dictRaw, agentRelation):
        dict = {}
        rels = []
##        self._evalValue(dict, 'rprt_id', dictRaw['rprt_id'])
        self._evalValue(dict, 'rprt_name', dictRaw['rprt_name'])
        if not agentRelation:
            self._evalValue(dict, 'agent_id', dictRaw['agent_id'])
        else:
            rels.append(agentRelation)
        return ['reporter', dict, rels]

    def createSourceEntry(self, dictRaw, agentRelation):
        dict = {}
        rels = []
##        self._evalValue(dict, 'src_id', dictRaw['src_id'])
        self._evalValue(dict, 'src_name', dictRaw['src_name'])
        if not agentRelation:
            self._evalValue(dict, 'agent_id', dictRaw['agent_id'])
        else:
            rels.append(agentRelation)
        return ['source', dict, rels]
        
    def createDestinationEntry(self, dictRaw, agentRelation):
        dict = {}
        rels = []
##        self._evalValue(dict, 'dstn_id', dictRaw['dstn_id'])
        self._evalValue(dict, 'dstn_name', dictRaw['dstn_name'])
        if not agentRelation:
            self._evalValue(dict, 'agent_id', dictRaw['agent_id'])
        else:
            rels.append(agentRelation)
        return ['destination', dict, rels]
        
    def createEncodingEntry(self, dictRaw):
        dict = {}
##        self._evalValue(dict, 'encoding_id', dictRaw['encoding_id'])
        self._evalValue(dict, 'encoding_type', dictRaw['encoding_type'])
        return ['encoding', dict, []]
        
    def createDataEntry(self, dictRaw, encodingRelation):
        dict = {}
        rels = []
##        self._evalValue(dict, 'data_id', dictRaw['data_id'])
        self._evalValue(dict, 'data_text', dictRaw['data_text'])
        if not encodingRelation:
            self._evalValue(dict, 'encoding_id', dictRaw['encoding_id'])
        else:
            rels.append(encodingRelation)
        return ['data', dict, rels]
        
    def createEventTypeEntry(self, dictRaw):
        dict = {}
##        self._evalValue(dict, 'event_type_id', dictRaw['event_type_id'])
        self._evalValue(dict, 'event_type_name', dictRaw['event_type_name'])
        return ['event_type', dict, []]        
        
    def createEventEntry(self, dictRaw, observerRelation, reporterRelation, sourceRelation, destinationRelation, 
        dataRelation, eventTypeRelation):
        dict = {}
        rels = []
##        self._evalValue(dict, 'event_id', dictRaw['event_id'])
        self._evalValue(dict, 'timestmp', dictRaw['timestmp'])
        if not observerRelation:
            self._evalValue(dict, 'obsrv_id', dictRaw['obsrv_id'])
        else:
            rels.append(observerRelation)
        if not reporterRelation:
            self._evalValue(dict, 'rprt_id', dictRaw['rprt_id'])
        else:
            rels.append(reporterRelation)
        if not sourceRelation:
            self._evalValue(dict, 'src_id', dictRaw['src_id'])
        else:
            rels.append(sourceRelation)
        if not destinationRelation:
            self._evalValue(dict, 'dstn_id', dictRaw['dstn_id'])
        else:
            rels.append(destinationRelation)
        if not eventTypeRelation:
            self._evalValue(dict, 'event_type_id', dictRaw['event_type_id'])
        else:
            rels.append(eventTypeRelation)
        if not dataRelation:
            self._evalValue(dict, 'data_id', dictRaw['data_id'])
        else:
            rels.append(dataRelation)
        return ['event', dict, rels]
 
 
 
    def restructureEventEntry(self, normalDict):        
        attributes = {}
        relations = []
        
        for key in normalDict.keys():
##            if key == 'event_id':
##                attributes[key] = "'" + normalDict[key] + "'"
##            else:
##                attributes[key] = "'" + normalDict[key] + "'"   - done by server
            self._evalValue(attributes, key, normalDict[key])
##                attributes[key] = normalDict[key] 
        
        return ['event', attributes, relations]
 
