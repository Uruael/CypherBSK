from tkinter import *
from tkinter import filedialog
import threading
import tkinter as aa
import communication as tcpcom
from Crypto.Cipher import AES
import hashlib as Hash
import tkinter.ttk as ttk
import RSA as RS

appState = 1
connection = tcpcom.tcpcon()


def DoUpdate():
	appState["UI"]["root"].update()


def Progress_SEND(value):
	appState["UI"]["barSEND"]["value"] = value


def Progress_AES(value):
	appState["UI"]["barAES"]["value"] = value


# !! Callback section
# Adds text to the log
def DisplayText(text):
	textbox = appState["UI"]["ChatLog"]
	textbox.config(state='normal')  # without setting the state to normal you can't interact with the textbox
	history = textbox.get("1.0", 'end-1c')
	newtext = history + '\n' + text
	textbox.delete('1.0', END)
	textbox.insert(0.0, newtext)
	textbox.config(state='disabled')

def ButtonRSA():
	ip = appState["UI"]["IpText"].get("1.0", 'end-1c')
	key = RS.shareAES(ip, appState)
	appState["AES"]["key"] = key
	DisplayText("New AES key shared!")

# Callback from the password entry button
def ButtonPassword():
	DisplayText("RSA keys read finished!")
	pssw = appState["UI"]["PasswordTextfield"].get()
	hasher = Hash.sha1()
	hasher.update(pssw.encode())
	key = hasher.digest()
	key = key[:16]
	appState["UI"]["rsaPublic"] = RS.readKey(0, key)
	appState["UI"]["rsaPrivate"] = RS.readKey(1, key)


def ButtonGenerate():
	DisplayText("RSA keys generated!")
	pssw = appState["UI"]["PasswordTextfield"].get()
	hasher = Hash.sha1()
	hasher.update(pssw.encode())
	key = hasher.digest()
	key = key[:16]
	RS.generateKey(key)


# Callback from the "Connect" button
def ButtonConnect():
	DisplayText("Connecting: " + appState["UI"]["IpText"].get("1.0", 'end-1c'))
	ip = appState["UI"]["IpText"].get("1.0", 'end-1c')
	connection.set_ip(ip)
	recive_thread = threading.Thread(target=connection.reciveText)
	recive_thread.start()


# Callback from the "Choose File" button
def ButtonChooseFile():
	filename = filedialog.askopenfilename()
	filenamebox = appState["UI"]["SendFilename"]
	filenamebox.delete('1.0', END)
	filenamebox.insert(0.0, filename)


# Callback from the "Choose Folder" button
def ButtonChooseFolder():
	foldername = filedialog.askdirectory()
	foldernamebox = appState["UI"]["ReceiveFoldername"]
	foldernamebox.delete('1.0', END)
	foldernamebox.insert(0.0, foldername)


# Callback from the "Send File" button
def ButtonSendFile():
	filenamebox = appState["UI"]["SendFilename"]
	filename = filenamebox.get('1.0', 'end-1c')
	if filename == '':
		DisplayText("Bad Filename")
		return
	DisplayText("Sending file: " + filename)
	connection.sendFile(filename)


# Callback from the "Send Message" button
def ButtonSendMessage():
	chatbox = appState["UI"]["ChatBox"]
	text = chatbox.get("1.0", 'end-1c')
	if text == '':
		return
	DisplayText("[Me]:" + text)
	chatbox.delete('1.0', END)
	connection.sendText(text)


# !! UI building section
# Builds Connection UI
def ConnectUISegment(parent):
	frame = Frame(parent)

	Label(frame, text="Target IP").grid()

	ip = Text(frame, height=1, width=30)
	ip.insert(INSERT, "127.0.0.1")
	ip.grid(columnspan=2)
	appState["UI"]["IpText"] = ip
	b = Button(frame, text="Connect", command=ButtonConnect)
	c = Button(frame, text="Share AES key", command=ButtonRSA)
	b.grid(column=0, row=2)
	c.grid(column=1, row=2)
	b.grid()

	return frame


# Builds Connection UI
def ReceiveUISegment(parent):
	frame = Frame(parent)
	Label(frame, text="Receive File").grid(row=0)
	foldername = Text(frame, height=1, width=30)
	foldername.grid(row=1)
	appState["UI"]["ReceiveFoldername"] = foldername
	buttonframe = Frame(frame)
	Button(buttonframe, text="Choose Folder", command=ButtonChooseFolder).grid(row=1, column=0)
	# Button(buttonframe, text="Receive", command=ButtonSendFile).grid(row=1, column=1)
	buttonframe.grid(row=2)
	# Add progress bar?
	return frame


# Builds the password entry UI segment
def passwordEntryUISegment(parent):
	frame = Frame(parent)

	Label(frame, text="Enter Password for RSA").grid(row=0)

	pwrd = Entry(frame, width=30, show="*")
	pwrd.grid(column=0, row=1, columnspan=2)
	appState["UI"]["PasswordTextfield"] = pwrd
	b = Button(frame, text="Read Keys", command=ButtonPassword)
	c = Button(frame, text="Generate Keys", command=ButtonGenerate)
	b.grid(column=0, row=2)
	c.grid(column=1, row=2)
	return frame


# Builds Connection UI
def SendUISegment(parent):
	frame = Frame(parent)
	Label(frame, text="Send File").grid(row=0)
	filename = Text(frame, height=1, width=30)
	filename.grid(row=1)
	appState["UI"]["SendFilename"] = filename
	buttonframe = Frame(frame)
	Button(buttonframe, text="Choose File", command=ButtonChooseFile).grid(row=1, column=0)
	Button(buttonframe, text="Send", command=ButtonSendFile).grid(row=1, column=1)
	buttonframe.grid(row=2)
	# Add progress bar?
	return frame


# Builds AES Block method selection UI
def AESBlockUISegment(parent):
	frame = Frame(parent)
	Label(frame, text="AES Block type").grid(row=0, columnspan=4)
	appState["UI"]["blockopt"] = StringVar()
	options = ["ECB", "CBC", "CFB", "OFB"]
	values = [AES.MODE_ECB, AES.MODE_CBC, AES.MODE_CFB, AES.MODE_OFB]
	i = 0
	for text in options:
		radio = Radiobutton(frame, text=text, variable=appState["UI"]["blockopt"], value=values[i], indicatoron=0, )
		radio.grid(row=1, column=i)
		i = i + 1
	return frame


# Builds Chat UI
def ChatUISegment(parent):
	frame = Frame(parent)

	chatframe = Frame(frame)
	chatlog = Text(chatframe, height=30, width=80)
	chatlog.grid(row=0, column=0)
	scroll = Scrollbar(chatframe, command=chatlog.yview)
	scroll.grid(row=0, column=1, sticky="nsew")
	chatlog.config(yscrollcommand=scroll.set)
	chatlog.config(state='disabled')
	chatframe.grid()
	appState["UI"]["ChatLog"] = chatlog

	chatbox = Text(frame, height=1, width=80)
	chatbox.grid()
	appState["UI"]["ChatBox"] = chatbox

	b = Button(frame, text="Send Message", command=ButtonSendMessage)
	b.grid()
	return frame


def PbarAES(parent):
	frame = Frame(parent)
	bar = ttk.Progressbar(frame, length=800)
	Label(frame, text="Szyfrowanie").grid(row=0, column=1)
	bar["value"] = 0
	bar.grid(row=0, column=2)
	appState["UI"]["barAES"] = bar
	return frame


def PbarSEND(parent):
	frame = Frame(parent)
	bar = ttk.Progressbar(frame, length=800)
	Label(frame, text="Wysyłanie   ").grid(row=0, column=1)
	bar["value"] = 0
	bar.grid(row=0, column=2)
	appState["UI"]["barSEND"] = bar
	return frame


# !!
# Entry Function
def StartUI(passedState):
	# Make the state dictionary available to this file
	global appState
	appState = passedState

	# Add UI subdirectory
	appState["UI"] = {"dictionary": "please"}

	# Initiate the window
	root = Tk()
	appState["UI"]["root"] = root
	frame = Frame(root)
	pbarAES = PbarAES(root)
	pbarSEND = PbarSEND(root)
	chat = ChatUISegment(root)

	connect = ConnectUISegment(frame)
	receive = ReceiveUISegment(frame)
	send = SendUISegment(frame)
	block = AESBlockUISegment(frame)
	password = passwordEntryUISegment(frame)

	# Gridding the frame children
	password.grid(row=0)
	connect.grid(row=1)
	send.grid(row=2)
	receive.grid(row=3)
	block.grid(row=4)

	# Gridding the root children
	chat.grid(row=1, column=2)
	frame.grid(row=1, column=1)
	pbarAES.grid(row=2, columnspan=4)
	pbarSEND.grid(row=3, columnspan=4)
	root.mainloop()
