<?xml version="1.0" encoding="UTF-8"?>
<tcdl>
    <id>C004</id>
    <version>1.0.0.0</version>
    <name>ISRG Test 04</name>
    <creationdate>2005-09-16</creationdate>
    
    <description>
        <fullname>Test Community for G4DS communication evaluation</fullname>
        <organisation>University of Glamorgan</organisation>
        <location>
            <country>
                <code>UK</code>
                <name>United Kingdom</name>
            </country>
            <city>Cardiff</city>
        </location>
    </description>
    
    <communication>
        <protocols>
            <protocol>
                <name>soap</name>
                <comment>SOAP, as implemented for G4DS. Server must listen to incoming messages on function 'newMessage'</comment>
            </protocol>
            <protocol>
                <name>tcpsocket</name>
                <comment>Simple communication over TCP sockets as implemented in G4DS / protcols for TCP sockets</comment>
            </protocol>
        </protocols>
        <algorithms>
            <algorithm>
                <name>rsa</name>
                <comment>RSA, as implemented in G4DS / algorithms</comment>
            </algorithm>
            <algorithm>
                <name>elgamal</name>
                <comment>ElGamal, as implemented in G4DS / algorithms</comment>
            </algorithm>
        </algorithms>
    </communication>
    
    <authorities>
        <authority>
            <memberid>M002</memberid>
            <endpoint>
                <protocol>soap</protocol>
                <address>193.63.129.193:8080</address>
                <credential>
                    <algorithm>rsa</algorithm>
                    <publickey>
                        <![CDATA[3c5374617274507963727970746f4b65793e0a4b456b774d41704f5665636f56514e53553046784143686a51334a35634852764c6c4231596d78705930746c655335535530454b556c4e4262324a7158324d4b6351467663514a396351516f0a5651466c6351564d4e6a55314d7a644d436c5542626e4547544445794e5449334f5463794d6a41774f4445334e7a45344d6a49324d6a49314e6a6b314e7a59784e4451324f4459774e7a63340a4d7a55794d7a51774d7a67794f5445324d7a63784e6a6b354f4449794e7a55334e6a55784d6a45774e544d784f4449314e7a51774e5449344f544d344d6a6b784d6a63344e6a4d794d44637a0a4e6a6b774f5459324e5463354e5445784f4451784e7a4d314e6a4d334d54457a4d7a45314e5463324f4459784e446b344f4449784f5467304e4463344e7a41304d4445314d444d354e6a41770a4f44413554417031596e527842793578414852784153343d0a3c456e64507963727970746f4b65793e0a]]>
                    </publickey>
                </credential>
            </endpoint>
        </authority>
    </authorities>
    
    <routing>
        <gateways>
            <incoming>
                <gateway>
                    <memberid>M002</memberid>
                    <source>
                        <communityid>C002</communityid>
                    </source>
                </gateway>
            </incoming>
            <outgoing>
                <gateway>
                    <memberid>M002</memberid>
                    <destination>
                        <communityid>C002</communityid>
                    </destination>
                </gateway>
            </outgoing>
        </gateways>
    </routing>
    
</tcdl>
