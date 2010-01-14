"""
Setup module for G4DS

SnortDB To SoapSy (SnDB2Soapsy)

This module should be started for installation of g4ds as a python site package. This way
it may used used easily with any application afterwards.

@author: Michael Pilgermann
@contact: mailto:mpilgerm@glam.ac.uk
@license: GPL (General Public License)
"""


from distutils.core import setup

version = '0.1'


if __name__ == "__main__":
    global version
    setup (
        name = "sndb2soapsy",
        version = version,
        description = "SnortDB To SoapSy",
        author = "Michael Pilgermann",
        author_email = "mpilgerm@glam.ac.uk",
        url = "http://j4-itrl-12.comp.glam.ac.uk/g4ds/",
        package_dir = {'sndb2soapsy': '.'},
        packages = ["sndb2soapsy"]
        )
