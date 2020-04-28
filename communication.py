import socket
import UI
import json
import os
import math
import base64

class tcpcon:

    def __init__(self, myip='127.0.0.1'):
        self.ip = myip

    def get_ip(self):
        return self.ip

    def set_ip(self, x):
        self.ip = x

    def reciveText(self):

        server_address = (self.ip, 10000)

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(server_address)
        s.listen(1)
        mess = []
        newflag = True  #sprawdza czy jest to nowa wiadomosc
        control = None  #Wiadomość wzorcowa, do której będą porównywane pozostałe które przyszły
        recivcount = 0

        while True:
            print("wait for connection")
            connection, ClientIp = s.accept()
            try:
                print("connection from:", ClientIp)

                while True:
                    data = connection.recv(1024)
                    print('recived: {!r}'.format(data))

                    if data:
                        message = json.loads(data)

                        if (newflag):   #odebranie pierwszej, nowej wiadomości
                            control = message
                            for i in range(message["parts"]):
                                mess = [None] * control["parts"]
                            newflag = False
                        if (control["type"] == message["type"] and control["parts"] == message["parts"]): #laczenie odbieranej wiadomości jeżeli pasuje do wzorcowej
                            mess[message["part"]] = message["text"]
                            recivcount += 1
                        if (recivcount == control["parts"] and control["type"] == "t"): #odebranie i wypisanie textu
                            print(mess)
                            UI.DisplayText("[Someone:]" + "".join(mess))
                            mess = ""
                            newflag = True
                            control = None
                            recivcount = 0
                        elif (recivcount == control["parts"]): #odebranie i tworzenie pliku
                            print("File")
                            file = open("rec" + control["type"], "wb")
                            filemess = base64.b64decode(("".join(mess)).encode('utf-8'))

                            file.write(filemess)
                            file.close()
                            mess = ""
                            newflag = True
                            control = None
                            recivcount = 0

                    else:
                        print("no data")
                        break;
            finally:
                print("clossing connection")
                connection.close()

    def sendText(self,message):
        print(message)

        mess=[]
        server_address = (self.ip, 10001)
        n =10                               #ile znakow w wiadomosci
        for i in range(0, len(message), n):
            mess.append(message[i:i + n])

        for i in range(len(mess)):
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect(server_address)


            try:

                # Send data

                    data = json.dumps({"type":"t", "text": mess[i], "parts": len(mess), "part": i})
                    print('sending {!r}' + data)
                    sock.send(data.encode())

            finally:
                print('closing socket')
                sock.close()

    def sendFile(self,f):
        server_address = (self.ip, 10001)

        file = open(f,"rb")
        name, ext = os.path.splitext(f)
        sendData=file.read()
        filemess = (base64.b64encode(sendData)).decode('utf-8')
        print(filemess)
        mess = []

        n = 50  # ile znakow w wiadomosci
        for i in range(0, len(filemess), n):
            mess.append(filemess[i:i + n])

        for i in range(len(mess)):
            sock = socket.socket()
            sock.connect(server_address)

            try:
                data = json.dumps({"type": ext, "text": mess[i], "parts": len(mess), "part": i})
                i+=1
                sock.send(data.encode())
            finally:
                sock.close()
