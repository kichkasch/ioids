"""
Client - several services can connect this way.

Grid for Digital Security (G4DS)

@author: Michael Pilgermann
@contact: mailto:mpilgerm@glam.ac.uk
@license: GPL (General Public License)
"""

METADATA_SENDERID = 'senderid'
METADATA_COMMUNITYID = 'communityid'
METADATA_SERVICEID = 'serviceid'
METADATA_MESSAGEID = 'messageid'

import os, time
from config import FIFO_PATH_IN, FIFO_PATH_OUT
from messagewrapper import getConnectedServicesWrapper

class G4dsService:
    """
    That's the one to use from your program
    """
    
    def __init__(self):
        """
        Connects to the G4ds Service Listener
        """
        pass
    
    def connect(self, serviceId, privateKey = None, privateKeyLocation = None, callback = None):
        """
        Connect to the server.
        
        You have to provide either privateKey or privateKeyLocation
        """
        if not privateKey and not privateKeyLocation:
            from errorhandling import G4dsDependencyException
            raise G4dsDependencyException('No private key provided.')
        
        if not privateKey:
            file = open(privateKeyLocation)
            privateKey = file.read()
            file.close()
        
        self._serviceId = serviceId
        self._privateKey = privateKey
        self._callback = callback
    
        # rendevous :)
        majorPipeIn = open(FIFO_PATH_IN,'w')
        
        majorPipeIn.write('connect')
        majorPipeIn.close()
        try:
            majorPipeOut = open(FIFO_PATH_OUT,'r')
        except IOError, msg:
            from errorhandling import G4dsDependencyException
            raise G4dsDependencyException('Could not connect against server process. Check, whether G4ds server is runing. (Low level error message: %s)' %(msg))
    
        myPipeInfo = majorPipeOut.read()    # here we get the number of our fifo
        majorPipeOut.close()
        
        # wait one sec, for the server to establish the fifo
        time.sleep(1)
        self._rendevous(myPipeInfo)
        
    def _createAuthenticationToken(self):
        """
        We simply use RSA here.
        """
        from algorithmcontroller import getAlgorithmController
        rsa = getAlgorithmController().getAlgorithm('rsa')
        rsa.setKeyPair(self._privateKey)
        
        import random
        plain = ''
        for i in range(0,100):
            plain += chr(random.randint(0,127))
        
        signature = rsa.signMessage(plain)
        
        return plain, signature
        
    def _decryptWithMyPrivateKey(self, message):
        from algorithmcontroller import getAlgorithmController
        rsa = getAlgorithmController().getAlgorithm('rsa')
        rsa.setKeyPair(self._privateKey)

        return rsa.decrypt(message)

    def _receiveOne(self, multiple = 0):
        self._pipeOut = open(self._name_pipe_out,'r')
        # so, let's read the command from the client then - rendevous
        data = ' '
        datalens = ''
        alldata = ''
        while data != '':
            data = self._pipeOut.read().rstrip()
            alldata += data
            datalens += "%d " %(len(data))
        self._pipeOut.close()
##        return alldata
        if multiple:
            extracted = getConnectedServicesWrapper().parseMessages(alldata)
        else:
            extracted = getConnectedServicesWrapper().parseMessage(alldata)
        return extracted
##        f = open('/tmp/after_dec.txt','a')
##        f.write('================= I received %d Bytes (%s) ===========\n' %(len(alldata), datalens))
##        f.close()
        
    def _sendOne(self, message):        
        self._pipeIn = open(self._name_pipe_in,'w')
##        self._pipeIn.write(message)
        wrapped = getConnectedServicesWrapper().assembleMessage(message)
        self._pipeIn.write(wrapped)
        self._pipeIn.close()

        
    def _rendevous(self, number):
        """
        Authenticates at the server process using the service fifo.
        """
        self._name_pipe_in = FIFO_PATH_IN + "." + str(number)
        self._name_pipe_out = FIFO_PATH_OUT + "." + str(number)
        
        from messagewrapper import getGenericWrapper
        plain, signature = self._createAuthenticationToken()
        args = {}
        args['action'] = 'authenticate'
        args['serviceid'] = self._serviceId
        datas = {}
        datas['plain'] = plain
        datas['signature'] = signature
        xmlRendevous = getGenericWrapper().wrapArgsAndDatas('rendevous', args, datas)
        
        self._sendOne(xmlRendevous)
        
        reply = self._receiveOne()
        
        args, datas = getGenericWrapper().unwrapArgsAndDatas('rendevous', reply)
        #print args
        if not int (args['sucess']):
            if args.has_key('errormessage'):
                error = args['errormessage']
            else:
                error = 'The provided key might have not been accepted.'
            from errorhandling import G4dsDependencyException
            raise G4dsDependencyException('Connecting against Service not sucessful. %s' %(error))
            
        sessionkey = datas['sessionkey']
        self._sessionkey = self._decryptWithMyPrivateKey(sessionkey)
        
        import thread
        thread.start_new_thread(self.listen, ())
        
    def _encryptSession(self, msg):
        """
        Encrypts a message with the session key.
        """
        from SSLCrypto import key
##        from ezPyCrypto import key
        k = key()
        k.importKey(self._sessionkey)
##        import binascii as hex
##        encoded = hex.hexlify(msg)
##        ciphered = k.encString(encoded)
        ciphered = k.encString(msg)
        return ciphered
        
    def _decryptSession(self, ciphered):
        """
        Decrypts a message with the session key.
        """
##        print "I decrypt length: %d" %(len(ciphered))
        from SSLCrypto import key
##        from ezPyCrypto import key
        k = key()
        k.importKey(self._sessionkey)
        msg = k.decString(ciphered)

##        f = open('/tmp/after_dec.txt','a')
##        f.write('%s %d | %d %s\n%s' %('*' * 50, len(msg), len(ciphered), '*' * 30, msg))
##        f.close()
        return msg
        
    def listen(self):
        while 1:
            msgs = self._receiveOne(multiple = 1)
            for msg in msgs:
                dec = self._decryptSession(msg)
                
                from messagewrapper import getGenericWrapper
                metadata, datas = getGenericWrapper().unwrapArgsAndDatas('servicemetadata', dec)
                msg = datas['message']
                self._callback(msg, metadata)

    def sendMessage(self, destinationMember, destinationCommunity, message, actionstring = None):
        from messagewrapper import getGenericWrapper
        
        if not actionstring:
            actionstring = "g4ds.service." + self._serviceId
        args = {}
        datas = {}
        args['serviceid'] = self._serviceId
        args['destinationmember'] = destinationMember
        args['destinationcommunity'] = destinationCommunity
        args['actionstring'] = actionstring
        datas['message'] = message
        msg = getGenericWrapper().wrapArgsAndDatas('servicemessage', args, datas)
##        print "Sending before cipher:\n%s" %(msg)
        ciphered = self._encryptSession(msg)
        self._sendOne(ciphered)
        
    def disconnect(self):
        """
        Closes down the connection of this client to the service.
        """
        from messagewrapper import getGenericWrapper
        args = {}
        datas = {}
        args['serviceid'] = self._serviceId
        args['disconnect'] = '1'
        msg = getGenericWrapper().wrapArgsAndDatas('servicemessage', args, datas)
        ciphered = self._encryptSession(msg)
        self._sendOne(ciphered)
        

## ###########################################
##
## This is just for testing purposes!
##    
##
    
def callback(msg, metadata):
    print "Received: %s" %(msg)
        
if __name__ == "__main__":
    # for now, let's run a test here
    gs = G4dsService()
    gs.connect('S00001', None, 'private_key', callback = callback)
    
    ch = ''
    while ch != 'q':
        dest = raw_input('Dest Member: ')
        ch = raw_input('Message: ')
        gs.sendMessage(dest, None, ch)
