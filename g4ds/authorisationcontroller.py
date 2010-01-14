"""
Deals with all ussues concerning authorisation / permissions.

Grid for Digital Security (G4DS)

Theoratically, there are 3 types of objects for the permission model:

    1. Actors
    2. Targets
    3. Operations
    
In fact, an actor performs a certain action on a certain target. 

Actors are always members. Targets might be either of members, communities or services. (in practise
described by their ids). Operations are strings, which are organised in a hierarchy. Follow this example:

    - g4ds  (describes all actions for G4DS)
    - g4ds.control  (descibes all actions for the control system of G4DS)
    - g4ds.control.member (describes all actions for member control subsystem of g4ds)
    - g4ds.control.member.requestmdl (is the action for requesting a member description)
    
Rules may either apply to an action itself or to a set of actions using the group identifier of any hierarchy.

In practise, the entire approach is based on policy files which are parsed at booting up time of G4DS and then applied
to a permission matrix. The  policy files have to be placed on the location as defined in the g4ds config file
(L{config.POLICY_DIRECTORY}). By default the files are loaded which are defined in the config file (L{config.POLICY_FILES}).

The access matrix is two dimensional. Each entry inside the matrix contains an ordered list of couples (action | reaction). 

For building the matrix the following steps are performed:

All requested policy files are loaded into memory using dictionaries. Afterwards the dictionaries are processed in
order starting with the ruleset defined in the config file with value L{config.POLICY_MAJOR_RULESET_ID}. Hence, the
order of the policy files does not matter (at least as long as no result set id is used severeal times). The processor
iterates the list of rules in the major ruleset ordered by rule id (so keep your rules in order!!!). Whenever a rule has
the reaction type 'direct', the value is put directly into the access matrix. (In fact, for each possible combination of the
rule for actor / target one item is appended to the list of rules for the corrosponding couple.) Whenever the rule has
the reaction type 'redirect', the processing is continued with this list immedeately and, after finishing the redirected list,
continued after the redirected reaction. Redirection are allowed in all rulesets; hence they may be cascaded.

For validating one request, the following steps are performed:

The authorisation controller is performing a lookup in the access matrix and this way loading the list for the
requested couple of actor / target. This list is then iterated (by order as established at bootup time) and the first rule
hitting the requested action is taken. Regarding the action stored for this rule the the function will return
the value.

For the roles inside the rules you may use wildcards. Supported wildcards are:
    - '*' - all possible values
    - 'authorities_communities' - All authorities for a community
    - 'authorities_services' - all authorities for a service
    - 'Cxxxxxx' (in conjunction with type attribute 'membergroup') - All members of the community with ID Cxxxxxx
    - 'Sxxxxxx' (in conjunction with type attribute 'membergroup') - All members of the service with ID Sxxxxxx

@author: Michael Pilgermann
@contact: mailto:mpilgerm@glam.ac.uk
@license: GPL (General Public License)

@var REACTION_POS: String indicating a positive reaction in the policies
@type REACTION_POS: C{String}
@var REACTION_NEG: String, indiicatng a negative reaction in the policies
@type REACTION_NEG: C{String}
@var REACTION_DICT: Dictionary of interpreted reaction strings
@type REACTION_DICT: C{dict}
"""

REACTION_POS = 'allow'
REACTION_NEG = 'drop'

REACTION_DICT = {}
REACTION_DICT[REACTION_POS] = 1
REACTION_DICT[REACTION_NEG] = 0

# "singleton"
_authorisationController = None
def getAuthorisationController():
    """
    Singleton Implementation.
    
    Returns the instance to the AuthorisationController class.
    """
    global _authorisationController
    if not _authorisationController:
        _authorisationController = AuthorisationController()
        _authorisationController.recalculateMatrix()
    return _authorisationController

class AuthorisationController:
    """
    Handles all stuff about permissions.
    """
    
    def __init__(self):
        """
        Only initialises the matrix. 
        
        Call function L{recalculateMatrix} for processing policies.
        """
        self._matrix = {}

    
    def recalculateMatrix(self):
        """
        Loads the permissions information from files and databases into the memory.
        
        Creates the permission matrix. The matrix itself is implemented using nested
        dictionaries.
        """
        from config import POLICY_DIRECTORY, POLICY_FILES, POLICY_MAJOR_RULESET_ID
        import os.path
        from messagewrapper import getPolicyFileWrapper

        self._matrix = {}

        
        all_rolesets = []
        all_rulesets = []
        all_groups = []
        
        filelist = []
        for filename in POLICY_FILES:
            filelist.append(os.path.join(POLICY_DIRECTORY, filename))
        
        for filename in filelist:
            file = open(filename)
            content = file.read()
            file.close()
            try:
                rolesets, groups, rulesets = getPolicyFileWrapper().parsePolicyString(content)
                all_rolesets += rolesets
                all_rulesets += rulesets
                all_groups += groups
##                print '\n', rolesets, '\n', groups, '\n', rulesets
            except Exception, msg:
                from errorhandling import G4dsException
                raise G4dsException('%s: %s' %(filename, msg))
            
##        print '\n', all_rolesets, '\n', all_groups, '\n', all_rulesets
            
        
        d_rulesets, d_groups, d_rolesets, d_roles = self._createDictionaries(all_rolesets, all_groups, all_rulesets)
##        print d_rulesets, "\n", d_groups, "\n", d_roles
        self._assembleMatrix(d_rulesets, d_groups, POLICY_MAJOR_RULESET_ID)

    def printMatrix(self):
        for x in self._matrix.keys():
            print "%s" %(x)
            for y in self._matrix[x].keys():
                print "  %s" %(y)
                a = 1
                for z1, z2  in self._matrix[x][y]:
                    print "    Rule %d - %s" %(a, z2) + ""
                    b = 1
                    for zand in z1:
                        c = 1
                        print "      ",
                        for tmp, zor in zand:
                            print "%s" %(zor) + "",
                            if len(zand) > c:
                                print "OR",
                            c += 1
                        if len(z1) > b:
                            print "AND"
                        else:
                            print 
                        b += 1
                    a+=1
        
    def _createDictionaries(self, rolesets, groups, rulesets):
        """
        Processed the list from the unwrapper and creates easier accessible dictionaries.
        """
        d_rulesets = {}
        d_groups = {}
        d_rolesets = {}
        d_roles = {}

        for ruleset in rulesets:
            d_rulesets[ruleset['id']] = ruleset
            # also transform the rules list into a rules dictionary
            rules = ruleset['rules']
            ruleset['rules'] = {}
            for rule in rules:
                ruleset['rules'][rule['id']] = rule
        
        for roleset in rolesets:
            d_rolesets[roleset['type']] = roleset
            roles = roleset['roles']
            roleset['roles'] = {}
            for role in roles:
                d_roles[role['name']] = role
                roleset['roles'][role['name']] = role
        
        for group in groups:
            d_groups[group['rolename']] = group
            
        return d_rulesets, d_groups, d_rolesets, d_roles
    
    def _decodeGroup(self, type, wildcard):
        """
        Processes wildcard information in one group.
        
        @param type: Type of role; either actor, action or target
        @type type: C{String}
        @param wildcard: Wildcard string as given in the XML description (most likely a star)
        @type wildcard: C{String}
        """
        from errorhandling import G4dsDependencyException
        retList = []
        if type == 'membergroup':
            from communitymanager import getMemberManager
            if wildcard == '*':     # all members  - easy stuff
                return getMemberManager().getMemberIds()
            elif wildcard[0] == 'C':      # here we want all the members of a certain community
                from communitymanager import getCommunityManager
                return getCommunityManager().getCommunity(wildcard).getMembers()
            elif wildcard[0] == 'S':        # all the members of a service
                from servicerepository import getServiceManager
                return getServiceManager().getService(wildcard).getMembers()
        elif type == 'communitygroup':
            from communitymanager import getCommunityManager
            if wildcard == '*':     # that should be all communities then
                return getCommunityManager().getCommunityIds()
        elif type == 'servicegroup':
            from servicerepository import getServiceManager
            if wildcard == '*':     # all the services here
                return getServiceManager().getServiceIds()
        else:
            raise G4dsDependencyException('Policy error - unknown group type "%s".' %(type))
        return retList
        
    def _determineIndependantTargets(self, targettype, target):
        """
        Assembles a target list which is independant from the actor type.
        """
        from errorhandling import G4dsDependencyException
        retList = []
            
        if targettype == 'member':
            if target[0] != 'M':
                raise G4dsDependencyException('Policy error - only member ids allowed for target type "member".')
            retList.append(target)
        elif targettype == 'community':
            if target[0] != 'C':
                raise G4dsDependencyException('Policy error - only community ids allowed for target type "community".')
            retList.append(target)
        elif targettype == 'service':
            if target[0] != 'S':
                raise G4dsDependencyException('Policy error - only service ids allowed for target type "service".')
            retList.append(target)
        elif targettype == 'membergroup' or targettype == 'communitygroup' or targettype == 'servicegroup':
            targets = self._decodeGroup(targettype, target)
            for t in targets:
                retList.append(t)
        else:
            raise G4dsDependencyException('Policy error - unknown target type "%s" for policy.' %(targettype))
        return retList
        
    
    def _decodeCouples_SingleActorMember(self, actor, target, targettype):
        """
        Sub routine for L{_decodeCouples}.
        """
        from errorhandling import G4dsDependencyException
        if actor[0] != 'M': # first character of a member id is always an M
            raise G4dsDependencyException('Policy error - only member ids allowed for actor type "member".')
        
        retList = []
        for x in self._determineIndependantTargets(targettype, target):
            retList.append((actor, x))
        return retList

    def _decodeCouples_ActorMemberGroup(self, actor, target, targettype):
        """
        Sub routine for L{_decodeCouples}.
        """
        from errorhandling import G4dsDependencyException

        retList = []
        if actor == '*' or actor[0] == 'C'  or actor[0] == 'S':     # simple (independent group)
            actorlist = self._decodeGroup('membergroup', actor)
            targetlist = self._determineIndependantTargets(targettype, target)
            for a in actorlist:
                for t in targetlist:
                    retList.append((a,t))
            return retList
        elif actor == 'authorities_community':
            # check targets as well
            targetList = self._determineIndependantTargets(targettype, target)
            from communitymanager import getCommunityManager
            for cid in getCommunityManager().getCommunityIds():
                c = getCommunityManager().getCommunity(cid)
                try:
                    targetList.index(cid)
                    for mid in c.getAuthorities():
                        retList.append((mid, cid))
                except ValueError, msg:
                    pass        # alright, this community is not in our target list
            return retList
        elif actor == 'authorities_service':
            # check targets as well
            targetList = self._determineIndependantTargets(targettype, target)
            from servicerepository import getServiceManager
            for sid in getServiceManager().getServiceIds():
                s = getServiceManager().getService(sid)
                try:
                    targetList.index(sid)
                    for mid in s.getAuthorities():
                        retList.append((mid, sid))
                except ValueError, msg:
                    pass       # alright, this service is not in our target list
            return retList
        elif actor == 'authorities_member':
            # each member is its own authority
            targetList = self._determineIndependantTargets(targettype, target)
            from communitymanager import getMemberManager
            for mid in getMemberManager().getMemberIds():
                try:
                    targetList.index(mid)
                    retList.append((mid, mid))
                except ValueError, msg:
                    pass        # ok, this is not in our target list
            return retList
        elif actor == 'gateways_community':
            # check targets as well
            targetList = self._determineIndependantTargets(targettype, target)
            # assemble list of all gateways
            gws = []
            from communitymanager import getCommunityManager
            for cid in getCommunityManager().getCommunityIds():
                for gw in getCommunityManager().getCommunity(cid).getSourceGateways():
                    gws.append(gw)
            for gw in gws:
                mid = gw.getMemberId()
                sid = gw.getSourceCommunityId()
                did = gw.getDestinationCommunityId()
                try:
                    targetList.index(did)       # we only check the dest tc here; the src is left to the user
                    retList.append((mid, did))
                except ValueError, msg:
                    pass    # alright, this dest tc is not in our target list
            return retList            
        else:
            raise G4dsDependencyException('Policy error - unrecognised actor string (%s) for actor type "membergroup".' %(actor))
        return retList

        
    def _decodeCouples(self, actor, actortype, target, targettype):
        """
        Processes a actor - target wildcard relation and returns the corresponding values for them.
        
        @return: List of couples - actor | target
        @rtype: C{List} of C{Couple}
        """
        from errorhandling import G4dsDependencyException
        if actortype == 'member':
            return self._decodeCouples_SingleActorMember(actor, target, targettype)
        elif actortype == 'membergroup':
            return self._decodeCouples_ActorMemberGroup(actor, target, targettype)
        else:       # only member or membergroup allowed  for actor types
            raise G4dsDependencyException('Policy error - actor type "%s" unkown.' %(actortype))
    
    
    def _resolveGroup(self, rolename, groups):
        """
        Actors and targets may be defined as groups in the rule - let's resolve them in here.
        """
        retList = []
        try:
            group = groups[rolename]
        except KeyError, msg:
            from errorhandling import G4dsDependencyException
            raise G4dsDependencyException('Policy Error: No group with name "%s" found to refer to.' %(rolename))
        for rep in group['representatives']:
            if rep['type'] == 'role':
                retList = retList + self._resolveGroup(rep['value'])
            else:
                retList.append((rep['type'],rep['value']))
        return retList
        
    def _applyOneDirectRule(self, rule, groups, actorsTargets = None, actionFilters = [], depth = 0):
        """
        Applies a single rule to the matrix.
        """
        indent = " " * 3
##        print indent * depth + "> Started direct processing of rule %s | %s" %(rule['id'], rule['comment'])
        
##        actors = rule['actor']
##        actions = rule['action']
##        targets = rule['target']
        reaction  =rule['reaction']
##        
##        listActors = [] # couples of type  / value
##        listTargets = []    # couples of type / value
##        listActions = []    # couples of type / value

##        if rule['actor_type'] == 'role':
##            listActors = listActors + self._resolveGroup(actors, groups)
##        else:
##            listActors.append((rule['actor_type'], actors))
##
##        if rule['target_type'] == 'role':
##            listTargets = listTargets + self._resolveGroup(targets, groups)
##        else:
##            listTargets.append((rule['target_type'], targets))
##            
##        if rule['action_type'] == 'role':
##            listActions = listActions + self._resolveGroup(actions, groups)
##        else:
##            listActions.append((rule['action_type'], actions))
            
##        for actortype, actor in listActors:
##            for targettype, target in listTargets:
##                addresses = self._decodeCouples(actor, actortype, target, targettype)
                
                # put the list of rules on each address
##                for a, t in addresses:
        for a,t in actorsTargets:
##            for actiontype, action in listActions:
##            for action in actionFilters:
            try:
                self._matrix[a]
            except KeyError, msg:
                self._matrix[a] = {}
            try:
                self._matrix[a][t]
            except KeyError, msg:
                self._matrix[a][t] = []
                
            self._matrix[a][t].append((actionFilters, reaction))
    
##        print indent * depth + "< Finished direct processing of rule"

        
    def _processOneRuleset(self, rulesets, groups, currentRule, actorsTargets = None, actionFilters = [], depth = 0):
        """
        Processes one rule.
        
        This function is called recursively.
        
        I will rather explain this another day - have had some pints today already ... :)
        """
        indent = " " * 3
        
        
##        print indent * depth + "> Started processing of rule set %s" %(currentRule)
        try:
            ruleset = rulesets[currentRule]
        except KeyError, msg:
            from errorhandling import G4dsDependencyException
            raise G4dsDependencyException('Referenced rule set (%s) not available.' %(currentRule))
            
##        print indent * (depth+1) + "* Ruleset name is: %s" %(ruleset['name'])
            
        keys = ruleset['rules'].keys()
        keys.sort()
        oldActorsTargets = actorsTargets
        oldActionFilters = actionFilters
        for key in keys:
            # make a copy of actorsTargets and actionFilters
            if oldActorsTargets:
                tmp = oldActorsTargets
                actorsTargets = []
                for item in tmp:
                    actorsTargets.append(item)
            else:
                actorsTargets = None
                
            tmp = oldActionFilters
            actionFilters = []
            for item in tmp:
                actionFilters.append(item)
            # that's it copying ;)
            

            rule = ruleset['rules'][key]
    ##            print indent * (depth+1) + "- Apply rule %s | %s" %(rule['id'], rule['comment'])
            
            if rule['actor_type'] == 'role':
                listActors =self._resolveGroup(rule['actor'], groups)
            else:
                listActors = [(rule['actor_type'], rule['actor'])]
            
            if rule['target_type'] == 'role':
                listTargets = self._resolveGroup(rule['target'], groups)
            else:
                listTargets = [(rule['target_type'], rule['target'])]

                
            tmpList = []
            for actortype, actor in listActors:
                for targettype, target in listTargets:
                    addresses = self._decodeCouples(actor, actortype, target, targettype)
                    tmpList += addresses

                    
##            tmpList = self._decodeCouples(rule['actor'], rule['actor_type'], rule['target'], rule['target_type'])
            if actorsTargets:   # validate against pre selected actor / target couple list
                retList = []
                for item in tmpList:
                    try:
                        actorsTargets.index(item)
                        retList.append(item)
                    except Exception, msg:
                        pass
                actorsTargets = retList
            else:
                actorsTargets = tmpList
                
            if rule['action_type'] == 'role':
                actionFilters.append(self._resolveGroup(rule['action'], groups))
            else:
                actionFilters.append([(rule['action_type'], rule['action'])])
            
            if rule['reaction_type'] == 'direct':
##                print indent * (depth+2) + "* Ruletype direct - create matrix entries now"
                self._applyOneDirectRule(rule, groups, actorsTargets, actionFilters, depth = depth + 3)
            elif rule['reaction_type'] == 'redirect':
##                print indent * (depth+2) + "* Ruletype redirect - load rule set %s" %(rule['reaction'])
                self._processOneRuleset(rulesets, groups, rule['reaction'], actorsTargets, actionFilters, depth + 2)
        
##        print indent * depth + "< Finished processing of rule set %s" %(currentRule)

    
    def _assembleMatrix(self, rulesets, groups, startRuleset):
        """
        Assembles the access matrix by processing the given dictionaries and further local information.
        """
        
##        print "Start assembling of access matrix"
##        print "  Start with rule set %s" %(startRuleset)
        
        self._processOneRuleset(rulesets, groups, startRuleset, depth = 1)
##        print "Finished assembling"
        
    def _logEntry(self, actor, target, action, reaction, reportPolicyError = 0):
        """
        Reports this access control access to the logging facilities.
        """
        from g4dslogging import getDefaultLogger, PERMISSION_MESSAGE_PASSED, PERMISSION_MESSAGE_DROPPED, PERMISSION_POLICY_ERROR
        
        if reportPolicyError:
            getDefaultLogger().newMessage(PERMISSION_POLICY_ERROR, 'Access Control Policy error - rules are not covering all actions. Check your rulesets. Apply default reaction from config module for now.')
        
        global REACTION_DICT
        if REACTION_DICT[reaction]:
            getDefaultLogger().newMessage(PERMISSION_MESSAGE_PASSED, 'Access Control - message passed: %s -> %s (A: %s)' %(actor, target, action))
        else:
            getDefaultLogger().newMessage(PERMISSION_MESSAGE_DROPPED, 'Access Control - access violation: %s -> %s (A: %s)' %(actor, target, action))
        
    def _checkAgainstOneActionString(self, action, polActionString):
        """
        Checks the given action string against an action string from a policy.
        """
        return polActionString == "*" or action.startswith(polActionString)
            
        
    def validate(self, actor, target, action):
        """
        Checks the given action against the available rules.
        
        Picks up the value for the couple of the given actor and target and iterates this ordered list and compares
        each item against the given action.
        """
        global REACTION_DICT
        
        # let's first of all pics the access list for the given couple of actor / target
        accessForCouple = self._matrix[actor][target]
        # the first iteration goes through the ordered list - each item = 1 rule
        for maction, mreaction in accessForCouple:
            # the second iteration goes through the AND combinations of rule parts (occuring due to rule nesting)
            for mactionAnd in maction:
                oneAnd = 0
                # the third iteratiion is for the OR combinations within one AND combination part (occuring due to roles for operations / actions)
                for actionid, mactionOr in mactionAnd:
                    if self._checkAgainstOneActionString(action, mactionOr):
                        oneAnd = 1
                        break
                if not oneAnd:
                    break
            if oneAnd:
                self._logEntry(actor, target, action, mreaction)
                return REACTION_DICT[mreaction]
                        
##            if maction == "*" or action.startswith(maction):        # 2nd condition should actually look a bit more for the dots; but this will do for now
##                self._logEntry(actor, target, action, mreaction)
##                return REACTION_DICT[mreaction]
        from config import POLICY_DEFAULT_REACTION
        
        self._logEntry(actor, target, action, POLICY_DEFAULT_REACTION, reportPolicyError = 1)
        return POLICY_DEFAULT_REACTION
