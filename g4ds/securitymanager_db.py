"""
The database backend functions for the security module.

Grid for Digital Security (G4DS)


@author: Michael Pilgermann
@contact: mailto:mpilgerm@glam.ac.uk
@license: GPL (General Public License)
"""

import config
import pg
import securitymanager

class SecDB:
    """
    Handles all requests form the security module for backend connectivity with database.

    @ivar _connection: Reference to database connection
    @type _connection: PSQL-DB-Connection
    """
    
    def __init__(self):
        """
        Initialises the database manager for secure communication.
        
        The database connection is established using the appropriate settings in the configuations
        file / module config.py.
        
        Please run L{shutdown} before you shutdown the application in order to clear the database
        connections.
        """
        dbname = config.g4ds_sec_dbname
        host = config.g4ds_sec_host
        port = config.g4ds_sec_port
        user = config.g4ds_sec_username
        password = config.g4ds_sec_password
        options = None
        tty = None
        
        self._connection = pg.connect(dbname, host, port, options, tty, user, password)
        
    def shutdown(self):
        """
        Closes open database connections.
        """
        self._connection.close()
        
    
    def getAlgorithms(self):
        """
        Returns a list of all algorithms in the database.
        """
        result = self._connection.query('select id, name from ' + config.g4ds_sec_table_algorithms)
        list = result.getresult()
        returnList = []
        for item in list:
            id = item[0]
            name = item[1]
            c = securitymanager.Algorithm(id, name, 1)
            returnList.append(c)
        return returnList        
        
    def addAlgorithm(self, algorithm):
        """
        Adds one algorithm to the algorithm table in the database.
        """
        self._connection.query("""insert into """ + config.g4ds_sec_table_algorithms + 
                """(id, name) values ('""" +
                algorithm.getId() + """', '""" + algorithm.getName() + """')""")
                
    def getCredentials(self):
        """
        Returns a list of all credentials in the database.
        """
        result = self._connection.query('select id, algorithmid, username, key, memberid from ' + config.g4ds_sec_table_credentials)
        list = result.getresult()
        returnList = []
        for item in list:
            id = item[0]
            algorithmid = item[1]
            username = item[2]
            key = item[3]
            ownerid = item[4]
            c = securitymanager.Credential(id, algorithmid, username, key, ownerid, 1)
            returnList.append(c)
        return returnList        
        
    def addCredential(self, credential):
        """
        Adds one credential to the credential table in the database.
        """
        self._connection.query("""insert into """ + config.g4ds_sec_table_credentials + 
                """(id, algorithmid, username, key, memberid) values ('""" +
                credential.getId() + """', '""" + credential.getAlgorithmId() + """', '""" + credential.getUsername()
                 + """', '""" + credential.getKey() + """', '""" + credential.getOwnerId()  + """')""")

    def removeCredentials(self, credentialid = None, memberid = None):
        """
        Removes credentials from the database.
        
        Depending on which parameters are given. If no parameter is set, all data in the table
        will be dropped.
        """
        st = """delete from """ + config.g4ds_sec_table_credentials + """ where 1=1 """
        if credentialid:
            st = st + """ and id = '""" + credentialid + """' """
        if memberid:
            st = st + """ and memberid = '""" + memberid + """'"""
        self._connection.query(st)
                 
    def getPersonalCredentials(self):
        """
        Returns a list of all personal credentials in the database.
        """
        result = self._connection.query('select id, name, algorithmid, key_private, key_public, username from ' + config.g4ds_sec_table_mycredentials)
        list = result.getresult()
        returnList = []
        for item in list:
            id = item[0]
            name = item[1]
            algorithmid = item[2]
            privateKey = item[3]
            publicKey = item[4]
            username = item[5]
            c = securitymanager.PersonalCredential(id, name, algorithmid, privateKey, publicKey, username, 1)
            returnList.append(c)
        return returnList        
        
    def addPersonalCredential(self, credential):
        """
        Adds one personal credential to the personal credential table in the database.
        """
        self._connection.query("""insert into """ + config.g4ds_sec_table_mycredentials + 
                """(id, name, algorithmid, key_private, key_public, username) values ('""" +
                credential.getId() + """', '""" + credential.getName() + """', '""" + credential.getAlgorithmId()
                 + """', '""" + credential.getPrivateKey() + """', '""" + credential.getPublicKey()  + 
                 """', '""" + credential.getUsername()  + """')""")


