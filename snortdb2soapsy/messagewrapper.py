"""
Handles all concerns for wrapping and parsing xml data.

SnortDB To SoapSy (SnDB2Soapsy)

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
    @rtype: L{SnDB2SoapsyXMLDBWrapper}
    """
    global _xmlDBWrapper
    if not _xmlDBWrapper:
        _xmlDBWrapper = SnDB2SoapsyXMLDBWrapper()
    return _xmlDBWrapper
        
class SnDB2SoapsyXMLDBWrapper(soapsytools.messagewrapper.XMLDBWrapper):
    """
    Wrapper / Parser for XML database queries / replies.
    """
    def __init__(self):
        """
        Yet empty constructor.
        """
        from config import DB_DATA_TYPE
        soapsytools.messagewrapper.XMLDBWrapper.__init__(self, DB_DATA_TYPE)
        
