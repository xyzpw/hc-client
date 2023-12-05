#!/usr/bin/env python3
#
# Version:  3.2.0

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
import pathlib
import re
from pygments.styles import get_all_styles
from pygments import highlight
from pygments.style import Style
import pygments.lexers
from pygments.formatters import Terminal256Formatter

parser = argparse.ArgumentParser()
parser.add_argument("--nick", help="Name to use when joining channel", dest="_nick")
parser.add_argument("--channel", help="Channel to join", dest="_channel")
args = parser.parse_args()
args = vars(args)

colorama.init()
bindings = prompt_toolkit.key_binding.KeyBindings()
run_in_terminal = prompt_toolkit.application.run_in_terminal
uiSession = prompt_toolkit.PromptSession()

allSyntaxStyles = list(get_all_styles())

#getCode = re.compile(r"^`{3}([\w]*)\n([\S\s]+?)\n`{3}$") # v3.0.1
getCode = re.compile(r"```(?P<lang>\w+)?\n(?P<code>.*?)\n```", re.DOTALL)

def getFormattedCode(lang="python", code="", style="monokai"):
    try:
        lexer = pygments.lexers.get_lexer_by_name(lang)
    except pygments.util.ClassNotFound:
        lexer = pygments.lexers.guess_lexer(code)
    syntaxExists = style in allSyntaxStyles
    if syntaxExists == False:
        style="monokai"
    result = highlight(code, lexer, Terminal256Formatter(style=style))
    return result

# :)
# c-m = enter.
@bindings.add('c-m')
def _(event: prompt_toolkit.key_binding.KeyPressEvent):
    global myText
    currentText = event.current_buffer.text
    myText = currentText
    uiSession.history.append_string(currentText)
    event.app.current_buffer.reset()
    event.app.exit(result=currentText)
# ctrl+n
@bindings.add('c-n')
def _(event):
    event.current_buffer.insert_text("\n")

# clear = lambda: os.system("cls" if os.name=="nt" else "clear")
def clear():
    if config.get("altClear") == "1":
        os.system("printf '\e3J' && clear")
    else:
        os.system("clear" if os.name != "nt" else "cls")

configName = "hc-client-config.json" # can be changed, not recommended
hasConfig = pathlib.Path(configName).exists()

config = {}
if hasConfig == True:
    try:
        with open("hc-client-config.json", 'r') as myConfig:
            config = json.loads(myConfig.read())
    except Exception as ERROR:
        exit("Error opening config file: {}".format(ERROR))

def getColor(colorName):
    match colorName:
        case "red":
            return COLORS.RED
        case "green":
            return COLORS.GREEN
        case "blue":
            return COLORS.BLUE
        case "yellow":
            return COLORS.YELLOW
        case "magenta":
            return COLORS.MAGENTA
        case "white":
            return COLORS.WHITE
        case "black":
            return COLORS.BLACK
        case "cyan":
            return COLORS.CYAN
        case "lightred":
            return COLORS.LIGHTRED
        case "lightgreen":
            return COLORS.LIGHTGREEN
        case "lightblue":
            return COLORS.LIGHTBLUE
        case "lightyellow":
            return COLORS.LIGHTYELLOW
        case "lightmagenta":
            return COLORS.LIGHTMAGENTA
        case "lightcyan":
            return COLORS.LIGHTCYAN
        case "reset":
            return COLORS.RESET
    return COLORS.RESET

def checkConfig():
    """
    Check config file and set data to config dictionary
    DONOTSAY (default=[null]) => is an array ["wordone", "wordtwo"], if your message contains these words the message will not send
    ignoreConfigWarnings (default=0) => either 0 or 1. 0 is default, set to 1 to ignore warnings
    nick (default=null) => custom default nick if none is listed
    channel (default=null) => custom channel if none is listed
    altClear (default=null) => clears scrollback buffer and clears (some consoles don't clear scrollback buffer by default [this is meant for Linux])
    blockedUserReplaceText (default="{TEXT REMOVED}") => replace a blocked users messages with this text
    blockedUsers (default=null) => default blocked users
    passwordProtection (default=1) => appends password to DONOTSAY array
    userColor => color of default users: red, green, blue, yellow, magenta, white, cyan (must be lowercase)
    modColor => color of moderators: red, green, blue, yellow, magenta, white, cyan (must be lowercase)
    adminColor => color of admin: red, green, blue, yellow, magenta, white, cyan (must be lowercase)
    colorMe => color of self: red, green, blue, yellow, magenta, white, cyan (must be lowercase)
    mySyntaxStyle (default=monokai) => syntax style of code
    """
    global config, DONOTSAY, ignoreConfigWarnings, blockedUserReplaceText, blockedUsers, ADMINCOLOR, MODCOLOR, DEFAULTCOLOR, COLORME, mySyntaxStyle
    if config == {}:
        return
    else:
        DONOTSAYappend = config.get("DONOTSAY") if config.get("DONOTSAY") != None else []
        if DONOTSAYappend != None:
            if isinstance(DONOTSAY, list) == False:
                DONOTSAY = []
            for word in DONOTSAYappend:
                DONOTSAY.append(word)
            config['DONOTSAY'] = DONOTSAY

        ignoreConfigWarnings = config.get("ignoreConfigWarnings") if config.get("ignoreConfigWarnings") != None else "0"
        config["ignoreConfigWarnings"] = "1" if ignoreConfigWarnings == "1" else "0"
        ignoreConfigWarnings = True if config.get("ignoreConfigWarnings") == "1" else False

        blockedUserReplaceText = config.get("blockedUserReplaceText") if config.get("blockedUserReplaceText") != None else "{TEXT REMOVED}"
        config["blockedUserReplaceText"] = config.get("blockedUserReplaceText") if config.get("blockedUserReplaceText") != None else "{TEXT REMOVED}"

        blockedUsers = config.get("blockedUsers") if config.get("blockedUsers") != None else []
        if isinstance(blockedUsers, list) == False:
            blockedUsers = []

        configColors = {
            "admin": config.get("adminColor"),
            "mod": config.get("modColor"),
            "default": config.get("userColor"),
            "me": config.get("colorMe"),
        }

        for key, val in configColors.items():
            if val == None:
                continue
            match key:
                case "admin":
                    ADMINCOLOR = getColor(val)
                case "mod":
                    MODCOLOR = getColor(val)
                case "default":
                    DEFAULTCOLOR = getColor(val)
                case "me":
                    COLORME = getColor(val)

        mySyntaxStyle = config.get("mySyntaxStyle") if config.get("mySyntaxStyle") != None else "monokai"
        config["mySyntaxStyle"] = mySyntaxStyle

class COLORS:
    RED = colorama.Fore.RED
    GREEN = colorama.Fore.GREEN
    BLUE = colorama.Fore.BLUE
    YELLOW = colorama.Fore.YELLOW
    MAGENTA = colorama.Fore.MAGENTA
    WHITE = colorama.Fore.WHITE
    BLACK = colorama.Fore.BLACK
    CYAN = colorama.Fore.CYAN
    LIGHTRED = colorama.Fore.LIGHTRED_EX
    LIGHTGREEN = colorama.Fore.LIGHTGREEN_EX
    LIGHTBLUE = colorama.Fore.LIGHTBLUE_EX
    LIGHTYELLOW = colorama.Fore.LIGHTYELLOW_EX
    LIGHTMAGENTA = colorama.Fore.LIGHTMAGENTA_EX
    LIGHTCYAN = colorama.Fore.LIGHTCYAN_EX
    RESET = colorama.Fore.RESET

def cursorUp(unit): return f'\033[{unit}A'
def cursorDown(unit): return f'\033[{unit}B'
def cursorLeft(unit): return f'\033[{unit}D'
def cursorRight(unit): return f'\033[{unit}C'
#def cursorClear(): return '\033[A'
def cursorClear(): return '\033[2K' # moves cursor to beginning

chatCommands = {
    "help": "Usage: --help [command]\nShows this message or usage of other commands if specified",
    "clear": "Clears the screen",
    "notify": "Plays notify.mp3 if a message is received",
    "block": "Usage: --block <user>\nBlocks a user",
    "unblock": "Usage: --unblock <user>\nRemoves specified user from block list",
    "blocklist": "Returns a list of blocked users",
    "showblocked": "Same as blocklist",
    "color": "Usage: --color [text] (admin | mod | user | me) (red | blue | green | yellow | magenta | white | cyan)\nChanges the color of users or text. You can use light colors by adding \"light\" in front, e.g. lightred",
    "syntaxstyle": "Usage: --syntaxstyle <style>\nChanges syntax style of highlighted code",
    "config": "Returns the users config (some results may be limited)",
}

NOTIFY = False

def send(msg):
    if (ws and ws.connected):
        ws.send(json.dumps(msg))

# keep this
levels = {
    "admin": 9999999,
    "moderator": 999999,

    "channelOwner": 99999,
    "channelModerator": 9999,
    "ChannelTrusted": 8999,

    "trustedUser": 500,
    "default": 100
}

def getUserType(level):
    match level:
        case 9999999:
            return 'admin'
        case 999999:
            return 'moderator'
        case _:
            return 'default'

def getReadableTime(timestamp):
    readableTime = datetime.datetime.fromtimestamp(timestamp).strftime("%H:%M:%S")
    return readableTime

def playNotification():
    try:
        playsound.playsound("notify.mp3")
    except:
        pass

def show_msg(msg):
    print(f"{cursorUp(1)}{msg}\n")

def print_error(msg):
    print(f"{cursorUp(1)}{COLORS.RED}{msg}{COLORS.RESET}\n")

def print_cmdResponse(msg, error=False, warning=False):
    if error == True and warning == True:
        warning = False
    if error:
        print(f"{cursorClear()}{COLORS.RED}{msg}{COLORS.RESET}\n\n")
    elif warning:
        print(f"{cursorClear()}{COLORS.YELLOW}{msg}{COLORS.RESET}\n\n")
    else:
        print(f"{cursorClear()}{msg}\n\n")

def showHelp(command=None):
    if command == None:
        helpList = [key for key in chatCommands]
        print_cmdResponse(", ".join(helpList))
    else:
        if command in chatCommands:
            helpMessage = chatCommands.get(command)
            print_cmdResponse(helpMessage)
        else:
            print_cmdResponse(f"Command not found: {command}", error=True)

def browserStyle(text, initialColor, resetColorAfterHighlight=True):
    text = re.sub("(__(.*?)__)", "\x1b[1m\\2\x1b[22m", text)
    text = re.sub("(\*\*(.*?)\*\*)", "\x1b[1m\\2\x1b[22m", text)
    text = re.sub("(~~(.*?)~~)", "\x1b[9m\\2\x1b[29m", text)
    if resetColorAfterHighlight:
        text = re.sub("(\=\=(.*?)\=\=)", f"{colorama.Back.GREEN}{getColor('black')}\\2{colorama.Back.RESET}{getColor('reset')}", text)
    else:
        text = re.sub("(\=\=(.*?)\=\=)", f"{colorama.Back.GREEN}{getColor('black')}\\2{colorama.Back.RESET}{getColor(initialColor)}", text)
    return text

def makeColorful(text, color):
    if color == None:
        return text
    colorName = getColor(color)
    resetCode = getColor("reset")
    coloredText = f"{colorName}{text}{resetCode}"
    return coloredText

try:
    useConfigName = args.get("_nick") == None and config.get("nick") != None
    useConfigChannel = args.get("_channel") == None and config.get("channel") != None
    if useConfigName:
        nick = config.get("nick")
    else:
        nick = prompt_toolkit.prompt("Nick: ") if args.get("_nick") == None else args.get("_nick")
    if useConfigChannel:
        channel = config.get("channel")
    else:
        channel = prompt_toolkit.prompt("Channel: ") if args.get("_channel") == None else args.get("_channel")
except (KeyboardInterrupt, EOFError):
    print("Terminating script")
    exit()
except Exception as ERROR:
    exit("Error received: {}".format(ERROR))

def main():
    global nickTags
    while ws.connected:
        data = json.loads(ws.recv())
        cmd = data['cmd']
        timestamp = time.time() // 1
        match cmd:
            case 'onlineSet':
                nicks = data['nicks']
                for i in nicks:
                    nickTags.append(f"@{i}")
                print(COLORS.GREEN, end='')
                show_msg(f"* Users online: {', '.join(nicks)}\n")
                print(COLORS.RESET, end='')
            case 'onlineAdd':
                user = data['nick']
                nicks.append(user)
                nickTags.append(f"@{user}")
                print(COLORS.GREEN, end='')
                show_msg(f"|{getReadableTime(timestamp)}| * @{user} joined")
                print(COLORS.RESET, end='')
            case 'onlineRemove':
                user = data['nick']
                nicks.remove(user)
                nickTags.remove(f"@{user}")
                print(COLORS.GREEN, end='')
                show_msg(f"|{getReadableTime(timestamp)}| * @{user} left")
                print(COLORS.RESET, end='')
            case 'info':
                text = data['text']
                trip = data.get("trip")
                if trip == None:
                    print(COLORS.GREEN, end='')
                    show_msg(f"|{getReadableTime(timestamp)}| * {text}")
                    print(COLORS.RESET, end='')
                else:
                    print(COLORS.GREEN, end='')
                    show_msg(f"|{getReadableTime(timestamp)}| <{trip}> * {text}")
                    print(COLORS.RESET, end='')
                if NOTIFY:
                    playNotification()
            case 'warn':
                text = data['text']
                print(COLORS.RED, end='')
                show_msg(f"|{getReadableTime(timestamp)}| * {text}")
                print(COLORS.RESET, end='')
                if NOTIFY:
                    playNotification()
            case 'emote':
                user = data.get("nick")
                trip = data.get("trip")
                ignoreUser = user in blockedUsers
                if ignoreUser:
                    text = blockedUserReplaceText
                else:
                    text = data.get("text")
                if trip == None:
                    trip = "null"
                print(COLORS.GREEN, end='')
                show_msg(f"|{getReadableTime(timestamp)}| <{trip}> * {text}")
                print(COLORS.RESET, end='')
                if NOTIFY and ignoreUser == False:
                    playNotification()
            case 'chat':
                user = data['nick']
                trip = data.get("trip")
                isMe = str(user) == str(nick)
                coloredUser = user
                ignoreUser = user in blockedUsers
                if ignoreUser:
                    text = blockedUserReplaceText
                else:
                    text = data['text']
                uType = getUserType(data['level']) if isMe == False else "me"
                match uType:
                    case 'admin':
                        coloredUser = makeColorful(user, ADMINCOLOR)
                        coloredText = makeColorful(text, ADMINTEXTCOLOR)
                        colorBeforeHighlight = ADMINTEXTCOLOR
                    case 'moderator':
                        coloredUser = makeColorful(user, MODCOLOR)
                        coloredText = makeColorful(text, MODTEXTCOLOR)
                        colorBeforeHighlight = MODTEXTCOLOR
                    case 'default':
                        coloredUser = makeColorful(user, DEFAULTCOLOR)
                        coloredText = makeColorful(text, DEFAULTTEXTCOLOR)
                        colorBeforeHighlight = DEFAULTTEXTCOLOR
                    case "me":
                        coloredUser = makeColorful(user, COLORME)
                        coloredText = makeColorful(text, TEXTCOLORME)
                        colorBeforeHighlight = TEXTCOLORME
                codeBlockMatches = getCode.findall(text)
                for block in codeBlockMatches:
                    codeBlockLang = block[0]
                    codeBlockCode = block[1]
                    currentCode = getFormattedCode(codeBlockLang, codeBlockCode, mySyntaxStyle)
                    text = text.replace(f"```{codeBlockLang}", '', 1).strip()
                    text = text.replace("```", '', 1).strip()
                    text = text.replace(codeBlockCode, currentCode, 1).strip()
                    text = f"\n{text}"
                if bool(codeBlockMatches) == False:
                    coloredText = browserStyle(coloredText, initialColor=colorBeforeHighlight, resetColorAfterHighlight=False)
                if trip != None:
                    show_msg(f"|{getReadableTime(timestamp)}| <{trip}> {coloredUser}: {coloredText}")
                else:
                    show_msg(f"|{getReadableTime(timestamp)}| {coloredUser}: {coloredText}")
                if NOTIFY and isMe == False and ignoreUser == False:
                    playNotification()

DONOTSAY = []
ws = websocket.WebSocket()
try:
    ws.connect("wss://hack.chat/chat-ws")
    if '#' in nick:
        myPassword = nick[nick.find("#")+1:]
        if config.get("passwordProtection") == "1":
            DONOTSAY.append(myPassword)
        send({"cmd": "join", "channel": channel, "nick": nick})
        nick = nick[:nick.find('#')]
        if myPassword in nick:
            raise Exception(f"{COLORS.RED}Password wasn't removed from name. Terminating script{COLORS.RESET}")
        del(myPassword)
    else:
        send({"cmd": "join", "channel": channel, "nick": nick})
    clear()
except Exception as ERROR:
    exit("Error connecting: {}".format(ERROR))

p = threading.Thread(target=main, daemon=True)
p.start()

nickTags = []
blockedUsers = []

ignoreConfigWarnings = False
blockedUserReplaceText = "{TEXT REMOVED}"

MODCOLOR, MODTEXTCOLOR = "green", None
ADMINCOLOR, ADMINTEXTCOLOR = "red", None
DEFAULTCOLOR, DEFAULTTEXTCOLOR = "blue", None
COLORME, TEXTCOLORME = "blue", None

mySyntaxStyle = "monokai"

commandPrefix = "--"

try:
    checkConfig()
except Exception as ERROR:
    exit("Error setting config: {}".format(ERROR))

exitAttempt = False
while True:
    try:
        myText = ''
        with prompt_toolkit.patch_stdout.patch_stdout(raw=True):
            uiCompleter = prompt_toolkit.completion.WordCompleter(nickTags, match_middle=False, ignore_case=True, sentence=True)
            myText = uiSession.prompt(completer=uiCompleter, wrap_lines=False, multiline=True, key_bindings=bindings)
            if myText == None: myText = ''
            print(cursorUp(2), cursorClear())
            exitAttempt = False
    except (KeyboardInterrupt, EOFError) as ERROR:
        if type(ERROR).__name__ == "KeyboardInterrupt":
            if exitAttempt:
                print("Terminating script...")
                exit()
            exitAttempt = True
            print("Press ^C again to exit")
        else:
            exit()
    if DONOTSAY != []:
        for word in DONOTSAY:
            if word in myText:
                myText = ''
                print_cmdResponse("Message contains words from DONOTSAY - did not send", error=True)
                continue
    isCommand, changingName = False, False
    if myText.startswith("/nick "): changingName = True

    for command in chatCommands:
        if myText.startswith(f"{commandPrefix}{command}"):
            isCommand = True
            continue

    failedCommand = isCommand == False and myText.startswith(commandPrefix)
    if failedCommand:
        failedCommandName = myText.replace(commandPrefix, '')
        print_cmdResponse(f"Command not found: {failedCommandName}", error=True)
    isSendableMessage = isCommand == False and failedCommand == False and changingName == False

    if myText != '' and isSendableMessage:
        send({"cmd": "chat", "text": myText})

    if changingName:
        newNick = myText.replace("/nick ", '')
        send({"cmd": "chat", "text": myText})
        nick = newNick

    if isCommand:
        if ' ' in myText:
            commandName = myText[:myText.find(' ')]
        else:
            commandName = myText
        match commandName:
            case "--clear":
                clear()
            case "--notify":
                notifyAction = 'status'
                if ' ' in myText:
                    notifyArg = myText.replace("--notify ", '').strip()
                    if notifyArg == "on":
                        notifyAction = "enable"
                    elif notifyArg == "off":
                        notifyAction = "disable"
                match notifyAction:
                    case "enable":
                        if NOTIFY:
                            print_cmdResponse("Notifications are already enabled", error=True)
                        else:
                            NOTIFY = True
                            print_cmdResponse("Notifications enabled")
                    case "disable":
                        if NOTIFY:
                            NOTIFY = False
                            print_cmdResponse("Notifications disabled")
                        else:
                            print_cmdResponse(f"Notifications are already disabled", error=True)
                    case "status":
                        print_cmdResponse(f"Notification status: {NOTIFY}")
            case "--block":
                properInputChecker = re.compile(r"--block (.*)")
                isProperInput = bool(properInputChecker.search(myText))
                if isProperInput == False:
                    showHelp("block")
                    continue
                targets = properInputChecker.search(myText).group(1).split()
                if targets == []:
                    showHelp("block")
                    continue
                if len(targets) > 1:
                    for target in targets:
                        isBlocked = target in blockedUsers
                        if isBlocked == False:
                            blockedUsers.append(target)
                    print_cmdResponse("Added users to blocklist. Current blocklist: {}".format(", ".join(blockedUsers)))
                elif len(targets) == 1:
                    target = targets[0]
                    isBlocked = target in blockedUsers
                    if isBlocked:
                        print_cmdResponse(f"{target} is already blocked", error=True)
                        continue
                    blockedUsers.append(target)
                    print_cmdResponse(f"Added {target} to blocklist")
            case "--unblock":
                properInputChecker = re.compile(r"--unblock (.*)")
                isProperInput = bool(properInputChecker.search(myText))
                if isProperInput == False:
                    showHelp("unblock")
                    continue
                targets = properInputChecker.search(myText).group(1).split()
                if targets == []:
                    showHelp("unblock")
                if len(targets) > 1:
                    for target in targets:
                        isBlocked = target in blockedUsers
                        if isBlocked:
                            blockedUsers.remove(target)
                    if len(blockedUsers) >= 1:
                        blockedUsersStringFormat = ", ".join(blockedUsers)
                        print_cmdResponse(f"Removed users from blocklist. Current blocklist: {blockedUsersStringFormat}")
                    elif len(blockedUsers) == 0:
                        print_cmdResponse("Removed all users from blocklist")
                elif len(targets) == 1:
                    target = targets[0]
                    isBlocked = target in blockedUsers
                    if isBlocked:
                        blockedUsers.remove(target)
                        print_cmdResponse(f"Removed {target} from blocklist")
                    elif target == '*':
                        blockedUsers = []
                        print_cmdResponse("Blocklist cleared")
                    else:
                        print_cmdResponse(f"{target} is not blocked", error=True)
                else:
                    showHelp("unblock")
            case "--blocklist" | "--showblocked":
                isEmpty = len(blockedUsers) == 0
                if isEmpty:
                    print_cmdResponse("No users in blocklist")
                else:
                    blockedUsersStringFormat = ', '.join(blockedUsers)
                    print_cmdResponse(f"List of blocked users: {blockedUsersStringFormat}")
            case "--config":
                isEmpty = config == {}
                if isEmpty:
                    print_cmdResponse("Custom config is empty")
                    continue
                if ignoreConfigWarnings:
                    print_cmdResponse(config)
                else:
                    unsafeKeys = ['DONOTSAY', 'nick']
                    safeConfig = {}
                    for key in config:
                        if key not in unsafeKeys:
                            safeConfig[key] = config.get(key)
                    print_cmdResponse("Some keys are not shown. To show all keys, change \"ignoreConfigWarnings\" to 1", warning=True)
                    print_cmdResponse(safeConfig)
            case "--color":
                colorList = "(red|blue|green|yellow|magenta|white|black|cyan|lightred|lightblue|lightgreen|lightyellow|lightmagenta|lightcyan)"
                textColorList = colorList.replace(')', '|reset)')
                reUserColor = re.compile(f"^--color (admin|mod|user|default|me) {colorList}$")
                reUserTextColor = re.compile(f"^--color text (admin|mod|user|default|me) {textColorList}$")
                isUserColor = bool(reUserColor.search(myText))
                isTextColor = bool(reUserTextColor.search(myText))
                if isUserColor:
                    groupToColor = reUserColor.search(myText).group(1)
                    colorToUse = reUserColor.search(myText).group(2)
                    match groupToColor:
                        case "admin":
                            ADMINCOLOR = colorToUse
                        case "mod":
                            MODCOLOR = colorToUse
                        case "user" | "default":
                            DEFAULTCOLOR = colorToUse
                        case "me":
                            COLORME = colorToUse
                    print_cmdResponse("New color set")
                elif isTextColor:
                    groupToColor = reUserTextColor.search(myText).group(1)
                    colorToUse = reUserTextColor.search(myText).group(2)
                    match groupToColor:
                        case "admin":
                            ADMINTEXTCOLOR = colorToUse
                        case "mod":
                            MODTEXTCOLOR = colorToUse
                        case "user" | "default":
                            DEFAULTTEXTCOLOR = colorToUse
                        case "me":
                            TEXTCOLORME = colorToUse
                    print_cmdResponse("New color set")
                else:
                    print_cmdResponse("Incorrect usage. See help for more info", error=True)
            case "--syntaxstyle":
                if myText == "--syntaxstyle" and ignoreConfigWarnings == False:
                    syntaxstyleWarning = lambda: print_cmdResponse("Syntax style list is very large, type this command again to view", warning=True)
                    sessionHistory = vars(uiSession.history).get("_storage")
                    if sessionHistory == None:
                        syntaxstyleWarning()
                        continue
                    if len(sessionHistory) > 2:
                        previousCommand = sessionHistory[len(sessionHistory)-2]
                        if previousCommand == "--syntaxstyle":
                            print_cmdResponse(allSyntaxStyles)
                            continue
                        else:
                            syntaxstyleWarning()
                            continue
                    else:
                        syntaxstyleWarning()
                        continue
                uiSyntaxStyle = myText.replace("--syntaxstyle ", '')
                if uiSyntaxStyle in allSyntaxStyles:
                    mySyntaxStyle = uiSyntaxStyle
                    config["mySyntaxStyle"] = mySyntaxStyle
                    print_cmdResponse("New style set")
                else:
                    print_cmdResponse("Invalid style", error=True)
            case "--help":
                if myText == "--help":
                    showHelp()
                else:
                    helpArg = myText.replace("--help ", '')
                    showHelp(helpArg)
