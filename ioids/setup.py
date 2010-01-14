"""
Setup module for G4DS

Inter-Organisational Intrusion Detection System (IOIDS)

This module should be started for installation of ioids as a python site package. This way
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
        name = "ioids",
        version = version,
        description = "inter-organisational intrusion detection system",
        author = "Michael Pilgermann",
        author_email = "mpilgerm@glam.ac.uk",
        url = "http://j4-itrl-12.comp.glam.ac.uk/g4ds/",
        package_dir = {'ioids': '.'},
        packages = ["ioids", "ioids.support"],
        data_files=[('/etc/init.d', ['thirdparty/soap_db/soap_server/xsmrc']),
            ('/usr/bin', ['thirdparty/soap_db/soap_server/XSM.py']),
	    ('/var/lib/g4ds/policy', ['descriptions/ioids_g4ds_policy.pol']),
            ('/etc', ['thirdparty/soap_db/soap_server/XSM-configuration.xml'])]
        )
