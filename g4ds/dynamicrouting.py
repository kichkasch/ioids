"""
Takes care of frequent updates of the routing table

Grid for Digital Security (G4DS)

Find the database connector for the routing table manager in module L{routingtablemanager}.

@author: Michael Pilgermann
@contact: mailto:mpilgerm@glam.ac.uk
@license: GPL (General Public License)
"""

# "singleton"
_routingTableUpdater = None
def getRoutingTableUpdater():
    """
    Singleton
    """
    global _routingTableUpdater
    if not _routingTableUpdater:
        _routingTableUpdater = RoutingTableUpdater()
    return _routingTableUpdater

class RoutingTableUpdater:
    """
    Keeps the routing table up to date by frequent polls from neighbour communities.
    
    @ivar _isAlive: Indicates, whether the updater is running.
    @type _isAlive: C{Boolean}
    """
    
    def __init__(self):
        """
        Initialises the background process.
        """
        self._isAlive = 1
        from config import ENABLE_ROUTING
        from g4dslogging import getDefaultLogger, ROUTING_TABLE_UPDATED
        import thread
        if ENABLE_ROUTING:
            thread.start_new_thread(self.runForEver, ())
            getDefaultLogger().newMessage(ROUTING_TABLE_UPDATED, 'Routing Table updater intialised')
        else:
            getDefaultLogger().newMessage(ROUTING_TABLE_UPDATED, 'Routing Table updater disabled in config file.')
            from errorhandling import G4dsRuntimeException
            raise G4dsRuntimeException('Dynamic routing is disabled in config file.')
    
    def runForEver(self):
        """
        Runs in an endless loop and initiates frequent routing table updates.
        
        Terminates as soon as the L{shutdown} function has set the L{_isAlive} flag to false.
        """
        from config import ROUTING_UPDATE_INTERVAL
        import time
        time.sleep(ROUTING_UPDATE_INTERVAL)
        while self._isAlive:
            self.updateNow()
            time.sleep(ROUTING_UPDATE_INTERVAL)
            
            
    def updateNow(self, timeout = 60):
        """
        Performs the actual updating process.
        """
        from g4dsconfigurationcontroller import getRoutingController
        from communitymanager import getMemberManager, getCommunityManager
        
        peerList = {}   # the dict here is a bit chicky - but the simpliest way to avoid duplicates
        # get the ids of connected gateways and download their routing tables
        for communityid in getMemberManager().getLocalMember().getCommunityIds():
            comm = getCommunityManager().getCommunity(communityid)
            for gw in comm.getSourceGateways():
                if gw.getMemberId() != getMemberManager().getLocalMember().getId():
                    peerList[gw.getMemberId()] = None
        
        peerList = peerList.keys()
        for peerId in peerList:
            routesRemote = getRoutingController().downloadRoutingTable(peerId, timeout = timeout)
            
            from routingtablemanager import getRoutingTableManager
            import thread
            thread.start_new_thread(getRoutingTableManager().applyRoutingTableFromNode, (peerId, routesRemote))
        
        from g4dslogging import getDefaultLogger, ROUTING_TABLE_UPDATED
        getDefaultLogger().newMessage(ROUTING_TABLE_UPDATED, 'Routing table updated')
        
    def shutdown(self):
        """
        Shut down the backend process.
        """
        self._isAlive = 0
        from g4dslogging import getDefaultLogger, ROUTING_TABLE_UPDATED
        getDefaultLogger().newMessage(ROUTING_TABLE_UPDATED, 'Routing Table updater is shutdown')
        
