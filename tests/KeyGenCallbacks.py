from M2Crypto import  RSA
from wxPython.wx import *
from getpass import getpass
from sys import stdout


class CreateCallback(wxGauge):
    def __init__(self, panel, stepsize = 10, *args):
        self.stepsize = stepsize
        self.gen_value = 0
        wxGauge.__init__(self, panel, -1, self.stepsize)
        self.SetValue(0)
    
    def updateValue(self):
        value = self.gen_value
        self.gen_value = (value+1)%(self.stepsize+1)
        #self.SetValue((value+1)%(self.stepsize+1))
    
    def __call__(self, *args):
        self.updateValue()
        

class CreateCallbackCLI:
    def __init__(self):
        return None
        
    def genparam_callback(self, p, n, out=stdout):
        ch=['.','+','*','\n']
        stdout.write(ch[p])
        stdout.flush()
        
    def __call__(self, *args):
        return self.genparam_callback(*args)
    

class SaveCallbackMessageBox(wxTextEntryDialog):
    def __init__(self, parentWindow, prompt=1,  *args):
        wxTextEntryDialog.__init__(self, parentWindow, "Please enter password for protecting your private key", 
            "Password required", style = wxOK | wxCANCEL | wxCENTRE | wxTE_PASSWORD)
        
    def __call__(self, *args):
        x = self.ShowModal()
        if x != wxID_OK:
            return None
        value1 = self.GetValue()
        self.SetValue("")
        self.SetTitle("Please Confirm")
        y = self.ShowModal()
        value2 = self.GetValue()
        if y != wxID_OK:
            return None
        if value1 == value2:
            return value1
        return None

class SaveCallbackCLI:
    def __init__(self):
        return None

    def passphrase(self, *args):
        p1=getpass("Password: ")
        return p1
    
    def __call__(self, *args):
        return self.passphrase(args)
