"""
Commonly used functions for G4DS

Grid for Digital Security (G4DS)

@author: Michael Pilgermann
@contact: mailto:mpilgerm@glam.ac.uk
@license: GPL (General Public License)
"""

import random

TYPE_COMMUNITY = 'C'
TYPE_MEMBER = 'M'
TYPE_SERVICE = 'S'
TYPE_MESSAGE = 'Z'
TYPE_ALGORITHM = 'A'
TYPE_PROTOCOL = 'P'
TYPE_CREDENTIAL = 'Q'
TYPE_ENDPOINT = 'E'
TYPE_PERSONALCREDENTIAL = 'X'
TYPE_ROUTINGTABLEENTRY = 'R'

def generateId(type = TYPE_COMMUNITY):
    """
    Generate a unique ID
    
    @todo: Implement unique properly - currently just a random mumber between 0 and 1000000
    """
    return type + str(random.randint(0,1000000))
