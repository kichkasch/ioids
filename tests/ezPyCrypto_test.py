
import ezPyCrypto

key = ezPyCrypto.key(512,'RSA')
print key.exportKeyPrivate()
print key.exportKey()

