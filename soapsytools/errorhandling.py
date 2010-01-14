"""
Error handling

Tools for SoapSy

@author: Michael Pilgermann
@contact: mailto:mpilgerm@glam.ac.uk
@license: GPL (General Public License)
"""

class SoapsyToolsException(Exception):
    """
    Super class for all SoapSy tools exceptions.
    """
    
    def __init__(self, message=None):
        """
        Passes the message arguments to the args attribute of the common L{Exception} instance.
        """
        self.args = (message)
        self._message = message
        
    def getMessage(self):
        return self._message

class SoapsyToolsDependencyException(SoapsyToolsException):
    """
    Exception for dependency problems .
    """
    def __init__(self, message):
        """
        Passes the message to the super constructor.
        """
        SoapsyToolsException.__init__(self, message)
        
class SoapsyToolsFormatException(SoapsyToolsException):
    """
    Exception for format problems (xml parsing mainly).
    """
    def __init__(self, message):
        """
        Passes the message to the super constructor.
        """
        SoapsyToolsException.__init__(self, message)        
