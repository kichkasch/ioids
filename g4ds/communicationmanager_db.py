"""
The database backend functions for the communication module.

Grid for Digital Security (G4DS)


@author: Michael Pilgermann
@contact: mailto:mpilgerm@glam.ac.uk
@license: GPL (General Public License)
"""

import config
import pg
import communicationmanager

class CommDB:
    """
    Handles all requests form the communication module for backend connectivity with database.

    @ivar _connection: Reference to database connection
    @type _connection: PSQL-DB-Connection
    """
    
    def __init__(self):
        """
        Initialises the database manager for communication.
        
        The database connection is established using the appropriate settings in the configuations
        file / module config.py.
        
        Please run L{shutdown} before you shutdown the application in order to clear the database
        connections.
        """
        dbname = config.g4ds_comm_dbname
        host = config.g4ds_comm_host
        port = config.g4ds_comm_port
        user = config.g4ds_comm_username
        password = config.g4ds_comm_password
        options = None
        tty = None
        
        self._connection = pg.connect(dbname, host, port, options, tty, user, password)
        
    def shutdown(self):
        """
        Closes open database connections.
        """
        self._connection.close()

    def getProtocols(self):
        """
        Provides a list of all protocols in the database.
        
        @return: List of protocol instances
        @rtype: C{List} of L{communicationmanager.Protocol}
        """
        result = self._connection.query('select id, name from ' + config.g4ds_comm_table_protocols)
        list = result.getresult()
        returnList = []
        for item in list:
            id = item[0]
            name = item[1]
            c = communicationmanager.Protocol(id, name, 1)
            returnList.append(c)
        return returnList        

    def addProtocol(self, protocol):
        """
        Adds one protocol to the protocol table in the database.
        
        @param protocol: Protocol to add to the repository
        @type protocol: L{communicationmanager.Protocol}
        """
        self._connection.query("""insert into """ + config.g4ds_comm_table_protocols + 
                """(id, name) values ('""" +
                protocol.getId() + """', '""" + protocol.getName() + """')""")

    def getEndpoints(self):
        """
        Provides a list of all endpoints in the database.
        
        @return: List of endpoint instances
        @rtype: C{List} of L{communicationmanager.Endpoint}
        """
        result = self._connection.query('select id, memberid, communityid, protocolid, address, credentialid from ' + 
            config.g4ds_comm_table_endpoints)
        list = result.getresult()
        returnList = []
        for item in list:
            id = item[0]
            memberid = item[1]
            communityid = item[2]
            protocolid = item[3]
            address = item[4]
            credentialid = item[5]
            e = communicationmanager.Endpoint(id, memberid, communityid, protocolid, address, credentialid, 1)
            returnList.append(e)
        return returnList        

    def addEndpoint(self, endpoint):
        """
        Adds one endpoint to the endpoint table in the database.
        
        @param endpoint: Endpoint to add to the repository
        @type endpoint: L{communicationmanager.Endpoint}
        """
        self._connection.query("""insert into """ + config.g4ds_comm_table_endpoints + 
                """(id, memberid, communityid, protocolid, address, credentialid) values ('""" +
                endpoint.getId() + """', '""" + endpoint.getMemberId() + """', '""" + endpoint.getCommunityId() + 
                """', '""" + endpoint.getProtocolId() + """', '""" + endpoint.getAddress() + """', '""" + 
                endpoint.getCredentialId() + """')""")

    def findEndpoint(self, memberid, communityid, protocolname, algorithmname):
        """
        There is a problem to find the correct endpoint instance for incoming message.
        
        This structure solves this problem. All the known information is put togehter, and voila,
        we have an endpoint id.
        
        @todo: The table names are hard coded. They must be replaced with the ones given in the config file.
        """
        # this only works if all tables reside on the same host and database
        if config.g4ds_cudb_host != config.g4ds_comm_host or config.g4ds_comm_host != config.g4ds_sec_host or config.g4ds_cudb_host != config.g4ds_sec_host:
            return None
        if config.g4ds_cudb_dbname != config.g4ds_comm_dbname or config.g4ds_comm_dbname != config.g4ds_sec_dbname or config.g4ds_cudb_dbname != config.g4ds_sec_dbname:
            return None
        query = """select """ + config.g4ds_comm_table_endpoints + """.id from """ + config.g4ds_comm_table_endpoints + \
            """, """ + config.g4ds_cudb_table_members + """, """ + config.g4ds_cudb_table_communities + """, """ + \
            config.g4ds_comm_table_protocols + """, """ + config.g4ds_sec_table_credentials + """, """ + \
            """algorithms where """ + config.g4ds_comm_table_endpoints + """.memberid = """ + config.g4ds_cudb_table_members + \
            """.id and """ + config.g4ds_comm_table_endpoints + """.communityid = """ + config.g4ds_cudb_table_communities + """.id """ + \
            """ and """ + config.g4ds_comm_table_endpoints + """.protocolid = """ + config.g4ds_comm_table_protocols + """.id and """ + \
            config.g4ds_comm_table_endpoints + """.credentialid = """ + config.g4ds_sec_table_credentials + """.id and """ + \
            config.g4ds_sec_table_credentials + """.algorithmid = algorithms.id and """ + config.g4ds_cudb_table_members + \
            """.id = '""" + memberid + \
            """' and """ + config.g4ds_comm_table_protocols + """.name = '""" + protocolname + """' and """ + \
            config.g4ds_cudb_table_communities + """.id = '""" + \
            communityid + """' and algorithms.name = '""" + algorithmname + """'"""
        result = self._connection.query(query)
        list = result.getresult()
        if not len(list):
            from errorhandling import G4dsDependencyException
            raise G4dsDependencyException('Incoming message has no valid endpoint. Try install / update member description.')
        return list[0][0]
            
    def removeEndpoints(self, endpointid = None):
        """
        Removes credentials from the database.
        
        Depending on which parameters are given. If no parameter is set, all data in the table
        will be dropped.
        """
        st = """delete from """ + config.g4ds_comm_table_endpoints + """ where 1=1 """
        if endpointid:
            st = st + """ and id = '""" + endpointid + """' """
        self._connection.query(st)
            
