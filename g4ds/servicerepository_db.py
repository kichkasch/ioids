"""
Database backend connector for knowledge services repository

Grid for Digital Security (G4DS)


@author: Michael Pilgermann
@contact: mailto:mpilgerm@glam.ac.uk
@license: GPL (General Public License)
"""

import config
import pg
import servicerepository

class ServDB:
    """
    Handles all requests form the services repository module for backend connectivity with database.

    @ivar _connection: Reference to database connection
    @type _connection: PSQL-DB-Connection
    """
    
    def __init__(self):
        """
        Initialises the database manager for services.
        
        The database connection is established using the appropriate settings in the configuations
        file / module config.py.
        
        Please run L{shutdown} before you shutdown the application in order to clear the database
        connections.
        """
        dbname = config.g4ds_serv_dbname
        host = config.g4ds_serv_host
        port = config.g4ds_serv_port
        user = config.g4ds_serv_username
        password = config.g4ds_serv_password
        options = None
        tty = None
        
        self._connection = pg.connect(dbname, host, port, options, tty, user, password)
        
    def shutdown(self):
        """
        Closes open database connections.
        """
        self._connection.close()
        
    def getServices(self):
        """
        Returns a list of all services in the database.
        """
        result = self._connection.query('select id, name, ksdl, ksdlversion, ksdldate from ' + 
            config.g4ds_serv_table_services)
        list = result.getresult()
        returnList = []
        for item in list:
            id = item[0]
            name = item[1]
            ksdl = item[2]
            from binascii import unhexlify
            if ksdl:
                ksdl = unhexlify(ksdl)
            ksdlversion = item[3]
            ksdldate = item[4]
            c = servicerepository.Service(id, name, ksdl, ksdlversion, ksdldate)
            returnList.append(c)
        return returnList        
        
    def addService(self, service):
        """
        Adds one service to the services table in the database.
        """
        ksdl  =service.getKsdl()
        if ksdl:
            from binascii import hexlify
            ksdl = hexlify(service.getKsdl())

        ksdldate = service.getKsdlDate()
        if not ksdldate:
            ksdldate = 'today'

        self._connection.query("""insert into """ + config.g4ds_serv_table_services + 
                """(id, name, ksdl, ksdlversion, ksdldate) values ('""" +
                service.getId() + """', '""" + service.getName() + """', '""" + ksdl + 
                """', '""" + service.getKsdlVersion() + """', '""" + ksdldate +  """')""")

    def addServiceCommunity(self, serviceid, communityid):
        """
        Adds an entry into the table for the relation between services and communities.
        """
        self._connection.query("""insert into """ + config.g4ds_serv_table_relation_services_communities + 
            """(serviceid, communityid) values ('""" +
            serviceid + """', '""" + communityid + """')""")

    def addServiceMember(self, serviceid, memberid):
        """
        Adds an entry into the table for the relation between services and members.
        """
        self._connection.query("""insert into """ + config.g4ds_serv_table_relation_services_members + 
            """(serviceid, memberid) values ('""" +
            serviceid + """', '""" + memberid + """')""")
        
    def addServiceAuthority(self, serviceid, memberid):
        """
        Adds an entry into the table for the relation between services and members as authorities.
        """
        self._connection.query("""insert into """ + config.g4ds_serv_table_relation_services_authorities + 
            """(serviceid, memberid) values ('""" +
            serviceid + """', '""" + memberid + """')""")

    def getCommunitiesForService(self, serviceid):
        """
        Fetches a list of ids of all communities subscribed to the given service.
        """
        result = self._connection.query("""select communityid from """ + config.g4ds_serv_table_relation_services_communities +
                """ where serviceid = '""" + serviceid + """'""" )
        list = result.getresult()
        returnList = []
        for item in list:
            communityid = item[0]
            returnList.append(communityid)
        return returnList        
        
    def getMembersForService(self, serviceid):
        """
        Fetches a list of ids of all members subscribed to the given service.
        """
        result = self._connection.query("""select memberid from """ + config.g4ds_serv_table_relation_services_members +
                """ where serviceid = '""" + serviceid + """'""" )
        list = result.getresult()
        returnList = []
        for item in list:
            memberid = item[0]
            returnList.append(memberid)
        return returnList        
        
    def getAuthoritiesForService(self, serviceid):
        """
        Fetches a list of ids of all members being authorities for the given service.
        """
        result = self._connection.query("""select memberid from """ + config.g4ds_serv_table_relation_services_authorities +
                """ where serviceid = '""" + serviceid + """'""" )
        list = result.getresult()
        returnList = []
        for item in list:
            memberid = item[0]
            returnList.append(memberid)
        return returnList        

    def updateService(self, service, dropAuthorityRelations = 1, dropMemberRelations = 0, dropCommunityRelations = 0):
        """
        Upadtes the database content with the given service description.
        """
        ksdl = service.getKsdl()
        if ksdl:
            from binascii import hexlify
            ksdl = hexlify(ksdl)

        ksdldate = service.getKsdlDate()
        if not ksdldate:
            ksdldate = 'today'

        self._connection.query("""update """ + config.g4ds_serv_table_services + 
                """ set id='""" + service.getId() + """', name='""" + 
                service.getName() + """',  ksdl='""" + ksdl + 
                """', ksdlversion='""" + service.getKsdlVersion() + """', ksdldate='""" + ksdldate + 
                """' where id='""" + service.getId() + """'""")
                
        if dropAuthorityRelations:
            self._connection.query("""delete from """ + config.g4ds_serv_table_relation_services_authorities + 
                """ where serviceid='""" + service.getId() + """'""")
                
        if dropMemberRelations:
            self._connection.query("""delete from """ + config.g4ds_serv_table_relation_services_members + 
                """ where serviceid='""" + service.getId() + """'""")
        
        if dropCommunityRelations:
            self._connection.query("""delete from """ + config.g4ds_serv_table_relation_services_communities + 
                """ where serviceid='""" + service.getId() + """'""")
