#!/usr/bin/env python3

import websocket, json, threading, os, playsound, colorama

NOTIFY = False
colorama.init()
def clear():
    from os import system as s;s("clear")

class COLORS:
    RED = colorama.Fore.RED
    GREEN = colorama.Fore.GREEN
    BLUE = colorama.Fore.BLUE
    RESET = colorama.Fore.RESET

# escape codes are for linux!
def cursorUp(unit):
    return f'\033[{unit}A'
def cursorDown(unit):
    return f'\033[{unit}B'
def cursorLeft(unit):
    return f'\033[{unit}D'
def cursorRight(unit):
    return f'\033[{unit}C'
def cursorClear():
    return '\033[A'

def send(msg):
    if (ws and ws.connected):
        ws.send(json.dumps(msg))


nick = input("Nick: ")
channel = input("Channel: ")

# taking break (touching grass)
def main():
    while ws.connected:
        data = json.loads(ws.recv())
        cmd = data['cmd']
        if cmd == 'onlineSet':
            nicks = data['nicks']
            print(COLORS.GREEN)
            print(f"{cursorUp(1)}* Users online: {', '.join(nicks)}\n")
            print(COLORS.RESET)
        elif cmd == 'onlineAdd':
            user = data['nick']
            print(COLORS.GREEN)
            print(f"{cursorUp(1)}* @{user} joined\n")
            print(COLORS.RESET)
        elif cmd == 'onlineRemove':
            user = data['nick']
            print(COLORS.GREEN)
            print(f"{cursorUp(1)}* @{user} left\n")
            print(COLORS.RESET)
        elif cmd == 'info':
            text = data['text']
            print(COLORS.GREEN)
            print(f"* {text}\n")
            print(COLORS.RESET)
        elif cmd == 'warn':
            text = data['text']
            print(COLORS.RED)
            print(f"* {text}\n")
            print(COLORS.RESET)
        elif cmd == 'emote':
            text = data['text']
            if 'trip' in data:
                trip = data['trip']
                print(COLORS.GREEN)
                print(f"<{trip}>* {text}\n")
                print(COLORS.RESET)
            else:
                print(COLORS.GREEN)
                print(f"<null> * {text}\n")
                print(COLORS.RESET)
        elif cmd == 'chat':
            user = data['nick']
            if NOTIFY == True and nick != user: playsound.playsound('notify.mp3')
            user = f"{COLORS.BLUE}{user}{COLORS.RESET}"
            text = data['text']
            uType = data['uType']
            ISMOD = uType == 'mod'
            if ISMOD: user = f"{COLORS.GREEN}{data['nick']}{COLORS.RESET}"
            if 'trip' in data:
                trip = data['trip']
                print(f"{cursorUp(1)}<{trip}> {user}: {text}\n")
            else:
                print(f"{cursorUp(1)}{user}: {text}\n")

ws = websocket.WebSocket()
ws.connect("wss://hack.chat/chat-ws")
send({"cmd": "join", "channel": channel, "nick": nick})
nick = nick[:nick.find('#')]
clear()

p = threading.Thread(target=main, daemon=True)
p.start()

while 1:
    try:
        myText = input()
        print(f"{cursorClear()}")
    except KeyboardInterrupt:
        exit("\nTerminating script...")
    if myText != '' and myText != '--clear' and myText != '--notify':
        send({"cmd": "chat", "text": myText})
    if myText == '--clear':
        clear()
    if myText == '--notify':
        if NOTIFY == False:
            NOTIFY = True
        else:
            NOTIFY = False
