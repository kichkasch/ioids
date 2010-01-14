<?xml version="1.0" encoding="UTF-8"?>
<tcdl>
    <id>C12345</id>
    <version>1.0.0.0</version>
    <name>ISRG Test for home use</name>
    <creationdate>2005-09-01</creationdate>
    
    <description>
        <fullname>Test Community for G4DS communication evaluation - home</fullname>
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
            <memberid>M111</memberid>
            <endpoint>
                <protocol>soap</protocol>
                <address>192.1683.1.120:8080</address>
                <credential>
                    <algorithm>rsa</algorithm>
                    <publickey>
                        <![CDATA[3c5374617274507963727970746f4b65793e0a4b456b774d41704f5665596f56514e53553046784143686a51334a35634852764c6c4231596d78705930746c655335535530454b556c4e4262324a7158324d4b6351467663514a396351516f0a5651466c6351564d4e6a55314d7a644d436c5542626e45475444637a4d5463794e444d794f4467304e6a4d344d7a41304e4463794d6a417a4f4455354d4463324f444d324e6a67794e7a51320a4d7a51344f5455794f5467314d5467304f5463794f544d314d5455304d5467334e5463314d6a63794f446b354e5463324e6a51304e544d784f4441784e54457a4e54497a4e4445784e6a6b780a4e5451774d5459334f4459314f5445304e6a59774f5449304d7a63784d4455774d6a51304f5459794e4441354d6a55304d6a51774e5441784e5463314e5441314e444d7a4d7a55314d6a55330a4d7a4e4d436e5669644845484c6e4541644845424c673d3d0a3c456e64507963727970746f4b65793e0a]]>
                    </publickey>
                </credential>
            </endpoint>
        </authority>
    </authorities>
    
    <routing>
        <gateways>
            <incoming/>
            <outgoing/>
        </gateways>
    </routing>
</tcdl>
