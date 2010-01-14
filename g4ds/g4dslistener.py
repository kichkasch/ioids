#!/usr/bin/env python

"""
Server for G4DS - several services can connect this way.

Grid for Digital Security (G4DS)

@author: Michael Pilgermann
@contact: mailto:mpilgerm@glam.ac.uk
@license: GPL (General Public License)
"""

import os, sys, signal, thread
try:
    # if we are running in daemon mode here, then it will use the modules / packages from
    # the site package installation
##    from g4ds.config import FIFO_PATH_IN, FIFO_PATH_OUT, PATH_PUBLIC_KEYS, DAEMON_MODE
    import g4ds.config as config
    from g4ds.g4ds import G4DS
    from g4ds.errorhandling import G4dsException
    from g4ds.messagewrapper import getGenericWrapper
    from g4ds.algorithmcontroller import getAlgorithmController
    from g4ds.authorisationcontroller import getAuthorisationController
    from g4ds.g4dslogging import getDefaultLogger, SERVICES_CLIENT_SENDINGERROR
    import g4ds.servicerepository as servicerepository 
##    from g4ds.servicerepository import getServiceManager
    from g4ds.messagewrapper import getConnectedServicesWrapper
except ImportError, msg:
    print "ImportError: %s\nLooks like we are not in the system installation paths; let's try importing directly." %(msg)
    # if we run it directly, however, that will course an import error, let's go and import it
    # directly from the current directory
##    from config import FIFO_PATH_IN, FIFO_PATH_OUT, PATH_PUBLIC_KEYS, DAEMON_MODE
    import config
    from g4ds import G4DS
    from errorhandling import G4dsException
    from messagewrapper import getGenericWrapper
    from algorithmcontroller import getAlgorithmController
    from authorisationcontroller import getAuthorisationController
    from g4dslogging import getDefaultLogger, SERVICES_CLIENT_SENDINGERROR
    import servicerepository
##    from servicerepository import getServiceManager
    from messagewrapper import getConnectedServicesWrapper

class G4dsListener:
    """
    Listens to requests from connected services through the G4dsService interface.
    """
    
    def __init__(self):
        """
        Opens the pipe to listen for incoming requests.
        """
        # start up G4DS instance
        self._g4ds = G4DS()
        self._g4ds.startup()
                
##        self.importRemaining()
                
        self._cleanPaths()

        signal.signal(signal.SIGTERM, self.SignalHandler)
        signal.signal(signal.SIGINT, self.SignalHandler)
    
    def listen(self):
        """
        Listen and listen and listen
        """
        import stat
        os.mkfifo(config.FIFO_PATH_IN, 0666)
        os.chmod(config.FIFO_PATH_IN, stat.S_IWOTH | stat.S_IRWXU | stat.S_IWGRP)
        os.mkfifo(config.FIFO_PATH_OUT, 0666)
        os.chmod(config.FIFO_PATH_OUT, stat.S_IROTH | stat.S_IRWXU | stat.S_IRGRP)
        self._majorPipeIn = None
        self._majorPipeOut = None

        self._fifoLock = thread.allocate_lock()
        
        number = 100    # the index number for the filenames of the fifos
        while 1:
            data = ' '
            alldata = ''
            self._majorPipeIn = open(config.FIFO_PATH_IN,'r')  
            self._majorPipeOut = open(config.FIFO_PATH_OUT,'w')
            while data != '':
                data = self._majorPipeIn.read().rstrip()
                alldata += data
            if alldata == 'connect':
                # if a client wants to connect, we just send the number of the fifo to use to him; 
                # this rest will be negotiated the other thread
                self._majorPipeOut.write(str(number))
            thread.start_new_thread(self.startNewService, (self._g4ds, data, number))
            self._majorPipeIn.close()
            self._majorPipeOut.close()
            number += 1


    def shutdown(self):
        self.cleanup()
        self._g4ds.shutdown()
        sys.exit(0)    

    
    def cleanup(self):
        if self._majorPipeIn != None:
          self._majorPipeIn.close()
        if self._majorPipeOut != None:
          self._majorPipeOut.close()
        self._cleanPaths()
          
    def _cleanPaths(self):
        if os.path.exists(config.FIFO_PATH_IN):
          os.unlink(config.FIFO_PATH_IN)
        if os.path.exists(config.FIFO_PATH_OUT):
          os.unlink(config.FIFO_PATH_OUT)

    def SignalHandler(self, sig, id):
        if sig == signal.SIGTERM or sig == signal.SIGINT:
            self.shutdown()            
            
            
    def startNewService(self, g4ds, data, number):
        """
        Handles with all connection from one service.
        """
        sh  =ServiceHandler(self._fifoLock)
        sh.serve(g4ds, data, number)
        
            
class ServiceHandler:
    """
    Responsible to deal with one service.
    """
    
    def __init__(self, fifoLock):
        """
        Yet empty constructor.
        """
        self._globalLock = fifoLock
        
    def _cleanUp(self, number):
        if os.path.exists(config.FIFO_PATH_IN + "." + str(number)):
          os.unlink(config.FIFO_PATH_IN + "." + str(number))
        if os.path.exists(config.FIFO_PATH_OUT + "." + str(number)):
          os.unlink(config.FIFO_PATH_OUT + "." + str(number))        
    
    def _receiveOne(self, multiple = 0):
        self._pipeIn = open(self._name_pipe_in,'r')
        # so, let's read the command from the client then - rendevous
        data = ' '
        alldata = ''
        while data != '':
            data = self._pipeIn.read().rstrip()
            alldata += data
        self._pipeIn.close()
##        return alldata
        if multiple:
            extracted = getConnectedServicesWrapper().parseMessages(alldata)
        else:
            extracted = getConnectedServicesWrapper().parseMessage(alldata)
        return extracted
        
    def _sendOne(self, message):
        self._globalLock.acquire()
        self._pipeOut = open(self._name_pipe_out,'w')
##        self._pipeIn.write(message)
        wrapped = getConnectedServicesWrapper().assembleMessage(message)
        self._pipeOut.write(wrapped)
        self._pipeOut.flush()
        self._pipeOut.close()
        self._globalLock.release()
##        f = open('/tmp/before_enc.txt','a')
##        f.write('================= I wrote %d Bytes  ==============\n' %(len(message)))
##        f.close()
    
    def _loadPublicKeys(self):
        keys = []
        try:
            file = open(config.PATH_PUBLIC_KEYS, 'r')
        except IOError:
            # looks like, the file has not been created yet
            return keys
        onekey = ''
        line = ' '
        while line != '':
            line = file.readline()
            if line != '\n':
                onekey += line
            else:
                keys.append(onekey)
                onekey = ''
        file.close()
        return keys
    
    def _createSessionKey(self):
        """
        Generates a symmetric session key.
        """
##        import ezPyCrypto
##        key = SSLCrypto.key(512, None, 'Blowfish')
        import SSLCrypto
        key = SSLCrypto.key(512, None, 'Blowfish')
        return key.exportKeyPrivate()
    
    def serve(self, g4ds, data, number):
        """
        Serves one cconnected service.
        """
        self._g4ds = g4ds
        
        # let's try to delete first - we never know; maybe somebody hasn't cleant up properly before - somebody?? heheh :)
        self._cleanUp(number)
        
        self._name_pipe_in = config.FIFO_PATH_IN + "." + str(number)
        self._name_pipe_out = config.FIFO_PATH_OUT + "." + str(number)
        
        import stat
        os.mkfifo(self._name_pipe_in, 0666)
        os.chmod(self._name_pipe_in, stat.S_IWOTH | stat.S_IRWXU | stat.S_IWGRP)
        os.mkfifo(self._name_pipe_out, 0666)
        os.chmod(self._name_pipe_out, stat.S_IROTH | stat.S_IRWXU | stat.S_IRGRP)

        try:
            message = self._receiveOne()
            
            args, datas = getGenericWrapper().unwrapArgsAndDatas('rendevous', message)
            serviceid = args['serviceid']
            
            plain = datas['plain']
            signature = datas['signature']
            
            # check first of all, whether we know the service
            try:
                servicerepository.getServiceManager().getService(serviceid)
            except KeyError, msg:
                args = {}
                args['sucess'] = '0'
                args['errormessage'] = 'Service id unknown on this node - service could not be loaded. You might have to apply service description to G4DS.'
                message = getGenericWrapper().wrapArgsAndDatas('rendevous',args, {})
                self._sendOne(message)
                return
            
            sucess = 0
            keys = self._loadPublicKeys()
            rsa = getAlgorithmController().getAlgorithm('rsa')
            usedKey = None
            for key in keys:
                if rsa.validate(plain, signature, key):
                    sucess = 1
                    usedKey = key
                    break
            
            args = {}
            datas = {}
            if sucess:
                args['sucess'] = '1'
                sessionkey = self._createSessionKey()
                # encrypt the session key with the public key of the application
                cipheredSessionKey = rsa.encrypt(sessionkey, usedKey)
                self._sessionkey = sessionkey
                datas['sessionkey'] = cipheredSessionKey
                message = getGenericWrapper().wrapArgsAndDatas('rendevous',args, datas)
                self._sendOne(message)
                try:
                    self._g4ds.registerClient(serviceid, self.g4dsCallBack)
                except G4dsException, msg:
                    args['sucess'] = '0'
                    args['errormesssage'] = str(list(msg))
                    message = getGenericWrapper().wrapArgsAndDatas('rendevous',args, {})
                    self._sendOne(message)                
                
                self.listen()
            else:
                args['sucess'] = '0'
                message = getGenericWrapper().wrapArgsAndDatas('rendevous',args, {})
                self._sendOne(message)
                                        
        except IOError, msg:
            # looks like, the client changed his mind and did not connect
            # let's clean up then
            self._cleanUp(number)
            #print "error %s" %(msg)
            return
            
        
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
##        f = open('/tmp/before_enc.txt','a')
##        f.write('%s %d | %d %s\n%s' %('*' * 50, len(msg), len(ciphered), '*' * 30, msg))
##        f.close()
        return ciphered
        
    def _decryptSession(self, ciphered):
        """
        Decrypts a message with the session key.
        """
        from SSLCrypto import key
##        from ezPyCrypto import key
        k = key()
        k.importKey(self._sessionkey)
        msg = k.decString(ciphered)
        return msg
##        import binascii as hex
##        decoded = hex.unhexlify(msg)
##        return decoded
        
    def g4dsCallBack(self, msg, senderid, serviceid, communityid, messageid):
        """
        Callback function; to be passed to the g4ds module. Each receiving message for this application
        will be passed to this function by the g4ds system.
        """
##        from messagewrapper import getGenericWrapper
        args, datas = getGenericWrapper().unwrapArgsAndDatas('serviceargs', msg)
        actionstring = args['actionstring']
        if not getAuthorisationController().validate(senderid, serviceid, actionstring):
            return
        msg = datas['message']

        metadata = {}
        metadata['senderid'] = senderid
        metadata['serviceid'] = serviceid
        metadata['communityid'] = communityid
        metadata['messageid'] = messageid
        metadata['actionstring'] = actionstring
        
        wrapped = getGenericWrapper().wrapArgsAndDatas('servicemetadata', metadata, datas)
        
##        ciphered = self._encryptSession(msg)        
        ciphered = self._encryptSession(wrapped)        
        self._sendOne(ciphered)
        
    def listen(self):
        """
        Listen for messages on the fifo. Once, a message arrives, pass it on to the g4ds system.
        """
        while 1:
            messages = self._receiveOne(multiple = 1)
            for message in messages:
                message = self._decryptSession(message)
                
    ##            from messagewrapper import getGenericWrapper
                args, datas = getGenericWrapper().unwrapArgsAndDatas('servicemessage', message)
                
                serviceid = args['serviceid']
    
                if args.has_key('disconnect'):
                    if int(args['disconnect']):
                        self._g4ds.unregisterClient(serviceid)
                        break
                
                destinationMember = args['destinationmember']
                destinationCommunity = args['destinationcommunity']
                actionstring = args['actionstring']
                message = datas['message']
                
                # we add one more wrapping here in order to put some data for the service
    ##            from messagewrapper import getGenericWrapper
                args = {}
                datas = {}
                args['actionstring'] = actionstring
                datas['message'] = message
                message = getGenericWrapper().wrapArgsAndDatas('serviceargs', args, datas)
                
                
                try:
                    self._g4ds.newMessage(serviceid, destinationMember, destinationCommunity, message)
                except G4dsException, msg:
                    getDefaultLogger().newMessage(SERVICES_CLIENT_SENDINGERROR, 'Could not send message for service %s: %s' %(serviceid, msg))
            
            
class DummyOut:
    def __init__(self, out):
        self._out = out

    def write(self, msg):
        #self._out.write(msg)
        pass
        
    def flush(self):
        pass
            
if __name__ == "__main__":

    import os, sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == '-d':     # daemon mode
            daemon_mode = 1
        elif sys.argv[1] == '-D':   # no daemon mode
            daemon_mode = 0
    else:
        daemon_mode = config.DAEMON_MODE
    
    if daemon_mode:
        try:
            pid = os.fork()
            if pid:
                os._exit(0) # kill original
        except OSError, msg:
            print "Could not start g4ds listener as deamon. Error: %s" %msg
            sys.exit(1)
        
        sys.stdout = DummyOut(sys.stdout)
        sys.stderr = DummyOut(sys.stdout)
        
    l = G4dsListener()
    l.listen()
