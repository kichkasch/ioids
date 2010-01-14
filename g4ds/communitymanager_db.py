"""
Database backend access for community manager

Grid for Digital Security (G4DS)



@author: Michael Pilgermann
@contact: mailto:mpilgerm@glam.ac.uk
@license: GPL (General Public License)
"""

import config
import pg
import communitymanager

class CM_DB:
    """
    Maintains the connection to the PostgreSQL database.
    
    @ivar _connection: Reference to database connection
    @type _connection: PSQL-DB-Connection
    """
    
    def __init__(self):
        """
        Initialises the CommunityManager Database Connector.
        
        Initialises the connection to the database using the settings in the configuration
        file / module L{config}. The connection itself is stored in a local variable.
        """
        dbname = config.g4ds_cudb_dbname
        host = config.g4ds_cudb_host
        port = config.g4ds_cudb_port
        user = config.g4ds_cudb_username
        password = config.g4ds_cudb_password
        options = None
        tty = None
        
        self._connection = pg.connect(dbname, host, port, options, tty, user, password)
                
    def shutdown(self):
        """
        Shutdown the database connection.
        """
        self._connection.close()

    def getCommunities(self):
        """
        Fetch list of all communities from the database.
        
        @return: List with instances of all communities.
        @rtype: C{List} of L{communitymanager.Community}
        """
        result = self._connection.query('select id, name, description, tcdl, tcdlversion, tcdldate from ' + 
            config.g4ds_cudb_table_communities)
        list = result.getresult()
        returnList = []
        for item in list:
            id = item[0]
            name = item[1]
            description = item[2]
            from binascii import unhexlify
            tcdl = unhexlify(item[3])
##            tcdl = item[3]
            tcdlversion = item[4]
            tcdldate = item[5]
            c = communitymanager.Community(id, name, description, tcdl, tcdlversion, tcdldate)
            returnList.append(c)
        return returnList
        
    def addCommunity(self, community, updateMemberRelations = 0):
        """
        Adds a community to the communities table.
        
        @param community: Community to be written to the database
        @type community: L{communitymanager.Community}
        @param updateMemberRelations: Indicates, whether the relation to the members shall be stored too. Be careful,
            only apply true on one of the sides: either community or member. Otherwise, duplicate entries in the
            table for the relationships will be occurent.
        @type updateMemberRelations: C{Boolean}
        """
        from binascii import hexlify
        tcdl = hexlify(community.getTcdl())
        self._connection.query("""insert into """ + config.g4ds_cudb_table_communities + 
                """(id, name, description, tcdl, tcdlversion, tcdldate) values ('""" +
                community.getId() + """', '""" + community.getName() + """', '""" + community.getDescription() + 
                """', '""" + tcdl + 
                """', '""" + community.getTcdlVersion() + """', '""" + community.getTcdlDate() + """')""")
        if updateMemberRelations:
            for memberid in community.getMembers():
                self.addCommunityMemberRelation(community.getId(), memberid)
        
    def updateCommunity(self, community, dropAuthorityRelations = 1, dropGatewayRelations = 1, dropMemberRelations = 0,
        dropProtocols = 1, dropAlgorithms = 1):
        """
        Updates the entry for the community in the database.
        
        @param community: Community instance to be updated
        @type community: L{communitymanager.Community}
        @param dropAuthorityRelations: Indicates, whether all relations for authorities shall be dropped
        @type dropAuthorityRelations: C{Boolean}
        @param dropGatewayRelations: Indicates, whether all relations for gateways shall be dropped
        @type dropGatewayRelations: C{Boolean}
        @param dropMemberRelations: Indicates, whether all relations for members shall be dropped
        @type dropMemberRelations: C{Boolean}
        @param dropProtocols: Indicates, whether all relations with protocols shall be dropped
        @type dropProtocols: C{Boolean}
        @param dropAlgorithms: Indicates, whether all relations with algorithms shall be dropped
        @type dropAlgorithms: C{Boolean}
        """
        from binascii import hexlify
        tcdl = hexlify(community.getTcdl())
        self._connection.query("""update """ + config.g4ds_cudb_table_communities + 
                """ set id='""" + community.getId() + """', name='""" + 
                community.getName() + """', description='""" + community.getDescription() + """',  tcdl='""" + tcdl + 
                """', tcdlversion='""" + community.getTcdlVersion() + """', tcdldate='""" + community.getTcdlDate() + 
                """' where id='""" + community.getId() + """'""")
        if dropAuthorityRelations:
            self._connection.query("""delete from """ + config.g4ds_cudb_table_relation_communities_authorities + 
                """ where communityid='""" + community.getId() + """'""")
        if dropGatewayRelations:
            self._connection.query("""delete from """ + config.g4ds_cudb_table_gateways +
                """ where source_community_id='""" + community.getId() + """' or dest_community_id='""" +
                community.getId() + """'""")
        if dropMemberRelations:
            self._connection.query("""delete from """ + config.g4ds_cudb_table_relation_communities_members + 
                """ where communityid='""" + community.getId() + """'""")
        if dropProtocols:
            self._connection.query("""delete from """ + config.g4ds_comm_table_relation_communities_protocols +
                """ where communityid='""" + community.getId() + """'""")
        if dropAlgorithms:
            self._connection.query("""delete from """ + config.g4ds_sec_table_relation_communities_algorithms +
                """ where communityid='""" + community.getId() + """'""")            
            
            
    def addCommunityMemberRelation(self, communityid, memberid):
        """
        Adds an entry into the table for the relation between members and communities.
        
        @param communityid: ID of the community to put into relation
        @type communityid: C{String}
        @param memberid: ID of the member to put into relation
        @type memberid: C{String}
        """
        self._connection.query("""insert into """ + config.g4ds_cudb_table_relation_communities_members + 
            """(communityid, memberid) values ('""" +
            communityid + """', '""" + memberid + """')""")

    def addCommunityAuthorityRelation(self, communityid, memberid):
        """
        Adds an entry into the table for the relation between authorities (members) and communities.
        
        @param communityid: ID of the community to put into relation
        @type communityid: C{String}
        @param memberid: ID of the member to put into relation as a authority for the given community
        @type memberid: C{String}
        """
        self._connection.query("""insert into """ + config.g4ds_cudb_table_relation_communities_authorities + 
            """(communityid, memberid) values ('""" +
            communityid + """', '""" + memberid + """')""")
            
    
    def getMembers(self):
        """
        Fetch list of all members from the database.
        
        @return: List with instances of all members.
        @rtype: C{List} of L{communitymanager.Member}
        """
        result = self._connection.query('select id, name, mdl, mdlversion, mdldate from ' + config.g4ds_cudb_table_members)
        list = result.getresult()
        returnList = []
        for item in list:
            id = item[0]
            name = item[1]
            from binascii import unhexlify
            mdl = unhexlify(item[2])
            mdlversion = item[3]
            mdldate = item[4]
            c = communitymanager.Member(id, name, mdl, mdlversion, mdldate)
            returnList.append(c)
        return returnList        
    
    def addMember(self, member, updateCommunityRelations = 0):
        """
        Adds a member to the members table.
        
        @param member: Member to be written to the database
        @type member: L{communitymanager.Member}
        @param updateCommunityRelations: Indicates, whether the relation to the communities shall be stored too. Be careful,
            only apply true on one of the sides: either community or member. Otherwise, duplicate entries in the
            table for the relationships will be occurent.
        @type updateCommunityRelations: C{Boolean}
        """
        from binascii import hexlify
        mdl = hexlify(member.getMdl())
        self._connection.query("""insert into """ + config.g4ds_cudb_table_members + 
                """(id, name, mdl, mdlversion, mdldate) values ('""" +
                member.getId() + """', '""" + member.getName() + """', '""" + mdl + 
                """', '""" + member.getMdlVersion() + """', '""" + member.getMdlDate() + """')""")
        if updateCommunityRelations:
            for communityid in member.getCommunityIds():
                self.addCommunityMemberRelation(communityid, member.getId())

    def updateMember(self,member, updateCommunityRelations = 0):
        """
        Updates the entry for the member in the database.
        """
        from binascii import hexlify
        mdl = hexlify(member.getMdl())
        self._connection.query("""update """ + config.g4ds_cudb_table_members + 
                """ set id='""" +
                member.getId() + """', name='""" + member.getName() + """',  mdl='""" + mdl + 
                """', mdlversion='""" + member.getMdlVersion() + """', mdldate='""" + member.getMdlDate() + 
                """' where id='""" + member.getId() + """'""")
        if updateCommunityRelations:
            self._connection.query("""delete from """ + config.g4ds_cudb_table_relation_communities_members +
                """ where memberid = '""" + member.getId() + """'""")
            for communityid in member.getCommunityIds():
                self.addCommunityMemberRelation(communityid, member.getId())            
                    
    def getMembersOfCommunity(self, community_id):
        """
        Fetches the list of all member id for the given community.
        
        @return: List of member ids
        @rtype: c{List} of C{String}
        """
        
        result = self._connection.query("""select memberid from """ + config.g4ds_cudb_table_relation_communities_members +
                """ where communityid = '""" + community_id + """'""" )
        list = result.getresult()
        returnList = []
        for item in list:
            memberid = item[0]
            returnList.append(memberid)
        return returnList        
        
    def getAuthoritiesOfCommunity(self, community_id):
        """
        Fetches the list of all member ids which are authorities for the given community.
        
        @return: List of member ids
        @rtype: c{List} of C{String}
        """
        result = self._connection.query("""select memberid from """ + config.g4ds_cudb_table_relation_communities_authorities +
                """ where communityid = '""" + community_id + """'""" )
        list = result.getresult()
        returnList = []
        for item in list:
            memberid = item[0]
            returnList.append(memberid)
        return returnList        
    
    def getAuthorisedCommunities(self, member_id):
        """
        Fetches the list of all communities, which the given member is an authority for.
        
        @return: List of ids of communities
        @rtype: C{List} of C{String}
        """
        result = self._connection.query("""select communityid from """ + config.g4ds_cudb_table_relation_communities_authorities +
                """ where memberid = '""" + member_id + """'""" )
        list = result.getresult()
        returnList = []
        for item in list:
            memberid = item[0]
            returnList.append(memberid)
        return returnList        
    
    def getCommunitiesForMember(self, member_id):
        """
        Fetches list of all communities the given member is a member of.
        
        @return: List of community ids
        @rtype: C{List} of C{String}
        """
        result = self._connection.query("""select communityid from """ + config.g4ds_cudb_table_relation_communities_members +
                """ where memberid = '""" + member_id + """'""" )
        list = result.getresult()
        returnList = []
        for item in list:
            communityid = item[0]
            returnList.append(communityid)
        return returnList        
        
    def getGateways(self, memberid = None, communityid = None):
        """
        Fetch list of all gateways from the database.
        
        @return: List with instances of all gateways.
        @rtype: C{List} of L{communitymanager.CommunityGateway}
        """
        query = """select member_id, source_community_id, dest_community_id from """ + config.g4ds_cudb_table_gateways
        if memberid or communityid:
            query = query + """ where 0=0"""
        if memberid:
            query = query + """ AND member_id='""" + memberid + """'"""
        if communityid:
            query = query + """ AND (source_community_id = '""" + communityid + """' OR dest_community_id = '""" + communityid + """')"""
        
        result = self._connection.query(query)
        list = result.getresult()
        returnList = []
        for item in list:
            memberid = item[0]
            srcid = item[1]
            destid = item[2]
            c = communitymanager.CommunityGateway(memberid, srcid, destid, persistent = 0)
            returnList.append(c)
        return returnList        

    def addGateway(self, memberid, sourcecommunityid, destinationcommunityid):
        """
        Adds a gateway relation to the database.
        
        @param memberid: ID of the member employing the role as a gateway
        @type memberid: C{String}
        @param sourcecommunityid: ID of the community the messages are passed from
        @type sourcecommunityid: C{String}
        @param destinationcommunityid: ID of the community the messages are passed to
        @type destinationcommunityid: C{String}
        """
        self._connection.query("""insert into """ + config.g4ds_cudb_table_gateways + """ values ('""" +
                    memberid + """', '""" + sourcecommunityid + """', '""" + destinationcommunityid + """')""")

    def getProtocolsForCommunity(self, communityid):
        """
        Fetch a list of protocols linked to the given community.
        
        @param communityid: ID of the community, the protocols shall be returned for
        @type communityid: C{String}
        @return: List of ids for protocols 
        @rtype: C{List} of C{String}
        """
        result = self._connection.query("""select protocolid from """ + config.g4ds_comm_table_relation_communities_protocols +
            """ where communityid ='""" + communityid + """'""")
        list = result.getresult()
        returnList = []
        for item in list:
            protocolid = item[0]
            returnList.append(protocolid)
        return returnList
    
    def addProtocolToCommunity(self, communityid, protocolid):
        """
        Adds a protocol to the given community.
        
        @param communityid: ID of the community the protocol shall be added to
        @type communityid: C{String}
        @param protocolid: ID of the protocol, which shall be added to the community
        @type protocolid: C{String}
        """
        self._connection.query("""insert into """ + config.g4ds_comm_table_relation_communities_protocols +
            """ (communityid, protocolid) values ('""" + communityid + """', '""" + protocolid + """')""")
        
    def getAlgorithmsForCommunity(self, communityid):
        """
        Fetch a list of algorithms linked to the given community.
        
        @param communityid: ID of the community, the algorithms shall be returned for
        @type communityid: C{String}
        @return: List of ids for algorithms 
        @rtype: C{List} of C{String}
        """
        result = self._connection.query("""select algorithmid from """ + config.g4ds_sec_table_relation_communities_algorithms +
            """ where communityid ='""" + communityid + """'""")
        list = result.getresult()
        returnList = []
        for item in list:
            algorithmid = item[0]
            returnList.append(algorithmid)
        return returnList
    
    def addAlgorithmToCommunity(self, communityid, algorithmid):
        """
        Adds a algorithm to the given community.
        
        @param communityid: ID of the community the algorithm shall be added to
        @type communityid: C{String}
        @param algorithmid: ID of the algorithm, which shall be added to the community
        @type algorithmid: C{String}
        """
        self._connection.query("""insert into """ + config.g4ds_sec_table_relation_communities_algorithms +
            """ (communityid, algorithmid) values ('""" + communityid + """', '""" + algorithmid + """')""")
