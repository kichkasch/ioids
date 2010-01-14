"""
Installation routines

Grid for Digital Security (G4DS)

@todo: we need some stuff here for loading the own keys into the database backend.

@author: Michael Pilgermann
@contact: mailto:mpilgerm@glam.ac.uk
@license: GPL (General Public License)
"""
from algorithmcontroller import getAlgorithmController
from maintainlib import _printAction, _finishActionLine, SUCESS_POS, SUCESS_NEG, SUCESS_SKIP, SUCESS_WARN

def checkModules(indent = 0):
    _printAction(indent, 'Check for availability of required modules', 1)
    
    allThere = 1
    _printAction(indent+1, 'output - colored console output')
    try:
        import output
        _finishActionLine()
    except ImportError, msg:
        _finishActionLine(SUCESS_NEG)
        allThere = 0

    _printAction(indent+1, 'pygresql - postgresql database connector')
    try:
        import pg
        _finishActionLine()
    except ImportError, msg:
        _finishActionLine(SUCESS_NEG)
        allThere = 0        

    _printAction(indent+1, 'PyXML - xml processing libraries')
    try:
        import xml.dom
        _finishActionLine()
    except ImportError, msg:
        _finishActionLine(SUCESS_NEG)
        allThere = 0        

    _printAction(indent+1, 'fpconst - required module for soap')
    try:
        import fpconst
        _finishActionLine()
    except ImportError, msg:
        _finishActionLine(SUCESS_NEG)
        allThere = 0        
        
    _printAction(indent+1, 'SOAPpy - SOAP implementation')
    try:
        import SOAPpy
        _finishActionLine()
    except ImportError, msg:
        _finishActionLine(SUCESS_NEG)
        allThere = 0        

    _printAction(indent+1, 'pycrypto - Low level cryptography toolkit')
    try:
        import Crypto
        _finishActionLine()
    except ImportError, msg:
        _finishActionLine(SUCESS_NEG)
        allThere = 0        
        
    _printAction(indent+1, 'ezPyCrypto - High level cryptography api')
    try:
        import ezPyCrypto
        _finishActionLine()
    except ImportError, msg:
        _finishActionLine(SUCESS_NEG)
        allThere = 0        
        
    _printAction(indent, 'Finished checking of modules')
    if allThere:
        _finishActionLine()
    else:
        _finishActionLine(SUCESS_NEG)
        
    return allThere

oneindent = "   "

def output(indent, text):
    global oneindent
    print (oneindent * indent + text)

def installOneKey(algId, i, localMemberId):
    """
    Install key for one algorithm
    """
    from algorithmcontroller import getAlgorithmController
    from securitymanager import getAlgorithmManager
    algName = getAlgorithmManager().getAlgorithm(algId).getName()
    _printAction (i, "Personal Credential for algorithm '" + algName + "'")
    algImplementation = getAlgorithmController().getAlgorithm(algName)
    privateKey = algImplementation.createKeyPair()
    publicKey = algImplementation.getPublicKey(privateKey)
    from securitymanager import PersonalCredential
    credential = PersonalCredential(None, algName + " key pair", algId, privateKey, publicKey, "")
    from securitymanager import getPersonalCredentialManager
    getPersonalCredentialManager().addPersonalCredential(credential)
    _finishActionLine()
    
    _printAction (i, "Public Credential for algorithm '" + algName + "'")
    from securitymanager import Credential
    from securitymanager import getCredentialManager
    credential = Credential(None, algId, "", publicKey, localMemberId)
    getCredentialManager().addCredential(credential)
    _finishActionLine()

def installKeys(i, algids):
    """
    Generate and store keys for the algorithms.
    
    @param algids: ID of the algorithms, public key pairs shall be created for.
    @type algids: C{List} of C{String}
    """
    _printAction (i, "Initialise credentials for algorithms", 1)
    for algid in algids:
        installOneKey(algid, i+1, localMemberId)
    _printAction (i, "Finished credentials")
    _finishActionLine()

def installAlgorithms(i, localMemberId):
    """
    Put all algorithms into the database.
    
    @return: list of algorithm ids.
    @rtype: C{List} of C{String}
    """
    _printAction (i, "Initialise algorithms", 1)
    from algorithmcontroller import getAlgorithmController
    from securitymanager import getAlgorithmManager
    from securitymanager import Algorithm
    
    allOpen = getAlgorithmController().getOpenAlgorithms()
    returnList = []
    for algName in allOpen:
        _printAction (i +1, "Algorithm '" + algName)
##        alg = Algorithm(None, algName)
##        getAlgorithmManager().addAlgorithm(alg)
        alg = getAlgorithmManager().getAlgorithmByNameAndInsert(algName)
        returnList.append(alg.getId())
        _finishActionLine()
    _printAction (i, "Finished algorithms")
    _finishActionLine()
    return returnList

def installNewMember(i, memberid = None):
    """
    Put myself in the member list.
    """
    _printAction (i, "Initialise member database with myself as the only member",1)
    _printAction(i+1, 'Create new member')
    from communitymanager import getMemberManager
    from communitymanager import Member
    member = Member(memberid, "temp description", "<mdl/>", "", "2005-07-05")
    #output (i+1, "New Member '" + member.getName() + "'")
    _finishActionLine()
    _printAction(i+1, 'Add member to local manager')
    try:
        getMemberManager().addMember(member)
        _finishActionLine()
    except Exception, msg:
        _finishActionLine(SUCESS_NEG)
        raise Exception(msg)
    memberid = member.getId()
    _printAction (i, "New member (%s) finished." %memberid)
    _finishActionLine()
    return memberid

def updateMemberDescription(i):
    """
    All the information is updated and the initial MDL for the user is created and stored.
    """
    _printAction (i, "Generate and store member description for the local node")
    filename = 'local-tmp.mdl'
    from descriptionprocessor import getMemberDescriptionProcessor
    mdl = getMemberDescriptionProcessor().generateLocalMdl("0.0.0.0", 4)    # should generate version number 1.0.0.0
    getMemberDescriptionProcessor().applyMdl(mdl)
    _finishActionLine()
    
    
def installNewCommunity(i, localMemberId):
    """
    We should have at least one community at the beginning.
    
    This community here every node is a member of. This way, any new node is able to connect to
    community authorities of certain communinties using this tc.
    """
    _printAction (i, "Initialise community database with one initial entry",1)
    from communitymanager import getCommunityManager
    from communitymanager import Community
    
##    from config import init_tcid
##    community = Community(init_tcid, "G4DS Startup", "StartUp service", "", "", "2005-07-05")
    from config import default_tcdl, default_mdls
    from descriptionprocessor import getCommunityDescriptionProcessor, getMemberDescriptionProcessor

    # it's a bit of a funny construction - has to be done like this due to back referencing between communties and members
    # that's how it works:
    # 1. The MDLs are applied without relations
    # 2. The TCDL is applied without relations
    # 3. The MDLs are applied including relations
    # 4. The TCDL is applied including relations

    _printAction (i+1, "Initialise temporary entries for back referencing",1)
    for mdl in default_mdls:
        file = open(mdl, 'r')
        content = file.read()
        if getMemberDescriptionProcessor().processMdl(content)['id'] != localMemberId:
            member = getMemberDescriptionProcessor().applyMdl(content, includingRelations = 0)
            _printAction(i+2, "Adding temporare member '" + member.getId() + "' (authority) to system and community.")
            _finishActionLine()
        file.close()
    _printAction (i+1, "Members temporaly added.")
    _finishActionLine()
    
    file = open(default_tcdl, 'r')
    tcdl = file.read()
    community = getCommunityDescriptionProcessor().applyTcdl(tcdl, includingRelations = 0)
    file.close()
    _printAction (i+1, "Preparing new Community '" + community.getName() + "'",1)
    for mdl in default_mdls:
        file = open(mdl, 'r')
        content = file.read()
        if getMemberDescriptionProcessor().processMdl(content)['id'] != localMemberId:
            member = getMemberDescriptionProcessor().applyMdl(content)
            _printAction (i+2, "Adding member '" + member.getId() + "' (authority) to system and community.")
            _finishActionLine()
        file.close()
    _printAction(i+1, "Community prepared.")
    _finishActionLine()
    
    _printAction(i+1, "Apply community description and add members")
    community = getCommunityDescriptionProcessor().applyTcdl(tcdl, includingRelations = 1)
    try:
        community.addMember(localMemberId, 0, 1)
    except ValueError:
        pass    # that's fine and only happens to the authorities of the communities since they have been added to the tc before
##    community.addMember(localMemberId, 1, 1)
    _finishActionLine()

    _printAction (i+2, "Add local member to the community")
    _finishActionLine()
    _printAction (i+1, "Finshed new Community '" + community.getName() + "'")
    _finishActionLine()
    communityid = community.getId()
    _printAction(i, "Finished community database")
    _finishActionLine()
    return communityid
    
def installEndPoints(i, localMemberId, tcId):
    """
    Add the local endpoints as defined in the config file in the protocols folder.
    """
    _printAction (i, "Initialise protocols and their endpoints", 1)
    from protocolcontroller import getProtocolController
    from communicationmanager import getProtocolManager
    from communicationmanager import Protocol
    from communicationmanager import getEndpointManager
    from communicationmanager import Endpoint
    from protocols.config import endpoints          # these are actually addesses, not really endpoints
    from securitymanager import getCredentialManager
    from securitymanager import getAlgorithmManager
    for protocolName in getProtocolController().getOpenProtocols():
        _printAction (i+1, "Add Protocol '" + protocolName + "'")
##        protocol = Protocol(None, protocolName)
##        getProtocolManager().addProtocol(protocol)
        protocol = getProtocolManager().getProtocolByNameAndInsert(protocolName)
        _finishActionLine()
        _printAction (i+1, "Add Endpoints for protocol '" + protocolName + "'", 1)
        address = endpoints[protocolName]
        for credential in getCredentialManager().getCredentialsForMember(localMemberId):
            algName = getAlgorithmManager().getAlgorithm(credential.getAlgorithmId()).getName()
            _printAction (i+2, "Add Endpoint for protocol '" + protocolName + "' and Algorithm '" + algName + "'")
            endpoint = Endpoint (None, localMemberId, tcId, protocol.getId(), address, credential.getId())
            getEndpointManager().addEndpoint(endpoint)
            _finishActionLine()
    _printAction (i, "Finished protocols and endpoints")
    _finishActionLine()
    
if __name__ == "__main__":
    import sys
    indent = 0
    _printAction(indent, "Installation started",1)
    
    if not checkModules(indent + 1):
        print "\nAt least one required python module could not be imported. Please check installation instructions"
        print "in the INSTALL file for more information and urls for downloading."
        sys.exit(1)
        
    try:
        from config import memberid
        localMemberId = installNewMember(indent + 1, memberid)
        if not localMemberId:
            sys.exit(1)
        tcId = installNewCommunity(indent + 1, localMemberId)
        algIds = installAlgorithms(indent + 1, localMemberId)
        installKeys(indent+1, algIds)
        installEndPoints(indent + 1, localMemberId, tcId)
        updateMemberDescription(indent + 1)
        _printAction (indent, "Installation finished")
        _finishActionLine()
    except Exception, msg:
        print
        _printAction (indent, "Installation not sucessful")
        _finishActionLine(SUCESS_NEG)
        print "\tError: %s" %(msg)
