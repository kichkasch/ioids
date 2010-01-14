"""
Package for implementations for algorithms

Grid for Digital Security (G4DS)

Required, to use the modules in this directory as a package.

Currently implemented algorithms:

    - RSA using the ezPyCrypto libs which is based on the PyCrypto libs
    
    - ElGamal using the ezPyCrypto libs which is based on the PyCrypto libs

Whenever a new algorithm shall be added, a new module must be developed. A class 
named AlgorithmImplementation must be provided in there, which inherits from 
L{algorithminterface.AlgorithmInterface} and overwrites the functions defined in
there. Finally, it must be registed inside the config module for algorithms.
    
@author: Michael Pilgermann
@contact: mailto:mpilgerm@glam.ac.uk
@license: GPL (General Public License)
"""
