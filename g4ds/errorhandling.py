"""
Error handling

Grid for Digital Security (G4DS)

@todo: we need some stuff here for loading the own keys into the database backend.

@author: Michael Pilgermann
@contact: mailto:mpilgerm@glam.ac.uk
@license: GPL (General Public License)
"""

class G4dsException(Exception):
    """
    Super class for all G4ds exceptions.
    """
    
    def __init__(self, message=None):
        """
        Passes the message arguments to the args attribute of the common L{Exception} instance.
        """
        self.args = (message)
        self._message = message
        
    def getMessage(self):
        return self._message
        
class G4dsDependencyException(G4dsException):
    """
    Exception for unresolved dependencies.
    
    E.g. - a community shall be stored but the member descriptions are missing and can not be downloaded.
    """
    def __init__(self, message):
        """
        Passes the message to the super constructor.
        """
        G4dsException.__init__(self, message)

class G4dsCommunicationException(G4dsException):
    """
    Exception for errors occuring during transport of data.
    
    E.g. - unvalid keys (message validation).
    """
    def __init__(self, message):
        """
        Passes the message to the super constructor.
        """
        G4dsException.__init__(self, message)

class G4dsRuntimeException(G4dsException):
    """
    Exception for errors occuring during processing of functions.
    """
    def __init__(self, message):
        """
        Passes the message to the super constructor.
        """
        G4dsException.__init__(self, message)

class G4dsDescriptionException(G4dsException):
    """
    Exception for errors occuring during processing or generating of (xml) descriptions.
    """
    def __init__(self, message):
        """
        Passes the message to the super constructor.
        """
        G4dsException.__init__(self, message)
