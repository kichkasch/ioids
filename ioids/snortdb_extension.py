"""
Provides functionality for accessing information from the IOIDS SnortDB extension.

Inter-Organisational Intrusion Detection System (IOIDS)

@author: Michael Pilgermann
@contact: mailto:mpilgerm@glam.ac.uk
@license: GPL (General Public License)
"""

import messagewrapper
import dbconnector
import dataengine_tools

_snortDBMessageWrapper = None
def getMessageWrapper():
    """
    Singleton implementation.
    
    @return: The instance for the snort db message wrapper class
    @rtype: L{SnortDBMessageWrapper}
    """
    global _snortDBMessageWrapper 
    if not _snortDBMessageWrapper :
        _snortDBMessageWrapper  = SnortDBMessageWrapper()
    return _snortDBMessageWrapper 

    # "singleton"
_dbConnector = None
def getDBConnector():
    """
    Singleton implementation.
    """
    global _dbConnector
    if not _dbConnector:
        _dbConnector = SnortDB_DBConnector()
        _dbConnector.connect()
    return _dbConnector

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
        _preXMLDictCreator = SnortDBPreXMLDictCreator()
    return _preXMLDictCreator
    

class SnortDBMessageWrapper(messagewrapper.IoidsMessageWrapper):

    def __init__(self, prefix = 'snortdb:'):
        """
        Yet empty constructor.
        """
        self._prefix = prefix
        
    def createPrefElement(self, doc, name):
        if self._prefix:
            name = self._prefix + name
        return doc.createElement(name)

    def getFullExtensionMessage(self, data, parentNode, doc):
        if data[0] != 'snortdb_event':
            raise ValueError('This is not a snort db extension data set: %s.' %(data[0]))
        self._wrapAnyItemToDom(data, parentNode, doc)
##        elementSnortDB = self.createPrefElement(doc, 'snortdb_event')
##        parentNode.appendChild(elementSnortDB)
##        elementTimeStamp = self.createPrefElement(doc, 'timestamp')
##        textTimestamp = doc.createTextNode(data[1]['timestamp'])
##        elementTimeStamp.appendChild(textTimestamp)
##        elementSnortDB.appendChild(elementTimeStamp)
        

class SnortDB_DBConnector(dbconnector.IoidsDBConnector):
    """
    Standard DB connector - work on XML RPC database.
    """

    def __init__(self):
        """
        Sets the parameters for the later db connections.
        
        Most of the settings are taken from the global config file.
        """
        dbconnector.IoidsDBConnector.__init__(self)

    def getSnortDBSensor(self, snortDBSendorId, full = 1):
        from messagewrapper import getXMLDBWrapper
        myEntry = self._getSomething('snortdb_sensor', 'sensor_id', snortDBSendorId)
        return getPreXMLDictCreator().createSnortDBSensorEntry(myEntry)
        
    def getSnortDBPayload(self, snortDBPayloadId, full = 1):
        from messagewrapper import getXMLDBWrapper
        myEntry = self._getSomething('snortdb_payload', 'payload_id', snortDBPayloadId)
        return getPreXMLDictCreator().createSnortDBPayloadEntry(myEntry)
        
    def getSnortDBSignature(self, snortDBSignatureId, full = 1):
        from messagewrapper import getXMLDBWrapper
        myEntry = self._getSomething('snortdb_signature', 'signature_id', snortDBSignatureId)
        return getPreXMLDictCreator().createSnortDBSignatureEntry(myEntry)
        
    def getSnortDBTCPHeader(self, snortDBTCPHeaderId, full = 1):
        from messagewrapper import getXMLDBWrapper
        myEntry = self._getSomething('snortdb_tcp_header', 'tcp_header_id', snortDBTCPHeaderId)
        return getPreXMLDictCreator().createSnortDBTCPHeaderEntry(myEntry)
        
    def getSnortDBUDPHeader(self, snortDBUDPHeaderId, full = 1):
        from messagewrapper import getXMLDBWrapper
        myEntry = self._getSomething('snortdb_udp_header', 'udp_header_id', snortDBUDPHeaderId)
        return getPreXMLDictCreator().createSnortDBUDPHeaderEntry(myEntry)
        
    def getSnortDBICMPHeader(self, snortDBICMPHeaderId, full = 1):
        from messagewrapper import getXMLDBWrapper
        myEntry = self._getSomething('snortdb_icmp_header', 'icmp_header_id', snortDBICMPHeaderId)
        return getPreXMLDictCreator().createSnortDBICMPHeaderEntry(myEntry)
        
    def getSnortDBIPHeader(self, snortDBIPHeaderId, full = 1):
        from messagewrapper import getXMLDBWrapper
        myEntry = self._getSomething('snortdb_ip_header', 'ip_header_id', snortDBIPHeaderId)
        tcpHeader = None
        udpHeader = None
        icmpHeader = None
        if full:
            if myEntry['tcp_header_id'] != 'None':
                tcpHeader = self.getSnortDBTCPHeader(myEntry['tcp_header_id'],1)
        if full:
            if myEntry['udp_header_id'] != 'None':
                udpHeader = self.getSnortDBUDPHeader(myEntry['udp_header_id'],1)
        if full:
            if myEntry['icmp_header_id'] != 'None':
                icmpHeader = self.getSnortDBICMPHeader(myEntry['icmp_header_id'],1)
        return getPreXMLDictCreator().createSnortDBIPHeaderEntry(myEntry, tcpHeader, udpHeader, icmpHeader)
        
        
    def getSnortDBEvent(self, snortDBEventId, event_id, full = 1):
        if snortDBEventId and event_id:
            raise ValueError('Programming Error: SnortDB event loading from db - you may only define SnortDBEventID or Plain EventID!')

        from messagewrapper import getXMLDBWrapper
        myEntry = None
        if snortDBEventId:
            myEntry = self._getSomething('snortdb_event', 'snortdb_event_id', snortDBEventId)
        elif event_id:
            xml = getXMLDBWrapper().wrapSelect('snortdb_event', 'all', [['event_id', dbconnector.OPERATOR_EQUAL, str(event_id)]])
            result = self._performRequest(xml)
            no, resolved = getXMLDBWrapper().parseSelectReply(result)
    
            snortEvent = None
            items = resolved[0]['relations']
            for item in items:
                # if we come back with more than one; we just take the last ... but that of course would never happen due to db constraints ;)
                myEntry = getPreXMLDictCreator().restructureEntry(item['attributes'], 'snortdb_event')  
            myEntry = myEntry[1]    # we only need the attributes here - relations will be added later on
        else:
            raise ValueError('Programming Error: SnortDB event loading from db - you must exactly provide one id - none is given tho!')
                
        event = None
        sensor = None
        payload = None
        signature = None
        ipHeader = None
        if full:
            if myEntry['event_id'] != 'None':
                event = self.getEvent(myEntry['event_id'],1)
            if myEntry['sensor_id'] != 'None':
                sensor = self.getSnortDBSensor(myEntry['sensor_id'], 1)
            if myEntry['payload_id'] != 'None':
                payload = self.getSnortDBPayload(myEntry['payload_id'], 1)
            if myEntry.has_key('signature_id'):
                if myEntry['signature_id'] != 'None':
                    signature = self.getSnortDBSignature(myEntry['signature_id'], 1)
            if myEntry['ip_header_id'] != 'None':
                ipHeader = self.getSnortDBIPHeader(myEntry['ip_header_id'], 1)
        return getPreXMLDictCreator().createSnortDBEventEntry(myEntry, event, ipHeader, signature, sensor, payload)
        
        
    def getExtensionEvent(self, plainEventId):            
        snortEvent = self.getSnortDBEvent(None, plainEventId)
##        if not snortEvent:
##            return None
        
        return snortEvent

    def insertExtensionEvent(self, data):
        if data[0] != 'snortdb_event':
            raise ValueError('This is not a valid extension message for the SnortDB extension.')
        from messagewrapper import getXMLDBWrapper
        xml = getXMLDBWrapper().wrapInsert(data[0], data[1], data[2])
        
        result = self._performRequest(xml)
        decode = getXMLDBWrapper().parseInsertReply(result)
##        print "Result - primary key: %s " %(decode[0][2])
        return decode[0][2][1:len(decode[0][2])-1]
        

class SnortDBPreXMLDictCreator(dataengine_tools.IoidsPreXMLDictCreator):

    def __init__(self):
        """
        Yet empty constructor.
        """
        pass
        
    def createSnortDBSensorEntry(self, dictRaw):
        dict = {}
        rels = []
        self._evalValue(dict, 'hostname', dictRaw['hostname'])        
        self._evalValue(dict, 'interface', dictRaw['interface'])        
        self._evalValue(dict, 'filter', dictRaw['filter'])        
        self._evalValue(dict, 'encoding', dictRaw['encoding'])        
        self._evalValue(dict, 'detail', dictRaw['detail'])        
        return ['snortdb_sensor', dict, rels]
    
    def createSnortDBPayloadEntry(self, dictRaw):
        dict = {}
        rels = []
        self._evalValue(dict, 'data', dictRaw['data'])        
        return ['snortdb_payload', dict, rels]
    
    def createSnortDBSignatureEntry(self, dictRaw):
        dict = {}
        rels = []
        self._evalValue(dict, 'name', dictRaw['name'])        
        self._evalValue(dict, 'class', dictRaw['class'])        
        self._evalValue(dict, 'priority', dictRaw['priority'])        
        self._evalValue(dict, 'revision', dictRaw['revision'])        
        self._evalValue(dict, 'internal_id', dictRaw['internal_id'])        
        return ['snortdb_signature', dict, rels]        
    
    def createSnortDBTCPHeaderEntry(self, dictRaw):
        dict = {}
        rels = []
        self._evalValue(dict, 'source_port', dictRaw['source_port'])        
        self._evalValue(dict, 'destination_port', dictRaw['destination_port'])        
        self._evalValue(dict, 'seq', dictRaw['seq'])        
        self._evalValue(dict, 'ack', dictRaw['ack'])        
        self._evalValue(dict, 'offset', dictRaw['offset'])        
        self._evalValue(dict, 'reserved', dictRaw['reserved'])        
        self._evalValue(dict, 'flags', dictRaw['flags'])        
        self._evalValue(dict, 'window', dictRaw['window'])        
        self._evalValue(dict, 'checksum', dictRaw['checksum'])        
        self._evalValue(dict, 'urgent', dictRaw['urgent'])        
        return ['snortdb_tcp_header', dict, rels]        

    def createSnortDBUDPHeaderEntry(self, dictRaw):
        dict = {}
        rels = []
        self._evalValue(dict, 'source_port', dictRaw['source_port'])        
        self._evalValue(dict, 'destination_port', dictRaw['destination_port'])        
        self._evalValue(dict, 'length', dictRaw['length'])        
        self._evalValue(dict, 'checksum', dictRaw['checksum'])        
        return ['snortdb_udp_header', dict, rels]        

    def createSnortDBICMPHeaderEntry(self, dictRaw):
        dict = {}
        rels = []
        self._evalValue(dict, 'type', dictRaw['type'])        
        self._evalValue(dict, 'code', dictRaw['code'])        
        self._evalValue(dict, 'checksum', dictRaw['checksum'])        
        self._evalValue(dict, 'icmp_id', dictRaw['icmp_id'])        
        self._evalValue(dict, 'seq', dictRaw['seq'])        
        return ['snortdb_icmp_header', dict, rels]        
        
    def createSnortDBIPHeaderEntry(self, dictRaw, tcpHeaderRelation = None, udpHeaderRelation = None, icmpHeaderRelation = None):
        dict = {}
        rels = []
        self._evalValue(dict, 'source_ip', dictRaw['source_ip'])        
        self._evalValue(dict, 'destination_ip', dictRaw['destination_ip'])        
        self._evalValue(dict, 'version', dictRaw['version'])        
        self._evalValue(dict, 'header_length', dictRaw['header_length'])        
        self._evalValue(dict, 'tos', dictRaw['tos'])        
        self._evalValue(dict, 'datagram_length', dictRaw['datagram_length'])        
        self._evalValue(dict, 'ip_id', dictRaw['ip_id'])        
        self._evalValue(dict, 'flags', dictRaw['flags'])        
        self._evalValue(dict, 'offst', dictRaw['offst'])        
        self._evalValue(dict, 'ttl', dictRaw['ttl'])        
        self._evalValue(dict, 'protocol', dictRaw['protocol'])        
        self._evalValue(dict, 'checksum', dictRaw['checksum'])        
        if not tcpHeaderRelation:
            self._evalValue(dict, 'tcp_header_id', dictRaw['tcp_header_id'])
        else:
            rels.append(tcpHeaderRelation)
        if not udpHeaderRelation:
            self._evalValue(dict, 'udp_header_id', dictRaw['udp_header_id'])
        else:
            rels.append(udpHeaderRelation)
        if not icmpHeaderRelation:
            self._evalValue(dict, 'icmp_header_id', dictRaw['icmp_header_id'])
        else:
            rels.append(icmpHeaderRelation)
        return ['snortdb_ip_header', dict, rels]        
    
    def createSnortDBEventEntry(self, dictRaw, eventRelation = None, ipHeaderRelation = None, signatureRelation = None, sensorRelation = None, payloadRelation = None):
        dict = {}
        rels = []
        self._evalValue(dict, 'timestamp', dictRaw['timestamp'])
        self._evalValue(dict, 'sid', dictRaw['sid'])
        self._evalValue(dict, 'cid', dictRaw['cid'])
        if not eventRelation:
            self._evalValue(dict, 'event_id', dictRaw['event_id'])
        else:
            rels.append(eventRelation)
        if not sensorRelation:
            self._evalValue(dict, 'sensor_id', dictRaw['sensor_id'])
        else:
            rels.append(sensorRelation)
        if not payloadRelation:
            if dictRaw.has_key('payload_id'):
                self._evalValue(dict, 'payload_id', dictRaw['payload_id'])
        else:
            rels.append(payloadRelation)
        if not signatureRelation:
            self._evalValue(dict, 'signature_id', dictRaw['signature_id'])
        else:
            rels.append(signatureRelation)
        if not ipHeaderRelation:
            self._evalValue(dict, 'ip_header_id', dictRaw['ip_header_id'])
        else:
            rels.append(ipHeaderRelation)
        return ['snortdb_event', dict, rels]
        
        
import xmldb_infos
DATATYPES = xmldb_infos.DATATYPES

DATATYPES['snortdb_event.snortdb_event_id'] = 'bigserial'
DATATYPES['snortdb_event.event_id'] = 'bigint'
DATATYPES['snortdb_event.timestamp'] = 'timestamp'
DATATYPES['snortdb_event.sid'] = 'varchar(100)'
DATATYPES['snortdb_event.cid'] = 'varchar(100)'
DATATYPES['snortdb_event.ip_header_id'] = 'bigint'
DATATYPES['snortdb_event.signature_id'] = 'bigint'
DATATYPES['snortdb_event.sensor_id'] = 'bigint'

DATATYPES['snortdb_payload.payload_id'] = 'bigserial'
DATATYPES['snortdb_payload.data'] = 'text'

DATATYPES['snortdb_signature.signature_id'] = 'bigserial'
DATATYPES['snortdb_signature.name'] = 'varchar(255)'
DATATYPES['snortdb_signature.class'] = 'varchar(60)'
DATATYPES['snortdb_signature.priority'] = 'bigint'
DATATYPES['snortdb_signature.revision'] = 'bigint'
DATATYPES['snortdb_signature.internal_id'] = 'bigint'

DATATYPES['snortdb_sensor.sensor_id'] = 'bigserial'
DATATYPES['snortdb_sensor.hostname'] = 'text'
DATATYPES['snortdb_sensor.interface'] = 'text'
DATATYPES['snortdb_sensor.filter'] = 'text'
DATATYPES['snortdb_sensor.detail'] = 'text'
DATATYPES['snortdb_sensor.encoding'] = 'text'

DATATYPES['snortdb_ip_header.ip_header_id'] = 'bigserial'
DATATYPES['snortdb_ip_header.source_ip'] = 'bigint'
DATATYPES['snortdb_ip_header.destination_ip'] = 'bigint'
DATATYPES['snortdb_ip_header.version'] = 'int'
DATATYPES['snortdb_ip_header.header_length'] = 'int'
DATATYPES['snortdb_ip_header.tos'] = 'int'
DATATYPES['snortdb_ip_header.datagram_length'] = 'int'
DATATYPES['snortdb_ip_header.ip_id'] = 'int'
DATATYPES['snortdb_ip_header.flags'] = 'int'
DATATYPES['snortdb_ip_header.offst'] = 'int'
DATATYPES['snortdb_ip_header.offset'] = 'int'
DATATYPES['snortdb_ip_header.ttl'] = 'int'
DATATYPES['snortdb_ip_header.protocol'] = 'int'
DATATYPES['snortdb_ip_header.checksum'] = 'int'
DATATYPES['snortdb_ip_header.tcp_header_id'] = 'bigint'
DATATYPES['snortdb_ip_header.udp_header_id'] = 'bigint'
DATATYPES['snortdb_ip_header.icmp_header_id'] = 'bigint'

DATATYPES['snortdb_tcp_header.tcp_header_id'] = 'bigserial'
DATATYPES['snortdb_tcp_header.source_port'] = 'int'
DATATYPES['snortdb_tcp_header.destination_port'] = 'int'
DATATYPES['snortdb_tcp_header.seq'] = 'bigint'
DATATYPES['snortdb_tcp_header.ack'] = 'bigint'
DATATYPES['snortdb_tcp_header.offst'] = 'int'
DATATYPES['snortdb_tcp_header.reserved'] = 'int'
DATATYPES['snortdb_tcp_header.flags'] = 'int'
DATATYPES['snortdb_tcp_header.window'] = 'int'
DATATYPES['snortdb_tcp_header.checksum'] = 'int'
DATATYPES['snortdb_tcp_header.urgent'] = 'int'

DATATYPES['snortdb_udp_header.udp_header_id'] = 'bigserial'
DATATYPES['snortdb_udp_header.source_port'] = 'int'
DATATYPES['snortdb_udp_header.destination_port'] = 'int'
DATATYPES['snortdb_udp_header.length'] = 'int'
DATATYPES['snortdb_udp_header.checksum'] = 'int'

DATATYPES['snortdb_icmp_header.icmp_header_id'] = 'bigserial'
DATATYPES['snortdb_icmp_header.type'] = 'int'
DATATYPES['snortdb_icmp_header.code'] = 'int'
DATATYPES['snortdb_icmp_header.checksum'] = 'int'
DATATYPES['snortdb_icmp_header.icmp_id'] = 'int'
DATATYPES['snortdb_icmp_header.seq'] = 'int'
