"""
All issues concerning the routing table itself are implemented here.

Grid for Digital Security (G4DS)

Find the database connector for the routing table manager in module L{routingtablemanager}.

@author: Michael Pilgermann
@contact: mailto:mpilgerm@glam.ac.uk
@license: GPL (General Public License)
"""

import config
from routingtablemanagerdb import RoutingTableManagerDB

# "singleton"
_routingTableManager = None
def getRoutingTableManager():
    """
    Singleton
    """
    global _routingTableManager
    if not _routingTableManager:
        _routingTableManager = RoutingTableManager()
    return _routingTableManager

class RoutingTableManager:
    """
    Holds the routing table in the memory.
    
    Architecture:
    
        1. For each reachable community we have one entry in the dictionary - key is the community id,
            value is an ordered list
        2. The ordered list is the list of routing entries with destination community, the key for ordering is
            the costs for the route.
    """

    def __init__(self, loadFromDatabase  = config.dbconnected):
        """
        Let's load the routing table here into memory.
        """
        self._routingtable = {}
        self._dbconnected = loadFromDatabase
        if loadFromDatabase:
            self._rtm_db = RoutingTableManagerDB()
            for entry in self._rtm_db.getRoutingTableEntries():
                self.addEntry(entry, 1)

    def __str__(self):
        """
        Some basic information about the object
        """
        return "RoutingTableManager: %d communities routable" %(len(self._routingtable))
        
    def addEntry(self, entry, loading = 0, skipMoreExpensive = 1):
        """
        Adds an routing entry to the manager.
        
        If loading is false, the new value is written through to the database.
        
        @param entry: Routing table entry to add
        @type entry: L{RoutingTableEntry}
        @param loading: Indicates, whether the change shall be written through to the routing table
        @type loading: C{Boolean}
        @param skipMoreExpensive: Inidicates, whether new entries with same src, dst community and same gw but higher costs than current value shall be skipped
        @type skipMoreExpensive: C{Boolean}
        """
        if not self._routingtable.has_key(entry.getDestinationTC()):
            self._routingtable[entry.getDestinationTC()] = {}
        if not self._routingtable[entry.getDestinationTC()].has_key(entry.getSourceTC()):
            self._routingtable[entry.getDestinationTC()][entry.getSourceTC()] = []
        entries = self._routingtable[entry.getDestinationTC()][entry.getSourceTC()]
        
        # put the new entry into the list at the correct position
        pos = 0
        for e in entries:
            if skipMoreExpensive:
                # if we have exactly this entry in the routing table already
                if e.getGWCommunityId() == entry.getGWCommunityId() and e.getGWMemberId() == entry.getGWMemberId():
                    # simply skip it if costs are higher
                    if e.getCosts() <= entry.getCosts(): 
                        pass
                    else:
                        # update the entry in the manager / database
                        self._routingtable[entry.getDestinationTC()][entry.getSourceTC()][pos] = entry
                        if not loading and self._dbconnected:
                            self._rtm_db.updateRoutingTableEntry(e, entry)
                    return
            if e.getCosts() > entry.getCosts():
                break
            pos += 1
        self._routingtable[entry.getDestinationTC()][entry.getSourceTC()].insert(pos, entry)
        
        if not loading and self._dbconnected:
            self._rtm_db.addRoutingTableEntry(entry)
                
    def getAllEntriesForCommunityPair(self, sourceCommunityId, destinationCommunityId):
        """
        Returns all entries for the pair - source commuity - destination community
        """
        return self._routingtable[destinationCommunityId][sourceCommunityId]

    def getNexthopForCommunity(self, destinationcommunityid, sourcecommunityid = None):
        """
        Returns the member id of the next hop on the route towards the final destination's community.
        
        Automatically, the route with the lowest costs for this destination community is chosen.
        
        If L{sourcecommunityid} is not given, any will be chosen, in fact the one which causes the lowest costs.
        """
        if not sourcecommunityid:
            # ok, there is not src given, so let's just iterate through the communities, the local member
            # is member of; take the one with the shortest route finally.
            from communitymanager import getMemberManager
            from errorhandling import G4dsCommunicationException
            retList = []
            for commid in getMemberManager().getLocalMember().getCommunityIds():
                try:
                    bestForSource = self.getNexthopForCommunity(destinationcommunityid, commid)
                    retList.append(bestForSource)
                except G4dsCommunicationException, msg:
                    # fair enough; nothing to get for this src
                    pass
                    
            if not len(retList):
                raise G4dsCommunicationException('No route found for community %s.' %(destinationcommunityid))
            
            fastest = retList[0]
            for entry in retList[1:]:
                if entry[2] < fastest[2]:
                    fastest = entry
            return fastest
        
        from errorhandling import G4dsCommunicationException
        try:
            entries = self.getAllEntriesForCommunityPair(sourcecommunityid, destinationcommunityid)
        except KeyError, msg:
            raise G4dsCommunicationException('No route found for community %s.' %(destinationcommunityid))
            
        if not len(entries):
            raise G4dsCommunicationException('No route found for community %s.' %(destinationcommunityid))
            
        entry = entries[0]
        return entry.getGWMemberId(), entry.getGWCommunityId(), entry.getCosts()
        
##        if communityid == 'C001':   #
##            return 'M001', 'C002'    # for our test configuration only
##        return 'M001', 'C001'       #

    def flushTable(self):
        """
        Flushes the routing table - the table will be totally empty afterwards.
        """
        self._routingtable = {}
        if self._dbconnected:
            self._rtm_db.emptyRoutingTable()
        from g4dslogging import getDefaultLogger, ROUTING_TABLE_UPDATED_MANUALLY
        getDefaultLogger().newMessage(ROUTING_TABLE_UPDATED_MANUALLY, 'Routing table flushed')

    def recalculateRoutingTable(self):
        """
        Creates routing entries from the scratch by processing gateway information.
        
        The values for directly reachable communities are applied. Furthermore, communities, which
        may be reached through one community only (1 hop) are put into as well.  The rest should be 
        sorted out be the dynamic routing faciliites.
        """
        numberOfEntries = 0
        tmpList = []    # we have to maintain this list with new entries; just in case
                                # the routing table was not flushed beforehand
        
        # first process directly reachable communities - cost = 1
        from communitymanager import getMemberManager, getCommunityManager
        for communityid in getMemberManager().getLocalMember().getCommunityIds():
            # everybody can route into its own community  ...that's just important to pass it on to any gw within the community
            entry = RoutingTableEntry(None, communityid, communityid, getMemberManager().getLocalMember().getId(), communityid, 1)
            getRoutingTableManager().addEntry(entry)
            numberOfEntries += 1
            tmpList.append(entry)
            
        # get all the gateways of the directly connected communities
        for communityid in getMemberManager().getLocalMember().getCommunityIds():
            comm = getCommunityManager().getCommunity(communityid)
            for gw in comm.getSourceGateways():
                # if it's myself, I can reach it directly (cost 1)
                if gw.getMemberId() == getMemberManager().getLocalMember().getId():
                    entry = RoutingTableEntry(None, communityid, gw.getDestinationCommunityId(), gw.getMemberId(), 
                        communityid, 1)
                    getRoutingTableManager().addEntry(entry)
                    numberOfEntries += 1                    
                    tmpList.append(entry)
                
        # now get all the entries with cost 2
        # what do we do: We check the available entries with cost 1 and have a look, which (source) gateways are
        # available for them (for their destination gateway)
        for item in tmpList:
            srcTC = item.getDestinationTC() #  the destination tc of the hop 1 entry will be the src tc of the hop 2 entry
            comm = getCommunityManager().getCommunity(srcTC)
            for gw in comm.getSourceGateways():
                entry = RoutingTableEntry(None, item.getSourceTC(), gw.getDestinationCommunityId(), gw.getMemberId(),
                    srcTC, 2)
                getRoutingTableManager().addEntry(entry)
                numberOfEntries += 1             
            
        from g4dslogging import getDefaultLogger, ROUTING_TABLE_UPDATED_MANUALLY
        getDefaultLogger().newMessage(ROUTING_TABLE_UPDATED_MANUALLY, 'Routing table recalculated - added %d entries.' %(numberOfEntries))
        return numberOfEntries
            
    def getRoutingTableXML(self):
        """
        Returns an XML formatted copy of the routing table.
        """
        # first calculate the matrix
        matrix = []
        for dest_tc in self._routingtable.keys():
            for src_tc in self._routingtable[dest_tc].keys():
                for entry in self._routingtable[dest_tc][src_tc]:
                    line = [entry.getSourceTC(), entry.getDestinationTC(), entry.getGWCommunityId(),
                        entry.getGWMemberId(), str(entry.getCosts())]
                    matrix.append(line)
        
        from messagewrapper import getRoutingTableWrapper
        xml = getRoutingTableWrapper().encodeRoutingTable(matrix)
        return xml
        
    def applyRoutingTableFromNode(self, peerId, tableXml):
        """
        Updates the local routing table with the information from the remote peer about its routes.
        """
        from messagewrapper import getRoutingTableWrapper
        matrix = getRoutingTableWrapper().decodeRoutingTable(tableXml)
##        print "RoutingTableManager.apply: Extracted %d entries from Routing Table XML from Peer %s." %(len(matrix), peerId)
        
        # what we  do - we check all available entries with cost 1, whenever their destination tc is the
        # source tc of any of the extracted routes; we add this one
        for dest_tc in self._routingtable.keys():
            for src_tc in self._routingtable[dest_tc].keys():
                for entry in self._routingtable[dest_tc][src_tc]:
                    if entry.getCosts() == 1:
                        for line in matrix:
                            if entry.getDestinationTC() == line[0]:
                                newentry = RoutingTableEntry(None, entry.getSourceTC(), line[1], peerId, 
                                    line[0], int(line[4]) + 1)
                                self.addEntry(newentry)
            
class RoutingTableEntry:
    """
    Hold the information for one entry in the routing table.
    """
    def __init__(self, id, source_tc, destination_tc, gw_member_id, gw_community_id, costs):
        """
        Assigns the parameters to instance variables.
        
        If id is C{None}, one will be generated using the tools module.
        """
        if id == None:
            from tools import generateId, TYPE_ROUTINGTABLEENTRY
            id = generateId(TYPE_ROUTINGTABLEENTRY)
        self._id = id
        self._source_tc = source_tc
        self._destination_tc = destination_tc
        self._gw_member_id = gw_member_id
        self._gw_community_id = gw_community_id
        self._costs = int(costs)
        
    def __str__(self):
        """
        Some basic information about the object
        """
        return "RoutingTableEntry: SrcTC - %s; DestTC - %s; GW (Member | Community) - %s | %s; Costs - %d" \
            %(self._source_tc, self._destination_tc, self._gw_member_id, self._gw_community_id, self._costs)

    def getId(self):
        """
        Getter
        """
        return self._id

    def getSourceTC(self):
        """
        Getter
        """
        return self._source_tc
        
    def getDestinationTC(self):
        """
        Getter
        """
        return self._destination_tc
        
    def getGWMemberId(self):
        """
        Getter
        """
        return self._gw_member_id
        
    def getGWCommunityId(self):
        """
        Getter
        """
        return self._gw_community_id
        
    def getCosts(self):
        """
        Getter
        """
        return self._costs
        
        
