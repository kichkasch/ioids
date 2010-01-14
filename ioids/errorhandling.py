"""
Error handling

Inter-Organisational Intrusion Detection System (IOIDS)

@author: Michael Pilgermann
@contact: mailto:mpilgerm@glam.ac.uk
@license: GPL (General Public License)
"""

class IoidsException(Exception):
    """
    Super class for all IOIDS exceptions.
    """
    
    def __init__(self, message=None):
        """
        Passes the message arguments to the args attribute of the common L{Exception} instance.
        """
        self.args = (message)
        self._message = message
        
    def getMessage(self):
        return self._message
        
        
class IoidsDatabaseException(IoidsException):
    """
    Exception for database problems.
    """
    def __init__(self, message):
        """
        Passes the message to the super constructor.
        """
        IoidsException.__init__(self, message)

class IoidsFormatException(IoidsException):
    """
    Exception for format problems (xml parsing mainly).
    """
    def __init__(self, message):
        """
        Passes the message to the super constructor.
        """
        IoidsException.__init__(self, message)

class IoidsDependencyException(IoidsException):
    """
    Exception for dependency problems .
    """
    def __init__(self, message):
        """
        Passes the message to the super constructor.
        """
        IoidsException.__init__(self, message)

class IoidsDescriptionException(IoidsException):
    """
    Exception for description problems .
    """
    def __init__(self, message):
        """
        Passes the message to the super constructor.
        """
        IoidsException.__init__(self, message)
