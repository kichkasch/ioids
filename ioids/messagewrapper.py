"""
Handles all concerns for wrapping and parsing xml data.

Inter-Organisational Intrusion Detection System (IOIDS)

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

import soapsytools.messagewrapper

# "singleton"
_genericWrapper = None
def getGenericWrapper():
    """
    Singleton implementation.
    
    @return: The instance for the generic wrapper class
    @rtype: L{soapsytools.messagewrapper.GenericWrapper}
    """
    soapsytools.messagewrapper.getGenericWrapper()

        
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
        _xmlDBWrapper = IoidsXMLDBWrapper()
    return _xmlDBWrapper
        
class IoidsXMLDBWrapper(soapsytools.messagewrapper.XMLDBWrapper):
    """
    Wrapper / Parser for XML database queries / replies.
    """
    def __init__(self):
        """
        Yet empty constructor.
        """
        from config import DB_DATA_TYPE
        soapsytools.messagewrapper.XMLDBWrapper.__init__(self, DB_DATA_TYPE)

    
# "singleton"
_ioidsMessageWrapper = None
def getIoidsMessageWrapper():
    """
    Singleton implementation.
    
    @return: The instance for the ioids message wrapper class
    @rtype: L{IoidsMessageWrapper}
    """
    global _ioidsMessageWrapper 
    if not _ioidsMessageWrapper :
        _ioidsMessageWrapper  = IoidsMessageWrapper()
    return _ioidsMessageWrapper 

class IoidsMessageWrapper(soapsytools.messagewrapper.EventMessageWrapper):
    """
    Wrapper for messages to be exchanged between IOIDS nodes.
    """
    
    def __init__(self):
        """
        Yet empty constructor.
        """
        pass
          
    def _assembleIoidsEventSubMessage(self, ioidsEvent, parentNode, doc):
        """
        Assemble the tree underneath a IOIDS event (no relations).
        """
        # the following (commented) code was made for incorperating IDMEF as message standard
        # for the base - event information
        # it has been decided, however, to use another (db alligned) message format ...
##        elementIoidsEvent = doc.createElement('ioidsevent')
##        parentNode.appendChild(elementIoidsEvent)
        
##        sender = None
##        source = None
##        event = None
##        classification = None
##        classificationCode = None
##        for rel in ioidsEvent[2]:
##            if rel[0] == 'ioids_sender':
##                sender = self._getValueInTree(rel, ['ioids_peer', 'peer_memberid'])
##            if rel[0] == 'ioids_source':
##                source = self._getValueInTree(rel, ['ioids_peer', 'peer_memberid'])
##            if rel[0] == 'ioids_classification':
##                classification = rel[1]['classification_name']
##                classification_code = rel[1]['classification_code']
##            if rel[0] == 'event':
##                event = rel
##
##        if sender:
##            elementSender = doc.createElement('sender')
##            elementIoidsEvent.appendChild(elementSender)
##            senderText = doc.createTextNode(sender)
##            elementSender.appendChild(senderText)
##
##        if source:
##            elementSource = doc.createElement('source')
##            elementIoidsEvent.appendChild(elementSource)
##            sourceText = doc.createTextNode(source)
##            elementSource.appendChild(sourceText)
##            
##        if classification and classification_code:
##            elementClassification = doc.createElement('classification')
##            elementIoidsEvent.appendChild(elementClassification)
##            elementClassification.setAttribute('code', classification_code)
##            classificationText = doc.createTextNode(classification)
##            elementClassification.appendChild(classificationText)
##
##        if event:
##            self._assemblePlainEvent(event, elementIoidsEvent, doc)
##            
##        elementCommunity = doc.createElement('community')
##        elementIoidsEvent.appendChild(elementCommunity)
##        communityText = doc.createTextNode(ioidsEvent[1]['community_id'])
##        elementCommunity.appendChild(communityText)

        # all we need to do now, is wrapping the ioids event into the corrosponding XML structure
        self._wrapAnyItemToDom(ioidsEvent, parentNode, doc)
  
        
    def _assembleAdditionalDataForIdmefFromEvent(self, event, parentNode, doc):
        elementAddData = doc.createElement('AdditionalData')
        elementAddData.setAttribute('type', 'xml')
        elementAddData.setAttribute('meaning', 'ioids remaining information')
        
        elementReporter = doc.createElement('ioids:Reporter')
        reporter = self._getRelationInTree(event, ['reporter']) 
        try:
            elementReporter.setAttribute('ioids:name', reporter[1]['rprt_name'])
        except KeyError, msg:
            pass
        self._assembleNode(self._getRelationInTree(reporter, ['agent']), elementReporter, doc)
        
        elementAddData.appendChild(elementReporter)
        
        parentNode.appendChild(elementAddData)
        
    def _assembleExtension(self, extension, parentNode, doc):
        elementExtension = doc.createElement('extension')
        elementExtension.setAttribute('type', extension[1]['extension_name'])
        parentNode.appendChild(elementExtension)
        getExtensionWrapperHandler().getFullExtensionMessage(extension[1]['extension_name'], extension[2][0], elementExtension, doc)
        
    def _assembleRelatedEvent(self, relation, parentNode, doc):
        event = self._getRelationInTree(relation, ['event']) 
        rel_type = self._getValueInTree(relation, ['ioids_relation_type', 'ioids_relation_type_name'])
        extension = self._getRelationInTree(relation, ['extension']) 
        elementRelation = doc.createElement('relation')
        elementRelation.setAttribute('type', rel_type)
        parentNode.appendChild(elementRelation)
        self._assemblePlainEvent(event, elementRelation, doc)
        self._assembleExtension(extension, elementRelation, doc)
  
    def assembleIoidsMessage(self, ioidsEvent, relatedEvents = [], doc = None, parentNode = None):
        """
        Assembled the XML message for the given ioids event.
        
        @param ioidsEvent: Information of the IOIDS event in list / dict format (name, attrbutes, relations)
        @type ioidsEvent: C{List} of [C{String}, C{Dict}, C{List}]
        @param relatedEvents: Information about related events for the given IOIDS event. Each relation as couple (type / pure event / extension information)
        @type relatedEvents: C{List} of Couples
        """
        if parentNode:
            elementRoot = doc.createElement('ioids')
            parentNode.appendChild(elementRoot)
        else:
            impl = xml.dom.getDOMImplementation()
            doc = impl.createDocument(None, 'ioids', None)
            elementRoot = doc.documentElement
        
        self._assembleIoidsEventSubMessage(ioidsEvent, elementRoot, doc)
        
        elementRelations = doc.createElement('relations')
        elementRoot.appendChild(elementRelations)
        
        for rel in relatedEvents:
            self._assembleRelatedEvent(rel, elementRelations, doc)
        
        if not parentNode:
            return self._toXml(doc)
        
    def _unwrapSomething(self, domNode):
        dict = {}
        relations = []
        attDict = domNode._get_attributes()
        for key in attDict.keys():
            dict[key[1]] = domNode.getAttribute(key)
        for child in domNode.childNodes:
            if child.nodeType == Node.ELEMENT_NODE:
                relations.append(self._unwrapSomething(child))
        return [domNode.nodeName, dict, relations]
        
    def unwrapFullIoidsEventMessage(self, data, domNode = None):
        from errorhandling import IoidsFormatException
        
        if not domNode:
            try:
                root = xml.dom.ext.reader.Sax2.FromXml(data)
            except Exception, msg:
    ##            print "!!!!!!!!! Internal message format error - XML message:\n****************\n%s\n**************\n" %(data)
                raise IoidsFormatException("XML Format string error: %s" %(msg))
            node = root.childNodes[1]
        else:
            node = domNode
        if node.nodeName != 'ioids':
            raise IoidsFormatException('This is not a ioids message.')
           
        ioidsEvent = None
        relations = []
        for child1 in node.childNodes:
            if child1.nodeType == Node.ELEMENT_NODE:
                if child1.nodeName == 'ioids_event':
                    ioidsEvent = self._unwrapSomething(child1)
                elif child1.nodeName == 'relations':
                    for child2 in child1.childNodes:
                        if child2.nodeType == Node.ELEMENT_NODE:
                            if child2.nodeName == 'relation':
                                rel = self._unwrapSomething(child2)
                                relations.append(rel)
                            else:
                                raise IoidsFormatException('Unknown tag at this location inside IOIDS message: %s' %(child2.nodeName))
                else:
                    raise IoidsFormatException('Unknown tag at this location inside IOIDS message: %s' %(child1.nodeName))
        
        return ioidsEvent, relations
            
            
    def wrapKnowledgeRequestMessage(self, conditions):
        impl = xml.dom.getDOMImplementation()
        doc = impl.createDocument(None, 'knowledge-request', None)
        elementRoot = doc.documentElement
        
        elementConditions = doc.createElement('conditions')
        elementRoot.appendChild(elementConditions)
        
        for condition in conditions:
            attributeName = condition[0]
            operatorKey = condition[1]
            value = condition[2]
        
            elementCondition = doc.createElement('condition')
            elementCondition.setAttribute('attribute', attributeName)
            elementCondition.setAttribute('operator', operatorKey)
            valueText = doc.createTextNode(value)
            elementCondition.appendChild(valueText)

            elementConditions.appendChild(elementCondition)
        return self._toXml(doc)
        
    def parseKnowledgeRequestMessage(self, xmlString):
        """
        @return: Conditions in List / List format
        @rtype: C{List} of C{List}
        """
        from errorhandling import IoidsFormatException
        try:
            root = xml.dom.ext.reader.Sax2.FromXml(xmlString)
        except Exception, msg:
            raise IoidsFormatException("XML Format string error: %s" %(msg))
        node = root.childNodes[1]
        if node.nodeName != 'knowledge-request':
            raise IoidsFormatException('This is not a ioids knowledge request message.')
           
        conditions = []
        for child1 in node.childNodes:
            if child1.nodeType == Node.ELEMENT_NODE:
                if child1.nodeName == 'conditions':
                    for child2 in child1.childNodes:
                        if child2.nodeType == Node.ELEMENT_NODE:
                            if child2.nodeName == 'condition':
                                attributeName = child2.getAttribute('attribute')
                                operator = child2.getAttribute('operator')
                                for child3 in child2.childNodes:
                                    if child3.nodeType == Node.TEXT_NODE:
                                        value = child3.nodeValue                                
                                conditions.append([attributeName, operator, value])
                            else:
                                raise IoidsFormatException('Unknown tag at this location inside knowledge request message: %s' %(child2.nodeName))
                else:
                    raise IoidsFormatException('Unknown tag at this location inside knowledge request message: %s' %(child1.nodeName))
        return conditions

    def wrapKnowledgeReplyMessage(self, fullIoidsEvents):
        """
        @param fullIoidsEvents: List of IOIDS events to include in the reply (full events including relations - optionally) - each entry as a couple (ioidsEvent, relationsList)
        @type fullIoidsEvents: C{List} of C{Couples}
        """
        impl = xml.dom.getDOMImplementation()
        doc = impl.createDocument(None, 'knowledge-reply', None)
        elementRoot = doc.documentElement
        
        elementResults = doc.createElement('results')
        elementResults.setAttribute('count', str(len(fullIoidsEvents)))
        elementRoot.appendChild(elementResults)
        
        for fullEvent, relations in fullIoidsEvents:
            elementResult = doc.createElement('result')
            self.assembleIoidsMessage(fullEvent, relations, doc, elementResult)
            elementResults.appendChild(elementResult)

        return self._toXml(doc)
        
    def parseKnowledgeReplyMessage(self, xmlString):
        """
        @return: List of full IOIDS events - couples in form (ioidsEvent | relationList)
        @rtype: C{List} of C{Couples}
        """
        from errorhandling import IoidsFormatException
        try:
            root = xml.dom.ext.reader.Sax2.FromXml(xmlString)
        except Exception, msg:
            raise IoidsFormatException("XML Format string error: %s" %(msg))
        node = root.childNodes[1]
        if node.nodeName != 'knowledge-reply':
            raise IoidsFormatException('This is not a ioids knowledge reply message.')
            
        fullIoidsEvents = []
        for child1 in node.childNodes:
            if child1.nodeType == Node.ELEMENT_NODE:
                if child1.nodeName == 'results':
                    for child2 in child1.childNodes:
                        if child2.nodeType == Node.ELEMENT_NODE:
                            if child2.nodeName == 'result':
                                for child3 in child2.childNodes:
                                    if child3.nodeType == Node.ELEMENT_NODE:
                                        if child3.nodeName == 'ioids':
                                            oneEvent, relations = self.unwrapFullIoidsEventMessage(None, child3)
                                            fullIoidsEvents.append((oneEvent, relations))
        return fullIoidsEvents 
        
        
# "singleton"
_extensionWrapperHandler = None
def getExtensionWrapperHandler():
    """
    Singleton implementation.
    """
    global _extensionWrapperHandler
    if not _extensionWrapperHandler:
        _extensionWrapperHandler = ExtensionWrapperHandler()
    return _extensionWrapperHandler
        
class ExtensionWrapperHandler:
    """
    Connects to the appropriate extension implementation to get the data wrapped.
    """
    
    def __init__(self):
        """
        Yet empty constructor.
        """
        from config import SOAPSY_EXTENSIONS
        self._extensions = SOAPSY_EXTENSIONS
        
    def getFullExtensionMessage(self, extensionName, extensionData, parentNode, doc):
        if not self._extensions.has_key(extensionName):
            return None
            
        ext_mw = self._extensions[extensionName]['messagewrapper']
        return ext_mw().getFullExtensionMessage(extensionData, parentNode, doc)
        
