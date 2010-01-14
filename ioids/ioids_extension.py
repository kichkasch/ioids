"""
Provides functionality for accessing information from the SoapSy DB IOIDS extension.

Inter-Organisational Intrusion Detection System (IOIDS)

@author: Michael Pilgermann
@contact: mailto:mpilgerm@glam.ac.uk
@license: GPL (General Public License)
"""

import messagewrapper
import dbconnector
import dataengine_tools

_ioidsDBMessageWrapper = None
def getMessageWrapper():
    """
    Singleton implementation.
    
    @return: The instance for the snort db message wrapper class
    @rtype: L{SnortDBMessageWrapper}
    """
    global _ioidsDBMessageWrapper 
    if not _ioidsDBMessageWrapper  :
        _ioidsDBMessageWrapper   = DBIOIDS_MessageWrapper()
    return _ioidsDBMessageWrapper  

    # "singleton"
_dbConnector = None
def getDBConnector():
    """
    Singleton implementation.
    """
    global _dbConnector
    if not _dbConnector:
        _dbConnector = IOIDS_DBConnector()
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
    from dataengine_tools import getPreXMLDictCreator
    return getPreXMLDictCreator()

class DBIOIDS_MessageWrapper(messagewrapper.IoidsMessageWrapper):

    def __init__(self):
        """
        Yet empty constructor.
        """
        pass
        
    def getFullExtensionMessage(self, data, parentNode, doc):
        if data[0] != 'ioids_event':
            raise ValueError('This is not a ioids extension data set: %s.' %(data[0]))
        self._wrapAnyItemToDom(data, parentNode, doc)
        

class IOIDS_DBConnector(dbconnector.IoidsDBConnector):
    """
    Standard DB connector - work on XML RPC database.
    """

    def __init__(self):
        """
        Sets the parameters for the later db connections.
        
        Most of the settings are taken from the global config file.
        """
        dbconnector.IoidsDBConnector.__init__(self)        
        
    def getExtensionEvent(self, plainEventId):            
        ioidsEventSlimDB = self.getIoidsEvents([['event_id', dbconnector.OPERATOR_EQUAL, plainEventId]])
        ioidsEventSlim = getPreXMLDictCreator().restructureIoidsEventEntry(ioidsEventSlimDB[0]['relations'][0]['attributes'] )
##        if not snortEvent:
##            return None
        ioidsEvent = self.getIoidsEvent(ioidsEventSlim[1]['ioids_event_id'])
        return ioidsEvent

    def insertExtensionEvent(self, data):
        if data[0] != 'ioids_event':
            raise ValueError('This is not a valid extension message for the IOIDS extension.')
        from messagewrapper import getXMLDBWrapper
        xml = getXMLDBWrapper().wrapInsert(data[0], data[1], data[2])
        
        result = self._performRequest(xml)
        decode = getXMLDBWrapper().parseInsertReply(result)
##        print "Result - primary key: %s " %(decode[0][2])
        return decode[0][2][1:len(decode[0][2])-1]
        
