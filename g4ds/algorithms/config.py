"""
Configuration file for algorithms for G4DS

Grid for Digital Security (G4DS)

Modules import that module and may read the settings important to them.


@author: Michael Pilgermann
@contact: mailto:mpilgerm@glam.ac.uk
@license: GPL (General Public License)
"""

import rsaalgorithm
import elgamalalgorithm

# The list of algorithms implemented
# 
# In form of a dictionary - key is the name and value the reference to the module
#   the module must contain a class with the name AlgorithmImplementation which
#   must inherit from algorithminterface.AlgorithmInterface
algorithms = {}
algorithms['rsa'] = rsaalgorithm
algorithms['elgamal'] = elgamalalgorithm

default_algorithm = 'rsa'


# Settings for RSA algorithm
rsa_keylength = 512

# Settings for ElGamal algorithm
elgamal_keylength = 512
