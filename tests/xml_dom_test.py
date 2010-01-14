#!/usr/bin/env python

# needs site package pyxml installed

import sys
from xml.dom import Node
import xml.dom
import xml.dom.ext.reader.Sax
from StringIO import StringIO

def showNode(node):
    if node.nodeType == Node.ELEMENT_NODE:
        print "Element \n\tName: %s\n\tValue: %s" %(node.nodeName, node.childNodes[0].nodeValue)
        for (name, value) in node.attributes.items():
            print "\t\tAttribute (%s): %s" %(name, value.value)

def readXml(xmlfilename):
    root = xml.dom.ext.reader.Sax.FromXmlFile(xmlfilename)
    node = root.childNodes[1]
    showNode(node)
    for child in node.childNodes:
        showNode(child)

def writeXml():     # http://www.python.org/doc/current/lib/module-xml.dom.html
    import xml.dom
    impl = xml.dom.getDOMImplementation()
    doc = impl.createDocument("","root", None)      # namespace, root element name, ???
    element1 = doc.createElement("name")
    doc.documentElement.appendChild(element1)
    textel1 = doc.createTextNode("Pilgermann")
    element1.appendChild(textel1)
    element1.setAttribute("birthname", "0")
    
    element2 = doc.createElement("firstname")
    doc.documentElement.appendChild(element2)
    element2.appendChild(doc.createTextNode("Michael"))
    
#    print doc.toprettyxml()     # or alternatively: doc.toxml()

    st = StringIO()

    import xml.dom.ext
    #xml.dom.ext.Print(doc)
    xml.dom.ext.PrettyPrint(doc, st)
    print st.getvalue()
    
    
if __name__ == "__main__":
    #print "\nStart reader"
    #readXml('xml_test.xml')
    print "\nStart writer"
    writeXml()
    print "Thats it\n"
