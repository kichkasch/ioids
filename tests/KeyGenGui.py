from wxPython.wx import *
from KeyGenCallbacks import *
from KeyGenCore import KeyGen
from thread import *

ID_B_CREATE = 101
ID_B_SAVE = 102
ID_B_FOLDER = 103
ID_B_TRANSFER = 103
TIMER_ID = 501
CIPHER_ID = 601

ST_NO_SAVECIPHER = "-- N.A. --"
ST_DEFAULT_FILE = "./key.pem"

DIM_NO_CALLBACK = wxSize(400,500)
DIM_CALLBACK = wxSize(400,600)

# whenever an application is using one of the GUI classes in here it should
# implement a class inheriting from GuiCallback in order to provide
# information, how to decorate the window and how to return the key to the
# application
class GuiCallback:
    def __init__(self):
        pass
    def getAppName(self):
        return "App"
    def passKeyToApp(self, cipher, key):
        pass

# Frame for Creating a Key
#
# this class is not an application; the application has to be created before 
# using an object of this class
class KeyCreator(wx.wxFrame):
    def __init__(self, parent, ID, title, guicallback = None):
        if guicallback:
            dim = DIM_CALLBACK
        else:
            dim = DIM_NO_CALLBACK
        wxFrame.__init__(self, parent, ID, title,
                         wxDefaultPosition, dim)

        self.guicallback = guicallback
                         
        self.keyGen = KeyGen()
        self.key = None
        self.usedCipher = None
        

        panel_outer = wxPanel(self, -1)
        
        panel_options = wxPanel(panel_outer, -1, style = wxSIMPLE_BORDER)
        lCipher = wxStaticText(panel_options, -1, "Choose your Cipher")
        ciphers = self.keyGen.getAvailableCiphers()
        self.cipher = wxChoice(panel_options, CIPHER_ID, size = (150, -1), choices = ciphers)
        lLength = wxStaticText(panel_options, -1, "Choose your Key Length")
        lengths = self.keyGen.getAvaiableBitLengths(self.keyGen.getAvailableCiphers()[0])
        self.bits = wxChoice(panel_options, -1, size = (150, -1), choices = lengths)
        
        panel_fill1 = wxPanel(panel_options, -1)
        panel_fill2 = wxPanel(panel_options, -1)
        panel_fill3 = wxPanel(panel_options, -1)
        boxOp = wxBoxSizer(wxVERTICAL)
        boxOp.Add(panel_fill1, 1, wxEXPAND)
        boxOp.Add(lCipher, 2, wxALIGN_CENTER)
        boxOp.Add(self.cipher, 2, wxALIGN_CENTER)
        boxOp.Add(panel_fill2, 2, wxEXPAND)
        boxOp.Add(lLength, 2, wxALIGN_CENTER)
        boxOp.Add(self.bits, 2, wxALIGN_CENTER)
        boxOp.Add(panel_fill3, 2, wxEXPAND)
        panel_options.SetAutoLayout(True)
        panel_options.SetSizer(boxOp)
        panel_options.Layout()
        

        panel_progress = wxPanel(panel_outer, -1)
        self.progress = CreateCallback(panel_progress, 50)
        self.bCreate = wxButton(panel_progress, ID_B_CREATE, "Generate")
        panel_fill1 = wxPanel(panel_progress, -1)
        panel_fill2 = wxPanel(panel_progress, -1)
        panel_fill3 = wxPanel(panel_progress, -1)
        boxP = wxBoxSizer(wxHORIZONTAL)
        boxP.Add(panel_fill1, 1, wxEXPAND)
        boxP.Add(self.progress, 10, wxEXPAND)
        boxP.Add(panel_fill2, 1, wxEXPAND)
        boxP.Add(self.bCreate, 3, wxEXPAND)
        boxP.Add(panel_fill3, 1, wxEXPAND)
        panel_progress.SetAutoLayout(True)
        panel_progress.SetSizer(boxP)
        panel_progress.Layout()
        

        self.panel_save = wxPanel(panel_outer, -1, style = wxSIMPLE_BORDER)
        self.panel_save.Enable(false)
        lSaveCipher = wxStaticText(self.panel_save, -1, "Choose Cipher to protect you private key")
        saveCiphers = self.keyGen.getAvailableSaveCiphers(self.keyGen.getAvailableCiphers()[0])
        self.saveCiphers = wxChoice(self.panel_save, -1, size = (150, -1), choices = saveCiphers)
        lFolder = wxStaticText(self.panel_save, -1, "Specify Filename for Key")
        
        panel_save1 = wxPanel(self.panel_save, -1)
        panel_fill1 = wxPanel(panel_save1, -1)
        panel_fill2 = wxPanel(panel_save1, -1)
        panel_fill3 = wxPanel(panel_save1, -1)
        self.tcFolder = wxTextCtrl(panel_save1, -1, ST_DEFAULT_FILE)
        self.tcFolder.SetEditable(false)
        self.bFolder = wxButton(panel_save1, ID_B_FOLDER, "Change")
        boxS1 = wxBoxSizer(wxHORIZONTAL)
        boxS1.Add(panel_fill1, 1, wxEXPAND)
        boxS1.Add(self.tcFolder, 10, wxALIGN_CENTER)
        boxS1.Add(panel_fill2, 1, wxEXPAND)
        boxS1.Add(self.bFolder, 3, wxEXPAND)
        boxS1.Add(panel_fill3, 1, wxEXPAND)
        panel_save1.SetAutoLayout(True)
        panel_save1.SetSizer(boxS1)
        panel_save1.Layout()

        panel_save2 = wxPanel(self.panel_save, -1)
        panel_fill1 = wxPanel(panel_save2, -1)
        panel_fill2 = wxPanel(panel_save2, -1)
        panel_fill3 = wxPanel(panel_save2, -1)
        self.cbPassword = wxCheckBox(panel_save2, -1, "Store key encrypted")
        self.cbPassword.SetValue(1)
        self.bCreate = wxButton(panel_save2, ID_B_SAVE, "Save")
        boxS2 = wxBoxSizer(wxHORIZONTAL)
        boxS2.Add(panel_fill1, 1, wxEXPAND)
        boxS2.Add(self.cbPassword, 10, wxALIGN_CENTER)
        boxS2.Add(panel_fill2, 1, wxEXPAND)
        boxS2.Add(self.bCreate, 3, wxEXPAND)
        boxS2.Add(panel_fill3, 1, wxEXPAND)
        panel_save2.SetAutoLayout(True)
        panel_save2.SetSizer(boxS2)
        panel_save2.Layout()
       
        
        panel_fill1 = wxPanel(self.panel_save, -1)
        panel_fill2 = wxPanel(self.panel_save, -1)
        panel_fill3 = wxPanel(self.panel_save, -1)
        panel_fill4 = wxPanel(self.panel_save, -1)
        panel_fill5 = wxPanel(self.panel_save, -1)
        boxS = wxBoxSizer(wxVERTICAL)
        boxS.Add(panel_fill1, 1, wxEXPAND)
        boxS.Add(lSaveCipher, 2, wxALIGN_CENTER)
        boxS.Add(self.saveCiphers, 3, wxALIGN_CENTER)
        boxS.Add(panel_fill2, 2, wxEXPAND)
        boxS.Add(lFolder, 2, wxALIGN_CENTER)
##        boxS.Add(panel_fill3, 1, wxEXPAND)
        boxS.Add(panel_save1, 3, wxEXPAND)
        boxS.Add(panel_fill4, 2, wxEXPAND)
        boxS.Add(panel_save2, 3, wxEXPAND)
        boxS.Add(panel_fill5, 1, wxEXPAND)
        self.panel_save.SetAutoLayout(True)
        self.panel_save.SetSizer(boxS)
        self.panel_save.Layout()

        # ############################################################
        # this stuff all for the gui callback - passing the key to the application
        #
        if guicallback:
            self.panel_callback = wxPanel(panel_outer, -1)
            panel_fill1 = wxPanel(self.panel_callback, -1)
            panel_fill2 = wxPanel(self.panel_callback, -1)
            panel_fill3 = wxPanel(self.panel_callback, -1)
            print guicallback.getAppName()
            lCallback = wxStaticText(self.panel_callback, -1, "Use this key in <" + guicallback.getAppName() + ">")
            self.bTransfer = wxButton(self.panel_callback, ID_B_TRANSFER, "Transfer")
            boxCB = wxBoxSizer(wxHORIZONTAL)
            boxCB.Add(panel_fill1, 1, wxEXPAND)
            boxCB.Add(lCallback, 10, wxALIGN_CENTER)
            boxCB.Add(panel_fill2, 1, wxEXPAND)
            boxCB.Add(self.bTransfer, 3, wxEXPAND)
            boxCB.Add(panel_fill3, 1, wxEXPAND)
            self.panel_callback.SetAutoLayout(True)
            self.panel_callback.SetSizer(boxCB)
            self.panel_callback.Layout()
        # end of creating callback stuff
        # ############################################################

        panel_fill1 = wxPanel(panel_outer, -1)
        panel_fill2 = wxPanel(panel_outer, -1)
        panel_fill3 = wxPanel(panel_outer, -1)
        panel_fill4 = wxPanel(panel_outer, -1)
        panel_fill5 = wxPanel(panel_outer, -1)
        
        box = wxBoxSizer(wxVERTICAL)
        box.Add(panel_fill1, 1, wxEXPAND)
        box.Add(panel_options, 6, wxEXPAND)
        box.Add(panel_fill2, 1, wxEXPAND)
        box.Add(panel_progress, 1, wxEXPAND)
        box.Add(panel_fill3, 1, wxEXPAND)
        box.Add(self.panel_save, 6, wxEXPAND)
        box.Add(panel_fill4, 1, wxEXPAND)
        if guicallback:
            box.Add(self.panel_callback, 1, wxEXPAND)
            box.Add(panel_fill5, 1, wxEXPAND)

        panel_outer.SetAutoLayout(True)
        panel_outer.SetSizer(box)
        panel_outer.Layout()

        pFill1 = wxPanel(self, -1)
        pFill2 = wxPanel(self, -1)
        boxo = wxBoxSizer(wxHORIZONTAL)
        boxo.Add(pFill1, 1, wxEXPAND)
        boxo.Add(panel_outer, 12, wxEXPAND)
        boxo.Add(pFill2, 1, wxEXPAND)


        self.SetAutoLayout(True)
        self.SetSizer(boxo)
        self.Layout()
        
        self.mytimer = wxTimer(self, TIMER_ID)

        EVT_BUTTON(self, ID_B_CREATE, self.startCreate)
        EVT_BUTTON(self, ID_B_SAVE, self.startSave)
        EVT_BUTTON(self, ID_B_FOLDER, self.changeFolder)
        EVT_TIMER(self, TIMER_ID, self.updateControls)
        EVT_CHOICE(self, CIPHER_ID, self.cipherChanged)

    def updateControls(self, event):
        self.progress.SetValue(self.progress.gen_value)
        self.Refresh()
    
    def cipherChanged(self, event):
        while self.bits.GetCount() > 0:
            self.bits.Delete(0)
        lengths = self.keyGen.getAvaiableBitLengths(self.cipher.GetStringSelection())
        for bit in lengths:
            self.bits.Append(bit)
        self.bits.SetSelection(0)
    
    def updateSaveCiphers(self, cipher = None):
        if cipher == None:
            cipher = self.cipher.GetStringSelection()
        save_ciphers = self.keyGen.getAvailableSaveCiphers(cipher)
        while self.saveCiphers.GetCount() > 0:
            self.saveCiphers.Delete(0)
        if save_ciphers == None:
            self.saveCiphers.Append(ST_NO_SAVECIPHER)
            self.saveCiphers.Enable(0)
        else:
            for sCipher in save_ciphers:
                self.saveCiphers.Append(sCipher)
            self.saveCiphers.Enable(1)
        self.saveCiphers.SetSelection(0)

    def startCreate(self, event):
        cipher = self.cipher.GetStringSelection()
        bits = int(self.bits.GetStringSelection())
        self.usedCipher = self.cipher.GetStringSelection()
        self.updateSaveCiphers()
        self.mytimer.Start(500)
        self.panel_save.Enable(false)
        self.bCreate.Enable(false)
        start_new_thread(self.keyGen.createKey, (cipher, bits, self.progress, self))
        
    def finishedGeneration(self, key, success = 1):
        self.progress.SetValue(self.progress.GetRange())
        self.key = key
        self.panel_save.Enable(true)
        self.bCreate.Enable(true)
        self.mytimer.Stop()
        print key

    def changeFolder(self, event):
        currentFile = self.tcFolder.GetValue()
        dialog = wxFileDialog(self, "Choose file for key", wildcard = "*.pem", style = wxSAVE)
        ret = dialog.ShowModal()
        if ret == wxID_OK:
            value = dialog.GetPath()
            self.tcFolder.SetValue(value)
        
    def startSave(self, event):
        filename = self.tcFolder.GetValue()
        saveCipher = self.saveCiphers.GetStringSelection()
        sel = self.cbPassword.GetValue()
        if saveCipher == ST_NO_SAVECIPHER or sel == 0:
            saveCipher = None
        self.keyGen.saveKey(self.usedCipher, filename, self.key, SaveCallbackMessageBox(self), saveCipher, 1, self)
        
    def finishedSaving(self, success = 1):
        if success:
            text = "Key was saved sucessfully."
            styles = wxOK | wxICON_INFORMATION
        else:
            text = "A problem occured whilst saving the key."
            styles = wxOK | wxICON_ERROR
        dialog = wxMessageDialog(self, text, "Save key", style = styles)
        dialog.ShowModal()

        
        
class KeyLoader(wx.wxFrame):
    def __init__(self, parent, ID, title):
        wxFrame.__init__(self, parent, ID, title,
                         wxDefaultPosition, wxSize(400, 500))

        self.keyGen = KeyGen()
        self.key = None

        panel_outer = wxPanel(self, -1)
        
        
        
        pFill1 = wxPanel(self, -1)
        pFill2 = wxPanel(self, -1)
        boxo = wxBoxSizer(wxHORIZONTAL)
        boxo.Add(pFill1, 1, wxEXPAND)
        boxo.Add(panel_outer, 12, wxEXPAND)
        boxo.Add(pFill2, 1, wxEXPAND)


        self.SetAutoLayout(True)
        self.SetSizer(boxo)
        self.Layout()
