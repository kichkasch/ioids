"""
Parses description files and is able to assemble new ones by using the local knowledge.

Grid for Digital Security (G4DS)

Names for XML tags are loaded from the L{xmlconfig} module.

@author: Michael Pilgermann
@contact: mailto:mpilgerm@glam.ac.uk
@license: GPL (General Public License)
"""
import xml.dom
import xml.dom.ext
from xml.dom import Node
import xml.dom.ext.reader.Sax2
import xmlconfig
import config
from StringIO import StringIO
from errorhandling import G4dsDependencyException, G4dsRuntimeException, G4dsException, G4dsDescriptionException

INITIAL_VERSION_NUMBER = '1.0.0.0'      # goes into version if no description exsisted before

class DescriptionProcessor:
    """
    Super class for all processor to provide some common functionality.
    """
    def _createOneNode(self, doc, parent, name, value = None, cdatavalue = None):
        """
        Integrates the steps for creating a node, adding it to the parent node and adding a child node for the text.
        
        @return: A node with the given name and the value as child text node
        @rtype: L{xml.dom.Node}
        """
        node = doc.createElement(name)
        parent.appendChild(node)
        if value:
            valueText = doc.createTextNode(value)
            node.appendChild(valueText)
            
        if cdatavalue:
            cdata = doc.createCDATASection(cdatavalue)
            node.appendChild(cdata)
            
        return node
        
    def _decodeOneNode(self, node):
        """
        Extracts text or CData section from a node.
        """
        text = None
        cdata = None
        for child in node.childNodes:
            if child.nodeType == Node.TEXT_NODE:
                text = child.nodeValue
            if child.nodeType == Node.CDATA_SECTION_NODE:
                cdata = child.nodeValue
        return text, cdata
        
    def _determineVersionString(self, prevVersion = None, significance = 1):
        """
        Increases the version number.
        
        @param prevVersion: Version String of the previous Version. If not, the initial version number will be applied
        @type prevVersion: C{String}
        @param significance: How big is the change from the last version; defines, which part of the version is changed - must be 1, 2, 3 or 4,
            1 is lowest significance
        @type significance: C{int}
        @return: Version String
        @rtype: C{String}
        """
        if not prevVersion:
            global INITIAL_VERSION_NUMBER
            return INITIAL_VERSION_NUMBER
    
        parts = prevVersion.split(".")
        
        # here increasing of number
        index = len(parts) - significance
        number = int(parts[index])
        number += 1
        parts[index] = str(number)
        
        ret = ""
        for x in range(0, len(parts)):
            ret += parts[x]
            if not x == len(parts) - 1:
                ret += "."
        return ret
    
# "singleton"
_communityDescriptionProcessor = None
def getCommunityDescriptionProcessor():
    """
    Singleton implementation.
    
    @return: The instance for the community description processor
    @rtype: L{CommunityDescriptionProcessor}
    """
    global _communityDescriptionProcessor
    if not _communityDescriptionProcessor:
        _communityDescriptionProcessor = CommunityDescriptionProcessor()
    return _communityDescriptionProcessor

class CommunityDescriptionProcessor(DescriptionProcessor):
    """
    Parses community descriptions (TCDL) and applies knowledge to the managers.
    """
    
    def __init__(self):
        """
        Yet empty constructor.
        """
        pass
    
    def applyTcdl(self, tcdl, resolveConstraints = 1, includingGateways = 1, inbackground = 0, includingRelations = 1, status = None, raiseExceptions = 1):
        """
        Processes a community description and distributes the knowledge to the local managers.
        
        The parameter includingRelations is for a 2 step application of community descriptions. The first step write through
        a dummy community with the required community id - no relations will be applied. Afterwards, all the referencing 
        objects are applied - this way, they are able to back-reference the community. Finally, the community description
        is applied again (the 2nd time) - but now properly with all relations. Since all related objects should have been download
        and applied, the shouldn't be any more problems with referencing.
        
        @param tcdl: Community description in XML format
        @type tcdl: C{String}
        @param resolveConstraints: Shall required descriptions (member descriptions for authorities) be downloaded during the process
        @type resolveConstraints: C{Boolean}
        @param includingGateways: Indicates, whether gateways shall be processed as well (necessary e.g. when two new TCs reference each other by GWs)
        @type includingGateways: C{Boolean}
        @param raiseExceptions: Only raise exceptions when we are in the main thread.
        @type raiseExceptions: C{Boolean}
        @return: Reference to the new (or updated) community instance
        @rtype: L{communitymanager.Community}
        """
        from runtimecontroller import JobStatus, JOB_UNINITIALISED, JOB_INITIALISED, JOB_FINISHED, JOB_ABORTED
        from errorhandling import G4dsDependencyException, G4dsRuntimeException, G4dsException, G4dsDescriptionException
        if not status:
            status = JobStatus()

        if inbackground:
            import thread
            thread.start_new_thread(self.applyTcdl,(tcdl, resolveConstraints, includingGateways, 0, includingRelations, status, 0))
            return status
        
        # aaah - one more time starting itself ... if we are in the sub thread, we  should catch all G4ds exceptions
        if not raiseExceptions:
            try:
                c = self.applyTcdl(tcdl, resolveConstraints, includingGateways, inbackground, includingRelations, status, 1)
                return c
            except G4dsException, msg:
                status.setStatus(JOB_ABORTED)
                code, mesg = status.getError()
                if code == None:
                    code = 5
                if mesg == None:
                    mesg = msg
                status.setError(code, mesg)
                return
        
        status.setStatus(JOB_INITIALISED)
        
        if includingRelations:  
            self.applyTcdl(tcdl, resolveConstraints, includingGateways, inbackground, 0, status = status)
        
        dict = self.processTcdl(tcdl)
            
        from communitymanager import getCommunityManager, Community
        
        from communitymanager import getMemberManager
        c = Community (dict['id'], dict['name'], dict['description'], tcdl, dict['version'], dict['creationdate'])
        c = getCommunityManager().updateCommunity(c, 1, 1, 0, 1, 1) # do not delete the members
        if not includingRelations:
            status.setStatus(JOB_FINISHED)
            return c
        
        # authorities
        # OK, we might have a problem here: we can only add the community description, if the member descriptions are in place
        # already (referencing, relations, ...) - let's try to download the descriptions
        known_members = []
        unknown_members = []
        
        # first we check, whether there are some authorities known (we need at least one)
        for authority in dict['authorities']:
            authorityid = authority[0]
            member = None
            try:
                member = getMemberManager().getMember(authorityid)
                known_members.append(member)
            except KeyError:
                unknown_members.append(authorityid)
                pass

        if len(known_members) == 0:
            from errorhandling import G4dsDependencyException
            status.setError(0,'Applying of TCDL impossible. Neither of the authorities is known in the system. Make sure, you download the description of at least authority manually.')
            status.setStatus(JOB_ABORTED)
            raise G4dsDependencyException('Applying of TCDL impossible. Neither of the authorities is known in the system. Make sure, you download the description of at least authority manually.')

        destination = known_members[0].getId()
        # alright - if we have at least one of the authorities, we should be able to download the remaining ones from this node
        for unknown in unknown_members:
            from g4dsconfigurationcontroller import getMemberController, MEMBER_SUCESS_MDL_NOT_FOUND
            from runtimecontroller import getJobDispatcher, JobLocker
            msgId = getMemberController().requestMemberDescription(unknown, destination)
            jl = JobLocker()
            getJobDispatcher().addJob(msgId, jl)
            # here we are waiting - once, it's coming back
            # we are checking for a message
            message, args = getJobDispatcher().getMessage(msgId)
            if args['sucess'] == MEMBER_SUCESS_MDL_NOT_FOUND:
                status.setError(1,'The required MDL (' + unknown + ') for applying TDL (' + c.getId() + ') authority information could not be downloaded. You have to download it manually.')
                status.setStatus(JOB_ABORTED)
                raise G4dsDependencyException('The required MDL (' + unknown + ') for applying TDL (' + c.getId() + ') authority information could not be downloaded. You have to download it manually.')
                
            newMember = getMemberDescriptionProcessor().applyMdl(message)
            known_members.append(newMember)
            
        for authority in dict['authorities']:
            authorityid = authority[0]
            if not c.hasMember(authorityid):
                c.addMember(authorityid,1,1)
            else:
                c.addAuthority(authorityid, registerInMember = 1)
        
        
        if includingGateways:
            from communitymanager import CommunityGateway
            for gw in dict['gateways_incoming']:
                memberid = gw[0]
                communityid = gw[1]
                try:
                    member = getMemberManager().getMember(memberid)
                except KeyError:
                    member = self._downloadMdlForGw(memberid, destination, c)
                    
                try:
                    community = getCommunityManager().getCommunity(communityid)
                except KeyError:
                    community = self._downloadTcdlForGw(communityid, destination, c)
                
                gw = CommunityGateway(memberid, communityid, c.getId(), 1, 1)
                
            for gw in dict['gateways_outgoing']:
                memberid = gw[0]
                communityid = gw[1]
                try:
                    member = getMemberManager().getMember(memberid)
                except KeyError:
                    member = self._downloadMdlForGw(memberid, destination, c)
                    
                try:
                    community = getCommunityManager().getCommunity(communityid)
                except KeyError:
                    community = self._downloadTcdlForGw(communityid, destination, c)
                
                gw = CommunityGateway(memberid, c.getId(), communityid, 1, 1)
                
        # also add the protocols to be used with this community
        from communicationmanager import getProtocolManager
        for protocol in dict['protocols']:
            protocol = protocol[0]
            prot = getProtocolManager().getProtocolByNameAndInsert(protocol)
            c.addProtocol(prot.getId())
        
        # not to forget about the algorithms for encryption and so on
        from securitymanager import getAlgorithmManager
        for algorithm in dict['algorithms']:
            algorithm = algorithm[0]
            alg = getAlgorithmManager().getAlgorithmByNameAndInsert(algorithm)
            c.addAlgorithm(alg.getId())
        
        status.setStatus(JOB_FINISHED)
        return c

    def _downloadMdlForGW(self, memberid, destination, c):
        # let's download the mdl from one of the authorities then
        from g4dsconfigurationcontroller import getMemberController, MEMBER_SUCESS_MDL_NOT_FOUND
        from runtimecontroller import getJobDispatcher, JobLocker
        msgId = getMemberController().requestMemberDescription(memberid, destination)
        jl = JobLocker()
        getJobDispatcher().addJob(msgId, jl)
        # here we are waiting - once, it's coming back
        # we are checking for a message
        message, args = getJobDispatcher().getMessage(msgId)
        if args['sucess'] == MEMBER_SUCESS_MDL_NOT_FOUND:
            status.setError(2,'The required MDL (' + memberid + ') for applying TDL (' + c.getId() + ') gateway information could not be downloaded. You have to download it manually.')
            status.setStatus(JOB_ABORTED)
            raise G4dsDependencyException('The required MDL (' + memberid + ') for applying TDL (' + c.getId() + ') gateway information could not be downloaded. You have to download it manually.')
            
        newMember = getMemberDescriptionProcessor().applyMdl(message)
        return newMember
        
    def _downloadTcdlForGw(self, communityid, destination, c):
        # let's download the tcdl from one of the authorities then
        from g4dsconfigurationcontroller import getCommunityController, COMMUNITY_SUCESS_TCDL_NOT_FOUND
        from runtimecontroller import getJobDispatcher, JobLocker
        msgId = getCommunityController().requestCommunityDescription(communityid, destination)
        jl = JobLocker()
        getJobDispatcher().addJob(msgId, jl)
        # wait and wait and wait
        # and go
        message, args = getJobDispatcher().getMessage(msgId)
        if not message or args['sucess'] == COMMUNITY_SUCESS_TCDL_NOT_FOUND:
            status.setError(3,'The required TCDL (' + communityid + ') for applying TDL (' + c.getId() + ') gateway information could not be downloaded. You have to download it manually.')
            status.setStatus(JOB_ABORTED)
            raise G4dsDependencyException('The required TCDL (' + communityid + ') for applying TDL (' + c.getId() + ') gateway information could not be downloaded. You have to download it manually.')

        newCommunity = getCommunityDescriptionProcessor().applyTcdl(message)
        return newCommunity
        
    def processTcdl(self, tcdl):
        """
        Processes a community description and returns the values in there in form of a dictionary.
        
        @param tcdl: Community description to process as XML formated string
        @type tcdl: C{String}
        """
        from xml.sax._exceptions import SAXParseException
        try:
            root = xml.dom.ext.reader.Sax2.FromXml(tcdl)
        except SAXParseException, msg:
            from errorhandling import G4dsDescriptionException
            raise G4dsDescriptionException('Error when parsing the TCDL: %s' %(msg))

        node = root.childNodes[1]
        if node.nodeName != xmlconfig.tcdl_node:
            from errorhandling import G4dsDescriptionException
            raise G4dsDescriptionException('Not a community description message; tcdl tag not found')

        id = None
        version = None
        name = None
        creationdate = None
        
        fullname = None
        organisation = None
        country_code = None
        country = None
        city = None

        protocols = []
        algorithms = []
        authorities = []
        
        gateways_incoming = []
        gateways_outgoing = []
        
        # policies are now handled in dedicated policy files
##        policy = {}     # policy is a dictionary itself       
        # policies are now handled in dedicated policy files

        for child1 in node.childNodes:
            if child1.nodeType == Node.ELEMENT_NODE:
                # general tags
                if child1.nodeName == xmlconfig.tcdl_id:
                    id, tmp = self._decodeOneNode(child1)
                if child1.nodeName == xmlconfig.tcdl_version:
                    version, tmp = self._decodeOneNode(child1)
                if child1.nodeName == xmlconfig.tcdl_name:
                    name, tmp = self._decodeOneNode(child1)
                if child1.nodeName == xmlconfig.tcdl_creationdate:
                    creationdate, tmp =self. _decodeOneNode(child1)
                # description
                if child1.nodeName == xmlconfig.tcdl_description:
                    for child2 in child1.childNodes:
                        if child2.nodeType == Node.ELEMENT_NODE:
                            if child2.nodeName == xmlconfig.tcdl_description_fullname:
                                fullname, tmp = self._decodeOneNode(child2)
                            if child2.nodeName == xmlconfig.tcdl_description_organisation:
                                organisation, tmp = self._decodeOneNode(child2)
                            if child2.nodeName == xmlconfig.tcdl_description_location:
                                for child3 in child2.childNodes:
                                    if child3.nodeType == Node.ELEMENT_NODE:
                                        if child3.nodeName == xmlconfig.tcdl_description_location_country:
                                            for child4 in child3.childNodes:
                                                if child4.nodeType == Node.ELEMENT_NODE:
                                                    if child4.nodeName == xmlconfig.tcdl_description_location_country_code:
                                                        country_code, tmp = self._decodeOneNode(child4)
                                                    if child4.nodeName == xmlconfig.tcdl_description_location_country_name:
                                                        country, tmp = self._decodeOneNode(child4)
                                        if child3.nodeName == xmlconfig.tcdl_description_location_city:
                                            city, tmp = self._decodeOneNode(child3)
                # communication (protocols and algorithms)
                if child1.nodeName == xmlconfig.tcdl_communication:
                    for child2 in child1.childNodes:
                        if child2.nodeType == Node.ELEMENT_NODE:
                            if child2.nodeName == xmlconfig.tcdl_communication_protocols:
                                for child3 in child2.childNodes:
                                    if child3.nodeType == Node.ELEMENT_NODE:
                                        if child3.nodeName == xmlconfig.tcdl_communication_protocols_protocol:
                                            protocolname = None
                                            protocolcomment = ""
                                            for child4 in child3.childNodes:
                                                if child4.nodeType == Node.ELEMENT_NODE:
                                                    if child4.nodeName == xmlconfig.tcdl_communication_protocols_protocol_name:
                                                        protocolname, tmp = self._decodeOneNode(child4)
                                                    if child4.nodeName == xmlconfig.tcdl_communication_protocols_protocol_comment:
                                                        protocolcomment, tmp = self._decodeOneNode(child4)
                                            protocols.append([protocolname, protocolcomment])
                            if child2.nodeName == xmlconfig.tcdl_communication_algorithms:
                                for child3 in child2.childNodes:
                                    if child3.nodeType == Node.ELEMENT_NODE:
                                        if child3.nodeName == xmlconfig.tcdl_communication_algorithms_algorithm:
                                            algname = None
                                            algcomment = ""
                                            for child4 in child3.childNodes:
                                                if child4.nodeType == Node.ELEMENT_NODE:
                                                    if child4.nodeName == xmlconfig.tcdl_communication_algorithms_algorithm_name:
                                                        algname, tmp = self._decodeOneNode(child4)
                                                    if child4.nodeName == xmlconfig.tcdl_communication_algorithms_algorithm_comment:
                                                        algcomment, tmp = self._decodeOneNode(child4)
                                            algorithms.append([algname, algcomment])
                # authorities
                if child1.nodeName == xmlconfig.tcdl_authorities:
                    for child2 in child1.childNodes:
                        if child2.nodeType == Node.ELEMENT_NODE:
                            if child2.nodeName == xmlconfig.tcdl_authorities_authority:
                                memberid = None
                                protocol = None
                                address = None
                                algorithm = None
                                publickey = None
                                for child3 in child2.childNodes:
                                    if child3.nodeType == Node.ELEMENT_NODE:
                                        if child3.nodeName == xmlconfig.tcdl_authorities_authority_id:
                                            memberid, tmp = self._decodeOneNode(child3)
                                        if child3.nodeName == xmlconfig.tcdl_authorities_authority_endpoint:
                                            for child4 in child3.childNodes:
                                                if child4.nodeType == Node.ELEMENT_NODE:
                                                    if child4.nodeName == xmlconfig.tcdl_authorities_authority_endpoint_protocol:
                                                        protocol, tmp = self._decodeOneNode(child4)
                                                    if child4.nodeName == xmlconfig.tcdl_authorities_authority_endpoint_address:
                                                        address, tmp = self._decodeOneNode(child4)
                                                    if child4.nodeName == xmlconfig.tcdl_authorities_authority_endpoint_credential:
                                                        for child5 in child4.childNodes:
                                                            if child5.nodeType == Node.ELEMENT_NODE:
                                                                if child5.nodeName == xmlconfig.tcdl_authorities_authority_endpoint_credential_algorithm:
                                                                    algorithm, tmp = self._decodeOneNode(child5)
                                                                if child5.nodeName == xmlconfig.tcdl_authorities_authority_endpoint_credential_publickey:
                                                                    tmp, publickey = self._decodeOneNode(child5)
                                authorities.append([memberid, protocol, address, algorithm, publickey])

                if child1.nodeName == xmlconfig.tcdl_routing:
                    for child2 in child1.childNodes:
                        if child2.nodeType == Node.ELEMENT_NODE:
                            if child2.nodeName == xmlconfig.tcdl_routing_gateways:
                                for child3 in child2.childNodes:
                                    if child3.nodeType == Node.ELEMENT_NODE:
                                        if child3.nodeName == xmlconfig.tcdl_routing_gateways_incoming:
                                            for child4 in child3.childNodes:
                                                if child4.nodeType == Node.ELEMENT_NODE:
                                                    if child4.nodeName == xmlconfig.tcdl_routing_gateways_incoming_gateway:
                                                        memberid = None
                                                        communityid = None
                                                        for child5 in child4.childNodes:
                                                            if child5.nodeType == Node.ELEMENT_NODE:
                                                                if child5.nodeName == xmlconfig.tcdl_routing_gateways_incoming_gateway_memberid:
                                                                    memberid, tmp = self._decodeOneNode(child5)
                                                                if child5.nodeName == xmlconfig.tcdl_routing_gateways_incoming_gateway_source:
                                                                    for child6 in child5.childNodes:
                                                                        if child6.nodeType == Node.ELEMENT_NODE:
                                                                            if child6.nodeName == xmlconfig.tcdl_routing_gateways_incoming_gateway_source_communityid:
                                                                                communityid, tmp = self._decodeOneNode(child6)
                                                        if memberid and communityid:
                                                            gateways_incoming.append([memberid, communityid])
                                                    
                                        elif child3.nodeName == xmlconfig.tcdl_routing_gateways_outgoing:
                                            for child4 in child3.childNodes:
                                                if child4.nodeType == Node.ELEMENT_NODE:
                                                    if child4.nodeName == xmlconfig.tcdl_routing_gateways_outgoing_gateway:
                                                        memberid = None
                                                        communityid = None
                                                        for child5 in child4.childNodes:
                                                            if child5.nodeType == Node.ELEMENT_NODE:
                                                                if child5.nodeName == xmlconfig.tcdl_routing_gateways_outgoing_gateway_memberid:
                                                                    memberid, tmp = self._decodeOneNode(child5)
                                                                if child5.nodeName == xmlconfig.tcdl_routing_gateways_outgoing_gateway_destination:
                                                                    for child6 in child5.childNodes:
                                                                        if child6.nodeType == Node.ELEMENT_NODE:
                                                                            if child6.nodeName == xmlconfig.tcdl_routing_gateways_outgoing_gateway_destination_communityid:
                                                                                communityid, tmp = self._decodeOneNode(child6)
                                                        if memberid and communityid:
                                                            gateways_outgoing.append([memberid, communityid])

        # policies are now handled in dedicated policy files
##                if child1.nodeName == xmlconfig.tcdl_policy:
##                    for child2 in child1.childNodes:
##                        if child2.nodeType == Node.ELEMENT_NODE:
##                            if child2.nodeName == xmlconfig.tcdl_policy_browsalbe:
##                                browsable, tmp = self._decodeOneNode(child2)
##                                policy['browsable'] = browsable
        # policies are now handled in dedicated policy files

        dict = {}
        dict['id'] = id
        dict['version'] = version
        dict['name'] = name
        dict['creationdate'] = creationdate
        dict['fullname'] = fullname
        dict['description'] = fullname
        dict['organisation'] = organisation
        dict['country_code'] = country_code
        dict['country'] = country
        dict['city'] = city
        dict['protocols'] = protocols
        dict['algorithms'] = algorithms
        dict['authorities'] = authorities
        dict['gateways_incoming'] = gateways_incoming
        dict['gateways_outgoing'] = gateways_outgoing
        # policies are now handled in dedicated policy files
##        dict['policy'] = policy
        # policies are now handled in dedicated policy files
        return dict
        
# "singleton"
_memberDescriptionProcessor = None
def getMemberDescriptionProcessor():
    """
    Singleton implementation.
    
    @return: The instance for the member description processor
    @rtype: L{MemberDescriptionProcessor}
    """
    global _memberDescriptionProcessor
    if not _memberDescriptionProcessor:
        _memberDescriptionProcessor = MemberDescriptionProcessor()
    return _memberDescriptionProcessor

class MemberDescriptionProcessor(DescriptionProcessor):
    """
    Parses member description (MDL) as well as it may create new MDLs from local knowledge.
    """
    
    def __init__(self):
        """
        Yet empty constructor.
        """
        pass
    
    def applyMdl(self, mdl, inbackground = 0, includingRelations = 1, status = None, raiseExceptions = 1):
        """
        Processes a member description and distributes the knowledge to the local managers.
        
        @param mdl: XML description of the member
        @type mdl: C{String}
        @return: Reference to the new (or updated) member instance
        @rtype: L{communitymanager.Member}
        """
        from runtimecontroller import JobStatus, JOB_UNINITIALISED, JOB_INITIALISED, JOB_FINISHED, JOB_ABORTED
        from errorhandling import G4dsDependencyException, G4dsRuntimeException, G4dsException, G4dsDescriptionException
        if not status:
            status = JobStatus()

        if inbackground:
            import thread
            thread.start_new_thread(self.applyMdl,(mdl, 0, includingRelations, status, 0))
            return status
        
        # aaah - one more time starting itself ... if we are in the sub thread, we  should catch all G4ds exceptions
        if not raiseExceptions:
            try:
                return self.applyMdl(mdl, inbackground, includingRelations, status, 1)
            except G4dsException, msg:
                status.setStatus(JOB_ABORTED)
                code, mesg = status.getError()
                if code == None:
                    code = 5
                if mesg == None:
                    mesg = msg
                status.setError(code, mesg)
                return
        
        status.setStatus(JOB_INITIALISED)
        
        if includingRelations:  
            self.applyMdl(mdl, inbackground, 0, status) # one run without relations before; just to make sure we have the reference in place
            
        dict = self.processMdl(mdl)
        from communitymanager import getMemberManager, Member, getCommunityManager
        from communicationmanager import getEndpointManager, Endpoint, getProtocolManager
        from securitymanager import getCredentialManager, Credential, getAlgorithmManager
    
        m = Member(dict['id'],dict['name'], mdl,dict['version'],dict['creationdate'])
        m = getMemberManager().updateMember(m, 0)
        if not includingRelations:
            status.setStatus(JOB_FINISHED)
            return m

        destination = dict['id']
            
        community = None
        for c in dict['communities']:
            try:
                community = getCommunityManager().getCommunity(c)
            except KeyError:
                # let's download then :)
                communityid = c
                from g4dsconfigurationcontroller import getCommunityController, COMMUNITY_SUCESS_TCDL_NOT_FOUND
                from runtimecontroller import getJobDispatcher, JobLocker
                msgId = getCommunityController().requestCommunityDescription(communityid, destination)
                jl = JobLocker()
                getJobDispatcher().addJob(msgId, jl)
                # wait and wait and wait
                # and go
                message, args = getJobDispatcher().getMessage(msgId)
                if not message or args['sucess'] == COMMUNITY_SUCESS_TCDL_NOT_FOUND:
                    status.setError(10,'The required TCDL (' + communityid + ') for applying TDL (' + c.getId() + ') gateway information could not be downloaded. You have to download it manually.')
                    status.setStatus(JOB_ABORTED)
                    raise G4dsDependencyException('The required TCDL (' + communityid + ') for applying MDL (' + m.getId() + ') could not be downloaded. You have to download it manually.')
        
                community = getCommunityDescriptionProcessor().applyTcdl(message)
                
            m.addCommunity(c, 0)
            try:
                community.addMember(m.getId())
            except ValueError:
                pass        # that's alright - this member is known in the community already.
                
        m = getMemberManager().updateMember(m, 1)
        
        getEndpointManager().removeEndpointsForMember(m.getId())
        getCredentialManager().removeCredentialsForMember(m.getId())
        
        credentials = {}
        for c_id in dict['credentials'].keys():
            username = dict['credentials'][c_id][0]
            key = dict['credentials'][c_id][1]
            algname = dict['credentials'][c_id][2]
            alg = getAlgorithmManager().getAlgorithmByNameAndInsert(algname)
            c = Credential(None, alg.getId(),username,key,m.getId())
            getCredentialManager().addCredential(c)
            credentials[c_id] = c
        
        for e in dict['endpoints']:
            communityid = e[0]
            protocol = e[1] 
            address = e[2]
            credentialid = e[3]
            protocol = getProtocolManager().getProtocolByNameAndInsert(protocol)
            e = Endpoint(None, m.getId(), communityid, protocol.getId(), address, credentials[credentialid].getId())
            getEndpointManager().addEndpoint(e)
            
        status.setStatus(JOB_FINISHED)
        return m
        
        
    def processMdl(self, mdl):
        """
        Processes a member description and returns the values in there in form of a dictionary.
        
        @param mdl: Member description to process as XML formated string
        @type mdl: C{String}
        """
        from xml.sax._exceptions import SAXParseException
        try:
            root = xml.dom.ext.reader.Sax2.FromXml(mdl)
        except SAXParseException, msg:
            from errorhandling import G4dsDescriptionException
            raise G4dsDescriptionException('Error when parsing the MDL: %s' %(msg))
            
        node = root.childNodes[1]
        if node.nodeName != xmlconfig.mdl_node:
            raise G4dsDescriptionException, 'Not a member description message; mdl tag not found'

        id = None
        version = None
        name = None
        creationdate = None
        
        fullname = None
        organisation = None
        country_code = None
        country = None
        city = None

        credentials = {}    # key is the doc id
        endpoints = []
        communities = []
        
        for child1 in node.childNodes:
            if child1.nodeType == Node.ELEMENT_NODE:
                # general tags
                if child1.nodeName == xmlconfig.mdl_id:
                    id, tmp = self._decodeOneNode(child1)
                if child1.nodeName == xmlconfig.mdl_version:
                    version, tmp = self._decodeOneNode(child1)
                if child1.nodeName == xmlconfig.mdl_name:
                    name, tmp = self._decodeOneNode(child1)
                if child1.nodeName == xmlconfig.mdl_creationdate:
                    creationdate, tmp =self. _decodeOneNode(child1)
                # description
                if child1.nodeName == xmlconfig.mdl_description:
                    for child2 in child1.childNodes:
                        if child2.nodeType == Node.ELEMENT_NODE:
                            if child2.nodeName == xmlconfig.mdl_description_fullname:
                                fullname, tmp = self._decodeOneNode(child2)
                            if child2.nodeName == xmlconfig.mdl_description_organisation:
                                organisation, tmp = self._decodeOneNode(child2)
                            if child2.nodeName == xmlconfig.mdl_description_location:
                                for child3 in child2.childNodes:
                                    if child3.nodeType == Node.ELEMENT_NODE:
                                        if child3.nodeName == xmlconfig.mdl_description_location_country:
                                            for child4 in child3.childNodes:
                                                if child4.nodeType == Node.ELEMENT_NODE:
                                                    if child4.nodeName == xmlconfig.mdl_description_location_country_code:
                                                        country_code, tmp = self._decodeOneNode(child4)
                                                    if child4.nodeName == xmlconfig.mdl_description_location_country_name:
                                                        country, tmp = self._decodeOneNode(child4)
                                        if child3.nodeName == xmlconfig.mdl_description_location_city:
                                            city, tmp = self._decodeOneNode(child3)
                # credentials
                if child1.nodeName == xmlconfig.mdl_credentials:
                    for child2 in child1.childNodes:
                        if child2.nodeType == Node.ELEMENT_NODE:
                            if child2.nodeName == xmlconfig.mdl_credentials_credential:
                                docid = None
                                username = None
                                publickey = None
                                algname = None
                                for child3 in child2.childNodes:
                                    if child3.nodeType == Node.ELEMENT_NODE:
                                        if child3.nodeName == xmlconfig.mdl_credentials_credential_docid:
                                            docid, tmp = self._decodeOneNode(child3)
                                        if child3.nodeName == xmlconfig.mdl_credentials_credential_username:
                                            username, tmp = self._decodeOneNode(child3)
                                            if username == None:
                                                username = ''
                                        if child3.nodeName == xmlconfig.mdl_credentials_credential_publickey:
                                            for child4 in child3.childNodes:
                                                if child4.nodeType == Node.ELEMENT_NODE:
                                                    if child4.nodeName == xmlconfig.mdl_credentials_credential_publickey_algorithm:
                                                        for child5 in child4.childNodes:
                                                            if child5.nodeType == Node.ELEMENT_NODE:
                                                                if child5.nodeName == xmlconfig.mdl_credentials_credential_publickey_algorithm_name:
                                                                    algname, tmp = self._decodeOneNode(child5)
                                                    if child4.nodeName == xmlconfig.mdl_credentials_credential_publickey_value:
                                                        tmp, publickey = self._decodeOneNode(child4)
                                                        import binascii as hex
                                                        publickey = hex.unhexlify(publickey) # keys might be binary - so we rather encode them as hex strings
                                credentials[docid] = [username, publickey, algname]

                # communities and endpoints
                if child1.nodeName == xmlconfig.mdl_communities:
                    for child2 in child1.childNodes:
                        if child2.nodeType == Node.ELEMENT_NODE:
                            if child2.nodeName == xmlconfig.mdl_communities_community:
                                communityid = None
                                for child3 in child2.childNodes:
                                    if child3.nodeType == Node.ELEMENT_NODE:
                                        if child3.nodeName == xmlconfig.mdl_communities_community_id:
                                            communityid, tmp = self._decodeOneNode(child3)
                                            communities.append(communityid)
                                        if child3.nodeName == xmlconfig.mdl_communities_community_endpoints:
                                            for child4 in child3.childNodes:
                                                if child4.nodeType == Node.ELEMENT_NODE:
                                                    if child4.nodeName == xmlconfig.mdl_communities_community_endpoints_endpoint:
                                                        protocol = None
                                                        address = None
                                                        credentialid = None
                                                        for child5 in child4.childNodes:
                                                            if child5.nodeType == Node.ELEMENT_NODE:
                                                                if child5.nodeName == xmlconfig.mdl_communities_community_endpoints_endpoint_protocol:
                                                                    protocol, tmp = self._decodeOneNode(child5)
                                                                if child5.nodeName == xmlconfig.mdl_communities_community_endpoints_endpoint_address:
                                                                    address, tmp = self._decodeOneNode(child5)
                                                                if child5.nodeName == xmlconfig.mdl_communities_community_endpoints_endpoint_credential:
                                                                    for child6 in child5.childNodes:
                                                                        if child6.nodeType == Node.ELEMENT_NODE:
                                                                            if child6.nodeName == xmlconfig.mdl_communities_community_endpoints_endpoint_credential_docid:
                                                                                credentialid, tmp = self._decodeOneNode(child6)
                                                        endpoint = [communityid, protocol, address, credentialid]
                                                        endpoints.append(endpoint)

        dict = {}
        dict['id'] = id
        dict['version'] = version
        dict['name'] = name
        dict['creationdate'] = creationdate
        dict['fullname'] = fullname
        dict['organisation'] = organisation
        dict['country_code'] = country_code
        dict['country'] = country
        dict['city'] = city
        dict['credentials'] = credentials
        dict['communities'] = communities
        dict['endpoints'] = endpoints
        return dict
        
    def generateLocalMdl(self, previousVersion = None, significance = 1):
        """
        Generates an MDL document for the local node by using local knowledge.
        
        @param previousVersion: Last Version; if non is given, this is handled as initial version
        @type previousVersion: C{String}
        @param significance: How big is the change from the last version; defines, which part of the version string is changed;
            must be 1, 2, 3 or 4, whereby 1 is lowest significance
        @return: XML formated String for the MDL for the local node
        @rtype: C{String}
        """
        localMemberId = config.memberid 
        
        impl = xml.dom.getDOMImplementation()
        doc = impl.createDocument("", xmlconfig.mdl_node, None)
        
        # top level
        elementMdl = doc.documentElement
        
        # identity
        self._createOneNode(doc, elementMdl, xmlconfig.mdl_id, localMemberId)     
        self._createOneNode(doc, elementMdl, xmlconfig.mdl_version, 
            self._determineVersionString(previousVersion, significance))
        self._createOneNode(doc, elementMdl, xmlconfig.mdl_name, config.member_name)
        import datetime
        now = datetime.date.today().__str__()       # luckily, __str__ provides exactly the format we need
        self._createOneNode(doc, elementMdl, xmlconfig.mdl_creationdate, now)
        
        # description
        elementDescription = self._createOneNode(doc, elementMdl, xmlconfig.mdl_description)
        self._createOneNode(doc, elementDescription, xmlconfig.mdl_description_fullname, config.description_fullname)
        self._createOneNode(doc, elementDescription, xmlconfig.mdl_description_organisation, config.description_organisation)
        elementLocation = self._createOneNode(doc, elementDescription, xmlconfig.mdl_description_location)
        elementCountry =self._createOneNode(doc, elementLocation, xmlconfig.mdl_description_location_country)
        self._createOneNode(doc, elementCountry, xmlconfig.mdl_description_location_country_code, config.description_location_countrycode)
        self._createOneNode(doc, elementCountry, xmlconfig.mdl_description_location_country_name, config.description_location_countryname)
        self._createOneNode(doc, elementLocation, xmlconfig.mdl_description_location_city, config.description_location_city)
        
        # credentials
        elementCredentials = self._createOneNode(doc, elementMdl, xmlconfig.mdl_credentials)
        from securitymanager import getCredentialManager, getAlgorithmManager
        for credential in getCredentialManager().getCredentialsForMember(localMemberId):
            elementCredential = self._createOneNode(doc, elementCredentials, xmlconfig.mdl_credentials_credential)
            self._createOneNode(doc, elementCredential, xmlconfig.mdl_credentials_credential_docid, credential.getId())
            self._createOneNode(doc, elementCredential, xmlconfig.mdl_credentials_credential_username, credential.getUsername())
            elementKey = self._createOneNode(doc, elementCredential, xmlconfig.mdl_credentials_credential_publickey)
            algName = getAlgorithmManager().getAlgorithm(credential.getAlgorithmId()).getName()
            elementKeyAlg = self._createOneNode(doc, elementKey, xmlconfig.mdl_credentials_credential_publickey_algorithm)
            self._createOneNode(doc, elementKeyAlg, xmlconfig.mdl_credentials_credential_publickey_algorithm_name, algName)
            import binascii as hex
            keyValue = hex.hexlify(credential.getKey()) # keys might be binary - so we rather encode them as hex strings
            self._createOneNode(doc, elementKey, xmlconfig.mdl_credentials_credential_publickey_value, None, keyValue)
            
        # communities with their endpoints
        elementCommunities = self._createOneNode(doc, elementMdl, xmlconfig.mdl_communities)
        from communitymanager import getCommunityManager, getMemberManager
        from communicationmanager import getEndpointManager, getProtocolManager
        communityids = getMemberManager().getLocalMember().getCommunityIds()
        for communityid in communityids:
            community = getCommunityManager().getCommunity(communityid)
            elementCommunity = self._createOneNode(doc, elementCommunities, xmlconfig.mdl_communities_community)
            self._createOneNode(doc, elementCommunity, xmlconfig.mdl_communities_community_id, communityid)

            elementEndpoints = self._createOneNode(doc, elementCommunity, xmlconfig.mdl_communities_community_endpoints)
            for endpoint in getEndpointManager().getEndpointsForMember(localMemberId, communityid):
                elementEndpoint = self._createOneNode(doc, elementEndpoints, xmlconfig.mdl_communities_community_endpoints_endpoint)
                protocolName = getProtocolManager().getProtocol(endpoint.getProtocolId()).getName()
                self._createOneNode(doc, elementEndpoint, xmlconfig.mdl_communities_community_endpoints_endpoint_protocol, protocolName)
                self._createOneNode(doc, elementEndpoint, xmlconfig.mdl_communities_community_endpoints_endpoint_address, endpoint.getAddress())
                elementCredential = self._createOneNode(doc, elementEndpoint, xmlconfig.mdl_communities_community_endpoints_endpoint_credential)
                self._createOneNode(doc, elementCredential, xmlconfig.mdl_communities_community_endpoints_endpoint_credential_docid, endpoint.getCredentialId())
        
        stio = StringIO()
        xml.dom.ext.PrettyPrint(doc, stio)
        value = stio.getvalue()
        stio.close()
        return value

        
# "singleton"
_serviceDescriptionProcessor = None
def getServiceDescriptionProcessor():
    """
    Singleton implementation.
    
    @return: The instance for the service description processor
    @rtype: L{ServiceDescriptionProcessor}
    """
    global _serviceDescriptionProcessor
    if not _serviceDescriptionProcessor:
        _serviceDescriptionProcessor = ServiceDescriptionProcessor()
    return _serviceDescriptionProcessor

class ServiceDescriptionProcessor(DescriptionProcessor):
    """
    Parses service descriptions (KSDL) and applies knowledge to the managers.
    """
    
    def __init__(self):
        """
        Yet empty constructor.
        """
        pass

    def processKsdl(self, ksdl):
        """
        Processes a service description given in xml format.
        
        Parses through the XML string and stores all values in easily accessable dictionaries.
        
        @param ksdl: Service description in XML representation
        @type ksdl: C{String}
        @return: Dictionary with all values encoded in the XML string
        @rtype: C{Dict}
        """
        from xml.sax._exceptions import SAXParseException
        try:
            root = xml.dom.ext.reader.Sax2.FromXml(ksdl)
        except SAXParseException, msg:
            from errorhandling import G4dsDescriptionException
            raise G4dsDescriptionException('Error when parsing the KSDL: %s' %(msg))

        node = root.childNodes[1]
        if node.nodeName != xmlconfig.ksdl_node:
            from errorhandling import G4dsDescriptionException
            raise G4dsDescriptionException('Not a service description message; ksdl tag not found')

        id = None
        version = None
        name = None
        creationdate = None
        lastupdate = None
        
        fullname = None
        contacts = []

        communities = []
        messageformats = []
        authorities = []
        
        for child1 in node.childNodes:
            if child1.nodeType == Node.ELEMENT_NODE:
                # general tags
                if child1.nodeName == xmlconfig.ksdl_id:
                    id, tmp = self._decodeOneNode(child1)
                if child1.nodeName == xmlconfig.ksdl_version:
                    version, tmp = self._decodeOneNode(child1)
                if child1.nodeName == xmlconfig.ksdl_name:
                    name, tmp = self._decodeOneNode(child1)
                if child1.nodeName == xmlconfig.ksdl_creationdate:
                    creationdate, tmp =self. _decodeOneNode(child1)
                if child1.nodeName == xmlconfig.ksdl_lastupdate:
                    lastupdate, tmp =self. _decodeOneNode(child1)
                # description
                if child1.nodeName == xmlconfig.ksdl_description:
                    for child2 in child1.childNodes:
                        if child2.nodeType == Node.ELEMENT_NODE:
                            if child2.nodeName == xmlconfig.ksdl_description_fullname:
                                fullname, tmp = self._decodeOneNode(child2)
                            elif child2.nodeName == xmlconfig.ksdl_description_contacts:
                                for child3 in child2.childNodes:
                                    if child3.nodeType == Node.ELEMENT_NODE:
                                        if child3.nodeName == xmlconfig.ksdl_description_contacts_contact:
                                            contact = {}
                                            for child4 in child3.childNodes:
                                                if child4.nodeType == Node.ELEMENT_NODE:
                                                    if child4.nodeName == xmlconfig.ksdl_description_contacts_contact_name:
                                                        cname, tmp = self._decodeOneNode(child4)
                                                        contact['name'] = cname
                                                    if child4.nodeName == xmlconfig.ksdl_description_contacts_contact_organisation:
                                                        organisation, tmp = self._decodeOneNode(child4)
                                                        contact['organisation'] = organisation
                                                    if child4.nodeName == xmlconfig.ksdl_description_contacts_contact_email:
                                                        email, tmp = self._decodeOneNode(child4)
                                                        contact['email'] = email
                                            contacts.append(contact)
                                            
                if child1.nodeName == xmlconfig.ksdl_communication:
                    for child2 in child1.childNodes:
                        if child2.nodeType == Node.ELEMENT_NODE:
                            if child2.nodeName == xmlconfig.ksdl_communication_communities:
                                for child3 in child2.childNodes:
                                    if child3.nodeType == Node.ELEMENT_NODE:
                                        if child3.nodeName == xmlconfig.ksdl_communication_communities_community:
                                            for child4 in child3.childNodes:
                                                if child4.nodeType == Node.ELEMENT_NODE:
                                                    if child4.nodeName == xmlconfig.ksdl_communication_communities_community_id:
                                                        comm_id, tmp = self._decodeOneNode(child4)
                                                        communities.append(comm_id)
                            elif child2.nodeName == xmlconfig.ksdl_communication_messageformats:
                                for child3 in child2.childNodes:
                                    if child3.nodeType == Node.ELEMENT_NODE:
                                        if child3.nodeName == xmlconfig.ksdl_communication_messageformats_messageformat:
                                            messageformat = {}
                                            for child4 in child3.childNodes:
                                                if child4.nodeType == Node.ELEMENT_NODE:
                                                    if child4.nodeName == xmlconfig.ksdl_communication_messageformats_messageformat_id:
                                                        mfid, tmp = self._decodeOneNode(child4)
                                                        messageformat['id'] = mfid
                                                    if child4.nodeName == xmlconfig.ksdl_communication_messageformats_messageformat_name:
                                                        mfname, tmp = self._decodeOneNode(child4)
                                                        messageformat['name'] = mfname
                                                    if child4.nodeName == xmlconfig.ksdl_communication_messageformats_messageformat_definition:
                                                        mfdef, tmp = self._decodeOneNode(child4)
                                                        messageformat['definition'] = mfdef
                                            messageformats.append(messageformat)

                if child1.nodeName == xmlconfig.ksdl_authorities:
                    for child2 in child1.childNodes:
                        if child2.nodeType == Node.ELEMENT_NODE:
                            if child2.nodeName == xmlconfig.ksdl_authorities_authority:
                                for child3 in child2.childNodes:
                                    if child3.nodeType == Node.ELEMENT_NODE:
                                        if child3.nodeName == xmlconfig.ksdl_authorities_authority_memberid:
                                            mid, tmp = self._decodeOneNode(child3)
                                            authorities.append(mid)
                            
        dict = {}
        dict['id'] = id
        dict['version'] = version
        dict['name'] = name
        dict['creationdate'] = creationdate
        dict['lastupdate'] = lastupdate
        
        dict['fullname'] = fullname
        dict['contacts'] = contacts
        
        dict['communities'] = communities
        dict['messageformats'] = messageformats
        dict['authorities'] = authorities
        
        return dict

    def applyKsdl(self, ksdl, includingRelations =1, inbackground = 0, status = None, raiseExceptions = 1):
        """
        Apply a knowledge service desciption to the local managers.
        """
        from runtimecontroller import JobStatus, JOB_UNINITIALISED, JOB_INITIALISED, JOB_FINISHED, JOB_ABORTED
        from errorhandling import G4dsDependencyException, G4dsRuntimeException, G4dsException, G4dsDescriptionException
        from communitymanager import getCommunityManager, getMemberManager
        from g4dsconfigurationcontroller import getMemberController, getCommunityController, COMMUNITY_SUCESS_TCDL_NOT_FOUND, MEMBER_SUCESS_MDL_NOT_FOUND
        
        if not status:
            status = JobStatus()
            
        if inbackground:
            import thread
            thread.start_new_thread(self.applyKsdl, (ksdl, includingRelations, 0, status, 0))
            return status
            
        if not raiseExceptions:
            try:
                s = self.applyKsdl(ksdl, includingRelations, inbackground, status, 1)
                return s
            except G4dsException, msg:
                status.setStatus(JOB_ABORTED)
                code, mesg = status.getError()
                if code == None:
                    code = 5
                if mesg == None:
                    mesg = msg
                status.setError(code, mesg)
                return
                
        status.setStatus(JOB_INITIALISED)
        

        dict = self.processKsdl(ksdl)
        from servicerepository import getServiceManager, Service
        s = Service(dict['id'], dict['name'], ksdl, dict['version'], dict['lastupdate'])
        s = getServiceManager().updateService(s, 1, 0, 1)       # we have to recreate community relations later on!
        
        
        if not includingRelations:
            status.setStatus(JOB_FINISHED)
            return s

        # authorities
        # we have to download member descriptions of authorities first (well, if they are not yet in place)
        known_members = []
        unknown_members = []
        
        for authorityid in dict['authorities']:
            member = None
            try:
                member = getMemberManager().getMember(authorityid)
                known_members.append(authorityid)
            except KeyError:
                unknown_members.append(authorityid)
                pass
                
        if len(known_members) == 0:
            from errorhandling import G4dsDependencyException
            status.setError(0, 'Applying of KSDL impossible. Neither of the authorities is known to the system. Make sure, you download the description of at least one authority manually.')
            status.setStatus(JOB_ABORTED)
            raise G4dsDependencyException( 'Applying of KSDL impossible. Neither of the authorities is known to the system. Make sure, you download the description of at least one authority manually.')
            
        destination = known_members[0]
        # let's simply download the remaining MDLs from the first member; it should know them ...
        
        for unknown in unknown_members:
            from g4dsconfigurationcontroller import getMemberController, MEMBER_SUCESS_MDL_NOT_FOUND
            from runtimecontroller import getJobDispatcher, JobLocker
            msgId = getMemberController().requestMemberDescription(unknown, destination)
            jl = JobLocker()
            getJobDispatcher().addJob(msgId, jl)
            # here we are waiting - once, it's coming back
            # we are checking for a message
            message, args = getJobDispatcher().getMessage(msgId)
            if args['sucess'] == MEMBER_SUCESS_MDL_NOT_FOUND:
                status.setError(1,'The required MDL (' + unknown + ') for applying KSDL (' + s.getId() + ') authority information could not be downloaded. You have to download it manually.')
                status.setStatus(JOB_ABORTED)
                raise G4dsDependencyException('The required MDL (' + unknown + ') for applying KSDL (' + s.getId() + ') authority information could not be downloaded. You have to download it manually.')
                
            newMember = getMemberDescriptionProcessor().applyMdl(message)
            known_members.append(newMember.getId())
            
            
        for authorityid in dict['authorities']:
            if not s.hasMember(authorityid):
                s.addMember(authorityid)
            if not s.hasAuthority(authorityid):
                s.addAuthority(authorityid)
            
        #
        # fine - authorities are there; let's do the same for the communities then ... 
        unknown_tcs = []
        
        for communityid in dict['communities']:
            community = None
            try:
                community = getCommunityManager().getCommunity(communityid)
            except KeyError:
                unknown_tcs.append(communityid)
                pass

        for unknown in unknown_tcs:
            from g4dsconfigurationcontroller import getMemberController, MEMBER_SUCESS_MDL_NOT_FOUND
            from runtimecontroller import getJobDispatcher, JobLocker
            msgId = getCommunityController().requestCommunityDescription(unknown, destination)
            jl = JobLocker()
            getJobDispatcher().addJob(msgId, jl)
            # here we are waiting - once, it's coming back
            # we are checking for a message
            message, args = getJobDispatcher().getMessage(msgId)
            if args['sucess'] == COMMUNITY_SUCESS_TCDL_NOT_FOUND:
                status.setError(1,'The required TCDL (' + unknown + ') for applying KSDL (' + c.getId() + ') community information could not be downloaded. You have to download it manually.')
                status.setStatus(JOB_ABORTED)
                raise G4dsDependencyException('The required TCDL (' + unknown + ') for applying KSDL (' + c.getId() + ') community information could not be downloaded. You have to download it manually.')
                
        for communityid in dict['communities']:
            if not s.hasCommunity(communityid):
                s.addCommunity(communityid)
        

        status.setStatus(JOB_FINISHED)
        return s
