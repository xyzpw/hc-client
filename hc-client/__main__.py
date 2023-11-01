#!/usr/bin/env python3

import websocket
import json
import threading
import os
import playsound
import colorama
import prompt_toolkit
import datetime
import time
import argparse

NOTIFY = False
colorama.init()
nickTags = []
uiSession = prompt_toolkit.PromptSession()

parse = argparse.ArgumentParser()
parse.add_argument("--nick", help="Name to use when joining channel", dest="_nick")
parse.add_argument("--channel", help="Channel to join", dest="_channel")
args = parse.parse_args()
var_args = vars(args)

clear = lambda: os.system("cls") if os.name == "nt" else os.system("clear")

class COLORS:
    RED = colorama.Fore.RED
    GREEN = colorama.Fore.GREEN
    BLUE = colorama.Fore.BLUE
    RESET = colorama.Fore.RESET

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


def getReadableTime(timestamp):
    readableTime = datetime.datetime.fromtimestamp(timestamp).strftime("%H:%M:%S")
    return readableTime

try:
    nick = prompt_toolkit.prompt("Nick: ") if var_args.get("_nick") == None else var_args.get("_nick")
    channel = prompt_toolkit.prompt("Channel: ") if var_args.get("_channel") == None else var_args.get("_channel")
except (KeyboardInterrupt, EOFError):
    exit("Terminating script...")
except Exception as _e:
    exit(_e)

def main():
    global nickTags
    while ws.connected:
        data = json.loads(ws.recv())
        cmd = data['cmd']
        if cmd == 'onlineSet':
            nicks = data['nicks']
            for i in nicks: nickTags.append(f"@{i}")
            print(COLORS.GREEN)
            print(f"{cursorUp(1)}* Users online: {', '.join(nicks)}\n")
            print(COLORS.RESET)
        elif cmd == 'onlineAdd':
            user = data['nick']
            nicks.append(user)
            nickTags.append(f"@{user}")
            print(COLORS.GREEN)
            print(f"{cursorUp(1)}* @{user} joined\n")
            print(COLORS.RESET)
        elif cmd == 'onlineRemove':
            user = data['nick']
            nicks.remove(user)
            nickTags.remove(f"@{user}")
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
            timestamp = time.time() // 1
            text = data['text']
            if 'trip' in data:
                trip = data['trip']
                print(COLORS.GREEN)
                print(f"|{getReadableTime(timestamp)}| <{trip}>* {text}\n")
                print(COLORS.RESET)
            else:
                print(COLORS.GREEN)
                print(f"|{getReadableTime(timestamp)}| <null> * {text}\n")
                print(COLORS.RESET)
        elif cmd == 'chat':
            timestamp = time.time() // 1
            user = data['nick']
            coloredUser = user
            if NOTIFY == True and nick != user: playsound.playsound('notify.mp3')
            text = data['text']
            uType = data['uType']
            match uType:
                case 'mod':
                    coloredUser = f"{COLORS.GREEN}{data['nick']}{COLORS.RESET}"
                case 'admin':
                    coloredUser = f"{COLORS.RED}{data['nick']}{COLORS.RESET}"
                case "user":
                    coloredUser = f"{COLORS.BLUE}{data['nick']}{COLORS.RESET}"
            if 'trip' in data:
                trip = data['trip']
                print(f"{cursorUp(1)}|{getReadableTime(timestamp)}| <{trip}> {coloredUser}: {text}\n")
                #print(f"{cursorUp(1)}<{trip}> {user}: {text}\n")
            else:
                print(f"{cursorUp(1)}|{getReadableTime(timestamp)}| {coloredUser}: {text}\n")
                #print(f"{cursorUp(1)}{user}: {text}\n")

ws = websocket.WebSocket()
ws.connect("wss://hack.chat/chat-ws")
send({"cmd": "join", "channel": channel, "nick": nick})
nick = nick[:nick.find('#')]
clear()

p = threading.Thread(target=main, daemon=True)
p.start()

while 1:
    try:
        with prompt_toolkit.patch_stdout.patch_stdout(raw=True):
            uiCompleter = prompt_toolkit.completion.WordCompleter(nickTags, match_middle=False, ignore_case=True, sentence=True)
            myText = uiSession.prompt(completer=uiCompleter, wrap_lines=False)
            print(f"{cursorClear()}")
            myText = myText.replace('--nl', '\n')
    except (KeyboardInterrupt, EOFError):
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
