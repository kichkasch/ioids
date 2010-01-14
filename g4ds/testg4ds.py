"""
Test module for G4DS

Grid for Digital Security (G4DS)


@author: Michael Pilgermann
@contact: mailto:mpilgerm@glam.ac.uk
@license: GPL (General Public License)
"""

import communitymanager
import communicationmanager
import securitymanager
import servicerepository
import securitycontroller

def test():
    pass
##    testCommunityManager()
##    testCommunicationManager()
##    testSecurityManager()
    testServiceManager()
##    testFullCommunication()
##    testSecurityController()
##    testUpdatingAndDeletingOnManager()
##    testDescriptionProcessor()
##    testJobLocking()
##    testDescriptionLoading()
##    testExceptionHandling()
##    testLogging()
##    checkEndpoints()
##    testTcp()
##    testRoutingTableManager()
##    testG4dsService()
##    testPermissionStuff()
    
def testTcp():
    from protocolcontroller import getProtocolController
    tcp = getProtocolController().getOpenProtocol('tcpsocket')
    print (tcp.sendMessage('192.168.1.120:2000', 'h'*50000))
    raw_input()
    
    
def checkEndpoints():
    from communicationmanager import getEndpointManager
    print len(getEndpointManager().getEndpointsForMember('M111', 'C12345'))
    
def testCommunityManager():
    cm = communitymanager.getCommunityManager()
    mm = communitymanager.getMemberManager()
    
##    c = communitymanager.Community(None,"Community F","pas de comment","<tcdl/>","0.9.9","2005-06-28")
##    m = communitymanager.Member(None, "Member F",  "<mdl>Member F description file</mdl>","0.9.9", "2005-06-28")
##
##    cm.addCommunity(c)
##    mm.addMember(m)
##
##    c2 = cm.getCommunity('C10001')
##    
##    c.addMember(m.getId())
##    m.addCommunity(c.getId())
##    c2.addMember(m.getId())
##    m.addCommunity(c2.getId())
##    c2.addAuthority(m.getId())
##    m.addAuthorityRole(c2.getId())
##    c.addAuthority(m.getId())
##    m.addAuthorityRole(c.getId())
##    communitymanager.CommunityGateway(m.getId(), c.getId(), c2.getId(), 1, 1)
        
##    print cm, "\n", mm
##    printCommunities()
##    printMembers()
##    print ""

##    from communitymanager_db import CM_DB
##    db = CM_DB()
##    db.addProtocolToCommunity('C001', 'P906688')
##    print db.getProtocolsForCommunity('C001')

    community = cm.getCommunity('C001')
    from communicationmanager import getProtocolManager
##    prot = getProtocolManager().getProtocolByNameAndInsert('soap')
##    community.addProtocol(prot.getId())
    print community.getProtocols()
    
    from securitymanager import getAlgorithmManager
    alg = getAlgorithmManager().getAlgorithmByNameAndInsert('rsa')
    community.addAlgorithm(alg.getId())
    print community.getAlgorithms()
    
def printCommunities():
    for commid in communitymanager.getCommunityManager().getCommunityIds():
        comm = communitymanager.getCommunityManager().getCommunity(commid)
        print comm
##        print "\tXML (%s): %s" %(comm.getTcdlVersion(), comm.getTcdl())
    
def printMembers():
    for memberid in communitymanager.getMemberManager().getMemberIds():
        member = communitymanager.getMemberManager().getMember(memberid)
        print member
        print "\tXML (%s): %s" %(member.getMdlVersion(), member.getMdl())

def testCommunicationManager():
    protMan = communicationmanager.getProtocolManager()
    print protMan
    prot1 = protMan.getProtocols()[0]
    print prot1
    
    endpMan = communicationmanager.getEndpointManager()
    print endpMan
    endp1 = endpMan.getEndpoints()[0]
    print endp1
##    endp2 = communicationmanager.Endpoint(None, 'M10003', 'C10002', 'P10003', 'j4-itrl-12.comp.glam.ac.uk:22', 'Q10001')
##    endpMan.addEndpoint(endp2)
##    print endp2
    
def testSecurityManager():
    algMan = securitymanager.getAlgorithmManager()
##    alg = securitymanager.Algorithm(None, "SSL")
##    algMan.addAlgorithm(alg)
    alg = algMan.getAlgorithms()[0]
    print algMan
    print alg

    credMan = securitymanager.getCredentialManager()
    cred = credMan.getCredentials()[0]
##    cred1 = securitymanager.Credential(None, alg.getId(), 'mpilgerm', 'key here', 'M10002')
##    credMan.addCredential(cred1)
    print credMan
    print cred
##    print cred1

    persCredMan = securitymanager.getPersonalCredentialManager()
    persCred = persCredMan.getPersonalCredentials()[0]
##    persCred1 = securitymanager.PersonalCredential(None, 'Test SSL 510 bit', alg.getId(), "key private", "key public")
##    persCredMan.addPersonalCredential(persCred1)
    print persCredMan
    print persCred
##    print persCred1

def testServiceManager():
    servMan = servicerepository.getServiceManager()
    serv = servMan.getService('S177696')  #servMan.getServiceIds()[0])
    print serv

    serv = servicerepository.Service('S177696', 'test service 3', ksdldate = 'today')
    servMan.updateService(serv)

    print servMan.getServiceIds()
    print servMan
    print serv
    
##    from communitymanager import getMemberManager, getCommunityManager
##    member = getMemberManager().getMember('M003')
##    serv.addMember(member.getId())
##    serv.addAuthority(member.getId())
##    
##    community = getCommunityManager().getCommunity('C002')
##    serv.addCommunity(community.getId())
##    print serv
##    service = servicerepository.Service(None, "Test Service", "<ksdl>soon</ksdl>","0.9.9","2005-06-28")
##    servMan.addService(service)
##    print servMan
##    print service

def testFullCommunication():
    from messagehandler import getGlobalOutgoingMessageHandler
    outgoing = getGlobalOutgoingMessageHandler()

    from serviceintegrator import getServiceIntegrator
    getServiceIntegrator().sendMessage("M854612", "S10001", "IOIDS", "<ioids>test it app</ioids>")
    import g4dsconfigurationcontroller
    g4dsconfigurationcontroller.getOutgoingControlMessagesHandler().sendMessage(
    "M854612", g4dsconfigurationcontroller.CONTROL_SUBSYSTEM_MEMBERS, 
        "Member managing", "<routing><gateway><add>bla</add></gateway></routing>")
    
    g4dsconfigurationcontroller.getOutgoingControlMessagesHandler().sendMessage(
    "M854612", g4dsconfigurationcontroller.CONTROL_ROUTER, 
        "Forward message", "<routing><gateway><add>bla</add></gateway></routing>")
    # just for testing purpose the old version, where we directly connect to the global outing message handler and we
    # have to define an endpoint. Actually, the service integrator should be used and only a member id should be 
    # provided. Endpoints are assembled automatically.
    #outgoing.sendServiceMessage("E393454", "S10002", "PLAIN TEST",  "plain old logging :)")      # "E770313"
    raw_input("waiting :)")


def testSecurityController():
    from algorithmcontroller import getAlgorithmController
    print getAlgorithmController().getAvailableAlgorithms()
    print getAlgorithmController().getOpenAlgorithms()
    algRsa = getAlgorithmController().getAlgorithm("rsa")
    privatekey = algRsa.createKeyPair(512)
    algRsa.setKeyPair(privatekey)
    pubkeystr = algRsa.getPublicKey()
    
    message = "hello world"
    cipher = algRsa.encrypt(message, pubkeystr)
    print cipher
    sig = algRsa.signMessage(message)
    print "Signature: ", sig
    
    plain = algRsa.decrypt(cipher)
    print plain
    print "Verified? ", algRsa.validate(plain, sig, pubkeystr)
    
def testUpdatingAndDeletingOnManager():
    from communitymanager import getMemberManager, Member
    from communicationmanager import getEndpointManager, Endpoint, getProtocolManager
    from securitymanager import getCredentialManager, Credential, getAlgorithmManager

    m = Member('123','kk test', '<mdl/>','1.0.0.0','2005-07-08')
    #m.addCommunity('C760394')
    getMemberManager().updateMember(m, 1)
    
    alg = getAlgorithmManager().getAlgorithmByNameAndInsert('nikos alg')
    getEndpointManager().removeEndpointsForMember(m.getId())
    c = Credential(None, alg.getId(),'','key5','123')
    getCredentialManager().removeCredentialsForMember(m.getId())
    getCredentialManager().addCredential(c)
    
    protocol = getProtocolManager().getProtocolByNameAndInsert('soap')
    e = Endpoint(None, '123', 'C426009', protocol.getId(), 'http://localhost', c.getId())
    getEndpointManager().addEndpoint(e)


def testDescriptionProcessor():
    from descriptionprocessor import getMemberDescriptionProcessor
    filename = 'mdl-test.xml'
##    file = open(filename, 'w')
##    file.write(getMemberDescriptionProcessor().generateLocalMdl())
####    print getMemberDescriptionProcessor().generateLocalMdl()
##    file.close()
##    file = open(filename, 'r')
##    mdl = file.read()
##    getMemberDescriptionProcessor().applyMdl(mdl)
##    file.close()

##    from descriptionprocessor import getCommunityDescriptionProcessor
##    #filename = 'xml/ISRGTest01.tcl'
##    filename = 'xml/DefaultCommunity.tcl'
##    file = open(filename, 'r')
##    tcdl = file.read()
##    d = getCommunityDescriptionProcessor().applyTcdl(tcdl)
##    print d
##    file.close()

    from descriptionprocessor import getServiceDescriptionProcessor
    #filename = 'xml/ISRGTest01.tcl'
    filename = 'xml/S177696.sdl'
    file = open(filename, 'r')
    ksdl = file.read()
    d = getServiceDescriptionProcessor().processKsdl(ksdl)
    print d
    file.close()
    
    
def testJobLocking():
    import thread
    from runtimecontroller import getJobDispatcher
    thread.start_new_thread(subTestLocking, ())
    raw_input('<enter> to give somethign to 101')
    getJobDispatcher().resumeJob('101', 'Go on 101')
    raw_input('<enter> to finish')
    
def subTestLocking():
    from runtimecontroller import getJobDispatcher, JobLocker
    print "\tDid some funny stuff now and waiting for a message to ID 101"
    jl = JobLocker()
    getJobDispatcher().addJob('101', jl)
    
    print "\twow - really got something in here: %s"  %(getJobDispatcher().getMessage('101')[0])

def testDescriptionLoading():
    import thread
    from runtimecontroller import getJobDispatcher
    
    thread.start_new_thread(subTestDescriptionLoading, ())
    raw_input('<enter> to break')
    
def subTestDescriptionLoading():
    from runtimecontroller import getJobDispatcher, JobLocker
    from g4dsconfigurationcontroller import getMemberController
    from g4dsconfigurationcontroller import getCommunityController
    
    print "Try to get this thing now and wait then"
    jl = JobLocker()
##    mid = getMemberController().requestMemberDescription('M002','M001')
##    mid = getCommunityController().requestCommunityDescription('C9999999999', 'M111')
    mid = getCommunityController().requestMemberList('C002', 'M001')
    getJobDispatcher().addJob(mid, jl)
    
    data, args = getJobDispatcher().getMessage(mid)
    print "\n\nWe got something here: ", data, args

def testExceptionHandling():
    from errorhandling import G4dsDependencyException, G4dsException
    
    try:
        raise G4dsDependencyException('test the error')
    except G4dsException:
        print "got you"
    
def testLogging():
    from g4dslogging import getDefaultLogger
    getDefaultLogger()

def testRoutingTableManager():
    from routingtablemanager import getRoutingTableManager, RoutingTableEntry
##    entry = RoutingTableEntry(None, 'C001', 'M001', 'C002', '10')
##    getRoutingTableManager().addEntry(entry)
##    entry = RoutingTableEntry(None, 'C001', 'M001', 'C002', '3')
##    getRoutingTableManager().addEntry(entry)
##    entry = RoutingTableEntry(None, 'C001', 'M001', 'C002', '12')
##    getRoutingTableManager().addEntry(entry)
##    for x in getRoutingTableManager().getAllEntriesForCommunity('C001'):
##        print "\t", x

##    print getRoutingTableManager().getNexthopForCommunity('C001')

##    from messagewrapper import getRoutingTableWrapper
##    y1 = ['C001','C002','C010','M005','5']
##    y2 = ['C002','C001','C009','M005','6']
##    x = [y1, y2]
##    
##    xml = getRoutingTableWrapper().encodeRoutingTable(x)
##    print xml
##    
##    dec = getRoutingTableWrapper().decodeRoutingTable(xml)
##    print dec

##    from routingtablemanager import getRoutingTableManager
##    print getRoutingTableManager().getRoutingTableXML()

##    from g4dsconfigurationcontroller import getRoutingController
##    print getRoutingController().downloadRoutingTable('M001', timeout = 10)
    
    from dynamicrouting import getRoutingTableUpdater
    getRoutingTableUpdater().updateNow()
    

def testG4dsService():
    from g4dsservice import G4dsService
    s = G4dsService()
    s.connect()

def testPermissionStuff():
    from authorisationcontroller import getAuthorisationController
    getAuthorisationController() #.printMatrix()
    
    
    ata = []
    ata.append(['M111','C12345','g4ds.control.community.write.updatetcdl'])
    ata.append(['M001','C12345','g4ds.control.community.write.updatetcdl'])
    ata.append(['M111','S0001','g4ds.control.service.read.requestksdl'])
    ata.append(['M111','S0001','g4ds.control.service.write.pushksdl'])
    ata.append(['M001','M002','g4ds.service'])
    
    for actor, target, action in ata:
        print ("%s -> %s: %s " %(actor, target, action)).ljust(60,'.') + " %d" %getAuthorisationController().validate(actor, target, action)
    
if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        if sys.argv[1] == '-S':
            test()
            sys.exit(0)
    from g4ds import G4DS
    g = G4DS()
    g.startup()

    test()

    g.shutdown()
