"""
Provides the interface, each algorithm implementation must implement to work with G4DS.

Grid for Digital Security (G4DS)


@author: Michael Pilgermann
@contact: mailto:mpilgerm@glam.ac.uk
@license: GPL (General Public License)
"""

class AlgorithmInterface:
    """
    Provides a common interface for all implementations for algorithms.
    
    @ivar _name: Name of the Implementation
    @type _name: C{String}
    """

    def __init__(self, name):
        """
        Just ot set up the name of the implementation.
        """
        self._name = name
        
    def getName(self):
        """
        GETTER
        """
        return self._name
        
    def setKeyPair(self, key):
        """
        SETTER
        """
        pass
        
    def decrypt(self, ciphertext, keyst = None):
        """
        Decrypts the ciphertext.
        
        @return: The plain text
        @rtype: C{String}
        """
        return None
        
    def encrypt(self, plaintext, keyst):
        """
        Encrypts the plain text.
        
        @return: The corresponding cipher text
        @rtype: C{String}
        """
        return None 

    def createKeyPair(self, bitlength = None):
        """
        Creates a key pair for the algorithm.
        """
        return None

    def getPublicKey(self, privateKeySt = None):
        """
        Returns the public part of the key pair.
        """
        return None
        
    def signMessage(self, message, keyst = None):
        """
        Provides a signature for the given message.

        @param message: Message to be signed (usually plain text)
        @type message: C{String}
        @param keyst: Private key to use for signing - if none given, the one stored in the instance will be used
        @type keyst: C{String}
        @return: Corresponding Signature
        @rtype: C{String}
        """
        return None
        
    def validate(self, message, signature, keyst):
        """
        Verifies, whether the exactly this message has been signed with the corresponding private key for this public key.
        
        @param message: Message, which was signed (usually plain text)
        @type message: C{String}
        @param signature: Signature, which was created for this message
        @type signature: C{String}
        @param keyst: Public key - the corresponding private key must have been used for signing the message
        @type keyst: C{String}
        @return: True, if this message has produced exactly this signature if the corresponding private key was used, otherwise false
        @rtype: C{Boolean}
        """
        return None
