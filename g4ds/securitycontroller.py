"""
Manages all issues for secure communications (en/de-cryption, message validation, ...)

Grid for Digital Security (G4DS)

Maintains a list of algorithm, which may by accessed by their name for tasks such as encryption,
decryption, message signing and message validation.

@author: Michael Pilgermann
@contact: mailto:mpilgerm@glam.ac.uk
@license: GPL (General Public License)

@var _securityController: Singleton - the only instance ever of the SecurityController class
@type _securityController: L{SecurityController}
"""

from algorithmcontroller import getAlgorithmController

# "singleton"
_securityController = None
def getSecurityController():
    """
    Singleton implementation.
    
    @return: The instance for the security controller class
    @rtype: L{SecurityController}
    """
    global _securityController
    if not _securityController:
        _securityController = SecurityController()
    return _securityController

class SecurityController:
    """
    Handles requests related to security and passes them to the appropriate implementation for the
    requested algorithm.
    """
    def __init__(self):
        """
        Yet empty Constructor.
        """
        pass
        
    def decrypt(self, message, algorithm):
        """
        Decrypts the message using the the given key and algorithm.
        
        The corresponding algorithm is loaded using the name and the messages together with
        the key is passed to the decryption method in there.
        
        Key is not need here since the private key stored for this algorithm will be used.
        
        @param message: Cipher text to be decrypted
        @type message: C{String}
        @param algorithm: Name of the algorithm to be used for decryption
        @type algorithm: C{String}
        @return: Return value of the corresponding decrypt function within the implementation for the algorithm - plain text
        @rtype: C{String}
        """
        algorithm = getAlgorithmController().getAlgorithm(algorithm)
        plain = algorithm.decrypt(message)
        return plain
        
    def encrypt(self, message, key, algorithm):
        """
        Encrypts the message using the the given key and algorithm.
        
        The corresponding algorithm is loaded using the name and the messages together with
        the key is passed to the encryption method in there.
        
        @param message: Plain text to be encrypted
        @type message: C{String}
        @param key: Key to be used for encryption
        @type key: C{String}
        @param algorithm: Name of the algorithm to be used for encryption
        @type algorithm: C{String}
        @return: Return value of the corresponding encrypt function within the implementation for the algorithm - cipher text
        @rtype: C{String}
        """
        algorithm = getAlgorithmController().getAlgorithm(algorithm)
        cipher = algorithm.encrypt(message, key)
        return cipher
        
    def signMessage(self, message, algorithm): 
        """
        Provides a signature for the given message.
        
        Key is not need here since the private key stored for this algorithm will be used.
        
        @return: The signature
        @rtype: C{String}
        """
        algorithm = getAlgorithmController().getAlgorithm(algorithm)
        signature = algorithm.signMessage(message)
        return signature
    
    def validate(self, message, signature, key, algorithm):
        """
        Verifies, whether the given signature corrosponds with the given message.
        
        @return: Indicates, whether message and signature belong togehter.
        @rtype: C{Boolean}
        """
        algorithm = getAlgorithmController().getAlgorithm(algorithm)
        return algorithm.validate(message, signature, key)
