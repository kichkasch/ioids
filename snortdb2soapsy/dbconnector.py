"""
Connect against (soap xml rpc) database backend.

SnortDB To SoapSy (SnDB2Soapsy)

@author: Michael Pilgermann
@contact: mailto:mpilgerm@glam.ac.uk
@license: GPL (General Public License)
"""

from soapsytools.dbconnector import *
import soapsytools.dbconnector


# "singleton"
_dbConnector = None
def getDBConnector():
    """
    Singleton implementation.
    """
    global _dbConnector
    if not _dbConnector:
        _dbConnector = SnDB2SoapsyDBConnector()
    return _dbConnector

class SnDB2SoapsyDBConnector(soapsytools.dbconnector.DBConnector):
    """
    Standard DB connector - work on XML RPC database.
    """

    def __init__(self):
        """
        Sets the parameters for the later db connections.
        
        Most of the settings are taken from the global config file.
        """
        from config import  SOAP_SERVER_URL
            
        soapsytools.dbconnector.DBConnector.__init__(self, SOAP_SERVER_URL)

    def insertSnortDBEvent(self, snortdbEvent):
        """
        Insert a new snortdb event.
        
        @return: The primary key of the new event
        @rtype: C{String}
        """
        from messagewrapper import getXMLDBWrapper
        xml = getXMLDBWrapper().wrapInsert(snortdbEvent[0], snortdbEvent[1], snortdbEvent[2])
        
        result = self._performRequest(xml)
        decode = getXMLDBWrapper().parseInsertReply(result)
##        print "Result - primary key: %s " %(decode[0][2])
        return decode[0][2][1:len(decode[0][2])-1]
        
