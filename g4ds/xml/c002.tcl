<?xml version="1.0" encoding="UTF-8"?>
<tcdl>
    <id>C002</id>
    <version>1.0.0.0</version>
    <name>ISRG Test 02</name>
    <creationdate>2005-08-10</creationdate>
    
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
            <memberid>M001</memberid>
            <endpoint>
                <protocol>soap</protocol>
                <address>193.63.129.184:8080</address>
                <credential>
                    <algorithm>rsa</algorithm>
                    <publickey>
                        <![CDATA[3c5374617274507963727970746f4b65793e0a4b456b774d41704f5665596f56514e53553046784143686a51334a35634852764c6c4231596d78705930746c655335535530454b556c4e4262324a7158324d4b6351467663514a396351516f0a5651466c6351564d4e6a55314d7a644d436c5542626e45475444637a4d5463794e444d794f4467304e6a4d344d7a41304e4463794d6a417a4f4455354d4463324f444d324e6a67794e7a51320a4d7a51344f5455794f5467314d5467304f5463794f544d314d5455304d5467334e5463314d6a63794f446b354e5463324e6a51304e544d784f4441784e54457a4e54497a4e4445784e6a6b780a4e5451774d5459334f4459314f5445304e6a59774f5449304d7a63784d4455774d6a51304f5459794e4441354d6a55304d6a51774e5441784e5463314e5441314e444d7a4d7a55314d6a55330a4d7a4e4d436e5669644845484c6e4541644845424c673d3d0a3c456e64507963727970746f4b65793e0a]]>
                    </publickey>
                </credential>
            </endpoint>
        </authority>
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
                    <memberid>M001</memberid>
                    <source>
                        <communityid>C001</communityid>
                    </source>
                </gateway>
            </incoming>
            <outgoing>
                <gateway>
                    <memberid>M001</memberid>
                    <destination>
                        <communityid>C001</communityid>
                    </destination>
                </gateway>
            </outgoing>
        </gateways>
    </routing>
    
</tcdl>
