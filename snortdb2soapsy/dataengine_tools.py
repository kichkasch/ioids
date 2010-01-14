"""
Some supportive functions for the data engine.

SnortDB To SoapSy (SnDB2Soapsy)

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
    
    @return: The instance for the SnDB2SoapsyPreXMLDictCreator
    @rtype: L{SnDB2SoapsyPreXMLDictCreator}
    """
    global _preXMLDictCreator
    if not _preXMLDictCreator:
        _preXMLDictCreator = SnDB2SoapsyPreXMLDictCreator()
    return _preXMLDictCreator

class SnDB2SoapsyPreXMLDictCreator(soapsytools.dataengine_tools.PreXMLDictCreator):
    """
    Extends the normal PreXMLDictCreator by functionality for the SnortDB extension.
    """

    def __init__(self):
        """
        Yet empty constructor.
        """
        pass


    def createNewSnortDBPayloadEntry(self, data):
        """
        Creates a new dict entry for the snortdb extension relation snortdb_payload.
        """
        dict = {}
        self._evalValue(dict, 'data', data)
        return ['snortdb_payload', dict, []]
        
    def createNewSnortDBSignatureEntry(self, name, classf, priority, revision, internal_id, relations = []):
        """
        Creates a new dict entry for the snortdb extension relation snortdb_signature.
        """
        dict = {}
        self._evalValue(dict, 'name', name)
        self._evalValue(dict, 'class', classf)
        self._evalValue(dict, 'priority', priority)
        self._evalValue(dict, 'revision', revision)        
        self._evalValue(dict, 'internal_id', internal_id)        
        return ['snortdb_signature', dict, relations]
    
    def createNewSnortDBSensorEntry(self, hostname, interface, filter, detail, encoding, relations = []):
        """
        Creates a new dict entry for the snortdb extension relation snortdb_sensor.
        """
        dict = {}
        self._evalValue(dict, 'hostname', hostname)
        self._evalValue(dict, 'interface', interface)
        self._evalValue(dict, 'filter', filter)
        self._evalValue(dict, 'detail', detail)
        self._evalValue(dict, 'encoding', encoding)
        return ['snortdb_sensor', dict, relations]
    
    def createNewSnortDBTCPHeaderEntry(self, src, dst, seq, ack, offset, reserved, flags, window, checksum, urgent, relations = []):
        """
        Creates a new dict entry for the snortdb extension relation snortdb_tcp_header.
        """
        dict = {}
        self._evalValue(dict, 'source_port', src)
        self._evalValue(dict, 'destination_port', dst)
        self._evalValue(dict, 'seq', seq)
        self._evalValue(dict, 'ack', ack)
        self._evalValue(dict, 'offst', offset)
        self._evalValue(dict, 'reserved', reserved)
        self._evalValue(dict, 'flags', flags)
        self._evalValue(dict, 'window', window)
        self._evalValue(dict, 'checksum', checksum)
        self._evalValue(dict, 'urgent', urgent)
        return ['snortdb_tcp_header', dict, relations]

    def createNewSnortDBUDPHeaderEntry(self, src, dst, length, checksum, relations = []):
        """
        Creates a new dict entry for the snortdb extension relation snortdb_udp_header.
        """
        dict = {}
        self._evalValue(dict, 'source_port', src)
        self._evalValue(dict, 'destination_port', dst)
        self._evalValue(dict, 'length', length)
        self._evalValue(dict, 'checksum', checksum)
        return ['snortdb_udp_header', dict, relations]
    
    def createNewSnortDBICMPPHeaderEntry(self, type, code, checksum, icmp_id, seq, relations = []):
        """
        Creates a new dict entry for the snortdb extension relation snortdb_icmp_header.
        """
        dict = {}
        self._evalValue(dict, 'type', type)
        self._evalValue(dict, 'code', code)
        self._evalValue(dict, 'checksum', checksum)
        self._evalValue(dict, 'icmp_id', icmp_id)
        self._evalValue(dict, 'seq', seq)
        return ['snortdb_icmp_header', dict, relations]

    def createNewSnortDBIPHeaderEntry(self, src, dst, version, header_length, tos, datagram_length, ip_id, flags, offset, ttl, protocol, checksum, relations = []):
        """
        Creates a new dict entry for the snortdb extension relation snortdb_ip_header.
        """
        dict = {}
        self._evalValue(dict, 'source_ip', src)
        self._evalValue(dict, 'destination_ip', dst)
        self._evalValue(dict, 'version', version)
        self._evalValue(dict, 'header_length', header_length)
        self._evalValue(dict, 'tos', tos)
        self._evalValue(dict, 'datagram_length', datagram_length)
        self._evalValue(dict, 'ip_id', ip_id)
        self._evalValue(dict, 'flags', flags)
        self._evalValue(dict, 'offst', offset)
        self._evalValue(dict, 'ttl', ttl)
        self._evalValue(dict, 'protocol', protocol)
        self._evalValue(dict, 'checksum', checksum)
        return ['snortdb_ip_header', dict, relations]
        
    
    def createNewSnortDBEventEntry(self, timestamp, sid, cid, relations = [], event_id = None):
        """
        Creates a new dict entry for the snortdb extension relation snortdb_event.
        """
        dict = {}
        self._evalValue(dict, 'timestamp', timestamp)
        self._evalValue(dict, 'sid', sid)
        self._evalValue(dict, 'cid', cid)
        self._evalValue(dict, 'event_id', event_id)
        return ['snortdb_event', dict, relations]        
        
    def createSnortDBEventEntry(self, dictRaw, eventRelation, ipHeaderRelation, sensorRelation, signatureRelation):
        dict = {}
        rels = []
##        self._evalValue(dict, 'timestamp_received', dictRaw['timestamp_received'])
##        self._evalValue(dict, 'community_id', dictRaw['community_id'])
##        if not eventRelation:
##            self._evalValue(dict, 'event_id', dictRaw['event_id'])
##        else:
##            rels.append(eventRelation)
        return ['snortdb_event', dict, rels]
