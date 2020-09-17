import UI
import threading
import communication as tcpcom
import AES
appState = {"dictionary": "please"}

AES.AES_Init(appState)
UI.StartUI(appState)

# Control does not reach this line!
