"""
Functions to g4ds for maintainence.

Grid for Digital Security (G4DS)

This module provides the functionality. The access is provided by the module L{maintain}.

Functions may call each other - proper output and appropriate indenting is maintained. This
module is still shell interactive; hence, in the current stage it could not simply be used
as a lib from another application or gui.

@author: Michael Pilgermann
@contact: mailto:mpilgerm@glam.ac.uk
@license: GPL (General Public License)

@var oneindent: The space to indent between functions within the hierarchy
@type oneindent: C{String}
@var SUCESS_POS: Default string for sucessful action
@type SUCESS_POS: C{String}
@var SUCESS_NEG: Default string for unsucessful action
@type SUCESS_NEG: C{String}
"""

from errorhandling import G4dsRuntimeException, G4dsException
import config, output
from sys import stdout

oneindent = ' ' * 3
SUCESS_POS = output.green('  OK  ')
SUCESS_NEG = output.red('FAILED')
SUCESS_SKIP = output.yellow(' SKIP ')
SUCESS_WARN = output.yellow('  !!  ')

COLUMN_SUCESS = 80
COLUMN_INPUT = 70
LENGTH_LINE = 89

def _printAction(indent, text, linebreak = 0, out = stdout):
    """
    Prints a line for an action and puts the cursor on a predefined column.
    
    Usually, no line break is written, the line should be finished after performing an
    action using the function L{_finishActionLine}.
    """
    print ((oneindent * indent) + text).ljust(COLUMN_SUCESS),
    if linebreak:
        print
    else:
        out.flush()
    
def _finishActionLine(sucess = SUCESS_POS):
    """
    Finishes a line as prepared by L{_printAction}.
    
    Puts the given sucess string in brackets.
    """
    print '[%s]' %(sucess)

def _requestInput(indent, prompt, default = None):
    """
    Prompts the user for input.
    """
    if default:
        defaultPr = ' [%s]' %(default)
    else:
        defaultPr = ' []'
    print ((oneindent * indent) + '** ' + prompt + defaultPr).ljust(COLUMN_INPUT) + ' :',
    input = raw_input()
    if len(input) != 0:
        default = input
    return default

def _enterFunction(indent, text = None):
    """
    Should be called by a function at entry stage. 
    
    Calculates indent and puts some additional output.
    """
    if indent == 0:
        print '\n' + ('-'*LENGTH_LINE)  + '\n'
    if text:
        _printAction (indent, '>%s' %(text), 1)
    return indent + 1
    
def _leaveFunction(indent, text = "Finished here", sucess = None):
    """
    Shoudl be called by a function before leaving.
    
    Puts some output and optionally information about sucess.
    """
    indent -= 1
    if sucess:
        _printAction (indent, '<%s' %(text), 0)
        print '[%s]' %(sucess)
    else:
        _printAction (indent, '<%s' %(text), 1)

    if indent == 0:
        print '\n' + ('-'*LENGTH_LINE)  + '\n'
    return indent


def addMdl(filename=None, indent = 0):
    """
    Applies a member description to the local managers from a file.
    """
    indent = _enterFunction(indent, 'Apply member description from local file')
    filename = _requestInput(indent, 'Name of file containing mdl', filename)
    if not filename:
        _leaveFunction(indent, 'Apply Member description', SUCESS_NEG)
        raise G4dsRuntimeException('No filename given for description')

    processTcs = _requestInput(indent, 'Process subscribed communities (y/n)', 'y')
    if len(processTcs) > 0 and (processTcs[0] == 'n' or processTcs[0] == 'N'):
        processTcs = 0
    else:
        processTcs = 1
    
    secs = _requestInput(indent, 'How many seconds to wait for this action', '120')
    try:
        secs = int(secs)
    except ValueError:
        _finishActionLine(SUCESS_NEG)
        _leaveFunction(indent, 'Community Description applying', SUCESS_NEG)
        raise G4dsRuntimeException('Is it so difficult to provide a number here???')
    
    from descriptionprocessor import getMemberDescriptionProcessor
    _printAction(indent, 'Loading file')
    try:
        file = open(filename, 'r')
        mdl = file.read()
        file.close()
        _finishActionLine()
    except IOError, msg:
        _finishActionLine(SUCESS_NEG)
        _leaveFunction(indent, 'Apply Member description', SUCESS_NEG)
        raise G4dsRuntimeException('Apply MDL: %s' %(msg))
        
    _printAction(indent, 'Parse and apply content')
    status = getMemberDescriptionProcessor().applyMdl(mdl, 1, processTcs)
    elapsed = 0
    timeover = 0
    import time
    from runtimecontroller import JOB_FINISHED, JOB_ABORTED
    while 1:
        time.sleep(1)
        elapsed += 1
        if status.getStatus() == JOB_FINISHED or status.getStatus() == JOB_ABORTED:
            break
        if elapsed > secs:
            timeover = 1
            break
    if status.getStatus() == JOB_ABORTED:
        _finishActionLine(SUCESS_NEG)
        _leaveFunction(indent, 'Member Description applying', SUCESS_NEG)
        if status.getError() != (None, None):
            raise G4dsRuntimeException('Error for applying MDL: (%d) (%s)' % status.getError())
        else:
            raise G4dsRuntimeException('Unknown error when applying mdl.')
    if timeover:
        _finishActionLine(SUCESS_NEG)
        _leaveFunction(indent, 'Member Description applying', SUCESS_NEG)
        raise G4dsRuntimeException('The requested action has been timed out.')
        
    _finishActionLine()
    _leaveFunction(indent, 'Member description applied', SUCESS_POS)
    

def getLocalMdl(filename = './local.mdl', indent = 0):
    """
    Generates the member description for the local node.
    
    Uses information from the local managers and config file.
    """
    indent = _enterFunction(indent, 'Generate MDL for local member')
    filename = _requestInput(indent, 'Name of file to save the member description', filename)
    if not filename:
        _leaveFunction(indent, 'Apply Member description', SUCESS_NEG)
        raise G4dsRuntimeException('No filename given for saving description')
    from descriptionprocessor import getMemberDescriptionProcessor
    _printAction(indent, 'Generating description')
    mdl = getMemberDescriptionProcessor().generateLocalMdl()
    _finishActionLine()
    _printAction(indent, 'Writing to file')
    try:
        file = open(filename, 'w')
        file.write(mdl)
        file.close()
    except IOError, msg:
        _finishActionLine(SUCESS_NEG)
        _leaveFunction(indent, 'Generate local member description', SUCESS_NEG)
        raise G4dsRuntimeException('Generate local MDL: %s' %(msg))
        
    _finishActionLine()

    choice = _requestInput(indent, 'Apply this MDL to managers (y/n)?','y')
    if choice == 'y':
        addMdl(filename, indent = indent)
        
    _leaveFunction(indent, 'Member description created', SUCESS_POS)
        
def addTcdl(filename = None, indent = 0):
    """
    Applies a community description to the local managers from a file.
    """
    indent = _enterFunction(indent, 'Apply community description')

    filename = _requestInput(indent, 'Name of file containing TCDL', filename)
    if not filename:
        _leaveFunction(indent, 'Apply community description', SUCESS_NEG)
        raise G4dsRuntimeException('No filename given for saving description')

    from descriptionprocessor import getCommunityDescriptionProcessor
    processGateways = _requestInput(indent, 'Process Gateways (y/n)', 'y')
    if len(processGateways) > 0 and (processGateways[0] == 'n' or processGateways[0] == 'N'):
        processGateways = 0
    else:
        processGateways = 1
    
    secs = _requestInput(indent, 'How many seconds to wait for this action', '120')
    try:
        secs = int(secs)
    except ValueError:
        _finishActionLine(SUCESS_NEG)
        _leaveFunction(indent, 'Community Description applying', SUCESS_NEG)
        raise G4dsRuntimeException('Is it so difficult to provide a number here???')

    _printAction(indent, 'Open the file')
    try:
        file = open(filename, 'r')
        tcdl = file.read()
        file.close()
    except IOError, msg:
        _finishActionLine(SUCESS_NEG)
        _leaveFunction(indent, 'Apply community description', SUCESS_NEG)
        raise G4dsRuntimeException('Apply TCDL: %s' %(msg))
        
    _finishActionLine()

    _printAction(indent, 'Parse and apply content')
    status = getCommunityDescriptionProcessor().applyTcdl(tcdl, 1, processGateways, 1)
    
    elapsed = 0
    timeover = 0
    import time
    from runtimecontroller import JOB_FINISHED, JOB_ABORTED
    while 1:
        time.sleep(1)
        elapsed += 1
        if status.getStatus() == JOB_FINISHED or status.getStatus() == JOB_ABORTED:
            break
        if elapsed > secs:
            timeover = 1
            break
    if status.getStatus() == JOB_ABORTED:
        _finishActionLine(SUCESS_NEG)
        _leaveFunction(indent, 'Community Description applying', SUCESS_NEG)
        if status.getError() != (None, None):
            raise G4dsRuntimeException('Error for applying TCDL: (%d) (%s)' % status.getError())
        else:
            raise G4dsRuntimeException('Unknown error when applying tcdl.')
    if timeover:
        _finishActionLine(SUCESS_NEG)
        _leaveFunction(indent, 'Community Description applying', SUCESS_NEG)
        raise G4dsRuntimeException('The requested action has been timed out.')
        
    _finishActionLine()
    
    choice = _requestInput(indent, 'Recalculate access control (y/n)?','y')
    if choice == 'y':
        recalculatePermissions(indent = indent)
    
    _leaveFunction(indent, 'Community description applied', SUCESS_POS)

def printNodeDescription(dict, local = 0):
    """
    Prints information about a certain node.
    """
    print '\nGeneral Information'
    print '\tID'.ljust(25) + '%s' %(dict['id'])
    print '\tName'.ljust(25) + '%s' %(dict['name'])
    print '\tVersion and Date'.ljust(25) + '%s, %s' %(dict['version'], dict['creationdate'])
    print '\tFull name'.ljust(25) + '%s' %(dict['fullname'])
    print '\tOrganisation'.ljust(25) + '%s' %(dict['organisation'])
    print '\tLocation'.ljust(25) + '%s in %s (%s)' %(dict['city'], dict['country'], dict['country_code'])
    
    print '\nCredentials'
    if local:
        print '  Public'
    for key in dict['credentials'].keys():
        value = dict['credentials'][key]
        print ('\t%s' %(value[2])).ljust(25) + 'ID %s (Username: %s)' %(key, value[0])
    if local:
        print '  Private'
        from securitymanager import getPersonalCredentialManager, getAlgorithmManager
        for value in getPersonalCredentialManager().getPersonalCredentials():
            algName = getAlgorithmManager().getAlgorithm(value.getAlgorithmId()).getName()
            print ('\t%s' %(value.getName())).ljust(25) + '%s - ID %s (Username: %s)' %(algName, value.getId(), value.getUsername())
    
    print '\nEndpoints'
    for comm in dict['communities']:
        print '  Community ID %s' %(comm)
##        for endpoint in dict['endpoints']:
        from communicationmanager import getEndpointManager, getProtocolManager
        for endpoint in getEndpointManager().getEndpointsForMember(dict['id'],comm):
##            if endpoint[0] == comm:
##            print '\t%s' %(endpoint[1]).ljust(25) + '%s; Credential: %s' %(endpoint[2], endpoint[3])
            print ('\t%s' %(getProtocolManager().getProtocol(endpoint.getProtocolId()).getName())).ljust(25) + '%s; Credential: %s' %(endpoint.getAddress(), endpoint.getCredentialId())
        
    print '\nSubscribed services'    
    from servicerepository import getServiceManager
    for serviceid in getServiceManager().getServiceIds():
        service = getServiceManager().getService(serviceid)
        if service.hasMember(dict['id']):
            print ('\t%s' %(service.getId())).ljust(25) + '%s' %(service.getName())
    
        
def status():
    """
    Prints information about the local node.
    """
    print '\n--------------------------------------------------------------------------'
    print '\tDescription of local node - %s' %(config.memberid)
    from communitymanager import getMemberManager
    member = getMemberManager().getMember(config.memberid)
    mdl = member.getMdl()
    from descriptionprocessor import getMemberDescriptionProcessor
    dict = getMemberDescriptionProcessor().processMdl(mdl)
    printNodeDescription(dict, 1)
    
    print '\nKnown members'
    i = 0
    for id in getMemberManager().getMemberIds():
        print '\t' + id,
        i+=1
        if i%4 == 0:
            print '\n',
    print
    
    print '\nKnown communities'
    from communitymanager import getCommunityManager
    for id in getCommunityManager().getCommunityIds():
        comm = getCommunityManager().getCommunity(id)
        print ('\t' + id).ljust(25) + '%s (%d members)' %(comm.getName(), len(comm.getMembers()))
    print '\n--------------------------------------------------------------------------\n'

def nodeInfo(id):
    """
    Prints information about a remote node.
    """
    print '\n--------------------------------------------------------------------------'
    print '\tDescription of g4ds node - %s' %(id)
    from communitymanager import getMemberManager
    member = getMemberManager().getMember(id)
    mdl = member.getMdl()
    from descriptionprocessor import getMemberDescriptionProcessor
    dict = getMemberDescriptionProcessor().processMdl(mdl)
    printNodeDescription(dict)
    print '\n--------------------------------------------------------------------------\n'
    
def communityInfo(id):
    """
    Prints information about a certain community.
    """
    print '\n--------------------------------------------------------------------------'
    print '\tDescription of community - %s' %(id)

    from communitymanager import getCommunityManager, getMemberManager
    comm = getCommunityManager().getCommunity(id)
    from descriptionprocessor import getCommunityDescriptionProcessor
    dict = getCommunityDescriptionProcessor().processTcdl(comm.getTcdl())
    
    print '\nGeneral Information'
    print '\tID'.ljust(25) + '%s' %(dict['id'])
    print '\tName'.ljust(25) + '%s' %(dict['name'])
    print '\tVersion and Date'.ljust(25) + '%s, %s' %(dict['version'], dict['creationdate'])
    print '\tFull name'.ljust(25) + '%s' %(dict['fullname'])
    print '\tOrganisation'.ljust(25) + '%s' %(dict['organisation'])
    print '\tLocation'.ljust(25) + '%s in %s (%s)' %(dict['city'], dict['country'], dict['country_code'])

    print '\nAuthorities'
    for auth in comm.getAuthorities():
        member = getMemberManager().getMember(auth)
        print ('\t%s' %(member.getId())).ljust(25) + '%s' %(member.getName())
        
    print '\nKnown members'
    i=0
    for id in comm.getMembers():
        print '\t' + id,
        i+=1
        if i%4 == 0:
            print '\n',
    print
    
    print '\nGateways'
    print '  Incoming'
    for gw in comm.getDestinationGateways():
        print ('\t%s' %(gw.getSourceCommunityId())).ljust(25) + '%s' %(gw.getMemberId())
    print '  Outgoing'
    for gw in comm.getSourceGateways():
        print ('\t%s' %(gw.getDestinationCommunityId())).ljust(25) + '%s' %(gw.getMemberId())
    
    print '\nSupported protocols'
    from communicationmanager import getProtocolManager
    i=0
    for prot in comm.getProtocols():
        protocol = getProtocolManager().getProtocol(prot)
        print '\t' + protocol.getName(),
        i+=1
        if i%4 == 0:
            print '\n',
    print
    
    print '\nSupported algorithms'
    from securitymanager import getAlgorithmManager
    i=0
    for alg in comm.getAlgorithms():
        algorithm = getAlgorithmManager().getAlgorithm(alg)
        print '\t' + algorithm.getName(),
        i+=1
        if i%4 == 0:
            print '\n',
    print    
    
    print '\n--------------------------------------------------------------------------\n'
    
def sendTestMessage(indent = 0):
    """
    Sends a test message to a member using a certain community.
    """
    indent = _enterFunction(indent, 'Send test message')
    receiver = _requestInput(indent, "Receiver ID")
    if not receiver:
        _leaveFunction(indent, 'Test message sent', SUCESS_NEG)
        raise G4dsRuntimeException('Test message: No receiver defined.')
        
    text = _requestInput(indent, "Message", 'test')
    if not text:
        _leaveFunction(indent, 'Test message sent', SUCESS_NEG)
        raise G4dsRuntimeException('Test message: No text defined.')

    community = _requestInput(indent, "Community to use", 'any')
    if community == 'any':
        community = None
        
    type = _requestInput(indent, 'Control or Service message? (c/s)','s')
    
    if type == 'c':
        _leaveFunction(indent, 'Test message sent', SUCESS_NEG)
        raise G4dsRuntimeException('Test message: Control message test sending not yet implemented.')
    else:
        serviceid = _requestInput(indent, 'Service ID to use', 'S10001')
        servicename = _requestInput(indent, 'Name of this service (optional)', 'IOIDS')
        _printAction(indent, 'Sending in progress')
        from serviceintegrator import getServiceIntegrator
        try:
            getServiceIntegrator().sendMessage(receiver, serviceid, servicename, text, community)
        except G4dsException, msg:
            _finishActionLine(SUCESS_NEG)
            _leaveFunction(indent, 'Test message sent', SUCESS_NEG)
            raise G4dsRuntimeException('Test message: %s' %(msg))
            
    _finishActionLine()
    _leaveFunction(indent, 'Test message sent', SUCESS_POS)


def _subdownloadTcdl(communityid, memberid, inbackground = 0, status = None):
    """
    Supporter function for downloading a tcdl from a remote host.
    
    Supports job functionality.
    """
    from runtimecontroller import JobStatus, JOB_UNINITIALISED, JOB_INITIALISED, JOB_FINISHED, JOB_ABORTED
    from errorhandling import G4dsDependencyException, G4dsException
    if not status:
        status = JobStatus()

    if inbackground:
        import thread
        thread.start_new_thread(_subdownloadTcdl,(communityid, memberid, 0, status))
        return status
    
    status.setStatus(JOB_INITIALISED)
    from g4dsconfigurationcontroller import getCommunityController, COMMUNITY_SUCESS_TCDL_NOT_FOUND
    from runtimecontroller import getJobDispatcher, JobLocker
    try:
        msgId = getCommunityController().requestCommunityDescription(communityid, memberid)
    except G4dsException, msg:
        status.setError(21,'Error for Tcdl download: ' + str(msg))
        status.setStatus(JOB_ABORTED)
##        raise G4dsDependencyException('Error for Tcdl download: ' + str(msg))
        return
        
    jl = JobLocker()
    getJobDispatcher().addJob(msgId, jl)
    # wait and wait and wait
    # and go
    message, args = getJobDispatcher().getMessage(msgId)
    if not message or args['sucess'] == COMMUNITY_SUCESS_TCDL_NOT_FOUND:
        status.setError(4,'The required TCDL (' + communityid + ') could not be downloaded. You have to download it manually.')
        status.setStatus(JOB_ABORTED)
        return
##        raise G4dsDependencyException('The required TCDL (' + communityid + ') could not be downloaded. You have to download it manually.')
    status.setMessage(message)
    status.setStatus(JOB_FINISHED)
    
def downloadAndInstallCommunityDescription(communityid = None, destinationmemberid = None, indent = 0):
    """
    Downloads the community description from the given member.
    """
    indent = _enterFunction(indent, 'Download and install community description')
    communityid = _requestInput(indent, 'ID of the community', communityid)
    destinationmemberid = _requestInput(indent, 'ID of member to download from', destinationmemberid)
    
    _printAction(indent, "Download description", 1)
    secs = _requestInput(indent, 'How many seconds to wait for reply', '20')
    _printAction(indent, "Download in progress" )
    try:
        secs = int(secs)
    except ValueError:
        _finishActionLine(SUCESS_NEG)
        _leaveFunction(indent, 'Community Description download', SUCESS_NEG)
        raise G4dsRuntimeException('Is it so difficult to provide a number here???')
    status = _subdownloadTcdl(communityid, destinationmemberid, 1)
    elapsed = 0
    timeover = 0
    import time
    from runtimecontroller import JOB_FINISHED, JOB_ABORTED
    while 1:
        time.sleep(1)
        elapsed += 1
        if status.getStatus() == JOB_FINISHED or status.getStatus() == JOB_ABORTED:
            break
        if elapsed > secs:
            timeover = 1
            break
    if status.getStatus() == JOB_ABORTED:
        _finishActionLine(SUCESS_NEG)
        _leaveFunction(indent, 'Community Description download', SUCESS_NEG)
        if status.getError() != (None, None):
            raise G4dsRuntimeException('Error for download TCDL: (%d) (%s)' % status.getError())
        else:
            raise G4dsRuntimeException('Unknown error when downloading tcdl.')
    if timeover:
        _finishActionLine(SUCESS_NEG)
        _leaveFunction(indent, 'Community Description download', SUCESS_NEG)
        raise G4dsRuntimeException('The requested action has been timed out.')
    # looks good here :)
    # let's show what we got
    _finishActionLine()
    message = status.getMessage()
    filename = _requestInput(indent, 'Name for temporaer file','./desc.tmp')
    _printAction(indent, 'Temporarely save description')
    
    try:
        file = open(filename, 'w')
        file.write(message)
        file.close()
    except IOError, msg:
        _finishActionLine(SUCESS_NEG)
        _leaveFunction(indent, 'Community Description download', SUCESS_NEG)
        raise G4dsRuntimeException('Problem with file: %s' %msg)
    _finishActionLine()
    
    # so, let's go and apply this thing then
    _printAction(indent, 'Apply description now', 1)
    addTcdl(filename, indent = indent)
    
    choice = _requestInput(indent, 'Clean up - delete file (y/n)?', 'y')
    if choice == 'y':
        _printAction(indent, 'Delete temporary file')
        try:
            import os
            os.remove(filename)
        except IOError, msg:
            _finishActionLine(SUCESS_NEG)
            _leaveFunction(indent, 'Community Description download', SUCESS_NEG)
            raise G4dsRuntimeException('Problem with deleting file: %s' %msg)
         
    _finishActionLine()
    _leaveFunction(indent, 'Community Description processed', SUCESS_POS)

    
def _addEndpointsAutomatically(memberid, communityid, indent = 0):
    """
    Supporter function for endpoint installation (L{addEndpointsForMember} ) - automatic mode.
    """
    indent = _enterFunction(indent, 'Create endpoints automatically')
    
    from communitymanager import getMemberManager, getCommunityManager
    
    _printAction(indent, 'Check if member available')
    try:
        member = getMemberManager().getMember(memberid)
    except ValueError, msg:
        _finishActionLine(SUCESS_NEG)
        _leaveFunction(indent, 'Endpoint creation', SUCESS_NEG)
        raise G4dsRuntimeException('Endpoint creation: Member not found.')
    _finishActionLine()

    _printAction(indent, 'Check if community available')
    try:
        community = getCommunityManager().getCommunity(communityid)
    except ValueError, msg:
        _finishActionLine(SUCESS_NEG)
        _leaveFunction(indent, 'Endpoint creation', SUCESS_NEG)
        raise G4dsRuntimeException('Endpoint creation: Community not found.')
    _finishActionLine()
    
    _printAction(indent, 'Check community / member subscription')
    try:
        members = community.getMembers()
        members.index(memberid)
    except ValueError, msg:
        _finishActionLine(SUCESS_NEG)
        _leaveFunction(indent, 'Endpoint creation', SUCESS_NEG)
        raise G4dsRuntimeException('Endpoint creation: Member is not subscribed to the community.')
    _finishActionLine()
    
    _printAction(indent, 'Check for protocols of community')
    protocols = community.getProtocols()
    if len(protocols) == 0:
        _finishActionLine(SUCESS_NEG)
        _leaveFunction(indent, 'Endpoint creation', SUCESS_NEG)
        raise G4dsRuntimeException('Endpoint creation: No protocols available for the community.')
    _finishActionLine()

    _printAction(indent, 'Check for algorithms of community')
    algorithms = community.getAlgorithms()
    if len(algorithms) == 0:
        _finishActionLine(SUCESS_NEG)
        _leaveFunction(indent, 'Endpoint creation', SUCESS_NEG)
        raise G4dsRuntimeException('Endpoint creation: No algorithms available for the community.')
    _finishActionLine()

    _printAction(indent, 'Check credentials of member')
    from securitymanager import getCredentialManager, getAlgorithmManager
    credentials = getCredentialManager().getCredentialsForMember(memberid)
    if len(credentials) == 0:
        _finishActionLine(SUCESS_NEG)
        _leaveFunction(indent, 'Endpoint creation', SUCESS_NEG)
        raise G4dsRuntimeException('Endpoint creation: No credentials known for this member.')
    _finishActionLine()
    
    _printAction(indent, 'Check member support for community algorithms',1)
    for alg in algorithms:
        algname = getAlgorithmManager().getAlgorithm(alg).getName()
        _printAction(indent+1, 'Algorithm %s' %(algname))
        found = 0
        for c in credentials:
            if c.getAlgorithmId() == alg:
                found = 1
                break
        if not found:
            _finishActionLine(SUCESS_NEG)
            _leaveFunction(indent, 'Endpoint creation', SUCESS_NEG)
            raise G4dsRuntimeException('Endpoint creation: Missing credential for algorithm.')
        _finishActionLine()    
    
    _printAction(indent, 'Installing the endpoints', 1)
    from protocols.config import endpoints
    from communicationmanager import getProtocolManager, getEndpointManager, Endpoint
    for protocol in protocols:
        prot = getProtocolManager().getProtocol(protocol)
        for algorithm in algorithms:
            alg = getAlgorithmManager().getAlgorithm(algorithm)
            _printAction(indent+1, 'Endpoint %s | %s' %(prot.getName(), alg.getName()))
            
            try:
                address = endpoints[prot.getName()]
            except KeyError, msg:
                _finishActionLine(SUCESS_NEG)
                _leaveFunction(indent, 'Endpoint creation', SUCESS_NEG)
                raise G4dsRuntimeException('Endpoint creation: No address information found for the given protocol. Check protocols/config.py.')
                
            found = 0
            for c in credentials:
                if c.getAlgorithmId() == algorithm:
                    found = 1
                    break
            if not found:
                _finishActionLine(SUCESS_NEG)
                _leaveFunction(indent, 'Endpoint creation', SUCESS_NEG)
                raise G4dsRuntimeException('Endpoint creation: Missing credential for algorithm.')
            
            endpoint = Endpoint (None, memberid, communityid, protocol, address, c.getId())
            getEndpointManager().addEndpoint(endpoint)
            
            _finishActionLine()
    _printAction(indent, 'Finishing installing of enpoints')
    _finishActionLine()
    _leaveFunction(indent, 'Automatic endpoint creation finished', SUCESS_POS)
    
    
def addEndpointsForMember(memberid = None, communityid = None, indent = 0):
    """
    Installs enpoints for a member and a community.
    """
    indent = _enterFunction(indent, 'Install endpoints for member')
    memberid = _requestInput(indent, 'ID of the member', memberid)
    communityid = _requestInput(indent, 'ID of the community', communityid)
    
    choice = _requestInput(indent, 'Automatically all possible (y/n)?: ', 'y')
    try:
        if choice == 'y':
            _addEndpointsAutomatically(memberid, communityid, indent)
        else:
            _leaveFunction(indent, 'Community Description processed', SUCESS_NEG)
            raise G4dsRuntimeException('Manual endpoint adding not yet implemented.')
    except G4dsException, msg:
##        _finishActionLine(SUCESS_NEG)
        _leaveFunction(indent, 'Endpoint creation', SUCESS_NEG)
        raise G4dsRuntimeException('Endpoints: %s' %msg)

    
    # only if I am the func in first place
    if indent == 1:
        choice = _requestInput(indent, 'Export new local member description (y/n)?','y')
        if choice == 'y':
            getLocalMdl(indent = indent)
    _leaveFunction(indent, 'Installing endpoints', SUCESS_POS)
 
    
def pushMemberDescription(memberid=None, communityid=None, destinationList = [], indent=0):
    """
    Uploads the local member description to certain nodes.
    
    @param memberid: ID of the member whose mdl shall be dealt with
    @type memberid: C{String}
    @param communityid: ID of the community - MDL will be uploaded to its authorities
    @type communityid: C{String}
    @param destinationList: List of members to send the mdl to
    @type destinationList: C{List} of C{String}
    """
    indent = _enterFunction(indent, 'Upload member description')
    
    memberid = _requestInput(indent, 'Upload mdl of member with ID',memberid)
    from communitymanager import getMemberManager, getCommunityManager
    _printAction(indent, 'Load member')
    try:
        member = getMemberManager().getMember(memberid)
    except KeyError, msg:
        _finishActionLine(SUCESS_NEG)
        _leaveFunction(indent, 'Member description upload', SUCESS_NEG)
        raise G4dsRuntimeException('MDL upload: Member not found.')
    _finishActionLine()
    
    if communityid:
        _printAction(indent, 'Determine authorities for community')
        try:
            community = getCommunityManager().getCommunity(communityid)
        except KeyError, msg:
            _finishActionLine(SUCESS_NEG)
            _leaveFunction(indent, 'Member description upload', SUCESS_NEG)
            raise G4dsRuntimeException('MDL upload: Authorities for community could not be determined')
        authorities = community.getAuthorities()
        destinationList.extend(authorities)
        _finishActionLine()
        
    st = ''
    for i in range(0,len(destinationList)):
        st += destinationList[i]
        if i < len(destinationList)-1:
            st += ','
        
    input = _requestInput(indent, 'To which nodes - comma seperated', st)
    if input:
        destinationList = input.split(',')
    else:
        destinationList = []

    secs = _requestInput(indent, 'How many seconds to wait for each upload', '30')
    try:
        secs = int(secs)
    except ValueError:
        _finishActionLine(SUCESS_NEG)
        _leaveFunction(indent, 'Community Description applying', SUCESS_NEG)
        raise G4dsRuntimeException('Is it so difficult to provide a number here???')
    
    
    _printAction(indent, 'Upload mdl to %s nodes' %(len(destinationList)),1)
    for destination in destinationList:
        _printAction(indent+1, 'Upload to node %s' %(destination))
        from g4dsconfigurationcontroller import getMemberController
        dest = []
        dest.append(destination)
        pos, neg, error = getMemberController().uploadMdlToMembers(memberid, member.getMdl(), None, dest, timeout = secs)
        if len(neg):
            _finishActionLine(SUCESS_NEG)
            from g4dslogging import getDefaultLogger, COMMUNICATION_OUTGOING_ERROR
            if error.has_key(neg[0]):
                getDefaultLogger().newMessage(COMMUNICATION_OUTGOING_ERROR, 'MDL Upload failed: %s' %str(list(error[neg[0]])))
            else:
                getDefaultLogger().newMessage(COMMUNICATION_OUTGOING_ERROR, 'MDL Upload failed: Unknown error')
                
        else:
            _finishActionLine()
    
    _leaveFunction(indent, 'Member description upload', SUCESS_POS)

def _connectForSubscription(communityid, memberid, destination, inbackground = 0, status = None):
    """
    Supporter function for subsribing a member to a community.
    
    Supports job functionality.
    """
    from runtimecontroller import JobStatus, JOB_UNINITIALISED, JOB_INITIALISED, JOB_FINISHED, JOB_ABORTED
    from errorhandling import G4dsDependencyException, G4dsException
    if not status:
        status = JobStatus()

    if inbackground:
        import thread
        thread.start_new_thread(_connectForSubscription,(communityid, memberid, destination, 0, status))
        return status
    
    status.setStatus(JOB_INITIALISED)
    from g4dsconfigurationcontroller import getCommunityController, COMMUNITY_SUCESS_NO_ERROR, COMMUNITY_SUCESS_MEMBER_ALREADY
    from runtimecontroller import getJobDispatcher, JobLocker
    try:
        msgId = getCommunityController().requestMemberSubscription(communityid, memberid, destination)
    except G4dsException, msg:
        status.setError(21,'Error for member subscription: ' + str(msg))
        status.setStatus(JOB_ABORTED)
##        raise G4dsDependencyException('Error for Tcdl download: ' + str(msg))
        return
        
    jl = JobLocker()
    getJobDispatcher().addJob(msgId, jl)
    # wait and wait and wait
    # and go
    message, args = getJobDispatcher().getMessage(msgId)
    if args['sucess'] != COMMUNITY_SUCESS_NO_ERROR and args['sucess'] != COMMUNITY_SUCESS_MEMBER_ALREADY:
        status.setError(4,'The subscription could not be performed. Error Code is %s' %args['sucess'])
        status.setStatus(JOB_ABORTED)
        return
##        raise G4dsDependencyException('The required TCDL (' + communityid + ') could not be downloaded. You have to download it manually.')
    status.setMessage(message)
    status.setStatus(JOB_FINISHED)

    
def _doSubscribe(indent, communityid, newmemberid, destination):
    """
    Supporter function for member subscription process.
    
    Encapsulates the user input and the timer for waiting for replies.
    """
    _printAction(indent, "Perform subscription", 1)
    secs = _requestInput(indent, 'How many seconds to wait for reply', '20')
    _printAction(indent, "Subscription in progress" )
    try:
        secs = int(secs)
    except ValueError:
        _finishActionLine(SUCESS_NEG)
##        _leaveFunction(indent, 'Community subscription', SUCESS_NEG)
        raise G4dsRuntimeException('Is it so difficult to provide a number here???')
    status = _connectForSubscription(communityid, newmemberid, destination, 1)
    elapsed = 0
    timeover = 0
    import time
    from runtimecontroller import JOB_FINISHED, JOB_ABORTED
    while 1:
        time.sleep(1)
        elapsed += 1
        if status.getStatus() == JOB_FINISHED or status.getStatus() == JOB_ABORTED:
            break
        if elapsed > secs:
            timeover = 1
            break
    if status.getStatus() == JOB_ABORTED:
        _finishActionLine(SUCESS_NEG)
##        _leaveFunction(indent, 'Community subscription', SUCESS_NEG)
        if status.getError() != (None, None):
            raise G4dsRuntimeException('Error for subscription: (%d) (%s)' % status.getError())
        else:
            raise G4dsRuntimeException('Unknown error when performing subscription.')
    if timeover:
        _finishActionLine(SUCESS_NEG)
##        _leaveFunction(indent, 'Community subscription', SUCESS_NEG)
        raise G4dsRuntimeException('The requested action has been timed out.')
    # looks good here :)
    # let's show what we got
    _finishActionLine()
##    message = status.getMessage()
    
def subscribeMemberToCommunity(memberid = None, communityid = None, destination = None, indent = 0):
    """
    Performs the subscription of a member to a community.
    
    If the community is not yet known on this system, it's attempted to be downloaded.
    
    @param memberid: The id of the member to subscribe (if None, it will be requested from the stdin)
    @type memberid: C{String}
    @param communityid: The id of the community to subscribe to (if None, it will be requested from stdin)
    @type communityid: C{String}
    """
    indent = _enterFunction(indent, "Subscripe this member to a certain community")
    if not memberid:
        from communitymanager import getMemberManager
        memberid = getMemberManager().getLocalMember().getId()
    
    memberid = _requestInput(indent, 'Member ID', memberid)
    if not memberid:
        _leaveFunction(indent, sucess = SUCESS_NEG)
        raise G4dsRuntimeException('No member id provided')
    
    communityid = _requestInput(indent, 'Community ID', communityid)
    if not communityid:
        _leaveFunction(indent, sucess = SUCESS_NEG)
        raise G4dsRuntimeException('No community id provided')

    _printAction (indent, "Check whether community is known on this node")
    from communitymanager import getCommunityManager
    try:
        c = getCommunityManager().getCommunity(communityid)
        _finishActionLine()
    except KeyError:
        _finishActionLine(SUCESS_NEG)
        choice = _requestInput(indent, 'Download community description? (y/n)', 'y')
        if choice != 'y':
            _leaveFunction(indent, 'Subscribe Member aborted', SUCESS_NEG)
            raise G4dsRuntimeException('Action aborted by user.')
        try:
            downloadAndInstallCommunityDescription(communityid, indent = indent)
        except G4dsRuntimeException, msg:
            _leaveFunction(indent, sucess = SUCESS_NEG)
            raise G4dsRuntimeException(msg)
    
    _printAction(indent, 'Check for current subscription')
    try:
        c.getMembers().index(memberid)
        _finishActionLine(SUCESS_NEG)
        _leaveFunction(indent, sucess = SUCESS_NEG)
        raise G4dsRuntimeException('Check subscription: The requested member is subsribed already.')
    except ValueError:
        _finishActionLine()
    
##    _printAction(indent, 'Connect for final subscription')
    destinationid = _requestInput(indent, 'Member ID for authority')
    if not destinationid:
        _leaveFunction(indent, sucess = SUCESS_NEG)
        raise G4dsRuntimeException('No authority id provided')

    try:
        _doSubscribe(indent, communityid, memberid, destinationid)
    except G4dsException, msg:
        _leaveFunction(indent, sucess = SUCESS_NEG)
        raise G4dsRuntimeException('During subscription: %s' %(msg))
    
    # here we go - let's put it in the managers as well
    from communitymanager import getMemberManager, getCommunityManager
    member = getMemberManager().getMember(memberid)
    community = getCommunityManager().getCommunity(communityid)
    member.addCommunity(communityid)
    community.addMember(memberid)
    
    choice = _requestInput(indent, 'Install endpoints for this community (y/n)?','y')
    if choice == 'y':
        addEndpointsForMember(memberid, communityid, indent)

    choice = _requestInput(indent, 'Export new local member description (y/n)?','y')
    if choice == 'y':
        getLocalMdl(indent = indent)

        choice = _requestInput(indent, 'Push member description to authorities (y/n)?','y')
        if choice == 'y':
            pushMemberDescription(memberid, communityid, indent = indent)    
##    choice = _requestInput(indent, 'Download list of members (y/n)?','y')
##    choice = _requestInput(indent, 'Push member description to all members (y/n)?','y')
    
    choice = _requestInput(indent, 'Recalculate access control (y/n)?','y')
    if choice == 'y':
        recalculatePermissions(indent = indent)
    
    _leaveFunction(indent, 'Community subscription', sucess = SUCESS_POS)
    
    
## ##########################################################
## ##########################################################
## ##########################################################
##
## Maintain function for logging
##
## ##########################################################
## ##########################################################
## ##########################################################
    
def readLog(n = 10, indent = 0):
    """
    Show log entries.
    """
    indent = _enterFunction(indent, "Show latest log entries")

    from g4dslogging import getDefaultLogger

    n = _requestInput(indent, 'How many lines to show', str(n))
    try:
        n = int(n)
    except ValueError:
        _finishActionLine(SUCESS_NEG)
        _leaveFunction(indent, 'Show log', SUCESS_NEG)
        raise G4dsRuntimeException('Is it so difficult to provide a number here???')
    
    print 
    for line in getDefaultLogger().getLatestMessages(n):
        print line
    print
    _leaveFunction(indent, 'Show log entries', sucess = SUCESS_POS)

    
## ##########################################################
## ##########################################################
## ##########################################################
##
## Maintain functions for routing
##
## ##########################################################
## ##########################################################
## ##########################################################    
    
def addRoute(indent = 0):
    """
    Add a route to the routing table manually.
    """
    from communitymanager import getCommunityManager, getMemberManager
    
    indent = _enterFunction(indent, "Add route to routing table")
    
    srcCommunityId = _requestInput(indent, 'Source community')
    destCommunityId = _requestInput(indent, 'Destination community')
    gwCommunityId  =_requestInput(indent, 'ID of the community to route through: ')
    gwMemberId = _requestInput(indent, 'ID of the member of the gateway: ')
    costs = _requestInput(indent, 'Costs for this entry: ')
    
    _printAction(indent, 'Check source community')
    try:
        srcCommunity = getCommunityManager().getCommunity(srcCommunityId)
    except KeyError, msg:
        _finishActionLine(SUCESS_NEG)
        _leaveFunction(indent, 'Add route to routing table', SUCESS_NEG)
        raise G4dsRuntimeException('Source community unknown on this node - install community description first.')
    _finishActionLine()

    _printAction(indent, 'Check destination community')
    try:
        destCommunity = getCommunityManager().getCommunity(destCommunityId)
    except KeyError, msg:
        _finishActionLine(SUCESS_NEG)
        _leaveFunction(indent, 'Add route to routing table', SUCESS_NEG)
        raise G4dsRuntimeException('Destination community unknown on this node - install community description first.')
    _finishActionLine()
    
    _printAction(indent, 'Check for gateway community')
    try:
        gwCommunity = getCommunityManager().getCommunity(gwCommunityId)
    except KeyError, msg:
        _finishActionLine(SUCESS_NEG)
        _leaveFunction(indent, 'Add route to routing table', SUCESS_NEG)
        raise G4dsRuntimeException('Gateway community unknown on this node - install community description first.')
    _finishActionLine()
    
    _printAction(indent, 'Check for gateway member')
    try:
        gwMember = getMemberManager().getMember(gwMemberId)
    except KeyError, msg:
        _finishActionLine(SUCESS_NEG)
        _leaveFunction(indent, 'Add route to routing table', SUCESS_NEG)
        raise G4dsRuntimeException('Gateway member unknown on this node - install community description first.')
    _finishActionLine()

    _printAction(indent, 'Verify value for costs')
    try:
        costs = int(costs)
    except ValueError, msg:
        _finishActionLine(SUCESS_NEG)
        _leaveFunction(indent, 'Add route to routing table', SUCESS_NEG)
        raise G4dsRuntimeException('Value for costs must be an integer.')
    _finishActionLine()
    
    _printAction(indent, 'Apply new entry to routing table')
    from routingtablemanager import getRoutingTableManager, RoutingTableEntry
    try:
        entry = RoutingTableEntry(None, srcCommunityId, destCommunityId, gwMemberId, gwCommunityId, costs)
        getRoutingTableManager().addEntry(entry)
    except Exception, msg:
        _finishActionLine(SUCESS_NEG)
        _leaveFunction(indent, 'Add route to routing table', SUCESS_NEG)
        raise G4dsRuntimeException('Adding route: %s' %msg)
        
    _finishActionLine()
    
    _leaveFunction(indent, 'Entry added to routing table', sucess = SUCESS_POS)

def printRoutingTable(indent = 0):
    """
    Print the routing table.
    """
    indent = _enterFunction(indent, "Print current routing table")

    from communitymanager import getCommunityManager
    from routingtablemanager import getRoutingTableManager
    
    # print header
    print 
    print 'Source'.ljust(20) + ' | ' +   'Destination'.ljust(20) + ' | ' + 'GW Community'.ljust(20) + ' | ' +  \
        'GW Member'.ljust(20) + ' | ' + 'Costs'.ljust(5)
    print '-' * 97
    for communityid in getCommunityManager().getCommunityIds():
        for communityid1 in getCommunityManager().getCommunityIds():
            try:
                for route in getRoutingTableManager().getAllEntriesForCommunityPair(communityid, communityid1):
                    print ('%s' %(route.getSourceTC()).ljust(20) + ' | ' + \
                        ('%s' %route.getDestinationTC()).ljust(20) + ' | ' + ('%s' %route.getGWCommunityId()).ljust(20) + ' | ' + \
                        ('%s' %route.getGWMemberId()).ljust(20) + ' | ' + ('%d' %route.getCosts()).rjust(5))
            except KeyError, msg:
                pass    # that's fine - just no route to this community available
    
    from config import ENABLE_ROUTING
    if ENABLE_ROUTING:
        print "<Dynamic routing is ENABLED>".center(97)
    else:
        print "<Dynamic routing is DISABLED>".center(97)
            
    print
    _leaveFunction(indent, 'Routing table printed', sucess = SUCESS_POS)
    
    
def flushRoutingTable(indent = 0):
    """
    Causes a flush of the entire routing table.
    """
    indent = _enterFunction(indent, "Flush routing table")

    choice = _requestInput(indent, 'Sure (table will be totally empty!) (y/n)?','y')
    if choice == 'y':
        try:
            _printAction(indent, 'Flushing routing table')
            from routingtablemanager import getRoutingTableManager
            getRoutingTableManager().flushTable()
        except Exception, msg:
            _finishActionLine(SUCESS_NEG)
            _leaveFunction(indent, 'Flushing routing table', SUCESS_NEG)
            raise G4dsRuntimeException('Flush Routing table: %s' %msg)
            
    else:
        _leaveFunction(indent, 'Routing table flushed', sucess = SUCESS_SKIP)
        raise G4dsRuntimeException('Routing table flush aborted by user.')

    _finishActionLine()
    _leaveFunction(indent, 'Routing table flushed', sucess = SUCESS_POS)
    
def recalculateRoutingTable(indent = 0):
    """
    Recreates the routing table by the use of gateway information.
    """
    indent = _enterFunction(indent, "Recalculate routing table")
    choice = _requestInput(indent, 'Flush routing table before (y/n)?','y')
    if choice == 'y':
        try:
            flushRoutingTable(indent)
        except G4dsRuntimeException, msg:
            _leaveFunction(indent, 'Recalculating routing table', sucess = SUCESS_NEG)
            raise G4dsRuntimeException('Routing table recalculating: %s' %msg)
    
    choice = _requestInput(indent, 'Recreate routing table now (y/n)?','y')
    if choice != 'y':    
        _leaveFunction(indent, 'Recalculating routing table', sucess = SUCESS_SKIP)
        raise G4dsRuntimeException('Routing table recalculation aborted by user.')
        
    _printAction(indent, 'Recalculate routing table')
    try:
        from routingtablemanager import getRoutingTableManager
        number = getRoutingTableManager().recalculateRoutingTable()
    except Exception, msg:
        _finishActionLine(SUCESS_NEG)
        _leaveFunction(indent, 'Recalculating routing table', SUCESS_NEG)
        raise G4dsRuntimeException('Routing table recalculation: %s' %msg)
    
    _finishActionLine()
    _printAction(indent +1, '%d routing entries processed.' %(number), 1)
    _leaveFunction(indent, 'Routing table recreated', sucess = SUCESS_POS)
    
def dynamicRoutingUpdate(indent = 0):
    """
    Polls routing information from connected gateways and applies infos to the local routing table.
    """
    indent = _enterFunction(indent, "Update routing table")

    choice = _requestInput(indent, 'Update routing table now (y/n)?','y')
    if choice != 'y':    
        _leaveFunction(indent, 'Updating routing table', sucess = SUCESS_SKIP)
        raise G4dsRuntimeException('Routing table update aborted by user.')

    secs = _requestInput(indent, 'How many seconds to wait for each poll', '60')
    try:
        secs = int(secs)
    except ValueError:
        _finishActionLine(SUCESS_NEG)
        _leaveFunction(indent, 'Routing table update', SUCESS_NEG)
        raise G4dsRuntimeException('Is it so difficult to provide a number here???')
        
    _printAction(indent, 'Updating routing table')
    try:
        from dynamicrouting import getRoutingTableUpdater
        getRoutingTableUpdater().updateNow(secs)
    except Exception, msg:
        _finishActionLine(SUCESS_NEG)
        _leaveFunction(indent, 'Updating routing table', SUCESS_NEG)
        raise G4dsRuntimeException('Routing table updating: %s' %msg)
        
    _finishActionLine()    
    
    _leaveFunction(indent, 'Routing table updated', sucess = SUCESS_POS)

    
## ##########################################################
## ##########################################################
## ##########################################################
##
## Maintain functions for access control
##
## ##########################################################
## ##########################################################
## ##########################################################
        
def recalculatePermissions(indent = 0):
    indent = _enterFunction(indent, "Recalculate permission matrix")

    choice = _requestInput(indent, 'Perform recalculation now (y/n)?','y')
    if choice != 'y':
        _leaveFunction(indent, 'Permission matrix recalculation', sucess = SUCESS_SKIP)
        raise G4dsRuntimeException('Permission matrix recalculation: Aborted by user interaction.' )
 
    try:
        from authorisationcontroller import getAuthorisationController
        getAuthorisationController().recalculateMatrix()
    except Exception, msg:
        _finishActionLine(SUCESS_NEG)
        _leaveFunction(indent, 'Permission matrix recalculation', SUCESS_NEG)
        raise G4dsRuntimeException('Error for matrix calculation: %s' %(msg))
        
    _printAction(indent, 'Processing policy information and update matrix')
    
    _finishActionLine()
    _leaveFunction(indent, 'Permission matrix updated', sucess = SUCESS_POS)

def printPermissionMatrix(indent = 0):
    indent = _enterFunction(indent, "Print permission matrix")
    
    print
    
    from authorisationcontroller import getAuthorisationController
    getAuthorisationController().printMatrix()
    
    print
    _leaveFunction(indent, 'Permission matrix printed', sucess = SUCESS_POS)
    
    
## ##########################################################
## ##########################################################
## ##########################################################
##
## Maintain functions for services
##
## ##########################################################
## ##########################################################
## ##########################################################
    
def createServiceKeys(indent = 0):
    indent = _enterFunction(indent, "Create public key pair (RSA)")

    keylength = _requestInput(indent, 'Keylength to use', '512')
    try:
        keylength = int(keylength)
    except ValueError:
        _finishActionLine(SUCESS_NEG)
        _leaveFunction(indent, 'Public key pair creation', SUCESS_NEG)
        raise G4dsRuntimeException('Is it so difficult to provide a number here???')    
    
    choice = _requestInput(indent, 'Create keys now (y/n)?','y')
    if choice != 'y':
        _leaveFunction(indent, 'Public key pair creation', sucess = SUCESS_SKIP)
        raise G4dsRuntimeException('Public key pair creation: Aborted by user interaction.' )
 
    _printAction(indent, 'Create RSA key')
    try:
        from algorithmcontroller import getAlgorithmController
        rsa = getAlgorithmController().getAlgorithm('rsa')
        key = rsa.createKeyPair(keylength)
        public_key = rsa.getPublicKey(key)
        _finishActionLine()
    except Exception, msg:
        _finishActionLine(SUCESS_NEG)
        _leaveFunction(indent, 'Public key pair creation', SUCESS_NEG)
        raise G4dsRuntimeException('Public key pair creation: %s' %msg)
        
    filename = _requestInput(indent, 'File name to save private key: ')
    choice = _requestInput(indent, 'Add public key to permitted keys (y/n)?','y')
    
    _printAction(indent, 'Save private key', 1)
    _printAction(indent+1, 'Open file')
    try:
        file = open(filename, 'w')
        _finishActionLine()
    except Exception, msg:
        _finishActionLine(SUCESS_NEG)
        _leaveFunction(indent, 'Public key pair creation', SUCESS_NEG)
        raise G4dsRuntimeException('Public key pair creation - could not open file for writing private key: %s' %msg)

    _printAction(indent+1, 'Save key and close')
    try:
        file.write(key)
        file.close()
        _finishActionLine()
    except Exception, msg:
        _finishActionLine(SUCESS_NEG)
        _leaveFunction(indent, 'Public key pair creation', SUCESS_NEG)
        raise G4dsRuntimeException('Public key pair creation - problems when writing private key: %s' %msg)
        
    _printAction(indent, 'Add key to list of permitted keys')
    if choice != 'y':
        _finishActionLine(SUCESS_SKIP)
    else:
        print
        from config import PATH_PUBLIC_KEYS
        _printAction(indent+1, 'Open file for appending')
        try:
            file = open(PATH_PUBLIC_KEYS, 'a')
            _finishActionLine()
        except Exception, msg:
            _finishActionLine(SUCESS_NEG)
            _leaveFunction(indent, 'Public key pair creation', SUCESS_NEG)
            raise G4dsRuntimeException('Public key pair creation - could not open file for writing public key: %s' %msg)
            
        _printAction(indent+1, 'Append key and close file')
        try:
            file.write(public_key + '\n')
            file.close()
            _finishActionLine()
        except Exception, msg:
            _finishActionLine(SUCESS_NEG)
            _leaveFunction(indent, 'Public key pair creation', SUCESS_NEG)
            raise G4dsRuntimeException('Public key pair creation - problems when writing public key: %s' %msg)
 
    _leaveFunction(indent, 'Public key pair creation', sucess = SUCESS_POS)
    
    
def printServiceList(indent = 0):
    """
    Prints list of known services with basic information.
    """
    indent = _enterFunction(indent, "Print list of known services")

    print
    from servicerepository import getServiceManager
    for serviceId in getServiceManager().getServiceIds():
        service = getServiceManager().getService(serviceId)
        print "  %s | %s" %(service.getId(), service.getName())
        print "\tAuthorities: ",
        for auth in service.getAuthorities():
            print auth,
        print
        print "\tNumber of subscribed members: %d" %(len(service.getMembers()))
    print
    _leaveFunction(indent, 'Service list printed', sucess = SUCESS_POS)
    
def printServiceInformation(serviceid, indent = 0):
    """
    Prints information about one service.
    """
    indent = _enterFunction(indent, "Print information about a service")

    serviceid = _requestInput(indent, 'ID of requested service: ', serviceid)

    print
    from servicerepository import getServiceManager
    from descriptionprocessor import getServiceDescriptionProcessor
    from communitymanager import getMemberManager, getCommunityManager
    service = getServiceManager().getService(serviceid)
    
    dict = getServiceDescriptionProcessor().processKsdl(service.getKsdl())
    
    print '\nGeneral Information'
    print '\tID'.ljust(25) + '%s' %(dict['id'])
    print '\tName'.ljust(25) + '%s' %(dict['name'])
    print '\tCreation'.ljust(25) + '%s' %(dict['creationdate'])
    print '\tVersion and Date'.ljust(25) + '%s, %s' %(dict['version'], dict['lastupdate'])
    print '\tFull name'.ljust(25) + '%s' %(dict['fullname'])

    print '\nContacts'
    for contact in dict['contacts']:
        print '    %s' %(contact['name'])
        print '\tOrganisation:'.ljust(25) + '%s' %(contact['organisation'])
        print '\tEmail:'.ljust(25) + '%s' %(contact['email'])
    
    print '\nCommunities'
    for commid in service.getCommunities():
        comm = getCommunityManager().getCommunity(commid)
        print ('\t%s:' %comm.getId() ).ljust(25) + '%s' %(comm.getName())
    
    print '\nAuthorities'
    for auth in service.getAuthorities():
        member = getMemberManager().getMember(auth)
        print ('\t%s' %(member.getId())).ljust(25) + '%s' %(member.getName())
        
    print '\nKnown members'
    i=0
    for id in service.getMembers():
        print '\t' + id,
        i+=1
        if i%4 == 0:
            print '\n',
    print
    
    print '\nSupported Message formats'
    for format in dict['messageformats']:
        print ('\t%s:' %(format['id'])).ljust(25) + '%s' %(format['name'])
        print '\t '.ljust(25) + 'Def: %s' %(format['definition'])
    
    print
    _leaveFunction(indent, 'Service information printed', sucess = SUCESS_POS)


def addKsdl(filename = None, indent = 0):
    indent = _enterFunction(indent, "Add / update knowledge service description from file")

    filename = _requestInput(indent, 'Name of file containing KSDL', filename)
    if not filename:
        _leaveFunction(indent, 'Apply service description', SUCESS_NEG)
        raise G4dsRuntimeException('No filename given for saving description')

    from descriptionprocessor import getServiceDescriptionProcessor
    
    secs = _requestInput(indent, 'How many seconds to wait for this action', '120')
    try:
        secs = int(secs)
    except ValueError:
        _finishActionLine(SUCESS_NEG)
        _leaveFunction(indent, 'Service Description applying', SUCESS_NEG)
        raise G4dsRuntimeException('Is it so difficult to provide a number here???')

    _printAction(indent, 'Open the file')
    try:
        file = open(filename, 'r')
        ksdl = file.read()
        file.close()
    except IOError, msg:
        _finishActionLine(SUCESS_NEG)
        _leaveFunction(indent, 'Apply service description', SUCESS_NEG)
        raise G4dsRuntimeException('Apply KSDL: %s' %(msg))
        
    _finishActionLine()

    _printAction(indent, 'Parse and apply content')
    status = getServiceDescriptionProcessor().applyKsdl(ksdl, 1, 1)

    elapsed = 0
    timeover = 0
    import time
    from runtimecontroller import JOB_FINISHED, JOB_ABORTED
    while 1:
        time.sleep(1)
        elapsed += 1
        if status.getStatus() == JOB_FINISHED or status.getStatus() == JOB_ABORTED:
            break
        if elapsed > secs:
            timeover = 1
            break
    if status.getStatus() == JOB_ABORTED:
        _finishActionLine(SUCESS_NEG)
        _leaveFunction(indent, 'Service Description applying', SUCESS_NEG)
        if status.getError() != (None, None):
            raise G4dsRuntimeException('Error for applying KSDL: (%d) (%s)' % status.getError())
        else:
            raise G4dsRuntimeException('Unknown error when applying ksdl.')
    if timeover:
        _finishActionLine(SUCESS_NEG)
        _leaveFunction(indent, 'Service Description applying', SUCESS_NEG)
        raise G4dsRuntimeException('The requested action has been timed out.')
        
    _finishActionLine()
    
    choice = _requestInput(indent, 'Recalculate access control (y/n)?','y')
    if choice == 'y':
        recalculatePermissions(indent = indent)
    
    _leaveFunction(indent, 'Knowledge service description applied', sucess = SUCESS_POS)
    
def downloadAndInstallKsdl(serviceid = None, destinationmemberid  =None, indent = 0):
    indent = _enterFunction(indent, "Add / update service description from remote host")

    serviceid = _requestInput(indent, 'ID of the service', serviceid)
    destinationmemberid = _requestInput(indent, 'ID of member to download from', destinationmemberid)
    
    _printAction(indent, "Download description", 1)
    secs = _requestInput(indent, 'How many seconds to wait for reply', '20')
    try:
        secs = int(secs)
    except ValueError:
        _finishActionLine(SUCESS_NEG)
        _leaveFunction(indent, 'Service Description download', SUCESS_NEG)
        raise G4dsRuntimeException('Is it so difficult to provide a number here???')

    _printAction(indent, "Download in progress" )
        
    from g4dsconfigurationcontroller import getServiceController
    status = getServiceController().downloadServiceDescriptionJob(serviceid, destinationmemberid, 1)
    elapsed = 0
    timeover = 0
    import time
    from runtimecontroller import JOB_FINISHED, JOB_ABORTED
    while 1:
        time.sleep(1)
        elapsed += 1
        if status.getStatus() == JOB_FINISHED or status.getStatus() == JOB_ABORTED:
            break
        if elapsed > secs:
            timeover = 1
            break
    if status.getStatus() == JOB_ABORTED:
        _finishActionLine(SUCESS_NEG)
        _leaveFunction(indent, 'Service Description download', SUCESS_NEG)
        if status.getError() != (None, None):
            raise G4dsRuntimeException('Error for download KSDL: (%d) (%s)' % status.getError())
        else:
            raise G4dsRuntimeException('Unknown error when downloading ksdl.')
    if timeover:
        _finishActionLine(SUCESS_NEG)
        _leaveFunction(indent, 'Service Description download', SUCESS_NEG)
        raise G4dsRuntimeException('The requested action has been timed out.')
    # looks good here :)
    # let's show what we got
    _finishActionLine()
    message = status.getMessage()
    filename = _requestInput(indent, 'Name for temporaer file','./desc.tmp')
    _printAction(indent, 'Temporarely save description')
    
    try:
        file = open(filename, 'w')
        file.write(message)
        file.close()
    except IOError, msg:
        _finishActionLine(SUCESS_NEG)
        _leaveFunction(indent, 'Service Description download', SUCESS_NEG)
        raise G4dsRuntimeException('Problem with file: %s' %msg)
    _finishActionLine()
    
    # so, let's go and apply this thing then
    _printAction(indent, 'Apply description now', 1)
    addKsdl(filename, indent = indent)
    
    choice = _requestInput(indent, 'Clean up - delete file (y/n)?', 'y')
    if choice == 'y':
        _printAction(indent, 'Delete temporary file')
        try:
            import os
            os.remove(filename)
            _finishActionLine()
        except IOError, msg:
            _finishActionLine(SUCESS_NEG)
            _leaveFunction(indent, 'Service Description download', SUCESS_NEG)
            raise G4dsRuntimeException('Problem with deleting file: %s' %msg)
    
    _leaveFunction(indent, 'Service description updated from remote', sucess = SUCESS_POS)
    
def subscribeMemberToService(memberid = None, serviceid = None, indent = 0):
    indent = _enterFunction(indent, "Subscribe member to knowledge service")

    if not memberid:
        from communitymanager import getMemberManager
        memberid = getMemberManager().getLocalMember().getId()
    
    memberid = _requestInput(indent, 'Member ID', memberid)
    if not memberid:
        _leaveFunction(indent, sucess = SUCESS_NEG)
        raise G4dsRuntimeException('No member id provided')
    
    serviceid = _requestInput(indent, 'Service ID', serviceid)
    if not serviceid:
        _leaveFunction(indent, sucess = SUCESS_NEG)
        raise G4dsRuntimeException('No service id provided')

    _printAction (indent, "Check whether service is known on this node")
    from servicerepository import getServiceManager
    try:
        s = getServiceManager().getService(serviceid)
        _finishActionLine()
    except KeyError:
        _finishActionLine(SUCESS_NEG)
        choice = _requestInput(indent, 'Download service description? (y/n)', 'y')
        if choice != 'y':
            _leaveFunction(indent, 'Subscribe Member aborted', SUCESS_NEG)
            raise G4dsRuntimeException('Action aborted by user.')
        try:
            downloadAndInstallKsdl(serviceid, indent = indent)
        except G4dsRuntimeException, msg:
            _leaveFunction(indent, 'Subscribe member failed', sucess = SUCESS_NEG)
            raise G4dsRuntimeException(msg)
    
    _printAction(indent, 'Check for current subscription')
    try:
        s.getMembers().index(memberid)
        _finishActionLine(SUCESS_NEG)
        _leaveFunction(indent, 'Subscribe member to service', sucess = SUCESS_NEG)
        raise G4dsRuntimeException('Check subscription: The requested member is subsribed already.')
    except ValueError:
        _finishActionLine()
    
    destinationid = _requestInput(indent, 'Member ID for authority')
    if not destinationid:
        _leaveFunction(indent, 'Subscribe member to service', sucess = SUCESS_NEG)
        raise G4dsRuntimeException('No authority id provided')

    secs = _requestInput(indent, 'How many seconds to wait for reply', '20')
    try:
        secs = int(secs)
    except ValueError:
        _finishActionLine(SUCESS_NEG)
        _leaveFunction(indent, 'Service subscription', SUCESS_NEG)
        raise G4dsRuntimeException('Is it so difficult to provide a number here???')
        
    _printAction(indent, 'Connect for final subscription')
    try:
        from g4dsconfigurationcontroller import getServiceController
        getServiceController().requestSubscriptionJob(serviceid, memberid, destinationid, secs)
        _finishActionLine()
    except G4dsException, msg:
        _finishActionLine(SUCESS_NEG)
        _leaveFunction(indent, 'Service subscription', sucess = SUCESS_NEG)
        raise G4dsRuntimeException('During subscription: %s' %(msg))
    
    # here we go - let's put it in the managers as well
    from servicerepository import getServiceManager
    getServiceManager().getService(serviceid).addMember(memberid)
    
    choice = _requestInput(indent, 'Recalculate access control (y/n)?','y')
    if choice == 'y':
        recalculatePermissions(indent = indent)    
    
    _leaveFunction(indent, 'Member subscribed to knowledge service', sucess = SUCESS_POS)

def uploadKsdl(serviceid = None, indent = 0):

    indent = _enterFunction(indent, 'Upload service description')
    
    serviceid = _requestInput(indent, 'Upload ksdl of service with ID', serviceid)
    from servicerepository import getServiceManager
    _printAction(indent, 'Load service')
    try:
        service = getServiceManager().getService(serviceid)
        ksdl = service.getKsdl()
    except KeyError, msg:
        _finishActionLine(SUCESS_NEG)
        _leaveFunction(indent, 'Service description upload', SUCESS_NEG)
        raise G4dsRuntimeException('KSDL upload: Service not found.')
    _finishActionLine()

    destination = _requestInput(indent, 'Upload to which node')

    secs = _requestInput(indent, 'How many seconds to wait for the upload', '30')
    try:
        secs = int(secs)
    except ValueError:
        _finishActionLine(SUCESS_NEG)
        _leaveFunction(indent, 'Service description upload', SUCESS_NEG)
        raise G4dsRuntimeException('Is it so difficult to provide a number here???')
    
    _printAction(indent, "Upload in progress" )
        
    from g4dsconfigurationcontroller import getServiceController
    try:
        if getServiceController().uploadKsdlToMemberJob(serviceid, ksdl, destination, timeout = secs):
            pass
    except Exception, msg:
        _finishActionLine(SUCESS_NEG)
        _leaveFunction(indent, 'Service description upload', SUCESS_NEG)
        raise G4dsRuntimeException('KSDL upload failed: %s' %(msg))
        
    _finishActionLine()
    
    _leaveFunction(indent, 'Service description uploaded', sucess = SUCESS_POS)

    
