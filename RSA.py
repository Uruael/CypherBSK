import os
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import random
import AES
import socket
import time
import Port

def shareAES(ip, appState):

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ('127.0.0.1', Port.portRSArec)
    other_address = ('127.0.0.1', Port.portRSAsend)
    s.bind(server_address)
    try:
        # Try to connect to the other client, if this fails then go to except clause
        s.connect(other_address)

    except:
        s.listen(1)
        connection, ClientIp = s.accept()
        recievedPublic = connection.recv(1024)
        rsaPublic = RSA.import_key(recievedPublic)
        aes = os.urandom(16)
        cipherU = PKCS1_OAEP.new(rsaPublic)
        cyphAes = cipherU.encrypt(aes)
        duo = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        duo.bind(('127.0.0.1', 44381))
        time.sleep(1)

        duo.connect(('127.0.0.1', 44386))
        duo.send(cyphAes)
        return aes

    rsaPublic = appState["UI"]["rsaPublic"]
    rsaPrivate = appState["UI"]["rsaPrivate"]
    message = rsaPublic.exportKey()
    s.send(message)


    duo = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    duo.bind(('127.0.0.1', 44386))
    duo.listen(1)
    connection2, ClientIp = duo.accept()
    aes = connection2.recv(1024)
    cipherR = PKCS1_OAEP.new(rsaPrivate)
    aes = cipherR.decrypt(aes)
    return aes


def generateKey(password = b'pppppppppppppppp', length = 2048):
    """
    :param password: password to encrypt file
    :param length: length of key in RSA
    :return: 0 if success
    """
    key = RSA.generate(length)

    fpub = open('publickey.pem', 'wb')
    fpriv = open('privatekey.pem', 'wb')

    fpriv.write(AES.encrypt_bytes(key.export_key('PEM'), None, password, 2)[0])
    fpub.write(AES.encrypt_bytes(key.publickey().exportKey('PEM'), None, password, 2)[0])

    fpriv.close()
    fpub.close()
    return 0


def readKey(keytype, password = b'pppppppppppppppp'):
    """
    :param keytype: 1 -> private, 0 ->public
    :param password: password to encrypt file
    :return: private/public RSA key
    """

    if(keytype == 1):
        fpriv2 = open('privatekey.pem', 'rb')
        temppriv = AES.decrypt_bytes(fpriv2.read(), None, password, 2)
        while (temppriv[len(temppriv) - 1] == 0):
            temppriv = temppriv[:-1]
        return RSA.import_key(temppriv)

    else:
        fpub2 = open('publickey.pem', 'rb')
        temppub = AES.decrypt_bytes(fpub2.read(), None, password, 2)
        while (temppub[len(temppub) - 1] == 0):
            temppub = temppub[:-1]
        return RSA.import_key(temppub)

    return -1

