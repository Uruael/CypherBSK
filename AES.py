from Crypto.Cipher import AES as A
appState = 1
def Get_BlockType():
	modes = [None,A.MODE_ECB, A.MODE_CBC, A.MODE_CFB, None, A.MODE_OFB]
	no = appState["UI"]["blockopt"].get()
	return modes[int(no)]

def AES_Init(passedState):
	global appState
	appState = passedState

	# Add AES subdirectory
	appState["AES"] = {"dictionary": "please"}

	# !!!!!Todo: Non-static key
	appState["AES"]["key"] = b"0123456789ABCDEF"

	# Block type for encoding
	appState["AES"]["blockopt"] = A.MODE_ECB

	# Initialization Vector coz we apparently need one Todo: Non-static IV
	appState["AES"]["IV"] = b"aeiouyaeiouy1234"


def AES_encrypt(data, cipher):
	ret = []
	for block in data:
		text = cipher.encrypt(block)
		ret.append(text)
	return ret


def AES_decrypt(data, cipher):
	ret = []
	for block in data:
		text = cipher.decrypt(block)
		ret.append(text)
	return ret

def AES_GetCipher(key=None, blocktype=None):
	if key is None:
		key = appState["AES"]["key"]
	if blocktype is None:
		blocktype = Get_BlockType()
	if blocktype == 1:
		ret = A.new(key, blocktype)
	else:
		ret = A.new(key, blocktype, appState["AES"]["IV"])
	return ret

# Encrypt a byte data block
def encrypt_bytes(data, cipher=None, key=None, blocktype=None):
	if cipher is None:
		cipher = AES_GetCipher(key, blocktype)
	if len(data) == 0:
		return

	i = 0
	array = []
	padding = (16 - (len(data) % 16)) % 16
	data = data + (b"\x00" * padding)
	j = 10000
	while i < len(data):
		array.append(cipher.encrypt(data[i:i+16]))
		i += 16
		j -= 1
		if j == 0:
			j = 10000
			appState["UI"]["barAES"]["value"] = i / len(data) * 100
			appState["UI"]["root"].update()

	padding = 0
	ret = b''.join(array)
	return ret, padding

def decrypt_bytes(data, cipher=None, key=None, blocktype=None):
	if cipher is None:
		cipher = AES_GetCipher(key, blocktype)

	array = []
	i = 0
	plz = bytearray(data)
	while len(plz) > i:
		array.append(plz[i:i + 16])
		i += 16
	# padded with x00 bytes, so size of the padding does not matter
	array = AES_decrypt(array, cipher)
	ret = b''.join(array)
	return ret
