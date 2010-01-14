"""
Module which does the acutal work on the database.

SnortDB To SoapSy (SnDB2Soapsy)

@author: Michael Pilgermann
@contact: mailto:mpilgerm@glam.ac.uk
@license: GPL (General Public License)
"""

import time
import config
import pg
import dataengine_tools
import dbconnector


class DatabaseAction:
    """
    Works like a trigger on the source SnortDB database and checks frequently for new events.
    """

    def __init__(self):
        """
        Loads settings from the config file.
        
        Use L{startup} to make this module really running!
        """
        self._dbhost = config.DB_HOST
        self._dbport = config.DB_PORT 
        self._dbname = config.DB_DATABASENAME 
        self._dbuser = config.DB_USERNAME 
        self._dbpassword = config.DB_PASSWORD 
        self._dboptions = None
        self._dbtty = None
        
        self._interval = config.DB_POLL_INTERVAL
    
    def startup(self):
        """
        Establishes the database connection regarding to settings in the config file and
        keeps us running forever.
        """
        self._dictCreator = dataengine_tools.getPreXMLDictCreator()
        self._DBConnector = dbconnector.getDBConnector()
        self._DBConnector.connect()
        
        lastestEventOid = '0'
        try:
            filename = config.EVENT_STATUS_LOCATION
            file = open(filename, 'r')
            lastestEventOid = file.readline()
            file.close()
        except Exception, msg:
            pass
        
        lastestEventOid = int(lastestEventOid)
        self._connection = pg.connect(self._dbname, self._dbhost, self._dbport, self._dboptions, self._dbtty, self._dbuser, self._dbpassword)
        while 1:
            lastestEventOid = self._triggerNow(lastestEventOid)
            file = open(filename, 'w')
            file.write(str(lastestEventOid) + "\n")
            file.close()
            time.sleep(self._interval)
        
        
    def _getEventsFromDbOverOid(self, min_oid):
        """
        Collects events from the database with oid greater than or equal the given one.
        """
        query = """select oid, sid, cid, signature, timestamp from event where oid > '""" + str(min_oid) + """'"""
        result = self._connection.query(query)
        list = result.getresult()
        returnList = []
        for item in list:
            newItem = {}
            newItem['oid'] = item[0]
            newItem['sid'] = str(item[1])
            newItem['cid'] = str(item[2])
            newItem['signature'] = item[3]
            newItem['timestamp'] = item[4]
            returnList.append(newItem)
            if int(item[0]) > min_oid:
                min_oid = int(item[0])
        return returnList, min_oid
        
    def _getSensorInformation(self, sid):
        """
        Collect information about one sensor from the database.
        """
        query = """select sid, hostname from sensor where sid = '""" + str(sid) + """'"""
        result = self._connection.query(query)
        list = result.getresult()
        item = list[0]
        newSensor = {}
        newSensor['name'] = item[1]
        return newSensor
        
    def _createObserverFromSensor(self, sensor):
        """
        Create a new SoapSy observer from SnortDB sensor information.
        """
        computer =self._dictCreator.createNewComputerEntry(sensor['name'], None, None, None, None, [])
        agent = self._dictCreator.createNewAgentEntry(config.SOAPSY_OBSERVER_AGENT_NAME, [computer], '2')
        observer = self._dictCreator.createNewObserverEntry(config.SOAPSY_OBSERVER_NAME,[agent])
        return observer
        
    def _createLocalReporter(self):
        """
        Create a new SoapSy reporter from local information as given in the config file.
        """
        computer = self._dictCreator.createNewComputerEntry(config.SOAPSY_LOCAL_NAME, 
            config.SOAPSY_LOCAL_OS, config.SOAPSY_LOCAL_IP, config.SOAPSY_LOCAL_MAC, config.SOAPSY_LOCAL_DOMAIN, [])
        agent = self._dictCreator.createNewAgentEntry(config.SOAPSY_LOCAL_AGENT_NAME, [computer], '2')
        reporter = self._dictCreator.createNewReporterEntry(config.SOAPSY_LOCAL_REPORTER_NAME,[agent])
        return reporter
        
    def _convertIPDecToStr(self, ipDec):
        """
        Converts a decimal encoded IP nummer into its string representation.
        """
        ipStr = ''
        for i in range(0,3):
            ipStr += str(ipDec % 256) + "."
            ipDec = ipDec / 256
        ipStr += str(ipDec)
        return ipStr
        
    def _getSrcAndDestIP(self, sid, cid):
        """
        Collects source and destination IP address for a SnortDB event.
        """
        query = """select ip_src, ip_dst from iphdr where sid = '""" + str(sid) + """' and cid = '""" + str(cid) + """'"""
        result = self._connection.query(query)
        list = result.getresult()
        if len(list) == 0:
            return None, None
        item = list[0]
        srcIP = item[0]
        dstIP = item[1]
        return self._convertIPDecToStr(srcIP), self._convertIPDecToStr(dstIP)
        
    def _getData(self, sid, cid):
        """
        Collects the payload of a SnortDB event.
        """
        query = """select data_payload from data where sid = '""" + str(sid) + """' and cid = '""" + str(cid) + """'"""
        result = self._connection.query(query)
        list = result.getresult()
        if len(list) == 0:
            return None
        item = list[0]
        data = item[0]
        return data
        
    def _getSignatureInfo(self, signature_id):
        """
        Collects available signature information for one signature id.
        
        Including its linked information about signatures classification.
        """
        query = """select sig_name, sig_priority, sig_rev, sig_sid, sig_class_name from signature, sig_class where signature.sig_class_id=sig_class.sig_class_id and sig_id = '""" + str(signature_id) + """'"""
        result = self._connection.query(query)
        list = result.getresult()
        if len(list) == 0:
            return None
        item = list[0]
        dict = {}
        dict['name'] = str(item[0])
        dict['class'] = str(item[4])
        dict['priority'] = str(item[1])
        dict['revision'] = str(item[2])
        dict['internal_id'] = str(item[3])
        return dict
    
    def _getSensorInfo(self, sid):
        """
        Collects sensor information from the SnortDB database.
        
        Including its linked information about details and encoding.
        """
        query = """select hostname, interface, filter, detail_text, encoding_text from sensor, detail, encoding where sensor.detail = detail.detail_type and sensor.encoding = encoding.encoding_type and sensor.sid = '""" + str(sid) + """'"""
        result = self._connection.query(query)
        list = result.getresult()
        if len(list) == 0:
            return None
        item = list[0]
        dict = {}
        dict['hostname'] = str(item[0])
        dict['interface'] = str(item[1])
        dict['filter'] = str(item[2])
        dict['detail'] = str(item[3])
        dict['encoding'] = str(item[4])
        return dict
        
    def _getHeaderInfoQuery(self, sid, cid, table, attributes):
        """
        Collects information about one header entry (IP, TCP, UDP or ICMP) from the database.
        """
        atts = str(attributes[0][0])
        for att, realName in attributes[1:]:
            atts += ", " + str(att)
        
        query = """select """ + atts + """ from """ + table + """ where sid = '""" + str(sid) + """' and cid = '""" + str(cid) + """'"""
        result = self._connection.query(query)
        list = result.getresult()
        if len(list) == 0:
            return None
        item = list[0]
        dict = {}
        for i in range(0,len(attributes)):
            dict[attributes[i][1]] = str(item[i])
        return dict
        
        
    def _getHeaderInfo(self, sid, cid):
        """
        Integrates the header information of all protocols (IP, TCP, UDP and ICMP) for one event.
        
        @return: IP header, TCP header, UDP header, ICMP header
        """
        ip = self._getHeaderInfoQuery(sid, cid, 'iphdr', [('ip_src','source_ip'), ('ip_dst', 'destination_ip'), ('ip_ver', 'version'), ('ip_hlen', 'header_length'), ('ip_tos', 'tos'), ('ip_len', 'datagram_length'), ('ip_id', 'ip_id'), ('ip_flags', 'flags'), ('ip_off', 'offst'), ('ip_ttl', 'ttl'), ('ip_proto', 'protocol'), ('ip_csum', 'checksum')])
        tcp = self._getHeaderInfoQuery(sid, cid, 'tcphdr', [('tcp_sport', 'source_port'), ('tcp_dport', 'destination_port'), ('tcp_seq', 'seq'), ('tcp_ack', 'ack'), ('tcp_off', 'offst'), ('tcp_res', 'reserved'), ('tcp_flags', 'flags'), ('tcp_win', 'window'), ('tcp_csum', 'checksum'), ('tcp_urp', 'urgent')])
        udp = self._getHeaderInfoQuery(sid, cid, 'udphdr', [('udp_sport', 'source_port'), ('udp_dport', 'destination_port'), ('udp_len', 'length'), ('udp_csum', 'checksum')])
        icmp = self._getHeaderInfoQuery(sid, cid, 'icmphdr', [('icmp_type', 'type'), ('icmp_code', 'code'), ('icmp_csum', 'checksum'    ), ('icmp_id', 'icmp_id'), ('icmp_seq', 'seq')])
        return ip, tcp, udp, icmp
        
    def _createSourceFromIP(self, ip):
        """
        Creates a SoapSy source entry from an ip address and local information provided in the config file.
        """
        computer =self._dictCreator.createNewComputerEntry(ip, None, ip, None, None, [])
        agent = self._dictCreator.createNewAgentEntry(config.SOAPSY_SOURCE_AGENT_NAME, [computer], '2')
        source = self._dictCreator.createNewSourceEntry(config.SOAPSY_SOURCE_NAME,[agent])
        return source

    def _createDestinationFromIP(self, ip):
        """
        Creates a SoapSy destination entry from an ip address and local information provided in the config file.
        """
        computer =self._dictCreator.createNewComputerEntry(ip, None, ip, None, None, [])
        agent = self._dictCreator.createNewAgentEntry(config.SOAPSY_DESTINATION_AGENT_NAME, [computer], '2')
        destination = self._dictCreator.createNewDestinationEntry(config.SOAPSY_DESTINATION_NAME,[agent])
        return destination
        
        
    def _triggerNow(self, lastestEventOid):
        """
        Collects the latest events from the SnortDB database and creates a complete entry in the SoapSy database includinig SnortDB extension with as much information as possible.
        """
        dictEvents, lastestEventOid = self._getEventsFromDbOverOid(lastestEventOid)
        for event in dictEvents:
            snortEventRelations = []
        
            sensor = self._getSensorInformation(event['sid'])
            observer = self._createObserverFromSensor(sensor)
            reporter = self._createLocalReporter()
            srcIP, dstIP = self._getSrcAndDestIP(event['sid'], event['cid'])
            source = self._createSourceFromIP(srcIP)
            destination = self._createDestinationFromIP(dstIP)
            eventType = self._dictCreator.createNewEventTypeEntry(config.SOAPSY_EVENT_TYPE_NAME)
            
            eventEntry = self._dictCreator.createNewEventEntry(event['timestamp'], [observer, reporter, source, destination, eventType])
            snortEventRelations.append(eventEntry)
            
            payload = self._getData(event['sid'], event['cid'])
            if payload:
                payloadEntry = self._dictCreator.createNewSnortDBPayloadEntry(payload)
                snortEventRelations.append(payloadEntry)
            
            signatureInfo = self._getSignatureInfo(event['signature'])
            if signatureInfo:
                signatureEntry = self._dictCreator.createNewSnortDBSignatureEntry(signatureInfo['name'], signatureInfo['class'],signatureInfo['priority'], signatureInfo['revision'], signatureInfo['internal_id'])
                snortEventRelations.append(signatureEntry)
            
            sensorInfo = self._getSensorInfo(event['sid'])
            if sensorInfo:
                sensorEntry = self._dictCreator.createNewSnortDBSensorEntry(sensorInfo['hostname'], sensorInfo['interface'], sensorInfo['filter'], sensorInfo['detail'], sensorInfo['encoding'])
                snortEventRelations.append(sensorEntry)
            
            ip, tcp, udp, icmp = self._getHeaderInfo(event['sid'], event['cid'])
            if ip:
                ipRels = []
                if tcp:
                    tcpEntry = self._dictCreator.createNewSnortDBTCPHeaderEntry(tcp['source_port'], tcp['destination_port'], tcp['seq'], tcp['ack'], tcp['offst'], tcp['reserved'], tcp['flags'], tcp['window'], tcp['checksum'], tcp['urgent'])
                    ipRels.append(tcpEntry)
                if udp:
                    udpEntry = self._dictCreator.createNewSnortDBUDPHeaderEntry(udp['source_port'], udp['destination_port'], udp['length'], udp['checksum'])
                    ipRels.append(udpEntry)
                if icmp:
                    icmpEntry = self._dictCreator.createNewSnortDBICMPPHeaderEntry(icmp['type'], icmp['code'], icmp['checksum'], icmp['icmp_id'], icmp['seq'])
                    ipRels.append(icmpEntry)
                ipEntry = self._dictCreator.createNewSnortDBIPHeaderEntry(ip['source_ip'], ip['destination_ip'], ip['version'], ip['header_length'], ip['tos'], ip['datagram_length'], ip['ip_id'], ip['flags'], ip['offst'], ip['ttl'], ip['protocol'], ip['checksum'], ipRels)
                snortEventRelations.append(ipEntry)
            
            snortEventEntry = self._dictCreator.createNewSnortDBEventEntry(event['timestamp'], event['sid'], event['cid'], snortEventRelations )
            primKey = self._DBConnector.insertSnortDBEvent(snortEventEntry)
            print "Inserted snort event into SoapSy with key %s" %(primKey)
##            import ioids.support.dictviewer
##            ioids.support.dictviewer.showNow(snortEventEntry)
            
        return lastestEventOid
        
    def shutdown(self):
        """
        Shutdown the database connections.
        """
        self._connection.close()
        self._DBConnector.disconnect()
        
