"""
Manages all issues wrapping / unwrapping (XML) messages.

Grid for Digital Security (G4DS)

All functionality is encapsulated in the class L{MessageWrapper}. Get the instance with the function
of this module L{getMessageWrapper}. (Singleton)

@author: Michael Pilgermann
@contact: mailto:mpilgerm@glam.ac.uk
@license: GPL (General Public License)

@var REPLACE_CLOSING_CDATA: String for replacement of CDATA keywords; see L{GenericWrapper._replaceCdata} for more details
@type REPLACE_CLOSING_CDATA: C{String}
@var REPLACE_OPENING_CDATA: String for replacement of CDATA keywords; see L{GenericWrapper._replaceCdata} for more details
@type REPLACE_OPENING_CDATA: C{String}
@var CDATA_DEPTH: CDATA replacement is supported for nested CDATA section. This indicates how deeply shall be checken. See L{GenericWrapper._replaceCdata} for more details
@type CDATA_DEPTH: C{int}
"""
import xmlconfig

import xml.dom
from xml.dom import Node
import xml.dom.ext.reader.Sax2
from StringIO import StringIO
import xml.dom.ext


REPLACE_CLOSING_CDATA = "@@g4dscdataclose@@"
REPLACE_OPENING_CDATA = "@@g4dscdataopen@@"
CDATA_DEPTH = 20

# "singleton"
_genericWrapper = None
def getGenericWrapper():
    """
    Singleton implementation.
    
    @return: The instance for the control message wrapper class
    @rtype: L{ControlMessageWrapper}
    """
    global _genericWrapper
    if not _genericWrapper:
        _genericWrapper = GenericWrapper()
    return _genericWrapper

class GenericWrapper:
    """
    Wrapper for generic functionality.
    
    Wrapping for things like an action and data.
    """
    def __init__(self):
        """
        Yet empty constructor.
        """
        pass

    def _replaceCdata(self, message):
        """
        Replaces CData section keywords by pre-defined substitutes.
        
        CData sections in XML documents must not be nested. Before any new CData section is
        created, this function should be invoked for "encoding" inner CData section and substituting
        the indicator beginning and end strings.
        
        It can now also handle nested, nested, ... CData sections.
        
        @param message: XML String, in which the CDATA sections shall be replaced.
        @type message: C{String}
        @return: XML String, in which the CDATA sections are replaced. (Be careful - this is not a valid XML String anymore. However, 
            it should be inside a CDATA section afterwards, which makes it a valid XML string again.)
        @rtype: C{String}
        
        @note: DEPRECATED. Use L{_encodeHex} and L{_decodeHex} instead.
        """
        for i in range (CDATA_DEPTH, 1, -1):
            message = message.replace(REPLACE_CLOSING_CDATA + str(i-1) + REPLACE_CLOSING_CDATA,
                REPLACE_CLOSING_CDATA + str(i) + REPLACE_CLOSING_CDATA)
            message = message.replace(REPLACE_OPENING_CDATA + str(i-1) + REPLACE_OPENING_CDATA,
                REPLACE_OPENING_CDATA + str(i) + REPLACE_OPENING_CDATA)
    
        message = message.replace("]]>",REPLACE_CLOSING_CDATA + str(1) + REPLACE_CLOSING_CDATA)
        message = message.replace("<![CDATA[", REPLACE_OPENING_CDATA + str(1) + REPLACE_OPENING_CDATA)
        return message
    
    def _unReplaceCdata(self, message):
        """
        Inverse function of L{_replaceCdata}
        
        Ones, CDATA section keywords have been replaced, there must be a way to get them back. That's
        exactly what this function is doing. Of course, nested CDATA sections are supported in here as well.
        
        @param message: XML String, in which the CDATA sections shall be recovered
        @type message: C{String}
        @return: XML String, in which CDATA sections have been recovered
        @rtype: C{String}
        
        @note: DEPRECATED. Use L{_encodeHex} and L{_decodeHex} instead.
        """
        message = message.replace(REPLACE_CLOSING_CDATA + str(1) + REPLACE_CLOSING_CDATA, "]]>")
        message = message.replace(REPLACE_OPENING_CDATA + str(1) + REPLACE_OPENING_CDATA, "<![CDATA[")
        
        for i in range (1, CDATA_DEPTH):
            message = message.replace(REPLACE_CLOSING_CDATA + str(i+1) + REPLACE_CLOSING_CDATA,
                REPLACE_CLOSING_CDATA + str(i) + REPLACE_CLOSING_CDATA)
            message = message.replace(REPLACE_OPENING_CDATA + str(i+1) + REPLACE_OPENING_CDATA,
                REPLACE_OPENING_CDATA + str(i) + REPLACE_OPENING_CDATA)
        return message
        
    def _encodeHex(self, message, compress = 1):
        """
        Replaces the function L{_replaceCdata}, which was not really a nice and sober solution for the 
        nested CData sections problem.
        
        CData sections in XML documents must not be nested. Before any new CData section is
        created, this function should be invoked for "encoding" the data to put into the CData section.
        The encoded version of the message will be a string of hex values, each character in the 
        source string is prepresented by two characters in the return string.
        
        A problem arised when using this approach due to the multiple wrappings for single messages. The
        messages have significantly blown up in size and could not be transmitted properly. To overcome these
        problems, compressing has been put in place. This way, before the data is hex encoded it will be compressed
        using the zlib python libraries. The oposite procedure was put in place for L{_decodeHex} - this way, it's totally
        transparent to the calling application. Control the use of compression with the parameter L{compress}; 
        by default compression is enabled now.
        
        @param message: XML String, in which shall be encoded
        @type message: C{String}
        @param compress: Shall the data be gzip compressed before hex encoding
        @type compress: C{Boolean}
        @return: A string of hex values representing the ASCII numbers of the source string
        @rtype: C{String}
        """
        if compress:
            import zlib
            message = zlib.compress(message)
        import binascii as hex
        encoded = hex.hexlify(message)
        return encoded
    
    def _decodeHex(self, message, decompress = 1):
        """
        Inverse function for L{_encodeHex}. This way replaces L{_unReplaceCdata}.
        
        Converts a hex code string back into its original real data. Two characters of hex code will
        represented one character in the output; hence, the given message must have a lenght of
        an even number.
        
        Due to size constraint with the multiple wrappings compression was put into place. Check the explanaitions
        in L{_encodeHex} for further details. Control decompression with the parameter L{decompress}. By 
        default, decompression is switched on.
        
        @param message: String of pairs of hex values exactly as produced by L{_encodeHex}
        @type message: C{String}
        @param decompress: Is the data inside the hex encoded area gzib compressed
        @type decompress: C{Boolean}
        @return: Original String - half the length of the passed string.
        @rtype: C{String}
        """
        import binascii as hex
        decoded = hex.unhexlify(message)
        if decompress:
            import zlib
            decoded = zlib.decompress(decoded)
        return decoded
                
    def wrapActionAndData(self, rootnode, action, data, encodeHex = 0):
        """
        Comparable with a function call.
        
        Action is wrapped as a text node, data in a CDATA section.
        
        @param rootnode: Name of the root node to create
        @type rootnode: C{String}
        @param action: Name of the action in string representation
        @type action: C{String}
        @param data: Any data to be wrapped (may even be binary data)
        @type data: C{String}
        @param encodeHex: Shall the data be hex encoded before put into the CDATA section
        @type encodeHex: C{Boolean}
        """
        if encodeHex: 
            if data:
                data = self._encodeHex(data)
        
        impl = xml.dom.getDOMImplementation()
        doc = impl.createDocument("", rootnode, None)
        
        elementAction = doc.createElement(xmlconfig.gen_action)
        doc.documentElement.appendChild(elementAction)
        actionValue = doc.createTextNode(action)
        elementAction.appendChild(actionValue)

        elementData = doc.createElement(xmlconfig.gen_data)
        doc.documentElement.appendChild(elementData)
        if data:
            cdata = doc.createCDATASection(data)
            elementData.appendChild(cdata)

        stio = StringIO()
        xml.dom.ext.PrettyPrint(doc, stio)
        value = stio.getvalue()
        stio.close()
        return value
            
            
    def unwrapActionAndData(self, rootnode, message, decodeHex = 0):
        """
        Unwraps a messge as assembled with L{wrapActionAndData} before.
        
        @param rootnode: Name of the rootnode inside the message
        @type rootnode: C{String}
        @param message: XML message
        @type message: C{String}
        @param decodeHex: Was the message hex encoded when assembled? Decode it with this parameter
        @type decodeHex: C{Boolean}
        @return: The action and the data extracted from the XML fragment
        @rtype: C{String} and C{String}
        """
        root = xml.dom.ext.reader.Sax2.FromXml(message)
        node1 = root.childNodes[1]
        if node1.nodeName != rootnode:
            raise ValueError, 'The tag ' + rootnode + ' was not found as top of the xml document.'
            
        action = None
        data = None
        for node in node1.childNodes:
            if node.nodeType == Node.ELEMENT_NODE:
                if node.nodeName == xmlconfig.gen_action:
                    for child in node.childNodes:
                        if child.nodeType == Node.TEXT_NODE:
                            action = child.nodeValue
                elif node.nodeName == xmlconfig.gen_data:
                    for child in node.childNodes:
                        if child.nodeType == Node.CDATA_SECTION_NODE:
                            data = child.nodeValue

        if not action:
            raise ValueError, 'No action found inside the message'
            
        if decodeHex and data:
            data = self._decodeHex(data)
        return action, data
        
    def wrapArgsAndDatas(self, root, args = None, datas = None):
        """
        Wraps a message with one root element, several args and several cdatas.
        """
        if datas:
            for key in datas.keys():
                if datas[key]:
                    datas[key] = self._encodeHex(datas[key])
        
        impl = xml.dom.getDOMImplementation()
        doc = impl.createDocument("", root, None)

        elementArguments = doc.createElement('arguments')
        doc.documentElement.appendChild(elementArguments)
        if args:
            for argname in args.keys():
                argvalue = args[argname]
                elementArg = doc.createElement(argname)
                elementArguments.appendChild(elementArg)
                if argvalue:
                    argValue = doc.createTextNode(argvalue)
                    elementArg.appendChild(argValue)
            
        elementDatas = doc.createElement('datas')
        doc.documentElement.appendChild(elementDatas)
        if datas:
            for argname in datas.keys():
                argvalue = datas[argname]
                elementArg = doc.createElement(argname)
                elementDatas.appendChild(elementArg)
                if argvalue:
                    argValue = doc.createCDATASection(argvalue)
                    elementArg.appendChild(argValue)

        stio = StringIO()
        xml.dom.ext.PrettyPrint(doc, stio)
        value = stio.getvalue()
        stio.close()
        return value
        
    def unwrapArgsAndDatas(self, rootname, message):
        """
        Extracts actions and data.
        """
        try:
            root = xml.dom.ext.reader.Sax2.FromXml(message)
        except Exception, msg:
            from errorhandling import G4dsDescriptionException
            raise G4dsDescriptionException("Error when parsing g4ds xml document: %s\nDocument:\n%s" %(msg, message))
        node1 = root.childNodes[1]
        if node1.nodeName != rootname:
            raise ValueError, 'This is not the message!'
            
        args = {}
        datas = {}
        for node in node1.childNodes:
            if node.nodeType == Node.ELEMENT_NODE:
                if node.nodeName == 'arguments':
                    for child in node.childNodes:
                        if child.nodeType == Node.ELEMENT_NODE:
                            args[child.nodeName] = None
                            for child1 in child.childNodes:
                                if child1.nodeType == Node.TEXT_NODE:
                                    args[child.nodeName] = child1.nodeValue
                elif node.nodeName == 'datas':
                    for child in node.childNodes:
                        if child.nodeType == Node.ELEMENT_NODE:
                            datas[child.nodeName] = None
                            for child1 in child.childNodes:
                                if child1.nodeType == Node.CDATA_SECTION_NODE:
                                    datas[child.nodeName] = child1.nodeValue
            
        for key in datas.keys():
            if datas[key]:
                datas[key] = self._decodeHex(datas[key])
        
        return args, datas
        

# "singleton"
_messageWrapper = None
def getMessageWrapper():
    """
    Singleton implementation.
    
    @return: The instance for the message  class
    @rtype: L{MessageWrapper}
    """
    global _messageWrapper
    if not _messageWrapper:
        _messageWrapper = MessageWrapper()
    return _messageWrapper


class MessageWrapper(GenericWrapper):
    """
    Integrates all functions for wrapping and unwrapping data with XML elements.
    """
    def __init__(self):
        """
        Yet empty Constructor.
        """
        pass
        
    def wrapG4dsMessage(self, node):
        """
        Creates a new XML document, which is a valid G4DS message, containing the data given by node.
        
        @param node: Content of the XML document to be appended underneath the G4DS root element.
        @type node: L{xml.dom.Node}
        @return: XML String containing the G4DS message, and the XML DOM document
        @rtype: C{String}; L{xml.dom.Document}
        """
        impl = xml.dom.getDOMImplementation()
        doc = impl.createDocument("", xmlconfig.g4ds_root_node, None)
        
        copy = node.cloneNode(1)
        doc.documentElement.appendChild(copy)
        
        stio = StringIO()
        xml.dom.ext.PrettyPrint(doc, stio)
        value = stio.getvalue()
        stio.close()
        return value, doc
    
    def unwrapG4dsMessage(self, message):
        """
        Processes a G4DS XML message and extracts and returns its content.
        
        @param message: XML String - G4DS message to be processed.
        @type message: C{String}
        @return: All the stuff underneath the G4DS node both as XML String and as DOM Tree Node, 
            None, None if no G4DS message was found
        @rtype: C{String}, L{xml.dom.Node}
        """
        root = xml.dom.ext.reader.Sax2.FromXml(message)
        node = root.childNodes[1]
        if node.nodeName != xmlconfig.g4ds_root_node:
            raise ValueError, 'Not a G4DS message; g4ds tag not found'                 # that's not a g4ds message

        child = node.childNodes[1]
        
        stio = StringIO()
        xml.dom.ext.PrettyPrint(child, stio)
        value = stio.getvalue()
        stio.close()
        return value, child
    
    def wrapG4dsPlain(self, xmltext, messageid, senderid, referenceid = None):
        """
        Creates a new G4DS plain message.
        """
        xmltext = self._encodeHex(xmltext)       
        impl = xml.dom.getDOMImplementation()
        doc = impl.createDocument("", xmlconfig.g4ds_plain_root, None)
        
        elementMessageId = doc.createElement(xmlconfig.g4ds_plain_messageid)
        doc.documentElement.appendChild(elementMessageId)
        idValue = doc.createTextNode(messageid)
        elementMessageId.appendChild(idValue)
        
        elementSenderId = doc.createElement(xmlconfig.g4ds_plain_senderid)
        doc.documentElement.appendChild(elementSenderId)
        idValue = doc.createTextNode(senderid)
        elementSenderId.appendChild(idValue)

        elementRefId = doc.createElement(xmlconfig.g4ds_plain_referenceid)
        doc.documentElement.appendChild(elementRefId)
        if referenceid:
            refValue = doc.createTextNode(referenceid)
            elementRefId.appendChild(refValue)
        elementData = doc.createElement(xmlconfig.g4ds_plain_data)
        doc.documentElement.appendChild(elementData)
        cdata = doc.createCDATASection(xmltext)
        elementData.appendChild(cdata)
                
        stio = StringIO()
        xml.dom.ext.PrettyPrint(doc, stio)
        value = stio.getvalue()
        stio.close()
        return value, doc
        
    def unwrapG4dsPlain(self, message):
        """
        Processes a G4DS XML plain message and extracts and returns its content.
        """
        root = xml.dom.ext.reader.Sax2.FromXml(message)
        node = root.childNodes[1]
        if node.nodeName != xmlconfig.g4ds_plain_root:
            raise ValueError, 'Not a G4DS message; g4ds tag not found'                 # that's not a g4ds message

        messageid = None
        data = None
        senderid = None
        referenceid = None
        for child1 in node.childNodes:
            if child1.nodeType == Node.ELEMENT_NODE:
                if child1.nodeName == xmlconfig.g4ds_plain_messageid:
                    for child in child1.childNodes:
                        if child.nodeType == Node.TEXT_NODE:
                            messageid = child.nodeValue
                if child1.nodeName == xmlconfig.g4ds_plain_senderid:
                    for child in child1.childNodes:
                        if child.nodeType == Node.TEXT_NODE:
                            senderid = child.nodeValue
                if child1.nodeName == xmlconfig.g4ds_plain_referenceid:
                    for child in child1.childNodes:
                        if child.nodeType == Node.TEXT_NODE:
                            referenceid = child.nodeValue
                if child1.nodeName == xmlconfig.g4ds_plain_data:
                    for child in child1.childNodes:
                        if child.nodeType == Node.CDATA_SECTION_NODE:
                            data = child.nodeValue
        
        data = self._decodeHex(data)       
        return data, messageid, senderid, referenceid

    def wrapControlMessage(self, subsystemid, subsystemname, message):
        """
        Wraps a message (String of any type (not only XML)) into a G4DS Control message.
        
        @param subsystemid: ID of the g4ds control subsystem
        @type subsystemid: C{String}
        @param subsystemname: Name of the g4ds control subsystem
        @type subsystemname: C{String}
        @param message: Message from the control subsystem to be wrapped (XML or plain text)
        @type message: C{String}
        @return: String representation of the XML stream, in which the data is encapsulated in a CDATA section
        @rtype: C{String}
        """
        message = self._encodeHex(message)   # message = self._replaceCdata(message)
        
        impl = xml.dom.getDOMImplementation()
        doc = impl.createDocument("",xmlconfig.g4ds_control_node, None)      # namespace, root element name, ???
        elementId = doc.createElement(xmlconfig.g4ds_control_ssid)
        doc.documentElement.appendChild(elementId)
        idValue = doc.createTextNode(subsystemid)
        elementId.appendChild(idValue)
        elementName = doc.createElement(xmlconfig.g4ds_control_ssname)
        doc.documentElement.appendChild(elementName)
        nameValue = doc.createTextNode(subsystemname)
        elementName.appendChild(nameValue)
        
        elementData = doc.createElement(xmlconfig.g4ds_control_data)
        doc.documentElement.appendChild(elementData)
        cdata = doc.createCDATASection(message)
        elementData.appendChild(cdata)
        
        stio = StringIO()
        xml.dom.ext.PrettyPrint(doc, stio)
        value = stio.getvalue()
        stio.close()
        return value

    def unwrapControlMessage(self, message):
        """ 
        Unwraps a control message and returns the data as to be passed to the service.
        
        @param message: XML String of the message containing control data.
        @type message: C{String}
        @return: Sub system ID, Sub system name and Control message; None, None, None if any of them was not found or the
            given message is not a g4ds control message
        @rtype: C{String}, C{String}, C{String}
        """
        root = xml.dom.ext.reader.Sax2.FromXml(message)
        node = root.childNodes[1]
        if node.nodeName != xmlconfig.g4ds_control_node:
            return None, None, None                 # that's not a control sub message

        id = None
        name = None
        data = None
        for child1 in node.childNodes:

            if child1.nodeType == Node.ELEMENT_NODE:
                if child1.nodeName == xmlconfig.g4ds_control_ssid:
                    for child in child1.childNodes:
                        if child.nodeType == Node.TEXT_NODE:
                            id = child.nodeValue
                if child1.nodeName == xmlconfig.g4ds_control_ssname:
                    for child in child1.childNodes:
                        if child.nodeType == Node.TEXT_NODE:
                            name = child.nodeValue
                elif child1.nodeName == xmlconfig.g4ds_control_data:       # let's do it with CDATA
                    for child in child1.childNodes:
                        if child.nodeType == Node.CDATA_SECTION_NODE:
                            data = child.nodeValue
        
        if not id or not name or not data:
            return None, None, None
        
        data = self._decodeHex(data)   # data = self._unReplaceCdata(data)
        return id, name, data
        
            
    def wrapServiceMessage(self, appid, appname, message):
        """
        Wraps a message (String of any type (not only XML)) into a G4DS Service message.
        
        The message is put into a CDATA section. This way it might of of any format; and not
        exclusively XML data. The XML message will look the following way:
        
        <service>
        
        <serviceid>$appid</serviceid>
        
        <servicename>$appname</servicename>
        
        <data>
        <[!CDATA[$message]]>
        </data>
        
        </service>
        
        @param appid: G4DS wide unique ID of the service
        @type appid: C{String}
        @param appname: Name of the service
        @type appname: C{String}
        @param message: Payload of the service, either XML or plain text
        @type message: C{String}
        @return: XML String of the service part of a G4DS message containing the service data
        @rtype: C{String}
        """
        message = self._encodeHex(message)       # message = self._replaceCdata(message)
        
        impl = xml.dom.getDOMImplementation()
        doc = impl.createDocument("",xmlconfig.g4ds_service_node, None)      # namespace, root element name, ???
        elementId = doc.createElement(xmlconfig.g4ds_service_sid)
        doc.documentElement.appendChild(elementId)
        idValue = doc.createTextNode(appid)
        elementId.appendChild(idValue)
        elementName = doc.createElement(xmlconfig.g4ds_service_name)
        doc.documentElement.appendChild(elementName)
        nameValue = doc.createTextNode(appname)
        elementName.appendChild(nameValue)
        
        elementData = doc.createElement(xmlconfig.g4ds_service_data)
        doc.documentElement.appendChild(elementData)
        cdata = doc.createCDATASection(message)
        elementData.appendChild(cdata)
        
        stio = StringIO()
        xml.dom.ext.PrettyPrint(doc, stio)
        value = stio.getvalue()
        stio.close()
        return value
        
    def unwrapServiceMessage(self, message):
        """ 
        Unwraps a service message and returns the data as to be passed to the service.
        
        The format of the message must be exactly the one as assembled the the function
        L{wrapServiceMessage}. Parameters for serive id and name are taken as text values
        from the corresponding nodes; the data itself is extracted from the CDATA section.
        
        @param message: XML String of the message, the service information shall be extracted from
        @type message: C{String}
        @return: Service ID, Serice name and Service message
        @rtype: C{String}, C{String}, C{String}
        """
        root = xml.dom.ext.reader.Sax2.FromXml(message)
        node = root.childNodes[1]
        if node.nodeName != xmlconfig.g4ds_service_node:
            return None, None, None                 # that's not a service sub message

        id = None
        name = None
        data = None
        for child1 in node.childNodes:

            if child1.nodeType == Node.ELEMENT_NODE:
                if child1.nodeName == xmlconfig.g4ds_service_sid:
                    for child in child1.childNodes:
                        if child.nodeType == Node.TEXT_NODE:
                            id = child.nodeValue
                if child1.nodeName == xmlconfig.g4ds_service_name:
                    for child in child1.childNodes:
                        if child.nodeType == Node.TEXT_NODE:
                            name = child.nodeValue
                elif child1.nodeName == xmlconfig.g4ds_service_data:       # let's do it with CDATA
                    for child in child1.childNodes:
                        if child.nodeType == Node.CDATA_SECTION_NODE:
                            data = child.nodeValue
        
        if not id or not name or not data:
            return None, None, None
        
        data = self._decodeHex(data)       # data = self._unReplaceCdata(data)
        return id, name, data
        
    def wrapForEncryption(self, message, algName):
        """
        Wraps an encrypted message chunk into a valid XML node.
        
        Encrypted message chunks have to be wrapped into a node named "enc". The name of the
        encryption algorithm has to be provided in the message itself too, sothat the receiver may
        choose the appropriate algorithm on its side. The cipher text itself (given as L{message}) 
        is stored into a CDATA section.
        
        @param message: Cipher text to be wrapped into a encrypted G4DS field
        @type message: C{String}
        @param algName: Name of the encryption algorithm to be used for decryption
        @type algName: C{String}
        @return: The result as String and as Dom tree and as root element of the dom tree
        @rtype: C{String}; L{xml.dom.Document}; L{xml.dom.Element}
        """
        message = self._encodeHex(message)       # message = self._replaceCdata(message)
        
        impl = xml.dom.getDOMImplementation()
        doc = impl.createDocument("",xmlconfig.g4ds_encryption_node, None)      # namespace, root element name, ???
        elementAlg = doc.createElement(xmlconfig.g4ds_encryption_algorithm)
        doc.documentElement.appendChild(elementAlg)
        algValue = doc.createTextNode(algName)
        elementAlg.appendChild(algValue)
        
        elementData = doc.createElement(xmlconfig.g4ds_encryption_data)
        doc.documentElement.appendChild(elementData)
        cdata = doc.createCDATASection(message)
        elementData.appendChild(cdata)
        
        stio = StringIO()
        xml.dom.ext.PrettyPrint(doc, stio)
        value = stio.getvalue()
        stio.close()
        return value, doc, doc.documentElement
        
    
    def unwrapForDecryption(self, message):
        """
        Extracts the cipher text and the name of the algorithm from an encrypted G4DS message chunk.
        
        Inverse function to L{wrapForEncryption}. Extracts the algorithm name and the cipher text from
        the message given. 
        
        @note: The decryption itself is not performed here. Only the information required for the decryption
        is gained.
        @param message: XML String of the G4DS encrypted message chunk
        @type message: C{String}
        @return: Name of the algorithm and the cipher text
        @rtype: C{String}; C{String}
        """
        root = xml.dom.ext.reader.Sax2.FromXml(message)
        node = root.childNodes[1]
        if node.nodeName != xmlconfig.g4ds_encryption_node:
            return None, None                 # that's not an encrypted
        
        alg = None
        data = None
        for node in node.childNodes:   # 2 child nodes should be given - 1 the algorithm; 2 the encrypted data
            if node.nodeType == Node.ELEMENT_NODE:
                if node.nodeName == xmlconfig.g4ds_encryption_algorithm:
                    for child in node.childNodes:
                        if child.nodeType == Node.TEXT_NODE:
                            alg = child.nodeValue
                elif node.nodeName == xmlconfig.g4ds_encryption_data:       # let's do it with CDATA
                    for child in node.childNodes:
                        if child.nodeType == Node.CDATA_SECTION_NODE:
                            data = child.nodeValue
        
        if not alg or not data:
            return None, None
        data = self._decodeHex(data)       # data = self._unReplaceCdata(data)
        return alg, data

        

    def wrapForSigning(self, message, signature, algName, senderid, communityid):
        """
        Wraps the message together with the signature into a signed G4DS message chunk.

        @param message: Message which was signed and is to be wrapped into a G4DS signed message chunk
        @type message: C{String}
        @param signature: The signature which was processed beforehand
        @type signature: C{String}
        @param algName: Name of the encryption algorithm to be used for signing
        @type algName: C{String}
        @param senderid: G4DS unique id of the sender
        @type senderid: C{String}
        @param communityid: G4DS unique id of the community
        @type communityid: C{String}
        @return: The result as String and as Dom tree and as root element of the dom tree
        @rtype: C{String}; L{xml.dom.Document}; L{xml.dom.Element}
        """
        message = self._encodeHex(message)       # message = self._replaceCdata(message)
        
        impl = xml.dom.getDOMImplementation()
        doc = impl.createDocument("", xmlconfig.g4ds_signature_node, None)
        elementAlg = doc.createElement(xmlconfig.g4ds_signature_algorithm)
        doc.documentElement.appendChild(elementAlg)
        algValue = doc.createTextNode(algName)
        elementAlg.appendChild(algValue)
        
        elementSender = doc.createElement(xmlconfig.g4ds_signature_senderid)
        doc.documentElement.appendChild(elementSender)
        senderValue = doc.createTextNode(senderid)
        elementSender.appendChild(senderValue)
        
        elementCommunity = doc.createElement(xmlconfig.g4ds_signature_communityid)
        doc.documentElement.appendChild(elementCommunity)
        communityValue = doc.createTextNode(communityid)
        elementCommunity.appendChild(communityValue)

        elementData = doc.createElement(xmlconfig.g4ds_signature_data)
        doc.documentElement.appendChild(elementData)
        cdata = doc.createCDATASection(message)
        elementData.appendChild(cdata)
        
        elementSignature = doc.createElement(xmlconfig.g4ds_signature_signature)
        doc.documentElement.appendChild(elementSignature)
        cdata = doc.createCDATASection(signature)
        elementSignature.appendChild(cdata)
        
        stio = StringIO()
        xml.dom.ext.PrettyPrint(doc, stio)
        value = stio.getvalue()
        stio.close()
        return value, doc, doc.documentElement

    def unwrapForValidation(self, message):
        """
        Extracts the message, the signature and the name of the algorithm from a G4DS signature message chunk.
        
        Inverse function to L{wrapForSigning}. 

        @param message: XML String of the G4DS signed message chunk
        @type message: C{String}
        @return: Name of the algorithm, unique id of the sender, unique id of the community, the message and the signature
        @rtype: C{String}; C{String}; C{String}; C{String}; C{String}
        """
        root = xml.dom.ext.reader.Sax2.FromXml(message)
        node1 = root.childNodes[1]
        if node1.nodeName != xmlconfig.g4ds_signature_node:
            return None, None, None, None         # this is not an signed message chunk
            
        alg = None
        senderid = None
        communityid = None
        data = None
        signature = None
        for node in node1.childNodes:
            if node.nodeType == Node.ELEMENT_NODE:
                if node.nodeName == xmlconfig.g4ds_signature_algorithm:
                    for child in node.childNodes:
                        if child.nodeType == Node.TEXT_NODE:
                            alg = child.nodeValue
                elif node.nodeName == xmlconfig.g4ds_signature_senderid:
                    for child in node.childNodes:
                        if child.nodeType == Node.TEXT_NODE:
                            senderid = child.nodeValue
                elif node.nodeName == xmlconfig.g4ds_signature_communityid:
                    for child in node.childNodes:
                        if child.nodeType == Node.TEXT_NODE:
                            communityid = child.nodeValue
                elif node.nodeName == xmlconfig.g4ds_signature_data:
                    for child in node.childNodes:
                        if child.nodeType == Node.CDATA_SECTION_NODE:
                            data = child.nodeValue
                elif node.nodeName == xmlconfig.g4ds_signature_signature:
                    for child in node.childNodes:
                        if child.nodeType == Node.CDATA_SECTION_NODE:
                            signature = child.nodeValue
        if not alg or not senderid or not communityid or not data or not signature:
            return None, None, None, None, None
        data = self._decodeHex(data)       # data = self._unReplaceCdata(data)
        return alg, senderid, communityid, data, signature

# "singleton"
_controlMessageWrapper = None
def getControlMessageWrapper():
    """
    Singleton implementation.
    
    @return: The instance for the control message wrapper class
    @rtype: L{ControlMessageWrapper}
    """
    global _controlMessageWrapper
    if not _controlMessageWrapper:
        _controlMessageWrapper = ControlMessageWrapper()
    return _controlMessageWrapper
    
class ControlMessageWrapper(GenericWrapper):
    """
    
    Does exactly the same job as MessageWrapper; just for structuring purposes and extracted class
    for messages sent as control messages.
    
    Inherits from L{MessageWrapper} for allowing access to functions for hexencoding L{_encodeHex} and
    hex decoding L{_decodeHex}.
    """
        
    def __init__(self):
        """
        Yet empty constructor.
        """
        
    def wrapSSMemberMessage(self, action, sucess=None, args = None, data = None):
        """
        Wraps a the inside of a control message for the member sub system usging the L{wrapSubSystemMessage}
        method.

        @param action: Action requested, passed to wrapSubSystemMessage
        @type action: C{String}
        @param sucess: Was the action sucessful (mainly for replies), passed to wrapSubSystemMessage
        @type sucess: C{String}
        @param args: Arguments to pass in form of dictionary - name | value, passed to wrapSubSystemMessage
        @type args: C{dict}
        @param data: Any additional data which does not fit into the args, passed to wrapSubSystemMessage
        @type data: C{String}
        @return: The result as String and as Dom tree and as root element of the dom tree
        @rtype: C{String}; L{xml.dom.Document}; L{xml.dom.Element}
        """
        return self.wrapSubSystemMessage(xmlconfig.g4ds_control_ss_member, action, sucess, args, data)

    def wrapSSCommunityMessage(self, action, sucess=None, args = None, data = None):
        """
        Wraps a the inside of a control message for the community sub system usging the L{wrapSubSystemMessage}
        method.

        @param action: Action requested, passed to wrapSubSystemMessage
        @type action: C{String}
        @param sucess: Was the action sucessful (mainly for replies), passed to wrapSubSystemMessage
        @type sucess: C{String}
        @param args: Arguments to pass in form of dictionary - name | value, passed to wrapSubSystemMessage
        @type args: C{dict}
        @param data: Any additional data which does not fit into the args, passed to wrapSubSystemMessage
        @type data: C{String}
        @return: The result as String and as Dom tree and as root element of the dom tree
        @rtype: C{String}; L{xml.dom.Document}; L{xml.dom.Element}
        """
        return self.wrapSubSystemMessage(xmlconfig.g4ds_control_ss_community, action, sucess, args, data)

    def wrapSSRoutingMessage(self, action, sucess=None, args = None, data = None):
        """
        Wraps a the inside of a control message for the routing sub system using the L{wrapSubSystemMessage}
        method.
        
        @Note: This wrapper is used for both routing messages and control messages  for routing sub system.

        @param action: Action requested, passed to wrapSubSystemMessage
        @type action: C{String}
        @param sucess: Was the action sucessful (mainly for replies), passed to wrapSubSystemMessage
        @type sucess: C{String}
        @param args: Arguments to pass in form of dictionary - name | value, passed to wrapSubSystemMessage
        @type args: C{dict}
        @param data: Any additional data which does not fit into the args, passed to wrapSubSystemMessage
        @type data: C{String}
        @return: The result as String and as Dom tree and as root element of the dom tree
        @rtype: C{String}; L{xml.dom.Document}; L{xml.dom.Element}
        """
        return self.wrapSubSystemMessage(xmlconfig.g4ds_control_ss_routing, action, sucess, args, data)

    def wrapSSServiceMessage(self, action, sucess=None, args = None, data = None):
        """
        Wraps a the inside of a control message for the service sub system using the L{wrapSubSystemMessage}
        method.
        
        @param action: Action requested, passed to wrapSubSystemMessage
        @type action: C{String}
        @param sucess: Was the action sucessful (mainly for replies), passed to wrapSubSystemMessage
        @type sucess: C{String}
        @param args: Arguments to pass in form of dictionary - name | value, passed to wrapSubSystemMessage
        @type args: C{dict}
        @param data: Any additional data which does not fit into the args, passed to wrapSubSystemMessage
        @type data: C{String}
        @return: The result as String and as Dom tree and as root element of the dom tree
        @rtype: C{String}; L{xml.dom.Document}; L{xml.dom.Element}
        """
        return self.wrapSubSystemMessage(xmlconfig.g4ds_control_ss_service, action, sucess, args, data)        
        
    def wrapSubSystemMessage(self, sstag, action, sucess=None, args = None, data = None):
        """
        Wraps a the inside of a control message for any sub system

        @param sstag: Tag of the sub system as to appear in the XML file later
        @type sstag: C{String}
        @param action: Action requested
        @type action: C{String}
        @param sucess: Was the action sucessful (mainly for replies)
        @type sucess: C{String}
        @param args: Arguments to pass in form of dictionary - name | value
        @type args: C{dict}
        @param data: Any additional data which does not fit into the args
        @type data: C{String}
        @return: The result as String and as Dom tree and as root element of the dom tree
        @rtype: C{String}; L{xml.dom.Document}; L{xml.dom.Element}
        """
        if data:
            data = self._encodeHex(data)
        
        impl = xml.dom.getDOMImplementation()
        doc = impl.createDocument("", sstag, None)

        elementAction = doc.createElement(xmlconfig.g4ds_control_ss_action)
        doc.documentElement.appendChild(elementAction)
        actionValue = doc.createTextNode(action)
        elementAction.appendChild(actionValue)
       
        elementSucess = doc.createElement(xmlconfig.g4ds_control_ss_sucess)
        doc.documentElement.appendChild(elementSucess)
        if sucess:
            sucessValue = doc.createTextNode(sucess)
            elementSucess.appendChild(sucessValue)
       
        elementArguments = doc.createElement(xmlconfig.g4ds_control_ss_arguments)
        doc.documentElement.appendChild(elementArguments)
        if args:
            for argname in args.keys():
                argvalue = args[argname]
                elementArg = doc.createElement(argname)
                elementArguments.appendChild(elementArg)
                argValue = doc.createTextNode(argvalue)
                elementArg.appendChild(argValue)
            
        elementData = doc.createElement(xmlconfig.g4ds_control_ss_data)
        doc.documentElement.appendChild(elementData)
        if data:
            cdata = doc.createCDATASection(data)
            elementData.appendChild(cdata)

        stio = StringIO()
        xml.dom.ext.PrettyPrint(doc, stio)
        value = stio.getvalue()
        stio.close()
        return value, doc, doc.documentElement

    def unwrapSSMemberMessage(self, message):
        """
        Extracts the action, the memberid, the mdl and the data from a control subsystem member message xml string.
        
        Inverse function to L{wrapSSMemberMessage}. 

        @param message: XML String of the control member message
        @type message: C{String}
        @return: Action, sucess, args, data
        @rtype: C{String}; C{String}; C{dict}; C{String} 
        """
        try:
            return self.unwrapSubSystemMessage(xmlconfig.g4ds_control_ss_member, message)
        except ValueError:
            raise ValueError, 'This is not a control message subsystem member controller message!'

    def unwrapSSCommunityMessage(self, message):
        """
        Extracts the action, the communityid, the tcdl and the data from a control subsystem member message xml string.
        
        Inverse function to L{wrapSSCommunityMessage}. 

        @param message: XML String of the control member message
        @type message: C{String}
        @return: Action, sucess, args, data
        @rtype: C{String}; C{String}; C{dict}; C{String} 
        """
        try:
            return self.unwrapSubSystemMessage(xmlconfig.g4ds_control_ss_community, message)
        except ValueError:
            raise ValueError, 'This is not a control message subsystem community controller message!'

    def unwrapSSRoutingMessage(self, message):
        """
        Extracts the information and the data from a control subsystem routing message xml string.
        
        Inverse function to L{wrapSSRoutingMessage}. 

        @Note: This wrapper is used for both routing messages and control messages  for routing sub system.
        
        @param message: XML String of the control service message
        @type message: C{String}
        @return: Action, sucess, args, data
        @rtype: C{String}; C{String}; C{dict}; C{String} 
        """
        try:
            return self.unwrapSubSystemMessage(xmlconfig.g4ds_control_ss_routing, message)
        except ValueError:
            raise ValueError, 'This is not a control message subsystem router controller message!'

    def unwrapSSServiceMessage(self, message):
        """
        Extracts the information and the data from a control subsystem service message xml string.
        
        Inverse function to L{wrapSSServiceMessage}. 
        
        @param message: XML String of the control service message
        @type message: C{String}
        @return: Action, sucess, args, data
        @rtype: C{String}; C{String}; C{dict}; C{String} 
        """
        try:
            return self.unwrapSubSystemMessage(xmlconfig.g4ds_control_ss_service, message)
        except ValueError:
            raise ValueError, 'This is not a control message subsystem service controller message!'            
            
    def unwrapSubSystemMessage(self, sstag, message):
        """
        Extracts the action, the memberid, the mdl and the data from a control subsystem member message xml string.
        
        Inverse function to L{wrapSubSystemMessage}. 

        @param sstag: Tag of the sub system as to appear in the XML file later
        @type sstag: C{String}
        @param message: XML String of the control member message
        @type message: C{String}
        @return: Action, sucess, args, data
        @rtype: C{String}; C{String}; C{dict}; C{String} 
        """
        root = xml.dom.ext.reader.Sax2.FromXml(message)
        node1 = root.childNodes[1]
        if node1.nodeName != sstag:
            raise ValueError, 'This is not the requested control message subsystem message!'
            
        action = None
        sucess = None
        args = {}
        data = None
        for node in node1.childNodes:
            if node.nodeType == Node.ELEMENT_NODE:
                if node.nodeName == xmlconfig.g4ds_control_ss_action:
                    for child in node.childNodes:
                        if child.nodeType == Node.TEXT_NODE:
                            action = child.nodeValue
                if node.nodeName == xmlconfig.g4ds_control_ss_sucess:
                    for child in node.childNodes:
                        if child.nodeType == Node.TEXT_NODE:
                            sucess = child.nodeValue
                elif node.nodeName == xmlconfig.g4ds_control_ss_arguments:
                    for child in node.childNodes:
                        if child.nodeType == Node.ELEMENT_NODE:
                            for child1 in child.childNodes:
                                if child1.nodeType == Node.TEXT_NODE:
                                    args[child.nodeName] = child1.nodeValue
                elif node.nodeName == xmlconfig.g4ds_control_ss_data:
                    for child in node.childNodes:
                        if child.nodeType == Node.CDATA_SECTION_NODE:
                            data = child.nodeValue
            
        if data:
            data = self._decodeHex(data)
        return action, sucess, args, data

        
# "singleton"
_routingTableWrapper = None
def getRoutingTableWrapper():
    """
    Singleton implementation.
    
    @return: The instance for the routing table wrapper class
    @rtype: L{RoutingTableWrapper}
    """
    global _routingTableWrapper
    if not _routingTableWrapper:
        _routingTableWrapper = RoutingTableWrapper()
    return _routingTableWrapper

class RoutingTableWrapper(GenericWrapper):
    """
    Encodes / decodes routing table into xml.
    """
    def __init__(self):
        """
        Yet empty constructor.
        """
        pass
        
    def encodeRoutingTable(self, routingTableArray):
        """
        Encodes routing table into XML.
        """
        impl = xml.dom.getDOMImplementation()
        doc = impl.createDocument("", xmlconfig.rtbl_routing_table, None)

        elementEntries = doc.createElement(xmlconfig.rtbl_routing_table_entries)
        doc.documentElement.appendChild(elementEntries)
        
        for entry in routingTableArray:
            elementEntry = doc.createElement(xmlconfig.rtbl_routing_table_entries_entry)
            elementEntries.appendChild(elementEntry)
            
            elementSource = doc.createElement(xmlconfig.rtbl_routing_table_entries_entry_source)
            elementEntry.appendChild(elementSource)
            srcValue = doc.createTextNode(entry[0])
            elementSource.appendChild(srcValue)

            elementDest = doc.createElement(xmlconfig.rtbl_routing_table_entries_entry_destination)
            elementEntry.appendChild(elementDest)
            destValue = doc.createTextNode(entry[1])
            elementDest.appendChild(destValue)

            elementgwtc = doc.createElement(xmlconfig.rtbl_routing_table_entries_entry_gatewaytc)
            elementEntry.appendChild(elementgwtc)
            gwtcValue = doc.createTextNode(entry[2])
            elementgwtc.appendChild(gwtcValue)

            elementgwm = doc.createElement(xmlconfig.rtbl_routing_table_entries_entry_gatewaymember)
            elementEntry.appendChild(elementgwm)
            gwmValue = doc.createTextNode(entry[3])
            elementgwm.appendChild(gwmValue)

            elementCosts = doc.createElement(xmlconfig.rtbl_routing_table_entries_entry_costs)
            elementEntry.appendChild(elementCosts)
            costsValue = doc.createTextNode(entry[4])
            elementCosts.appendChild(costsValue)

        stio = StringIO()
        xml.dom.ext.PrettyPrint(doc, stio)
        value = stio.getvalue()
        stio.close()
        return value
            
        
    def decodeRoutingTable(self, xmlstring):
        """
        Decodes and routing table xml string and returns the corrosponding matrix of values.
        """
        root = xml.dom.ext.reader.Sax2.FromXml(xmlstring)
        node1 = root.childNodes[1]
        if node1.nodeName != xmlconfig.rtbl_routing_table:
            from errorhandling import G4dsDescriptionException
            raise G4dsDescriptionException('This is not a valid XML formatted routing table!')
            
        entries = []
            
        for node in node1.childNodes:
            if node.nodeType == Node.ELEMENT_NODE:
                if node.nodeName == xmlconfig.rtbl_routing_table_entries:
                    for child in node.childNodes:
                        if child.nodeType == Node.ELEMENT_NODE:
                            if child.nodeName == xmlconfig.rtbl_routing_table_entries_entry:
                                src = dest = gw_tc = gw_mem = costs = None
                                for child1 in child.childNodes:
                                    if child1.nodeType == Node.ELEMENT_NODE:
                                        if child1.nodeName == xmlconfig.rtbl_routing_table_entries_entry_source:
                                            for child2 in child1.childNodes:
                                                if child2.nodeType == Node.TEXT_NODE:
                                                    src = child2.nodeValue
                                        elif child1.nodeName == xmlconfig.rtbl_routing_table_entries_entry_destination:
                                            for child2 in child1.childNodes:
                                                if child2.nodeType == Node.TEXT_NODE:
                                                    dest = child2.nodeValue                                        
                                        elif child1.nodeName == xmlconfig.rtbl_routing_table_entries_entry_gatewaytc:
                                            for child2 in child1.childNodes:
                                                if child2.nodeType == Node.TEXT_NODE:
                                                    gw_tc = child2.nodeValue                                        
                                        elif child1.nodeName == xmlconfig.rtbl_routing_table_entries_entry_gatewaymember:
                                            for child2 in child1.childNodes:
                                                if child2.nodeType == Node.TEXT_NODE:
                                                    gw_mem = child2.nodeValue                                        
                                        elif child1.nodeName == xmlconfig.rtbl_routing_table_entries_entry_costs:
                                            for child2 in child1.childNodes:
                                                if child2.nodeType == Node.TEXT_NODE:
                                                    costs = child2.nodeValue
                                entries.append([src, dest, gw_tc, gw_mem, costs])
        return entries

        
# "singleton"
_policyFileWrapper = None
def getPolicyFileWrapper():
    """
    Singleton implementation.
    
    @return: The instance for the polcity file wrapper class
    @rtype: L{PolicyFileWrapper}
    """
    global _policyFileWrapper
    if not _policyFileWrapper:
        _policyFileWrapper = PolicyFileWrapper()
    return _policyFileWrapper

class PolicyFileWrapper(GenericWrapper):
    """
    Parses permission policy files.
    """
    def __init__(self):
        """
        Yet empty constructor.
        """
        pass
        
    def _parseRoles(self, node, rolesets):
        """
        Parses a roles bit of a policy.
        """
        from errorhandling import G4dsDescriptionException
        
        for child in node.childNodes:
            if child.nodeType == Node.ELEMENT_NODE:
                if child.nodeName == xmlconfig.pol_policy_roles_roleset:
                    roleset = {}
                    roleset['type'] = child.getAttribute(xmlconfig.pol_policy_roles_roleset_type)
                    if not roleset['type']:
                        raise G4dsDescriptionException('One roleset is missing the type attribute.')
                        
                    roleset['roles'] = []
                    for child1 in child.childNodes:
                        if child1.nodeType == Node.ELEMENT_NODE:
                            if child1.nodeName == xmlconfig.pol_policy_roles_roleset_role:
                                role = {}
                                for child2 in child1.childNodes:
                                    if child2.nodeType == Node.ELEMENT_NODE:
                                        if child2.nodeName == xmlconfig.pol_policy_roles_roleset_role_name:
                                            for child3 in child2.childNodes:
                                                if child3.nodeType == node.TEXT_NODE:
                                                    role['name'] = child3.nodeValue
                                        elif child2.nodeName == xmlconfig.pol_policy_roles_roleset_role_description:
                                            for child3 in child2.childNodes:
                                                if child3.nodeType == node.TEXT_NODE:
                                                    role['description'] = child3.nodeValue
                                        else:
                                            raise G4dsDescriptionException('Unrecognised tag <%s> in policy description' %(child2.nodeName))
                                roleset['roles'].append(role)
                            else:
                                raise G4dsDescriptionException('Unrecognised tag <%s> in policy description' %(child1.nodeName))
                    rolesets.append(roleset)
                else:
                    raise G4dsDescriptionException('Unrecognised tag <%s> in policy description' %(child.nodeName))
        
    def _parseGroups(self, node, groups):
        """
        Parses a groups bit of a policy.
        """
        from errorhandling import G4dsDescriptionException
        
        for child in node.childNodes:
            if child.nodeType == Node.ELEMENT_NODE:
                if child.nodeName == xmlconfig.pol_policy_groups_group:
                    group = {}
                    group['representatives']  =[]
                    group['exceptions'] = []
                    
                    for child1 in child.childNodes:
                        if child1.nodeType == Node.ELEMENT_NODE:
                            if child1.nodeName == xmlconfig.pol_policy_groups_group_rolename:
                                for child2 in child1.childNodes:
                                    if child2.nodeType == Node.TEXT_NODE:
                                        group['rolename'] = child2.nodeValue
                            elif child1.nodeName == xmlconfig.pol_policy_groups_group_representatives:
                                for child2 in child1.childNodes:
                                    if child2.nodeType == Node.ELEMENT_NODE:
                                        if child2.nodeName == xmlconfig.pol_policy_groups_group_representatives_representative:
                                            representative = {}
                                            representative['type'] = child2.getAttribute(xmlconfig.pol_policy_groups_group_representatives_representative_type)
                                            if not representative['type']:
                                                raise G4dsDescriptionException('One representative is missing the type attribute.')
                                            for child3 in child2.childNodes:
                                                if child3.nodeType == Node.TEXT_NODE:
                                                    representative['value'] = child3.nodeValue
                                            group['representatives'].append(representative)
                                        else:
                                            raise G4dsDescriptionException('Unrecognised tag <%s> in policy description' %(child2.nodeName))
                            elif child1.nodeName == xmlconfig.pol_policy_groups_group_exceptions:
                                for child2 in child1.childNodes:
                                    if child2.nodeType == Node.ELEMENT_NODE:
                                        if child2.nodeName == xmlconfig.pol_policy_groups_group_exceptions_representative:
                                            representative = {}
                                            representative['type'] = child2.getAttribute(xmlconfig.pol_policy_groups_group_exceptions_representative_type)
                                            if not representative['type']:
                                                raise G4dsDescriptionException('One representative is missing the type attribute.')
                                            for child3 in child2.childNodes:
                                                if child3.nodeType == Node.TEXT_NODE:
                                                    representative['value'] = child3.nodeValue
                                            group['exceptions'].append(representative)
                                        else:
                                            raise G4dsDescriptionException('Unrecognised tag <%s> in policy description' %(child2.nodeName))
                            else:
                                raise G4dsDescriptionException('Unrecognised tag <%s> in policy description' %(child1.nodeName))
                    groups.append(group)
        
    def _parseRules(self, node, rulesets):
        """
        Parses a rules bit of a policy.
        """
        from errorhandling import G4dsDescriptionException
        
        for child in node.childNodes:
            if child.nodeType == Node.ELEMENT_NODE:
                if child.nodeName == xmlconfig.pol_policy_rules_ruleset:
                    ruleset = {}
                    ruleset['rules'] = []
                    for child1 in child.childNodes:
                        if child1.nodeType == Node.ELEMENT_NODE:
                            if child1.nodeName == xmlconfig.pol_policy_rules_ruleset_id:
                                for child2 in child1.childNodes:
                                    if child2.nodeType == Node.TEXT_NODE:
                                        ruleset['id'] = child2.nodeValue
                            elif child1.nodeName == xmlconfig.pol_policy_rules_ruleset_name:
                                for child2 in child1.childNodes:
                                    if child2.nodeType == Node.TEXT_NODE:
                                        ruleset['name'] = child2.nodeValue
                            elif child1.nodeName == xmlconfig.pol_policy_rules_ruleset_rule:                                
                                rule = {}
                                for child2 in child1.childNodes:
                                    if child2.nodeType == Node.ELEMENT_NODE:
                                        if child2.nodeName == xmlconfig.pol_policy_rules_ruleset_rule_id:
                                            for child3 in child2.childNodes:
                                                if child3.nodeType == Node.TEXT_NODE:
                                                    rule['id'] = child3.nodeValue
                                        elif child2.nodeName == xmlconfig.pol_policy_rules_ruleset_rule_comment:
                                            for child3 in child2.childNodes:
                                                if child3.nodeType == Node.TEXT_NODE:
                                                    rule['comment'] = child3.nodeValue
                                        elif child2.nodeName == xmlconfig.pol_policy_rules_ruleset_rule_actor:
                                            rule['actor_type'] = child2.getAttribute(xmlconfig.pol_policy_rules_ruleset_rule_actor_type)
                                            if not rule['actor_type']:
                                                raise G4dsDescriptionException('One actor is missing the type attribute.')
                                            for child3 in child2.childNodes:
                                                if child3.nodeType == Node.TEXT_NODE:
                                                    rule['actor'] = child3.nodeValue
                                        elif child2.nodeName == xmlconfig.pol_policy_rules_ruleset_rule_action:
                                            rule['action_type'] = child2.getAttribute(xmlconfig.pol_policy_rules_ruleset_rule_action_type)
                                            if not rule['action_type']:
                                                raise G4dsDescriptionException('One action is missing the type attribute.')
                                            for child3 in child2.childNodes:
                                                if child3.nodeType == Node.TEXT_NODE:
                                                    rule['action'] = child3.nodeValue
                                        elif child2.nodeName == xmlconfig.pol_policy_rules_ruleset_rule_target:
                                            rule['target_type'] = child2.getAttribute(xmlconfig.pol_policy_rules_ruleset_rule_target_type)
                                            if not rule['target_type']:
                                                raise G4dsDescriptionException('One target is missing the type attribute.')
                                            for child3 in child2.childNodes:
                                                if child3.nodeType == Node.TEXT_NODE:
                                                    rule['target'] = child3.nodeValue
                                        elif child2.nodeName == xmlconfig.pol_policy_rules_ruleset_rule_reaction:
                                            rule['reaction_type'] = child2.getAttribute(xmlconfig.pol_policy_rules_ruleset_rule_reaction_type)
                                            if not rule['reaction_type']:
                                                raise G4dsDescriptionException('One reaction is missing the type attribute.')
                                            for child3 in child2.childNodes:
                                                if child3.nodeType == Node.TEXT_NODE:
                                                    rule['reaction'] = child3.nodeValue
                                        else:
                                            raise G4dsDescriptionException('Unrecognised tag <%s> in policy description' %(child2.nodeName))                                
                                ruleset['rules'].append(rule)
                            else:
                                raise G4dsDescriptionException('Unrecognised tag <%s> in policy description' %(child1.nodeName))
                    rulesets.append(ruleset)
                else:
                    raise G4dsDescriptionException('Unrecognised tag <%s> in policy description' %(child.nodeName))

        
    def parsePolicyString(self, policy):
        """
        Parses a policy and returns the contents in form of dictionaries.
        
        @param policy: Policy in XML encoded String represenation
        @type policy: C{String}
        @return: The extracted Rolesets / Groups / Rulesets
        @rtype: C{List} of C{Dict} / C{List} of C{Dict} / C{List} of C{Dict}
        """
        rolesets = []
        groups = []
        rulesets = []
        
        root = xml.dom.ext.reader.Sax2.FromXml(policy)
        node = None
        for node1 in root.childNodes:
            if node1.nodeType == Node.ELEMENT_NODE:
                if node1.nodeName == xmlconfig.pol_policy:
                    if node:
                        from errorhandling import G4dsDescriptionException
                        raise G4dsDescriptionException('Only one policy per file allowed.')                    
                    node = node1
                else:
                    from errorhandling import G4dsDescriptionException
                    raise G4dsDescriptionException('Unrecognised tag <%s> in policy description' %(node1.nodeName))
        
        if not node:
            raise G4dsDescriptionException('Policy tag <%s> not found in policy description' %(xmlconfig.pol_policy))
            
        for node in node1.childNodes:
            if node.nodeType == Node.ELEMENT_NODE:
                if node.nodeName == xmlconfig.pol_policy_roles:
                    self._parseRoles(node, rolesets)
                elif node.nodeName == xmlconfig.pol_policy_groups:
                    self._parseGroups(node, groups)
                elif node.nodeName == xmlconfig.pol_policy_rules:
                    self._parseRules(node, rulesets)
                else:
                    from errorhandling import G4dsDescriptionException
                    raise G4dsDescriptionException('Unrecognised tag <%s> in policy description' %(node.nodeName))
        
        return rolesets, groups, rulesets

_connectedServicesWrapper = None
def getConnectedServicesWrapper():
    """
    Singleton implementation.
    
    @return: The instance for the connected services wrapper class
    @rtype: L{ConnectedServicesWrapper}
    """
    global _connectedServicesWrapper
    if not _connectedServicesWrapper:
        _connectedServicesWrapper = ConnectedServicesWrapper()
    return _connectedServicesWrapper
        
class ConnectedServicesWrapper(GenericWrapper):
    """
    Integrates all functions for wrapping and unwrapping data with XML elements for messages to and from connected services.
    """
    def __init__(self):
        """
        Yet empty Constructor.
        """
        pass

    def assembleMessage(self, data):
        datas = {}
        datas['payload'] = self._encodeHex(data)
        return self.wrapArgsAndDatas('app-message', datas = datas)
        
    def parseMessage(self, message):
        args, datas = self.unwrapArgsAndDatas('app-message', message)
        return self._decodeHex(datas['payload'])
        
    def parseMessages(self, messagesXml):
        start = 0
        end = 0
        payloads = []
        while 1:
            try:
                start = messagesXml.index('<?xml version=', end)
                end = messagesXml.index('</app-message>',end) + len('</app-message>')
                message = messagesXml[start:end]
            except ValueError, msg:
                break
            payloads.append(self.parseMessage(message))
        return payloads
