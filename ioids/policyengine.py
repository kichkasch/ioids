"""
Responsible for parsing IOIDS data engine policies and providing interfaces for checking against them.

Inter-Organisational Intrusion Detection System (IOIDS)

Check README in the IOIDS folder for more information.

@author: Michael Pilgermann
@contact: mailto:mpilgerm@glam.ac.uk
@license: GPL (General Public License)
"""

import config
from errorhandling import IoidsDescriptionException
import xml.dom
from xml.dom import Node
import xml.dom.ext.reader.Sax2
# from StringIO import StringIO
import xml.dom.ext

_policyEngine = None
def getPolicyEngine():
    """
    Maintains the instance of PolicyEngine.
    """
    global _policyEngine
    if not _policyEngine:
        _policyEngine = PolicyEngine()
    return _policyEngine

class PolicyEngine:

    def __init__(self):
        """
        Yet empty constructor.
        """
        self._rules = {}
        
    def startup(self):
        """
        Loads the policy XML files into memory.
        """
        tmpRules = []
        parser = PolicyParser()
        locations = config.LOCATION_POLICY_FILES
        for location in locations:
            file = open(location, 'r')
            policy = file.read()
            file.close()
            rules = parser.parsePolicy(policy)
            tmpRules += rules
        
        from ioidslogging import getDefaultLogger, DATAENGINE_POLICY_STATUS
        getDefaultLogger().newMessage(DATAENGINE_POLICY_STATUS, 'PolicyEngine: Processed %d rule(s) from %d file(s) on startup' %(len(tmpRules), len(locations)))
        
        for rule in tmpRules:
            self._rules[rule['id']] = rule
        
        self._sortedKeys = self._rules.keys()
        self._sortedKeys.sort()
        
    def lookup(self, parameters):
        """
        Checks the given parameters against its rules and comes back with the corrosponding action(s) including parameters.
        
        The parameters describe the situation of a rule. They have to be given in dictionary format. Allowed keys are:
        - origin (values: local | remote)
        - subsystem (values: name of the soapsy subsystem)
        - sender (values: G4DS id of the sender)
        
        @return: List of reactions
        """
        retReactions = []
        for ruleId in self._sortedKeys:
            # check against all parameters given in the attributes
            rule = self._rules[ruleId]
            if parameters.has_key('origin'):
                if rule['situation'].has_key('origin'):
                    if not (rule['situation']['origin'] == '*' or rule['situation']['origin'] == parameters['origin']):
                        continue
            if parameters.has_key('subsystem'):
                if rule['situation'].has_key('subsystem'):
                    if not (rule['situation']['subsystem'] == '*'):
                        try:
                            rule['situation']['subsystem'].index(parameters['subsystem'])
                        except ValueError, msg:
                            continue
            if parameters.has_key('sender'):
                if rule['situation'].has_key('sender'):
                    if not (rule['situation']['sender'] == '*' ):
                        try:
                            rule['situation']['sender'].index(parameters['sender'])
                        except ValueError, msg:
                            continue
            # looks like, this rule is suiting all the parameters - let's get the reactions then :) - in order of course
            
            reactions = rule['reactions']
            ids = reactions.keys()
            ids.sort()
            for reactionId in ids:
                reaction = reactions[reactionId]
                if reaction['type'] == 'Terminate':
                    return retReactions
                # elsewhise, just add it to the list of proposed reactions - the rest is up to the dataengine itself
                retReactions.append(reaction)   # this is an ordered list - so the dataengine will get it in order for appropriate processing
        return retReactions
        
class PolicyParser:

    def __init__(self):
        """
        Yet empty constructor.
        """
        pass
        
    def parsePolicy(self, policy):
        """
        Parses one policy file and returns the result in List / Dictionary format
        """
        rules = []
        
        root = xml.dom.ext.reader.Sax2.FromXml(policy)
        node = None
        for node1 in root.childNodes:
            if node1.nodeType == Node.ELEMENT_NODE:
                if node1.nodeName == 'ioids-policy':
                    if node:
                        from errorhandling import IoidsDescriptionException
                        raise IoidsDescriptionException('Only one policy per file allowed.')                    
                    node = node1
                else:
                    from errorhandling import IoidsDescriptionException
                    raise IoidsDescriptionException('Unrecognised tag <%s> in policy description' %(node1.nodeName))        

        for node in node1.childNodes:
            if node.nodeType == Node.ELEMENT_NODE:
                if node.nodeName == 'rule':
                    rules.append(self._parseRule(node))
                else:
                    from errorhandling import IoidsDescriptionException
                    raise IoidsDescriptionException('Unrecognised tag <%s> in policy description' %(node.nodeName))
            
        return rules
        
    def _parseRule(self, node):
        rule = {}
        
        for child in node.childNodes:
            if child.nodeType == Node.ELEMENT_NODE:
                if child.nodeName == 'id':      # here is only the id as a text value to be found
                    for child1 in child.childNodes:
                        if child1.nodeType == Node.TEXT_NODE:
                            rule['id'] = child1.nodeValue
                elif child.nodeName == 'situation': # we should find elements like origin, sender, subsystem
                    situation = {}
                    for child1 in child.childNodes:
                        if child1.nodeType == Node.ELEMENT_NODE:
                            if child1.nodeName == 'origin':
                                for child2 in child1.childNodes:
                                    if child2.nodeType == Node.TEXT_NODE:
                                        situation['origin'] = child2.nodeValue
                            elif child1.nodeName == 'sender':
                                for child2 in child1.childNodes:
                                    if child2.nodeType == Node.TEXT_NODE:
                                        situation['sender'] = child2.nodeValue
                            elif child1.nodeName == 'subsystem':
                                for child2 in child1.childNodes:
                                    if child2.nodeType == Node.TEXT_NODE:
                                        situation['subsystem'] = child2.nodeValue
                            else:
                                raise IoidsDescriptionException('Unrecognised tag <%s> in policy description' %(child1.nodeName))         
                    rule['situation'] = situation
                elif child.nodeName == 'reactions':
                    reactions = {}
                    for child1 in child.childNodes:
                        if child1.nodeType == Node.ELEMENT_NODE:
                            if child1.nodeName == 'reaction':
                                reaction = {}
                                id = None
                                type = None
                                parameters = {}
                                reaction ['type'] = None
                                id = child1.getAttribute('number')
                                
                                for child2 in child1.childNodes:
                                    if child2.nodeType == Node.ELEMENT_NODE:
                                        if child2.nodeName == 'type':
                                            for child3 in child2.childNodes:
                                                if child3.nodeType == Node.TEXT_NODE:
                                                    type = child3.nodeValue
                                        elif child2.nodeName == 'parameters':
                                            for child3 in child2.childNodes:
                                                if child3.nodeType == Node.ELEMENT_NODE:
                                                    if child3.nodeName == 'classification':
                                                        for child4 in child3.childNodes:
                                                            if child4.nodeType == Node.TEXT_NODE:
                                                                parameters['classification'] = child4.nodeValue
                                                    elif child3.nodeName == 'community':
                                                        for child4 in child3.childNodes:
                                                            if child4.nodeType == Node.TEXT_NODE:
                                                                parameters['community'] = child4.nodeValue
                                                    elif child3.nodeName == 'distribute':
                                                        distribute = {}
                                                        for child4 in child3.childNodes:
                                                            if child4.nodeType == Node.ELEMENT_NODE:
                                                                if child4.nodeName == 'domain':
                                                                    for child5 in child4.childNodes:
                                                                        if child5.nodeType == Node.TEXT_NODE:
                                                                            distribute['domain'] = child5.nodeValue
                                                                else:
                                                                    raise IoidsDescriptionException('Unrecognised tag <%s> in policy description' %(child4.nodeName))         
                                                        parameters['distribute'] = distribute
                                                    else:
                                                        raise IoidsDescriptionException('Unrecognised tag <%s> in policy description' %(child3.nodeName))         
                                        else:
                                            raise IoidsDescriptionException('Unrecognised tag <%s> in policy description' %(child2.nodeName))         
                                
                                reaction ['type'] = type
                                reaction ['parameters'] = parameters
                                reaction['id'] = id
                                reactions[id] = reaction
                            else:
                                raise IoidsDescriptionException('Unrecognised tag <%s> in policy description' %(child1.nodeName))         
                    
                    rule['reactions'] = reactions
                else:
                    raise IoidsDescriptionException('Unrecognised tag <%s> in policy description' %(child.nodeName))         
        
        return rule
        
        
