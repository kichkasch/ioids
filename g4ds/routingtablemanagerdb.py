"""
Database backend for routing table manager.

Grid for Digital Security (G4DS)

@author: Michael Pilgermann
@contact: mailto:mpilgerm@glam.ac.uk
@license: GPL (General Public License)
"""

import config
import pg
import routingtablemanager
#from routingtablemanager import RoutingTableEntry

class RoutingTableManagerDB:
    """
    Database backend for L{routingtablemanager.RoutingTableManager}
    """

    def __init__(self):
        """
        Initialise database connections.

        Initialises the connection to the database using the settings in the configuration
        file / module L{config}. The connection itself is stored in a local variable.
        """
        dbname = config.g4ds_rtdb_dbname
        host = config.g4ds_rtdb_host
        port = config.g4ds_rtdb_port
        user = config.g4ds_rtdb_username
        password = config.g4ds_rtdb_password
        options = None
        tty = None
        
        self._connection = pg.connect(dbname, host, port, options, tty, user, password)

    def getRoutingTableEntries(self):
        """
        Fetches list of routing table entries from the database.
        """
        result = self._connection.query('select id, source_community, destination_community, gateway_member_id, ' + 
            ' gateway_community_id, costs from ' + 
            config.g4ds_rtdb_table_routingtable)
        list = result.getresult()
        returnList = []
        for item in list:
            id = item[0]
            srctc = item[1]
            desttc = item[2]
            gw_member_id = item[3]
            gw_community_id = item[4]
            costs = item[5]
            entry = routingtablemanager.RoutingTableEntry(id, srctc, desttc, gw_member_id, gw_community_id, costs)
            returnList.append(entry)
        return returnList
    
    def addRoutingTableEntry(self, entry):
        """
        Adds one entry to the routing table table.
        """
        self._connection.query("""insert into """ + config.g4ds_rtdb_table_routingtable + 
                """(id, source_community, destination_community, gateway_member_id, gateway_community_id, costs ) values ('""" +
                entry.getId() + """', '""" + entry.getSourceTC() + """', '""" + entry.getDestinationTC() + """', '""" + entry.getGWMemberId() + 
                """', '""" + entry.getGWCommunityId() + """', """ + str(entry.getCosts()) + """)""")
                
    def updateRoutingTableEntry(self, oldEntry, newEntry):
        """
        Overwrites the data of the old entry with the one of the new entry.
        """
        self._connection.query("""update """ + config.g4ds_rtdb_table_routingtable + 
                """ set id='""" + newEntry.getId() + """', source_community = '""" + newEntry.getSourceTC() +
                """', destination_community = '""" + newEntry.getDestinationTC() + 
                """', gateway_member_id = '""" + newEntry.getGWMemberId() +
                """', gateway_community_id = '""" + newEntry.getGWCommunityId() +
                """', costs = """ + newEntry.getCosts() + """ where id = '""" + oldEntry.getId() + """'""")
                
    def emptyRoutingTable(self):
        """
        Drops all entries in the table for the routing table.
        """
        self._connection.query("""delete from """ + config.g4ds_rtdb_table_routingtable)
        
