"""
All stuff involving securing the communication for G4DS.

Grid for Digital Security (G4DS)


@author: Michael Pilgermann
@contact: mailto:mpilgerm@glam.ac.uk
@license: GPL (General Public License)

@var _algorithmManager: Singleton - the only instance ever of the AlgorithmManager class
@type _algorithmManager: L{AlgorithmManager}
@var _credentialManager: Singleton - the only instance ever of the CredentialManager class
@type _credentialManager: L{CredentialManager}
@var _personalCredentialManager: Singleton - the only instance ever of the PersonalCredentialManager class
@type _personalCredentialManager: L{PersonalCredentialManager}
"""

import tools
import config
import securitymanager_db


# ##########################################
# ##########################################
# "Singleton" stuff
_algorithmManager = None
_credentialManager = None
_personalCredentialManager = None

def getAlgorithmManager():
    """
    Singleton - returns the instance to the algorithm manager
    
    If the instance has not yet been initialised, this will be done. Finally, the
    instance is returned.
    
    @return: The only instance to a Algorithm Manager
    @rtype: L{AlgorithmManager}
    """
    global _algorithmManager
    if _algorithmManager == None:
        _algorithmManager = AlgorithmManager(config.dbconnected)
    return _algorithmManager
    
def getCredentialManager():
    """
    Singleton - returns the instance to the credential manager
    
    If the instance has not yet been initialised, this will be done. Finally, the
    instance is returned.
    
    @return: The only instance to a Credential Manager
    @rtype: L{CredentialManager}
    """
    global _credentialManager
    if _credentialManager == None:
        _credentialManager = CredentialManager(config.dbconnected)
    return _credentialManager
    
def getPersonalCredentialManager():
    """
    Singleton - returns the instance to the personal credential manager
    
    If the instance has not yet been initialised, this will be done. Finally, the
    instance is returned.
    
    @return: The only instance to a Personal Credential Manager
    @rtype: L{PersonalCredentialManager}
    """
    global _personalCredentialManager
    if _personalCredentialManager == None:
        _personalCredentialManager = PersonalCredentialManager(config.dbconnected)
    return _personalCredentialManager
# ##########################################
# ##########################################

class CredentialManager:
    """
    Maintains a list of credentials.
    
    @ivar _credentials: Dictionary, maintaining the credentials - accessable by its id
    @type _credentials: C{Dict} (C{String} | L{Credential})
    @ivar _dbconnected: Indicates, whether the manager is connected to a database; hence whether the changes 
        shall be written through
    @type _dbconnected: C{Boolean}
    @ivar _sec_db: Security Database Connector
    @type _sec_db: L{securitymanager_db.SecDB}
    """
    def __init__(self, loadFromDatabase = config.dbconnected):
        """
        Initialises the manager with the subjacent database.

        @param loadFromDatabase: Indicates, whether the manager shall be initialised from the database backend
        @type loadFromDatabase: C{Boolean}
        """
        self._credentials = {}
        self._dbconnected = loadFromDatabase
        if self._dbconnected:
            self._sec_db = securitymanager_db.SecDB()
            credentials = self._sec_db.getCredentials()
            
            for credential in credentials:
                self.addCredential(credential, 0)
                
    def __str__(self):
        """
        Some basic information about the object
        """
        return "CredentialManager: %d Credentials." %(len(self._credentials))

    def addCredential(self, credential, persistent = config.dbconnected):
        """
        Add one credential to the manager.
        
        @param credential: Credential to be added
        @type credential: L{Credential}
        @param persistent: Indicates, whether the credential shall be written through to the database
        @type persistent: C{Boolean}
        """
        self._credentials[credential.getId()] = credential
        if persistent:
            self._sec_db.addCredential(credential)
    
    def getCredential(self, credentialId):
        """
        Returns the credential instance for the given credential id.
        """
        return self._credentials[credentialId]
        
    def getCredentials(self):
        """
        Returns a list of all saved credentials.
        
        @return: List of all credentials
        @rtype: C{List} of L{Credential}
        """
        return self._credentials.values()
        
    def getCredentialsForMember(self, memberid):
        """
        Returns a list of credentials, whose member is the one with the id given.
        
        @return: List of credentials
        @rtype: C{List} of L{Credential}
        """
        returnList = []
        for c in self._credentials.values():
            if c.getOwnerId() == memberid:
                returnList.append(c)
        return returnList

    def removeCredential(self, credentialid):
        """
        Removes the credential with the given id from the manager (and the database if connected).
        """
        del self._credentials[credentialid]
        if self._dbconnected:
            self._sec_db.removeCredentials(credentialid)
        
    def removeCredentialsForMember(self, memberid):
        """
        Removes all credentials from the manager (and database) for the member with the given id.
        """
        for c in self._credentials.values():
            if c.getOwnerId() == memberid:
                self.removeCredential(c.getId())

                
class Credential:
    """
    All information needed for one bundle of information chunks for a credential.
    
    @ivar _id: Unique id for the credential
    @type _id: C{String}
    @ivar _algorithmid: ID of the algorithm, this credential can be used with (and was created for)
    @type _algorithmid: C{String}
    @ivar _username: Username for this credential
    @type _username: C{String}
    @ivar _key: Public key
    @type _key: C{String}
    @ivar _ownerid: ID of the owner of this key (Member, Community, ...)
    @type _ownerid: C{String}
    """
    def __init__(self, id = None, algorithmid = None, username = None, key = None, ownerid = None, init = 0):
        """
        Initalises the Algorithm and assigns the parameters to the local variables.
        
        @param id: Unique id for the algorithm (if None is given, one will be generated using the key generator in tools)
        @type id: C{String}
        @param algorithmid: ID of the algorithm, this credential can be used with (and was created for)
        @type algorithmid: C{String}
        @param username: Username for this credential (optional)
        @type username: C{String}
        @param key: Public key
        @type key: C{String}
        @param ownerid: ID of the owner of this key (Member, Community, ...)
        @type ownerid: C{String}
        @param init: Indidates, whether this instance is created during initialises process (of the container).
        @type init: C{Boolean}
        """
        self._id = id
        self._algorithmid = algorithmid
        self._username = username
        self._key = key
        self._ownerid = ownerid
        
        if self._id == None:
            self._id = tools.generateId(tools.TYPE_CREDENTIAL)

    def __str__(self):
        """
        Some basic information about the object
        """
        return "Credential (%s): %s (AlgID) - OwnerID: %s." %(self.getId(), self.getAlgorithmId(), self.getOwnerId())
    
    def getId(self):
        """
        GETTER
        """
        return self._id
        
    def setId(self, id):
        """
        SETTER
        """
        self._id = id

    def getAlgorithmId(self):
        """ 
        GETTER
        """
        return self._algorithmid
    
    def getUsername(self):
        """ 
        GETTER
        """
        return self._username
    
    def getKey(self):
        """ 
        GETTER
        """
        return self._key
    
    def getOwnerId(self):
        """ 
        GETTER
        """
        return self._ownerid
    
    
class PersonalCredentialManager:
    """
    Maintains the list of personal confidentials for this node.
    
    Unlike the L{CredentialManager}, which stores information for all nodes only including public information,
    this class maintains also private information; namely private keys. It is only responible for credentials
    for this node. However, this node has to maintain a credential for each algorithm (RSA; DSA).

    @ivar _credentials: Dictionary, maintaining the credentials - accessable by its id
    @type _credentials: C{Dict} (C{String} | L{Credential})
    @ivar _dbconnected: Indicates, whether the manager is connected to a database; hence whether the changes 
        shall be written through
    @type _dbconnected: C{Boolean}
    @ivar _sec_db: Security Database Connector
    @type _sec_db: L{securitymanager_db.SecDB}
    """
    def __init__(self, loadFromDatabase = config.dbconnected):
        """
        Initialises the manager with the subjacent database.

        @param loadFromDatabase: Indicates, whether the manager shall be initialised from the database backend
        @type loadFromDatabase: C{Boolean}
        """
        self._credentials = {}
        self._dbconnected = loadFromDatabase
        if self._dbconnected:
            self._sec_db = securitymanager_db.SecDB()
            credentials = self._sec_db.getPersonalCredentials()
            
            for credential in credentials:
                self.addPersonalCredential(credential, 0)
                
    def __str__(self):
        """
        Some basic information about the object
        """
        return "PersonalCredentialManager: %d Credentials." %(len(self._credentials))

    def addPersonalCredential(self, credential, persistent = config.dbconnected):
        """
        Add one personal credential to the manager.
        
        @param credential: Credential to be added
        @type credential: L{PersonalCredential}
        @param persistent: Indicates, whether the algorithm shall be written through to the database
        @type persistent: C{Boolean}
        """
        self._credentials[credential.getId()] = credential
        if persistent:
            self._sec_db.addPersonalCredential(credential)
    
    def getPersonalCredential(self, credentialId):
        """
        Returns the personal credential instance for the given credential id.
        """
        return self._credentials[credentialId]
        
    def getPersonalCredentials(self):
        """
        Returns a list of all saved personal credentials.
        
        @return: List of all personal credentials
        @rtype: C{List} of L{Personal Credential}
        """
        return self._credentials.values()
        
class PersonalCredential:
    """
    Maintains all information for one personal credential.

    @ivar _id: Unique id for the personal credential
    @type _id: C{String}
    @ivar _name: Name for the personal credential
    @type _name: C{String}
    @ivar _username: User name to be used
    @type _username: C{String}
    @ivar _algorithmid: ID of the algorithm, this credential is valid for and was created for
    @type _algorithmid: C{String}
    @ivar _privateKey: String represenation of the Private Key
    @type _privateKey: C{String}
    @ivar _publicKey: String representation of the Public Key
    @type _publicKey: C{String}
    """
    def __init__(self, id = None, name = None, algorithmid = None, privateKey = None, publicKey = None, username = None, init = 0):
        """
        Initalises the Personal Credential and assigns the parameters to the local variables.
        
        @param id: Unique id for the personal credential
        @type id: C{String}
        @param name: Name for the personal credential
        @type name: C{String}
        @param username: User name to be used
        @type username: C{String}
        @param algorithmid: ID of the algorithm, this credential is valid for and was created for
        @type algorithmid: C{String}
        @param privateKey: String represenation of the Private Key
        @type privateKey: C{String}
        @param publicKey: String representation of the Public Key
        @type publicKey: C{String}
        @param init: Indidates, whether this instance is created during initialises process (of the container).
        @type init: C{Boolean}
        """
        self._id = id
        self._name = name
        self._username = username
        self._algorithmid = algorithmid
        self._privateKey = privateKey
        self._publicKey = publicKey
        
        if self._id == None:
            self._id = tools.generateId(tools.TYPE_PERSONALCREDENTIAL)
        
    def __str__(self):
        """
        Some basic information about the object
        """
        return "Personal Credential (%s): %s - AlgID: %s." %(self.getId(), self.getName(), self.getAlgorithmId())
        
    
    def getId(self):
        """
        GETTER
        """
        return self._id
        
    def getName(self):
        """ 
        GETTER
        """
        return self._name
        
    def getUsername(self):
        """ 
        GETTER
        """
        return self._username
        
    def getAlgorithmId(self):
        """ 
        GETTER
        """
        return self._algorithmid
        
    def getPrivateKey(self):
        """ 
        GETTER
        """
        return self._privateKey
        
    def getPublicKey(self):
        """ 
        GETTER
        """
        return self._publicKey
        
        
class AlgorithmManager:
    """
    Maintains a list of algorithm suitable for credentials.
    
    @ivar _algorithms: Dictionary, maintaining the algorithms - accessable by its id
    @type _algorithms: C{Dict} (C{String} | L{Algorithm})
    @ivar _dbconnected: Indicates, whether the manager is connected to a database; hence whether the changes 
        shall be written through
    @type _dbconnected: C{Boolean}
    @ivar _sec_db: Security Database Connector
    @type _sec_db: L{securitymanager_db.SecDB}
    """
    def __init__(self, loadFromDatabase = config.dbconnected):
        """
        Initialises the manager with the subjacent database.

        @param loadFromDatabase: Indicates, whether the manager shall be initialised from the database backend
        @type loadFromDatabase: C{Boolean}
        """
        self._algorithms = {}
        self._dbconnected = loadFromDatabase
        if self._dbconnected:
            self._sec_db = securitymanager_db.SecDB()
            algorithms = self._sec_db.getAlgorithms()
            
            for algorithm in algorithms:
                self.addAlgorithm(algorithm, 0)
                
    def __str__(self):
        """
        Some basic information about the object
        """
        return "AlgorithmManager: %d Algorithms." %(len(self._algorithms))
        
    def addAlgorithm(self, algorithm, persistent = config.dbconnected):
        """
        Add one algorithm to the manager.
        
        @param algorithm: Algorithm to be added
        @type algorithm: L{Algorithm}
        @param persistent: Indicates, whether the algorithm shall be written through to the database
        @type persistent: C{Boolean}
        """
        self._algorithms[algorithm.getId()] = algorithm
        if persistent:
            self._sec_db.addAlgorithm(algorithm)
    
    def getAlgorithm(self, algorithmId):
        """
        Returns the algorithm instance for the given algoritm id.
        """
        return self._algorithms[algorithmId]
        
    def getAlgorithmByName(self, algName):
        """
        Returns the algorithm instance with the name as given.
        """
        for alg in self._algorithms.values():
            if alg.getName == algName:
                return alg
        return None
        
    def getAlgorithms(self):
        """
        Returns a list of all saved algorithms.
        
        @return: List of all algorithms
        @rtype: C{List} of L{Algorithm}
        """
        return self._algorithms.values()
        
    def getAlgorithmByNameAndInsert(self, algname):
        """
        Returns the algorithm with given algorithm name. 
        
        If the algorithm is not yet in the manager it will be created.
        """
        for a in self._algorithms.values():
            if a.getName() == algname:
                return a
        a = Algorithm(None, algname)
        self.addAlgorithm(a)
        return a
        
        
class Algorithm:
    """
    Maintains the relation between algorithm names and their ids.

    @ivar _id: Unique id for the algorithm
    @type _id: C{String}
    @ivar _name: Name for the algorithm
    @type _name: C{String}
    """
    def __init__(self, id = None, name = None, init = 0):
        """
        Initalises the Algorithm and assigns the parameters to the local variables.
        
        @param id: Unique id for the algorithm
        @type id: C{String}
        @param name: Name for the algorithm
        @type name: C{String}
        @param init: Indidates, whether this instance is created during initialises process (of the container).
        @type init: C{Boolean}
        """
        self._id = id
        self._name = name
        
        if self._id == None:
            self._id = tools.generateId(tools.TYPE_ALGORITHM)
        
    def __str__(self):
        """
        Some basic information about the object
        """
        return "Algorithm (%s): %s." %(self.getId(), self.getName())
        
    
    def getId(self):
        """
        GETTER
        """
        return self._id
        
    def getName(self):
        """ 
        GETTER
        """
        return self._name
