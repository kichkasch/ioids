"""
Handles all concerns for wrapping and parsing xml data.

Tools for SoapSy

@author: Michael Pilgermann
@contact: mailto:mpilgerm@glam.ac.uk
@license: GPL (General Public License)
"""

import xml.dom
from xml.dom import Node
import xml.dom.ext.reader.Sax2
from StringIO import StringIO
import xml.dom.ext

from xmldb_infos import DATATYPES

# "singleton"
_genericWrapper = None
def getGenericWrapper():
    """
    Singleton implementation.
    
    @return: The instance for the generic wrapper class
    @rtype: L{GenericWrapper}
    """
    global _genericWrapper
    if not _genericWrapper:
        _genericWrapper = GenericWrapper()
    return _genericWrapper

class GenericWrapper:
    """
    Wrapper for generic functionality.
    """
    def __init__(self):
        """
        Yet empty constructor.
        """
        pass
        
    def _toXml(self, doc):
        """
        Creates the XML string from the dom tree.
        """
        stio = StringIO()
        xml.dom.ext.PrettyPrint(doc, stio)
        value = stio.getvalue()
        stio.close()
        return value
        
# "singleton"
_xmlDBWrapper = None
def getXMLDBWrapper():
    """
    Singleton implementation.
    
    @return: The instance for the generic wrapper class
    @rtype: L{GenericWrapper}
    """
    global _xmlDBWrapper
    if not _xmlDBWrapper:
        _xmlDBWrapper = XMLDBWrapper()
    return _xmlDBWrapper
        
class XMLDBWrapper(GenericWrapper):
    """
    Wrapper / Parser for XML database queries / replies.
    """
    def __init__(self, dbDataType = 'Postgresv8.0'):
        """
        Yet empty constructor.
        """
        self._dbDataType = dbDataType
        
    def wrapSelect(self, relation, value = 'all' , attributes = []):
        """
        Wraps a SQL select into the appropriate XML representation.
        
        @param relation: Name of the relation, this select is for
        @type relation: C{String}
        @param value: Which columns are requested (comma seperated or place holder all)
        @type value: C{String}
        @param attirbutes: List of attributes (the where bit of a select) - each entry is a list of [Attribute name | operation | Value]
        @type attributes: C{List} of C{List} of C{String}
        @return: The xml representation of the query
        @rtype: C{String}
        """
        impl = xml.dom.getDOMImplementation()
        doc = impl.createDocument(None, 'RELATIONS', None)
        elementRoot = doc.documentElement
        elementRoot.setAttribute('command', 'SELECT')
        
        elementRelation = doc.createElement('REL')
        elementRoot.appendChild(elementRelation)
        elementRelation.setAttribute('name', relation)
        elementRelation.setAttribute('val', value)
        
        for att in attributes:
            elementAttribute = doc.createElement('ATT')
            elementRelation.appendChild(elementAttribute)
            elementAttribute.setAttribute('name', att[0])
            elementAttribute.setAttribute('op', att[1])
            attValue = doc.createTextNode(att[2])
            elementAttribute.appendChild(attValue)            

        return self._toXml(doc)

        
    def _wrapInsertRecursive(self, relation, attributes, parentNode, doc, references = []):
        elementRelation = doc.createElement('REL')
        parentNode.appendChild(elementRelation)
        elementRelation.setAttribute('name', relation)
        
##        print "Attributes (%s): %s" %(relation, attributes)
        for attkey in attributes.keys():
            value = attributes[attkey]
            
            elementAttribute = doc.createElement('ATT')
            elementRelation.appendChild(elementAttribute)
            elementAttribute.setAttribute('name', attkey)
            
            try:
                type = DATATYPES[relation + "." + attkey]
            except KeyError, msg:
                from errorhandling import SoapsyToolsDependencyException
                raise SoapsyToolsDependencyException('Data type for attribute %s in relation %s unknown. Check module xmldb_infos. Error msg: %s' %(attkey, relation, msg))
            elementAttribute.setAttribute('type', type)
            
            attValue = doc.createTextNode(value)
            elementAttribute.appendChild(attValue)   
    
        for reference in references:
            self._wrapInsertRecursive(reference[0], reference[1], elementRelation, doc, reference[2])
    
        
    def wrapInsert(self, relation, attributes, references = []):
        """
        Wraps a SQL insert into the appropriate XML representation.
        
        @param relation: Name of the (top level) table, to create the XML tree for
        @type relation: C{String}
        @param attributes: Dictionary with attributes for the (top level) table (column title : column value)
        @type attributes: C{dict} - (C{String} : C{String})
        @param references: References tables (List of list: [['table_a', attributes_a, references_a], ['table_b', attributes_b, references_b]])
        @type references: C{List} of C{List}
        @param parentNode: Parent node in the DOM tree; if None, a new document will be created and the root element will be created
        @type parentNode: L{xml.dom.Node}
        @return: XML representation of the structure
        @rtype: C{String}
        """
        impl = xml.dom.getDOMImplementation()
        doc = impl.createDocument(None, 'RELATIONS', None)
        elementRoot = doc.documentElement
        elementRoot.setAttribute('command', 'INSERT')
        
        elementRoot.setAttribute('datatype', self._dbDataType)

        self._wrapInsertRecursive(relation, attributes, elementRoot, doc, references)
        return self._toXml(doc)
        
    def parseInsertReply(self, xmlString):
        """
        Parses the XML reply to an insert requests and extracts the primary keys.
        
        @return: List of primary keys together with their relation names and column names for the primary key (relation | column name | primary key entry)
        @rtype: C{List} of C{List}
        """
        from errorhandling import SoapsyToolsFormatException
        
        try:
            root = xml.dom.ext.reader.Sax2.FromXml(xmlString)
        except Exception, msg:
            print "!!!!!!!!! Internal message format error - XML message:\n****************\n%s\n**************\n" %(xmlString)
            raise SoapsyToolsFormatException("XML Format string error: %s" %(msg))
        node = root.childNodes[1]
        if node.nodeName != 'RELATIONS':
            raise SoapsyToolsFormatException('This is not a reply from the xml rpc server at all.')
        
        commandAtt = node.getAttribute('command')
        if not commandAtt or commandAtt != 'INSERT_RESULTS':
            print "Error message from server:\n****************\n%s\n**************\n" %(xmlString)
            raise SoapsyToolsFormatException('This is not a reply from the xml rpc server for a select request.')
            
        # let's go and parse the result set
        results = []
        for child1 in node.childNodes:
            if child1.nodeType == Node.ELEMENT_NODE:
                if child1.nodeName == 'REL':
##                    result = []
                    name = child1.getAttribute('name')
                    if not name:
                        raise SoapsyToolsFormatException('No name for relation found for the entry.')

                    for child3 in child1.childNodes:
                        if child3.nodeType == Node.ELEMENT_NODE:
                            if child3.nodeName == 'ATT':
                                attName = child3.getAttribute('name')
                                if not attName:
                                    raise SoapsyToolsFormatException('Name primary key column not specified.')
                                value = None
                                for child4 in child3.childNodes:
                                    if child4.nodeType == Node.TEXT_NODE:
                                        value = child4.nodeValue
                                results.append([name, attName, value])
                            else:
                                raise SoapsyToolsFormatException('Unrecognised tag in xml select query result: %s.' %(child3.nodeName))
                        
                else:
                    raise SoapsyToolsFormatException('Unrecognised tag in xml select query result: %s.' %(child1.nodeName))
        return results
        
    def parseSelectReply(self, xmlString):
        """
        Parses the XML string and extracts the dataset information into dictionaries.
        
        @param xmlString: XML representation of the select query result
        @type xmlString: C{String}
        @return: List of entries
        @rtype: C{List} of C{Dict}
        """
        from errorhandling import SoapsyToolsFormatException
        
        try:
            root = xml.dom.ext.reader.Sax2.FromXml(xmlString)
        except Exception, msg:
            print "!!!!!!!!! Internal message format error - XML message:\n****************\n%s\n**************\n" %(xmlString)
            raise SoapsyToolsFormatException("XML Format string error: %s" %(msg))
            
        node = root.childNodes[1]
        if node.nodeName != 'RELATIONS':
            raise SoapsyToolsFormatException('This is not a reply from the xml rpc server at all.')
        
        commandAtt = node.getAttribute('command')
        if not commandAtt or commandAtt != 'SELECT_RESULTS':
            raise SoapsyToolsFormatException('This is not a reply from the xml rpc server for a select request. + \n*************\n%s\n****************\n' %(xmlString))
            
        # let's go and parse the result set
        results = []
        totalResults = None
            
        for child1 in node.childNodes:
            if child1.nodeType == Node.ELEMENT_NODE:
                if child1.nodeName == 'REL':
                    result = {}
                    name = child1.getAttribute('name')
                    if not name:
                        raise SoapsyToolsFormatException('No result ID provided for select query result.')

                    if name == 'TOTAL_RESULTS':
                        for child2 in child1.childNodes:
                            if child2.nodeType == Node.TEXT_NODE:
                                totalResults  = int(child2.nodeValue)
                        continue
                        
                    if name != 'RESULTS_ID':
                        raise SoapsyToolsFormatException('Unknown value for name: %s.' %(name))
                    id = child1.getAttribute('value')
                    if not id:
                        raise SoapsyToolsFormatException('No ID provided for the result!')
                    result['result_id'] = id
                    result['relations'] = []
                    for child2 in child1.childNodes:
                        if child2.nodeType == Node.ELEMENT_NODE:
                            if child2.nodeName == 'REL':
                                name = child2.getAttribute('name')
                                if name == 'TOTAL_RECORDS':
                                    for child3 in child2.childNodes:
                                        if child3.nodeType == Node.TEXT_NODE:
                                            totalRecords = int(child3.nodeValue)
                                            result['number_records'] = int (totalRecords)
                                else:       # here we have a name for a relation
                                    resultOneTable = {}
                                    table_name = name
                                    resultOneTable['name'] = table_name
                                    resultOneTable['attributes'] = {}
                                    for child3 in child2.childNodes:
                                        if child3.nodeType == Node.ELEMENT_NODE:
                                            if child3.nodeName == 'ATT':
                                                attName = child3.getAttribute('name')
                                                if not attName:
                                                    raise SoapsyToolsFormatException('Name for attribute no specified.')
                                                value = None
                                                for child4 in child3.childNodes:
                                                    if child4.nodeType == Node.TEXT_NODE:
                                                        value = child4.nodeValue
                                                resultOneTable['attributes'][attName] = value
                                            else:
                                                raise SoapsyToolsFormatException('Unrecognised tag in xml select query result: %s.' %(child3.nodeName))
                                    result['relations'].append(resultOneTable)
                            else:
                                raise SoapsyToolsFormatException('Unrecognised tag in xml select query result: %s.' %(child2.nodeName))
                    results.append(result)
                    
                else:
                    raise SoapsyToolsFormatException('Unrecognised tag in xml select query result: %s.' %(child1.nodeName))
                    
        return totalResults, results

        
class EventMessageWrapper(GenericWrapper):

    def _getValueInTree(self, relation, path):
        if len(path) == 1:
            return relation[1][path[0]]
        for rel in relation[2]:
            if rel[0] == path[0]:
                return self._getValueInTree(rel, path[1:])
        raise KeyError('Value not found in tree: %s.' %(path))
                
    def _getRelationInTree(self, relation, path):
        for rel in relation[2]:
            if rel[0] == path[0]:
                if len(path) == 1:
                    return rel
                return self._getRelationInTree(rel, path[1:])
        raise KeyError('Relation not found in tree: %s.' %(path))

    def _wrapAnyItemToDom(self, item, parentNode, doc):
        elementItem = doc.createElement(item[0])
        parentNode.appendChild(elementItem)
        for attName in item[1].keys():
            elementItem.setAttribute(attName, item[1][attName])
        for rel in item[2]:
            self._wrapAnyItemToDom(rel, elementItem, doc)
            
    ##
    ## from here we have IDMEF stuff; which is not in use any more
    ##
    def _assembleNode(self, agent, parentNode, doc):
        elementNode = doc.createElement('Node')
        elementNode.setAttribute('category', 'unknown')
        parentNode.appendChild(elementNode)
        
        # first the computer
        try:
            computer = self._getRelationInTree(agent, ['computer'])
            if computer[1].has_key('hostname'):
                elementName = doc.createElement('name')
                elementNode.appendChild(elementName)
                nameText = doc.createTextNode(computer[1]['hostname'])
                elementName.appendChild(nameText)
            if computer[1].has_key('ip'):
                elementAddress = doc.createElement('Address')
                elementAddress.setAttribute('category', 'ipv4-addr')
                elementNode.appendChild(elementAddress)
                elementAddressValue = doc.createElement('address')
                elementAddress.appendChild(elementAddressValue)
                addressText = doc.createTextNode(computer[1]['ip'])
                elementAddressValue .appendChild(addressText )                
        except Exception, msg:
            pass    #ok, no info here :(
        
    def _assembleProcess(self, agent, parentNode, doc):
        try:
            elementProcess = doc.createElement('Process')
            process = self._getRelationInTree(agent, ['process'])
            processName = self._getValueInTree(process, ['prcss_name', 'process_name'])
            elementName = doc.createElement('name')
            nameText = doc.createTextNode(processName)
            elementName.appendChild(nameText)
            elementProcess.appendChild(elementName)
            if process[1].has_key('prcss_pid'):
                pid = process[1]['prcss_pid']
                elementPid = doc.createElement('pid')
                pidText = doc.createTextNode(pid)
                elementPid.appendChild(pidText)
                elementProcess.appendChild(elementPid)
            parentNode.appendChild(elementProcess)
        except Exception, msg:
            print "tmp error: %s" %msg
            pass        # ok, looks like we don't have process information :)

    def _assembleIdmefFromEvent(self, event, parentNode, doc):
        elementIdmef = doc.createElement('IDMEF-Message')
        elementIdmef.setAttribute('version', '1.0')
        parentNode.appendChild(elementIdmef)
        
        elementAlert = doc.createElement('Alert')
        elementIdmef.appendChild(elementAlert)

        observer = self._getRelationInTree(event, ['observer'])     # used as Analyzer in IDMEF
        elementAnalyzer = doc.createElement('Analyzer')
        try:
            elementAnalyzer.setAttribute('name', observer[1]['obsrv_name'])
        except KeyError, msg:
            elementAnalyzer.setAttribute('name', 'unknown')
        observerAgent = self._getRelationInTree(observer,['agent'])
        self._assembleProcess(observerAgent, elementAnalyzer, doc)
        elementAlert.appendChild(elementAnalyzer)
        self._assembleNode(self._getRelationInTree(observer, ['agent']), elementAnalyzer, doc)
        
        source= self._getRelationInTree(event, ['source'])      # also source in IDMEF
        elementSource = doc.createElement('Source')
        elementAlert.appendChild(elementSource)
        self._assembleNode(self._getRelationInTree(source, ['agent']), elementSource, doc)
        
        dest = self._getRelationInTree(event, ['destination'])  # target in IDMEF
        elementTarget = doc.createElement('Target')
        elementAlert.appendChild(elementTarget)
        self._assembleNode(self._getRelationInTree(dest, ['agent']), elementTarget, doc)
        
        timestamp = event[1]['timestmp']
        elementTimestamp = doc.createElement('CreateTime')
        elementAlert.appendChild(elementTimestamp)
        timeText = doc.createTextNode(timestamp)
        elementTimestamp.appendChild(timeText)
        
        elementClass = doc.createElement('Classification')
        elementClass.setAttribute('text','unknown')
        elementAlert.appendChild(elementClass)
        
        # finally let's put the additinal data
        self._assembleAdditionalDataForIdmefFromEvent(event, elementAlert, doc)
  
    def _assemblePlainEvent(self, event, parentNode, doc):
        """
        Assembles the DOM structure for an event in IDMEF syntax.
        """
        elementEvent = doc.createElement('plainevent')
        parentNode.appendChild(elementEvent)
        self._wrapAnyItemToDom(event, elementEvent, doc)
        # old (IDMEF version)
##        elementEvent = doc.createElement('event')
##        parentNode.appendChild(elementEvent)
##        self._assembleIdmefFromEvent(event, elementEvent, doc)
