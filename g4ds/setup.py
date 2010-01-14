"""
Setup module for G4DS

Grid for Digital Security (G4DS)

This module should be started for installation of g4ds as a python site package. This way
it may used used easily with any application afterwards.

@author: Michael Pilgermann
@contact: mailto:mpilgerm@glam.ac.uk
@license: GPL (General Public License)
"""


from distutils.core import setup
import config

global version
version = config.VERSION


if __name__ == "__main__":
    global version
    setup (
        name = "g4ds",
        version = version,
        description = "grid for digital security - communication platform",
        author = "Michael Pilgermann",
        author_email = "mpilgerm@glam.ac.uk",
        url = "http://j4-itrl-12.comp.glam.ac.uk/g4ds/",
        package_dir = {'g4ds': '.'},
        packages = ["g4ds", "g4ds.algorithms","g4ds.protocols"],
        data_files=[('/etc/init.d', ['thirdparty/g4dsrc']),
            ('/usr/sbin', ['g4dslistener.py']),
            ('/etc', ['g4ds.conf']),
##            (config.POLICY_DIRECTORY, ['policies/default_policy.pol', 'policies/roles.pol'])]
            ('/var/lib/g4ds/policy/', ['policies/default_policy.pol', 'policies/roles.pol'])]
        )
