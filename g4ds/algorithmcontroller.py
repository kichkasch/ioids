"""
Manages the implementations for the different algorithms.

Grid for Digital Security (G4DS)

@author: Michael Pilgermann
@contact: mailto:mpilgerm@glam.ac.uk
@license: GPL (General Public License)

@var _algorithmController: For singleton implementation
@type _algorithmController: L{AlgorithmController}
"""

import algorithms.config
import algorithms.algorithminterface

# "singleton"
_algorithmController = None
def getAlgorithmController():
    """
    Singleton Implementation.
    
    Returns the instance to the AlgorithmController class.
    """
    global _algorithmController
    if not _algorithmController:
        _algorithmController = AlgorithmController()
    return _algorithmController
    
class AlgorithmController:
    """
    Maintains a dictionary with all available protocols.
    
    @ivar _algorithms: Dictionary of algorithms implemented and available on this node
    @type _algorithms: C{Dict} of {AlgorithmImplementationModules}
    @ivar _openalgorithms: Algorithms, which have been initialised; hence, keys are present and useable.
    @type _openalgorithms: C{Dict} of {AlgorithmImplementations}
    @ivar _defaultalgorithm: Name of the algorithm to be used whenever none is defined
    @type _defaultalgorithm: C{String}
    """

    def __init__(self, positiveList = None, negativeList = None, defaultAlgorithm = algorithms.config.default_algorithm):
        """
        Initialises the Algorithm controller. 
        
        The list of algorithms is loaded from the config file for algorithms. 
        
        If L{positiveList} is given, only the algorithms defined in there will be used. If not positiveList
        is given, the negativeList will be checked. Algorithms given in there will be skipped when intialising
        the algorithms. If neither of the two lists is given, all algorithms defined in the config file
        for algorithms will be initialised and activated.
        
        @param positiveList: List of names of algorithms to initialise
        @type positiveList: C{List} of C{String}
        @param negativeList: List of names of algorithms to skip for initialisation
        @type negativeList: C{List} of C{String}
        @param defaultAlgorithm: Name of algorithm to use if none is specified
        @type defaultAlgorithm: C{String}
        """
        self._algorithms = algorithms.config.algorithms
        self._openalgorithms = {}
        self._defaultalgorithm = defaultAlgorithm
        if positiveList:
            for algorithmName in positiveList:
                algorithmModule = self._algorithms[algorithmName]
                instance = algorithmModule.AlgorithmImplementation()
                self._openalgorithms[instance.getName()] = instance
        else:
            if not negativeList:
                negativeList = []
            for algorithmName in self._algorithms.keys():
                try:
                    negativeList.index(algorithmName)
                except ValueError:
                    # here we go if the algorithmName is not in the negativeList
                    algorithmModule = self._algorithms[algorithmName]
                    instance = algorithmModule.AlgorithmImplementation()
                    self._openalgorithms[instance.getName()] = instance

    def getAlgorithm(self, algName):
        """
        Provides the instance of the Algorithm with the requested name.
        """
        return self._openalgorithms[algName]
        
    def getAvailableAlgorithms(self):
        """
        Returns a list of names of available algorithms.
        
        @return: List of names of algorithms
        @rtype: C{List} of C{String}
        """
        return self._algorithms.keys()
    
    def getOpenAlgorithms(self):
        """
        Returns a list of names of algorithms, which are currently initialised on this node.

        @return: List of names of algorithms
        @rtype: C{List} of C{String}
        """
        return self._openalgorithms.keys()
    
    def loadKeys(self):
        """
        Loads the required keys for the algorithms.
        """
        from securitymanager import getAlgorithmManager
        from securitymanager import getPersonalCredentialManager
        for alg in getAlgorithmManager().getAlgorithms():
            if alg.getName() in self.getOpenAlgorithms():
                for cred in getPersonalCredentialManager().getPersonalCredentials():
                    if cred.getAlgorithmId() == alg.getId():
                        self.getAlgorithm(alg.getName()).setKeyPair(cred.getPrivateKey())
        
    
