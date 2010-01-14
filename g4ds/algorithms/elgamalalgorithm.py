"""
ElGamal algorithm implementation for G4DS.

Grid for Digital Security (G4DS)

Based on the libraries of PyCrypto. Accessed through the site package ezPyCrypto.

@author: Michael Pilgermann
@contact: mailto:mpilgerm@glam.ac.uk
@license: GPL (General Public License)
"""

from algorithminterface import AlgorithmInterface
import config
import ezPyCrypto

class AlgorithmImplementation(AlgorithmInterface):
    """
    Algorithm implementation for G4DS for the ElGamal algorithm.
    
    @ivar _privateKey: Holding the private key in String representation
    @type _privateKey: C{String}
    """
    
    def __init__(self):
        """
        Call super constructor and initialise with name.
        """
        AlgorithmInterface.__init__(self, "elgamal")
        self._privateKey = None
        
    def setKeyPair(self, key):
        """
        Loads the private key to be used for later decryptions.
        
        @Note: Due to the use of the pycrypto / exPyCrypto site packages the keys have to be
        in a certain format. This way, they have to be generated with exPyCrypto in the first place.
        """
        self._privateKey = key
        
    def decrypt(self, ciphertext, keyst = None):
        """
        Decrypts the ciphertext.
        
        @param ciphertext: ElGamal encrypted message
        @type ciphertext: C{String}
        @param keyst: (Private) key to be used. If none given, the key loaded will be used
        @type keyst: C{String}
        @return: The Plain Text
        @rtype: C{String}
        """
        if keyst == None:
            keyst = self._privateKey
        key = ezPyCrypto.key(keyst)
        plain = key.decStringFromAscii(ciphertext)
        return plain

    def encrypt(self, plaintext, keyst):
        """
        Encrypts the plain text.
        
        @param plaintext: String to be encrypted
        @type plaintext: C{String}
        @param keyst: Key to use for encryption (should be the public key of the receiver) - in PyCrypto Format!
        @type keyst: C{String}
        @return: The corresponding cipher text
        @rtype: C{String}
        """
        key = ezPyCrypto.key()
        key.importKey(keyst)
        cipher = key.encStringToAscii(plaintext)
        return cipher
        
    def createKeyPair(self, bitlength = None):
        """
        Creates a key pair for the algorithm.
        """
        if bitlength == None:
            bitlength = config.elgamal_keylength
        privatekey = ezPyCrypto.key(bitlength,'ElGamal')

        return privatekey.exportKeyPrivate()
        
    def getPublicKey(self, privateKeySt = None):
        """
        Returns the public part of the key pair.
        """
        if privateKeySt == None:
            privateKeySt = self._privateKey
        if privateKeySt == None:
            return None
        key = ezPyCrypto.key(privateKeySt)
        return key.exportKey()

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
        if keyst == None:
            keyst = self._privateKey
        key = ezPyCrypto.key(keyst)
        signature = key.signString(message)
        return signature
        
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
        key = ezPyCrypto.key()
        key.importKey(keyst)
        return key.verifyString(message, signature)
