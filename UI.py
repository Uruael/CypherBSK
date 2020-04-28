from tkinter import *
from tkinter import filedialog
import threading
import tkinter as aa
import communication as tcpcom

appState = 1
connection = tcpcom.tcpcon()


# Adds text to the log
def DisplayText(text):
	textbox = appState["UI"]["ChatLog"]
	textbox.config(state='normal')  # without setting the state to normal you can't interact with the textbox
	history = textbox.get("1.0", 'end-1c')
	newtext = history + '\n' + text
	textbox.delete('1.0', END)
	textbox.insert(0.0, newtext)
	textbox.config(state='disabled')


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

# Builds Connection UI
def ConnectUISegment(parent):
	frame = Frame(parent)

	Label(frame, text="Target IP").grid()

	ip = Text(frame, height=1, width=30)
	ip.grid()
	appState["UI"]["IpText"] = ip
	b = Button(frame, text="Connect", command=ButtonConnect)
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
	#Button(buttonframe, text="Receive", command=ButtonSendFile).grid(row=1, column=1)
	buttonframe.grid(row=2)
	# Add progress bar?
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


# Entry Function
def StartUI(passedState):
	# Make the state dictionary available to this file
	global appState
	appState = passedState

	# Add UI subdirectory
	appState["UI"] = {"dictionary": "please"}

	# Initiate the window
	root = Tk()
	frame = Frame(root)
	connection = ConnectUISegment(frame)

	chat = ChatUISegment(root)
	receive = ReceiveUISegment(frame)
	send = SendUISegment(frame)

	send.grid(row=2)
	connection.grid(row=1)
	receive.grid(row=3)

	chat.grid(row=1, column=2)
	frame.grid(row=1, column=1)
	root.mainloop()
