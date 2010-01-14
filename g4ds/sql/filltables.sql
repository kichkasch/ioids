-- Some dummy data for g4ds
--
-- Grid for Digital Security (G4DS)
-- Michael Pilgermann
-- mpilgerm@glam.ac.uk
--
-- Note: This script should NOT be used for a real use of G4DS; is was created
-- for testing purposes.
--
-- The data in here cannot be processed with G4DS anymore since there are some encoding procedures in place
-- in order to allow storing of all kinds of data. (mainly the descriptions - they are saved hex encoded now)

insert into communities values ('C10001','Community A', 'test tc - no real data', '<?xml version="1.0"><tcdl> here soon - comm A</tcdl>','1.0.0','2005-06-28');
insert into communities values ('C10002','Community B', 'test tc - no real data', '<?xml version="1.0"><tcdl> here soon - comm B</tcdl>','1.0.0','2005-06-28');
insert into communities values ('C10003','Community C', 'test tc - no real data', '<?xml version="1.0"><tcdl> here soon - comm C</tcdl>','1.0.0','2005-06-28');

insert into members values ('M10001', 'Member A', '<?xml version="1.0"?><mdl> here soon - Member A</mdl>','1.0.0','2005-06-28');
insert into members values ('M10002', 'Member B', '<?xml version="1.0"?><mdl> here soon - Member B</mdl>','1.0.0','2005-06-28');
insert into members values ('M10003', 'Member C', '<?xml version="1.0"?><mdl> here soon - Member C</mdl>','1.0.0','2005-06-28');

insert into communities_members values('M10001', 'C10001');
insert into communities_members values('M10002', 'C10001');
insert into communities_members values('M10001', 'C10002');
insert into communities_members values('M10003', 'C10002');
insert into communities_members values('M10003', 'C10003');

insert into gateways values ('M10001', 'C10001', 'C10002');
insert into gateways values ('M10001', 'C10002', 'C10001');
insert into gateways values ('M10003', 'C10002', 'C10003');

insert into communities_authorities values('M10001', 'C10001');
insert into communities_authorities values('M10001', 'C10002');
insert into communities_authorities values('M10003', 'C10002');
insert into communities_authorities values('M10003', 'C10003');
insert into communities_authorities values('M10002', 'C10001');

insert into algorithms values('A10001', 'DSA TEST');
insert into algorithms values('A10002', 'RSA TEST');
-- create a new credential (q10001) with the algorithm DSA and the public keys (starting with ssh-dss) - valid for the member M10001 - Member A
insert into credentials values('Q10001','A10001','mpilgerm','ssh-dss AAAAB3NzaC1kc3MAAAEBAJpRydx0MMg3wHwRN5J9U/VV5KkjsX6ywDHkTnNMOiJzSifFf3xA3QK5PvYgt3oE+4FymIhbOgrSNsPmjmU5CRd6YvcHq1uRoYZO1pdFYDSIqc4dE0lTPbOblvFfFG4w1zjTurUR33HTGbjx4c0z9WZwv2kg0pXLUyuhtQGKE8WLlo9Qlc4c9NMmGl7+JUA0vNHN93MdqSxO5imbhi3pEom9evjiPwRK9ej9wlayIbvMjetqh5hIsDDaG+S/aN/pRr3VPhyHPUHBin5laUNnT8rW0Crbn3RqYSB5kBTEjiSrn8JfJ83+1s6afa/RyBBMlRK9hRmu9WUAjqBFUkRJvDkAAAAVAIbSuoKB+A/UUN6bYxoxbIIwbaFbAAABAA4+6ScD943cHpegZrEa7zlBSQ1i4irBV8v2iGoOxX1YHaV7gUV8/cYeODodsWGYoVVmMZB0hfkO+HWficQVwdteG9Sz+ZjLESDcXneqxjJjkTj6UPQKX1kpnw2rTpPU66A8Z/EGPGE6eE8XRGbIBOfXZ9VNwCVDj1ooQPRbh2HBuS1cICTZe7nCofOOOk8G+mD8SILO5XhK5gTmzI6OIepFR6eV6Vv9sceqdw0QIya++gx8SXLl9RHAusoEHLJmvuiqxZ4slz7JRcNvm61blN7b1YqZX+X+BAM/iMahwYVxo9VkfH065N/hT/uNboBXIwASAX23cyCv0GZAfP2AL3sAAAEAeBUDpWqQRa5BPGcILMo9bGh8qLUycIM5ZTcfbXifgB6ZMpeAtfEDWHhrVBdbZX1suv9BOOZ58l2/PG1NIR8ESagF7yg+KA1oUMVgrqCgLkXsOFpaCPwkNuOjwyUzGmD5vzj/OqJrMRZvJUFmOJqWVbi8qIJUhQ7jP9Xy9PMT59bGlrPN6TYF1evmRwzHeDd1+LaiC5htKFZxCKc//NICW/qKtFsA/Pn7WuBRiKb68SnAXwkyUJdmAuaW3405mQT8qDl/KYuk3ARLVdFame19LlSdEghXaFpq0Q2ZhBzJacARhL7aiMmdudr1vXHfosaWzVaYYORJmSzFzELF7dTEqQ== michael@home.linux','M10001');
insert into protocols values('P10001', 'SOAP');
insert into protocols values('P10002', 'HTTP');
insert into protocols values('P10003', 'SSH');
insert into endpoints values('E10001', 'M10001', 'C10001', 'P10001', 'http://api.comp.glam.ac.uk/isrg/g4ds', 'Q10001');

insert into communities_protocols values ('C10001', 'P10001'); -- Comm A understands SOAP
insert into communities_protocols values ('C10002', 'P10001'); -- Comm B understands SOAP
insert into communities_protocols values ('C10002', 'P10001'); --    and understands SSH

insert into personalcredentials values('X10001', 'DSA Key Pair - 512 bit', 'A10001', '-----BEGIN DSA PRIVATE KEY-----MIH3AgEAAkEAjsHLUjEoWIRL/8A1XBI+iS9+2/pH2zCDd6+4yoCM85MEvdqafeEcox5F8+qQv62DWqPNk8iGtAspQL/+K1mZtQIVAL1gCRp1qiEurvS0jV5jgfSHpRwjAkA2Ot9KL6fxQa3G9A0OtizrQ6mmYZl6ivVVBEZWFp6d8rMZCz7NAVoBe0mXJ7glK29Pb+KcxEc21+rEsSZqsUPpAkBox7SijwUF35IlsLRFpOOeAm1PFLrvZOUL7rgqxkSkUhFbVHJ+Ns9f6blCoEs0PChOnwSSveC+GHEVRQKzAAL2AhQ4amU63B2Xrpj1rFLNxbkA1cGhGw==-----END DSA PRIVATE KEY-----', 'ssh-dss AAAAB3NzaC1kc3MAAABBAI7By1IxKFiES//ANVwSPokvftv6R9swg3evuMqAjPOTBL3amn3hHKMeRfPqkL+tg1qjzZPIhrQLKUC//itZmbUAAAAVAL1gCRp1qiEurvS0jV5jgfSHpRwjAAAAQDY630ovp/FBrcb0DQ62LOtDqaZhmXqK9VUERlYWnp3ysxkLPs0BWgF7SZcnuCUrb09v4pzERzbX6sSxJmqxQ+kAAABAaMe0oo8FBd+SJbC0RaTjngJtTxS672TlC+64KsZEpFIRW1RyfjbPX+m5QqBLNDwoTp8Ekr3gvhhxFUUCswAC9g== michael@j130-mp','');
insert into personalcredentials values('X10002', 'RSA Key Pair - 512 bit', 'A10002', '-----BEGIN RSA PRIVATE KEY-----MIIBOAIBAAJBAN9Uy9UnDySkRn041/ojX4X4onKWfsYpegOGbWb/Js1qS6A03+MEsDLnDFdE+2nUb1xHhY3fqGvAyjodCaAqhIsCASMCQQDMMEVVKwaH5qbY44Oi3oM4qM8JrirDziZpn3n3xLXDHaVrf6CF23u5L3qVKoN6VZkWZpmqhvlmvh8374aPLLOLAiEA+hO5KkRQnn4xGDgv4GPO05vlxbFBC23Wdk7XVJi6PDsCIQDknugeDEwCYioGC+6bODf8T+GHyhr8NYphxhe52tdj8QIgDkpFGFus1dtTQzZpIsPf7tW1W8D8Zw2XOfXgazvtYocCIHwbv9XMKUMfWKQyXPUtJbTa6CUkkk5mNS3DTrVZit57AiBPAcEYAzqd+OOAaGV5CEkflD7nwPY4ZDTFpqZlGGIadw==-----END RSA PRIVATE KEY-----', 'ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAEEA31TL1ScPJKRGfTjX+iNfhfiicpZ+xil6A4ZtZv8mzWpLoDTf4wSwMucMV0T7adRvXEeFjd+oa8DKOh0JoCqEiw== michael@j130-mp', '');

insert into services values('S10001','IOIDS Inter Organisational Intrusion Detection','<ksdl>Knowledge Service Description here</ksdl>','0.0.1','2005-06-23');
insert into services_communities values('S10001','C10001');
insert into services_members values('S10001','M10003');
insert into services_authorities values('S10001','M10003');
