#!/usr/bin/python

from M2Crypto import SSL
from M2Crypto import RSA
from wxPython.wx import *
from KeyGenCallbacks import SaveCallbackCLI
from KeyGenCallbacks import CreateCallbackCLI
from KeyGenGui import GuiCallback
from KeyGenGui import KeyCreator
import KeyGenCore

def cliGen():
    exp = 65537
    ##key = RSA.gen_key(2048, exp, CreateCallbackCLI().genparam_callback)
    key = RSA.gen_key(2048, exp, CreateCallbackCLI())
    print key
    key.save_key('/tmp/key.pem','aes_128_cbc', SaveCallbackCLI())
    print "ok"


class guiApp(wxApp):
    def OnInit(self):
        frame = KeyCreator(NULL, -1, "Key Creator", GuiCallback())
        frame.Show(true)
        self.SetTopWindow(frame)
        return TRUE
    
def guiGen():
    app = guiApp()
    app.MainLoop()
    

def cliLoad():
    filename = raw_input("Filename of key file: ")
    keyGen = KeyGenCore.KeyGen()
    key, cipher = keyGen.loadKey(filename, SaveCallbackCLI(), 'RSA')
    print key, cipher

    
    
guiGen()
##cliLoad()
