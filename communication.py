import socket
import UI
import json
import os
import math
import base64
import AES
import Port
import time

portrec = Port.portrec
portsend = Port.portsend

class tcpcon:

	def __init__(self, myip='127.0.0.1'):
		self.ip = myip

	def get_ip(self):
		return self.ip

	def set_ip(self, x):
		self.ip = x

	def reciveText(self):

		server_address = (self.ip, portsend)

		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.bind(server_address)
		s.listen(1)
		mess = []
		tempfin = b''
		newflag = True
		control = None
		recivcount = 0

		tempflag = False

		while True:
			print("wait for connection")
			connection, ClientIp = s.accept()
			try:
				print("connection from:", ClientIp)

				while True:
					data = connection.recv(4096)
					print('recived: {!r}'.format(data))

					if data:
						tempfin = tempfin + data

					else:

						temp = tempfin.split(b"}{")

						for sdata in temp:

							if (sdata[0] != ord('{')):
								sdata = b'{' + sdata
							if (sdata[-1] != ord('}')):
								sdata = sdata + b'}'

							# print('sdata')
							print(sdata)
							message = json.loads(sdata)

							if newflag:
								control = message
								for i in range(message["parts"]):
									mess = [None] * control["parts"]
								newflag = False
							if (control["type"] == message["type"] and control["parts"] == message["parts"]):
								mess[message["part"]] = message["text"]
								recivcount += 1
							if (recivcount == control["parts"] and control["type"] == "t"):
								# Turn base64 to bytes
								mess = base64.b64decode("".join(mess))
								# Decode the message
								# mess = AES.decrypt_bytes(bytes("".join(mess), encoding='utf-8'))
								mess = AES.decrypt_bytes(mess, AES.AES_GetCipher(None, control["cipher"]))
								# And turn it into text
								mess = mess.decode("utf-8")

								print(mess)
								UI.DisplayText("[Someone:]" + "".join(mess))
								mess = ""
								newflag = True
								control = None
								recivcount = 0
								tempflag = True
							elif (recivcount == control["parts"]):
								print("File")
								file = open("rec" + control["type"], "wb")
								filemess = base64.b64decode("".join(mess))

								# Decode the message

								filemess = AES.decrypt_bytes(filemess, AES.AES_GetCipher(None, control["cipher"]))

								while (filemess[len(filemess) - 1] == 0):
									filemess = filemess[:-1]

								file.write(filemess)
								file.close()
								mess = ""
								newflag = True
								control = None
								recivcount = 0
								tempflag = True
					if (tempflag):
						tempflag = False
						print("no data")
						break
			finally:
				print("clossing connection reciv")
				time.sleep(1)
				connection.close()

	def sendText(self, message):
		print(message)

		mess = []
		server_address = (self.ip, portrec)

		# Encode the message and turn it back to text
		mess, padding = AES.encrypt_bytes(bytes(message, encoding="utf-8"))
		mess = base64.b64encode(mess)
		mess = mess.decode('utf-8')

		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.connect(server_address)


		for i in range(len(mess)):

			try:

				# Send data
				data = json.dumps({"type":"t", "text": mess[i], "parts": len(mess), "part": i, "cipher": AES.Get_BlockType()})
				print('sending {!r}' + data)
				sock.send(data.encode())

			finally:
				print('fin')

		print('closing socket')
		sock.close()

	def sendFile(self, f):
		server_address = (self.ip, portrec)

		# sock = socket.socket()
		# sock.connect(server_address)
		i = 0
		n = 50
		file = open(f, "rb")
		name, ext = os.path.splitext(f)
		size = math.ceil((os.path.getsize(f)/n))
		sendData = file.read()

		# Encrypt the data
		sendData, padding = AES.encrypt_bytes(sendData)

		filemess = (base64.b64encode(sendData)).decode('utf-8')
		print(filemess)
		mess = filemess

		# n = 50  # ile znakow w wiadomosci
		# for i in range(0, len(filemess), n):
		#    mess.append(filemess[i:i + n])

		n = 3500  # ile znakow w wiadomosci
		choppedFile = []
		for i in range(0, len(filemess), n):
			choppedFile.append(filemess[i:i + n])
		sock = socket.socket()
		sock.connect(server_address)



		for i in range (len(choppedFile)):

			try:

				data = json.dumps({"type": ext, "text":choppedFile[i], "parts": len(choppedFile), "part": i, "cipher": AES.Get_BlockType()})
				#print('sending: '+data)
				sock.send(data.encode())
			finally:
				if i % 100 == 0:
					UI.Progress_SEND(i / len(choppedFile)* 100)
					UI.DoUpdate()
				print('fin')
		print('close')
		sock.close()
