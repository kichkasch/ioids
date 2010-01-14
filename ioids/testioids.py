"""
Test procedures for IOIDS.

Inter-Organisational Intrusion Detection System (IOIDS)

@author: Michael Pilgermann
@contact: mailto:mpilgerm@glam.ac.uk
@license: GPL (General Public License)
"""

def test():
##    testWrapper()
##    testSelect()
##    testDicts()
    testWrapper2()
    
def testWrapper():
    from messagewrapper import getXMLDBWrapper
    from dbconnector import OPERATOR_GREATER_THEN
    
##    print getXMLDBWrapper().wrapSelect('event', 'all', [['oid',OPERATOR_GREATER_THEN,'30608']])
    xml = "<RELATIONS command='SELECT_RESULTS' >" + \
        "<REL RESULTS_ID='1'>" + \
        "<REL name='table1'>" + \
        "<ATT name='x1'>128</ATT><ATT name='table1_id'>1</ATT><ATT name='table2_id'>1</ATT>" + \
        "</REL>" + \
        "<REL name='table1'>" + \
        "<ATT name='x1'>12</ATT><ATT name='table1_id'>2</ATT><ATT name='table2_id'>1</ATT>" + \
        "</REL>" + \
        "<REL name='TOTAL_RECORDS'>2</REL>" + \
        "</REL>" + \
        "<REL name='TOTAL_RESULTS'>1</REL>" + \
        "</RELATIONS>"
    
    print "Number of sets: %d\n%s" %(getXMLDBWrapper().parseSelectReply(xml))

def testSelect():
    from dbconnector import getDBConnector
    getDBConnector().connect()
    
    print getDBConnector().getEvents()
    print "\n", getDBConnector().getEventsFromEventID(3)
    
    print "\n", getDBConnector().getIoidsEvents()
    print "\n", getDBConnector().getIoidsEventsFromEventID(3)

def testDicts():
    from dbconnector import getDBConnector
    getDBConnector().connect()
    from messagewrapper import getXMLDBWrapper
##    lists = getDBConnector().getEvent('5')
    lists = getDBConnector().getIoidsEvent('2')
##    print lists
    xml = getXMLDBWrapper().wrapInsert(lists[0], lists[1], lists[2])
    print xml
    getDBConnector().disconnect()
    
def testWrapper2():
    from messagewrapper import getIoidsMessageWrapper
    xml =  getIoidsMessageWrapper().wrapKnowledgeRequestMessage([['timestamp', 'greater_than','2005-06-05'], ['source', 'equals', 'M003']])
    print xml
    print getIoidsMessageWrapper().parseKnowledgeRequestMessage(xml)
    
if __name__ == "__main__":
    test()
