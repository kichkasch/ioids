from M2Crypto import RSA
from M2Crypto import DSA

class KeyGen:
    def __init__(self):
        self._initCiphers()
        
    def _initCiphers(self):
        self.ciphers = []
        self.ciphers.append("RSA")
        self.ciphers.append("DSA")
        
        bits = ['512', '1024', '2048']
        self.cipher_lengths = {}
        self.cipher_lengths["RSA"] = bits
        bits = ['512', '1024', '2048', '4096']
        self.cipher_lengths["DSA"] = bits
        
        self.saveCiphers = {}
        saveCiphers = []
        saveCiphers.append('des_ede3_cbc')
        self.saveCiphers["RSA"] = saveCiphers
        self.saveCiphers["DSA"] = None
    
    def getAvailableCiphers(self):
        return self.ciphers
        
    def getAvaiableBitLengths(self, cipher):
        return self.cipher_lengths[cipher]

    def getAvailableSaveCiphers(self, cipher):
        return self.saveCiphers[cipher]
    
    
    def createKey(self, cipher, length, callback, parent = None):
        key = None
        if cipher == "RSA":
            exp = 65537
            print ("Create RSA key with key length %d bits\n" %length)
            key = RSA.gen_key(length, exp, callback)
        elif cipher == "DSA":
            print ("Create DSA key with key length %d bits\n" %length)
            dsa = DSA.gen_params(length, callback)
            dsa.gen_key()
            key = dsa
        if parent != None:
            parent.finishedGeneration(key)
        return key
    
    # if cipher is none, the method tries to work out the cipher itself
    #
    # returns the key and the cipher
    def loadKey(self, file, callback, cipher=None, parent = None):
        key = None
        if cipher == "RSA" or cipher == None:
            try:
                key = RSA.load_key(file, callback)
                return key, "RSA"
            except IOError, (errno, strerror):
                return None, "RSA" # file not found
            except RSA.RSAError, args:
                print "RSA key generation error: " + args[0]
                pass
            except ValueError:
                pass
        if cipher == "DSA" or cipher == None:
            try:
                key = DSA.load_key(file, callback)
                return key, "DSA"
            except IOError, (errno, strerror):
                return None, "DSA" # file not found
            except ValueError:
                pass
            except DSA.DSAError:
                pass
        return None, None
    
    
    def saveKey(self, cipher, filename, handle, callback, save_cipher='des_ede3_cbc', prompt = 0, parent = None):
        success = 1
        if cipher == "RSA":
            success = handle.save_key(filename, save_cipher, callback)
        elif cipher == "DSA":
            handle.save_key(filename, callback)
            success = 0
        if parent != None:
            parent.finishedSaving(success)
        return None
