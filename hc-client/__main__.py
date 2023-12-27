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
import pathlib
import re
from pygments.styles import get_all_styles
from pygments import highlight
from pygments.style import Style
import pygments.lexers
from pygments.formatters import Terminal256Formatter

parser = argparse.ArgumentParser()
parser.add_argument("--nick", help="name to use when joining channel", dest="_nick")
parser.add_argument("--channel", help="channel to join", dest="_channel")
parser.add_argument("--no-clear", help="screen does not clear when joining channel", action="store_true")
args = parser.parse_args()
args = vars(args)

colorama.init()
bindings = prompt_toolkit.key_binding.KeyBindings()
run_in_terminal = prompt_toolkit.application.run_in_terminal
uiSession = prompt_toolkit.PromptSession()

allSyntaxStyles = list(get_all_styles())

getCode = re.compile(r"```(?P<lang>.*?)?\n(?P<code>.*?)\n?(?:```|\Z)", re.DOTALL)
singleLineCodePattern = re.compile(r"`(?P<code>.{1,})`")

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
if hasConfig:
    try:
        with open("hc-client-config.json", 'r') as myConfig:
            config = json.loads(myConfig.read())
    except Exception as ERROR:
        exit("Error opening config file: {}".format(ERROR))

def getColor(colorName, back=False):
    match colorName:
        case "red":
            if back:
                return colorama.Back.RED
            return COLORS.RED
        case "green":
            if back:
                return colorama.Back.GREEN
            return COLORS.GREEN
        case "blue":
            if back:
                return colorama.Back.BLUE
            return COLORS.BLUE
        case "yellow":
            if back:
                return colorama.Back.YELLOW
            return COLORS.YELLOW
        case "magenta":
            if back:
                return colorama.Back.MAGENTA
            return COLORS.MAGENTA
        case "white":
            if back:
                return colorama.Back.WHITE
            return COLORS.WHITE
        case "black":
            if back:
                return colorama.Back.BLACK
            return COLORS.BLACK
        case "cyan":
            if back:
                return colorama.Back.CYAN
            return COLORS.CYAN
        case "lightred":
            if back:
                return colorama.Back.LIGHTRED_EX
            return COLORS.LIGHTRED
        case "lightgreen":
            if back:
                return colorama.Back.LIGHTGREEN_EX
            return COLORS.LIGHTGREEN
        case "lightblue":
            if back:
                return colorama.Back.LIGHTBLUE_EX
            return COLORS.LIGHTBLUE
        case "lightyellow":
            if back:
                return colorama.Back.LIGHTYELLOW_EX
            return COLORS.LIGHTYELLOW
        case "lightmagenta":
            if back:
                return colorama.Back.LIGHTMAGENTA_EX
            return COLORS.LIGHTMAGENTA
        case "lightcyan":
            if back:
                return colorama.Back.LIGHTCYAN_EX
            return COLORS.LIGHTCYAN
        case "lightblack":
            if back:
                return colorama.Back.LIGHTBLACK_EX
        case "reset":
            if back:
                return colorama.Back.RESET
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
    botColor => color of bots: red, green, blue, yellow, magenta, white, cyan (must be lowercase)
    mentionColor => color of highlighted mention: red, green, blue, yellow, magenta, white, cyan (must be lowercase)
    mySyntaxStyle (default=monokai) => syntax style of code
    botlist => list of bots in an array, e.g. ["nick1", "nick2"]
    notifymention (default=1) => play notification when @mentioned
    notifywhisper (default=1) => play notification when whispered
    stars (default=1) => displays stars near the moderators names
    """
    global config, DONOTSAY, ignoreConfigWarnings, blockedUserReplaceText, blockedUsers, ADMINCOLOR, MODCOLOR, DEFAULTCOLOR, COLORME, BOTCOLOR, mySyntaxStyle, botlist, NOTIFYMENTION, MENTIONCOLOR, NOTIFYWHISPER, STARS
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
            "bot": config.get("botColor"),
            "mention": config.get("mentionColor"),
        }

        for key, val in configColors.items():
            if val == None:
                continue
            match key:
                case "admin":
                    ADMINCOLOR = config.get("adminColor")
                case "mod":
                    MODCOLOR = config.get("modColor")
                case "default":
                    DEFAULTCOLOR = config.get("userColor")
                case "me":
                    COLORME = config.get("colorMe")
                case "bot":
                    BOTCOLOR = config.get("botColor")
                case "mention":
                    MENTIONCOLOR = config.get("mentionColor")

        mySyntaxStyle = config.get("mySyntaxStyle") if config.get("mySyntaxStyle") != None else "monokai"
        config["mySyntaxStyle"] = mySyntaxStyle
        botlist = config.get("botlist") if config.get("botlist") != None else []
        if config.get("notifymention") == '0': NOTIFYMENTION = False
        if config.get("notifywhisper") == '0': NOTIFYWHISPER = False
        if config.get("stars") == '0': STARS = False


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
def cursorClear(): return '\033[2K'

chatCommands = {
    "help": "Usage:\n\thelp [command]\nDescription:\n\tShows this message or usage of other commands if specified.",
    "clear": "Clears the screen.",
    "notify": "Usage:\n\tnotify [mention | whisper] [on | off]\nDescription:\n\tEnables or disables notifications.",
    "block": "Usage:\n\tblock <user...>\nDescription:\n\tBlocks specified users.",
    "unblock": "Usage:\n\tunblock <user...>\nDescription:\n\tRemoves specified users from block list.",
    "blocklist": "Returns a list of blocked users.",
    "showblocked": "Same as blocklist.",
    "color": "Usage:\n\tcolor ([mention <color>] | [text] <group> <color>)\nDescription:\n\tChanges the color of users, text, or mentions.\n\tLight colors can be used too. E.g. \"lightred.\"\nParameters:\n\tgroup    (admin | mod | user | bot | me)\n\tcolor    (red | blue | green | yellow | magenta | white | cyan)",
    "syntaxstyle": "Usage:\n\tsyntaxstyle [style]\nDescription:\n\tThe style argument will set the syntaxstyle, otherwise it will display a list of all styles (large).",
    "config": "Returns the users config (some results may be limited).",
    "nl": "Prints a few newlines to the screen. Nothing more.",
    "mentions": "Usage:\n\tmentions [on | off]\nDescription:\n\tMakes user mentions colored.",
    "browserstyle": "Usage:\n\tbrowserstyle [on | off]\nDescription:\n\tEnables or disables browserstyle.",
    "addbot": "Usage:\n\taddbot <user...>\nDescription:\n\tAdds specified users to botlist.\n\tBots have their own groups and don't trigger mention notifications.",
    "removebot": "Usage:\n\tremovebot <user...>\nDescription:\n\tRemoves specified users from botlist.",
    "botlist": "Displays the botlist.",
    "stars": "Usage:\n\tstars [on | off]\nDescription:\n\tDisplays stars next to the moderators names.",
    "whisperlock": "Usage:\n\twhisperlock [on | off]\nDescription:\n\tDisables the ability to send any messages other than whispers.",
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
    "default": 100,
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
    # some terminals don't have support for these
    makePattern = lambda val: f"(?<![\S])({val}(?=[\w\d])(?P<sentence>.*?)(?<=[\w\d\.]){val})(?=\s|$)"
    text = re.sub(makePattern("__"), "\x1b[1m\g<sentence>\x1b[22m", text)
    text = re.sub(makePattern('_'), "\x1b[3m\g<sentence>\x1b[23m", text)
    text = re.sub(makePattern("\*\*"), "\x1b[1m\g<sentence>\x1b[22m", text)
    text = re.sub(makePattern("\*"), "\x1b[3m\g<sentence>\x1b[23m", text)
    text = re.sub(makePattern("~~"), "\x1b[9m\g<sentence>\x1b[29m", text)
    text = re.sub(r"\.{3,}", "...", text)
    if resetColorAfterHighlight:
        text = re.sub(makePattern("=="), f"{colorama.Back.GREEN}{getColor('black')}\\2{colorama.Back.RESET}{getColor('reset')}", text)
    else:
        text = re.sub(makePattern("=="), f"{colorama.Back.GREEN}{getColor('black')}\\2{colorama.Back.RESET}{getColor(initialColor)}", text)
    return text

def makeColorful(text, color):
    if color == None:
        return text
    colorName = getColor(color)
    resetCode = getColor("reset")
    coloredText = f"{colorName}{text}{resetCode}"
    return coloredText

def coloredMention(text):
    mentionedUsers = re.findall("(?!\b)(@\w+)", text)
    if bool(mentionedUsers):
        for mentionedUser in mentionedUsers:
            text = text.replace(mentionedUser, f"{getColor(MENTIONCOLOR, back=True)}{mentionedUser}{getColor('reset', back=True)}")
    return text

def onoffSwitch(requestedStatus, currentStatus):
    if requestedStatus != currentStatus:
        return True
    return False

def createUtypeStyle(utype, user, text):
    utypeDict = dict()
    match utype:
        case "admin":
            utypeDict["coloredUser"] = makeColorful(user, ADMINCOLOR)
            utypeDict["coloredText"] = makeColorful(text, ADMINTEXTCOLOR)
            utypeDict["colorBeforeHighlight"] = ADMINTEXTCOLOR
        case "moderator":
            utypeDict["coloredUser"] = makeColorful(user, MODCOLOR)
            utypeDict["coloredText"] = makeColorful(text, MODTEXTCOLOR)
            utypeDict["colorBeforeHighlight"] = MODTEXTCOLOR
        case "default":
            utypeDict["coloredUser"] = makeColorful(user, DEFAULTCOLOR)
            utypeDict["coloredText"] = makeColorful(text, DEFAULTTEXTCOLOR)
            utypeDict["colorBeforeHighlight"] = DEFAULTTEXTCOLOR
        case "me":
            utypeDict["coloredUser"] = makeColorful(user, COLORME)
            utypeDict["coloredText"] = makeColorful(text, TEXTCOLORME)
            utypeDict["colorBeforeHighlight"] = TEXTCOLORME
    return utypeDict

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

messagesToUpdate = {}
userIds = {}
messageIds = {}

def updateMessageTimer():
    global messagesToUpdate
    while True:
        time.sleep(180)
        timestamp = time.time() // 1
        if messagesToUpdate != {}:
            for msgKey in list(messagesToUpdate.keys()):
                msgTimestamp = messagesToUpdate[msgKey].get("timestamp")
                if timestamp - int(msgTimestamp) >= 180:
                    user = messagesToUpdate[msgKey].get("nick")
                    trip = messagesToUpdate[msgKey].get("trip")
                    text = messagesToUpdate[msgKey].get("text")
                    expiredWarningUser = makeColorful(user, "yellow")
                    expireWarningText = makeColorful(text, "yellow")
                    if trip == None: trip = "null"
                    del(messagesToUpdate[msgKey])
                    show_msg(f"EXPIRED |{getReadableTime(msgTimestamp)}| <{trip}> {expiredWarningUser}: {expireWarningText}")
                else:
                    pass

def main():
    global nickTags, messagesToUpdate, userIds, messageIds
    while ws.connected:
        data = json.loads(ws.recv())
        cmd = data['cmd']
        timestamp = time.time() // 1
        match cmd:
            case 'onlineSet':
                nicks = data['nicks']
                users = data["users"]
                for i in nicks:
                    nickTags.append(f"@{i}")
                for i in users:
                    _id = i.get("userid")
                    _name = i.get("nick")
                    userIds[_id] = _name
                print(COLORS.GREEN, end='')
                show_msg(f"* Users online: {', '.join(nicks)}\n")
                print(COLORS.RESET, end='')
            case 'onlineAdd':
                user = data['nick']
                nicks.append(user)
                nickTags.append(f"@{user}")
                userIds[data.get("userid")] = user
                print(COLORS.GREEN, end='')
                show_msg(f"|{getReadableTime(timestamp)}| * @{user} joined")
                print(COLORS.RESET, end='')
            case 'onlineRemove':
                user = data['nick']
                nicks.remove(user)
                nickTags.remove(f"@{user}")
                del userIds[data.get("userid")]
                print(COLORS.GREEN, end='')
                show_msg(f"|{getReadableTime(timestamp)}| * @{user} left")
                print(COLORS.RESET, end='')
            case 'info':
                text = data['text']
                trip = data.get("trip")
                _from = data.get("from")
                isWhisper = data.get("type") == "whisper"
                ignoreUser = _from in blockedUsers or trip == None
                if _from in blockedUsers and trip != None:
                    text = "{TEXT REMOVED}"
                if trip == None:
                    print(COLORS.GREEN, end='')
                    show_msg(f"|{getReadableTime(timestamp)}| * {text}")
                    print(COLORS.RESET, end='')
                else:
                    print(COLORS.GREEN, end='')
                    show_msg(f"|{getReadableTime(timestamp)}| <{trip}> * {text}")
                    print(COLORS.RESET, end='')
                if NOTIFY and ignoreUser == False and isWhisper and NOTIFYWHISPER == False:
                    playNotification()
                if ignoreUser == False and isWhisper and NOTIFYWHISPER:
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
                isBot = user in botlist
                if ignoreUser:
                    text = blockedUserReplaceText
                else:
                    text = data['text']
                if data.get("customId") != None and ignoreUser == False:
                    customId = data.get("customId")
                    messageIds[customId] = {"text": data.get("text"), "timestamp": timestamp}
                    messagesToUpdate[customId] = {
                        "nick": data.get("nick"),
                        "trip": data.get("trip"),
                        "text": data.get("text"),
                        "timestamp": timestamp,
                        "expired": "false",
                    }
                uType = getUserType(data["level"]) if isMe == False else "me"
                utypeStyle = createUtypeStyle(uType, user, text)
                coloredUser = utypeStyle.get("coloredUser")
                coloredText = utypeStyle.get("coloredText")
                colorBeforeHighlight = utypeStyle.get("colorBeforeHighlight")
                if isBot and isMe == False:
                    coloredUser = makeColorful(user, BOTCOLOR)
                    coloredText = makeColorful(text, BOTTEXTCOLOR)
                    colorBeforeHighlight = BOTTEXTCOLOR
                codeBlockMatches = getCode.findall(text)
                for block in codeBlockMatches:
                    codeBlockLang = block[0]
                    codeBlockCode = block[1]
                    currentCode = getFormattedCode(codeBlockLang, codeBlockCode, mySyntaxStyle)
                    text = text.replace(f"```{codeBlockLang}", '', 1).strip()
                    text = text.replace("```", '', 1).strip()
                    text = text.replace(codeBlockCode, currentCode, 1).strip()
                    coloredText = f"\n{text}"
                singleLineCode = singleLineCodePattern.search(text)
                if bool(singleLineCode):
                    coloredText = re.sub(singleLineCodePattern, rf"{getColor('lightblack', back=True)}\g<code>{getColor('reset', back=True)}", coloredText)
                if COLOREDMENTIONS:
                    coloredText = coloredMention(coloredText)
                if bool(codeBlockMatches) == False and BROWSERSTYLE:
                    coloredText = browserStyle(coloredText, initialColor=colorBeforeHighlight, resetColorAfterHighlight=False)
                if trip != None:
                    if uType == "moderator" and STARS:
                        show_msg(f"|{getReadableTime(timestamp)}| \u2605 <{trip}> {coloredUser}: {coloredText}")
                    else:
                        show_msg(f"|{getReadableTime(timestamp)}| <{trip}> {coloredUser}: {coloredText}")
                else:
                    show_msg(f"|{getReadableTime(timestamp)}| {coloredUser}: {coloredText}")
                notifyMe = NOTIFY == True and isMe == False and ignoreUser == False
                alertMe = bool(re.search(f"@{nick}\\b", text)) and NOTIFYMENTION == True and isMe == False and isBot == False and NOTIFY == False
                if notifyMe:
                    playNotification()
                if alertMe:
                    playNotification()
            case "updateMessage":
                text = data.get("text")
                userId = data.get("userid")
                mode = data.get("mode")
                customId = data.get("customId")
                match mode:
                    case "append":
                        messageIds[customId]["text"] += text
                        messagesToUpdate[customId]["text"] += text
                    case "overwrite":
                        messageIds[customId]["text"] = text
                        messagesToUpdate[customId]["text"] = text
                    case "complete":
                        trip = messagesToUpdate[customId].get("trip")
                        del(messagesToUpdate[customId])
                        isMe = userIds[userId] == str(nick)
                        lastText = text
                        messageIds[customId]["text"] += lastText
                        user = userIds[userId]
                        uType = getUserType(data.get("level")) if isMe == False else "me"
                        textToSend = messageIds[customId]["text"]
                        isBot = user in botlist
                        utypeStyle = createUtypeStyle(uType, user, textToSend)
                        coloredUser = utypeStyle.get("coloredUser")
                        coloredText = utypeStyle.get("coloredText")
                        colorBeforeHighlight = utypeStyle.get("colorBeforeHighlight")
                        if isBot and isMe == False:
                            coloredUser = makeColorful(user, BOTCOLOR)
                            coloredText = makeColorful(textToSend, BOTTEXTCOLOR)
                            colorBeforeHighlight = BOTTEXTCOLOR
                        codeBlockMatches = getCode.findall(textToSend)
                        for block in codeBlockMatches:
                            codeBlockLang = block[0]
                            codeBlockCode = block[1]
                            currentCode = getFormattedCode(codeBlockLang, codeBlockCode, mySyntaxStyle)
                            textToSend = textToSend.replace(f"```{codeBlockLang}", '', 1).strip()
                            textToSend = textToSend.replace("```", '', 1).strip()
                            textToSend = textToSend.replace(codeBlockCode, currentCode, 1).strip()
                            coloredText = f"\n{textToSend}"
                        if bool(codeBlockMatches) == False:
                            coloredText = browserStyle(coloredText, initialColor=colorBeforeHighlight, resetColorAfterHighlight=False)
                        initialMsgTimestamp = messageIds[customId]["timestamp"]
                        if trip != None:
                            if uType == "moderator" and STARS:
                                show_msg(f"|{getReadableTime(initialMsgTimestamp)}| \u2605 <{trip}> {coloredUser}: {coloredText}")
                            else:
                                show_msg(f"|{getReadableTime(initialMsgTimestamp)}| <{trip}> {coloredUser}: {coloredText}")
                        else:
                            show_msg(f"|{getReadableTime(initialMsgTimestamp)}| {coloredUser}: {coloredText}")
                        del(messageIds[customId])
                        if NOTIFY and user not in blockedUsers:
                            playNotification()
                        if NOTIFYMENTION and NOTIFY == False and user not in blockedUsers and isBot == False:
                            playNotification()
            case "captcha":
                uiSession.app.exit()
                exit()

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
    if args.get("no_clear"):
        print_cmdResponse("")
    else:
        clear()
except Exception as ERROR:
    exit("Error connecting: {}".format(ERROR))

p = threading.Thread(target=main, daemon=True)
p.start()
expiredMessageListener = threading.Thread(target=updateMessageTimer, daemon=True)
expiredMessageListener.start()

nickTags = []
blockedUsers = []

ignoreConfigWarnings = False
blockedUserReplaceText = "{TEXT REMOVED}"

MODCOLOR, MODTEXTCOLOR = "green", None
ADMINCOLOR, ADMINTEXTCOLOR = "red", None
DEFAULTCOLOR, DEFAULTTEXTCOLOR = "blue", None
COLORME, TEXTCOLORME = "blue", None
COLOREDMENTIONS = True
NOTIFYMENTION = True
NOTIFYWHISPER = True
BROWSERSTYLE = True
BOTCOLOR, BOTTEXTCOLOR = "blue", None
MENTIONCOLOR = "blue"
STARS = True
WHISPERLOCK = False
botlist = []

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
    except:
        exit()
    if DONOTSAY != []:
        for word in DONOTSAY:
            if word in myText:
                myText = ''
                print_cmdResponse("Message contains words from DONOTSAY - did not send", error=True)
                continue
    isCommand, changingName, _isWhisper = False, False, False
    if bool(re.search(r"^/whisper", myText)): _isWhisper = True
    if bool(re.search(r"^/nick (\w+)$", myText)): changingName = True

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
        if WHISPERLOCK and _isWhisper == False:
            print_cmdResponse("Failed to send message: whisper lock enabled", error=True)
            continue
        send({"cmd": "chat", "text": myText})

    if changingName:
        newNick = re.sub(r"^/nick (?P<nick>\w+)$", r"\g<nick>", myText)
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
                if myText == "--notify":
                    print_cmdResponse(f"Notification status: {NOTIFY}")
                    continue
                notifyCheckStatusPattern = re.compile(r"^--notify (?P<type>mention|whisper)$")
                if bool(notifyCheckStatusPattern.search(myText)):
                    notifyType = notifyCheckStatusPattern.search(myText).group("type")
                    match notifyType:
                        case "mention":
                            print_cmdResponse(f"Mention notification status: {NOTIFYMENTION}")
                        case "whisper":
                            print_cmdResponse(f"Whisper notification status: {NOTIFYWHISPER}")
                notifyPattern = re.compile(r"^--notify (?:(?P<type>mention|whisper)(?:\s))?(?P<action>on|off)$")
                if bool(notifyPattern.search(myText)):
                    notifyType = notifyPattern.search(myText).group("type")
                    notifyAction = notifyPattern.search(myText).group("action")
                    packNotify = (notifyType, notifyAction)
                    match packNotify:
                        case ("mention", "on"):
                            switchStatus = onoffSwitch(True, NOTIFYMENTION)
                            if switchStatus:
                                NOTIFYMENTION = True
                                print_cmdResponse("Mention notifications enabled")
                            else:
                                print_cmdResponse("Mention notifications are already enabled", error=True)
                        case ("mention", "off"):
                            switchStatus = onoffSwitch(False, NOTIFYMENTION)
                            if switchStatus:
                                NOTIFYMENTION = False
                                print_cmdResponse("Mention notifications disabled")
                            else:
                                print_cmdResponse("Mention notifications are already disabled", error=True)
                        case ("whisper", "on"):
                            switchStatus = onoffSwitch(True, NOTIFYWHISPER)
                            if switchStatus:
                                NOTIFYWHISPER = True
                                print_cmdResponse("Whisper notifications enabled")
                            else:
                                print_cmdResponse("Whisper notifications are already enabled", error=True)
                        case ("whisper", "off"):
                            switchStatus = onoffSwitch(False, NOTIFYWHISPER)
                            if switchStatus:
                                NOTIFYWHISPER = False
                                print_cmdResponse("Whisper notifications disabled")
                            else:
                                print_cmdResponse("Whisper notifications are already disabled", error=True)
                        case (None, "on"):
                            switchStatus = onoffSwitch(True, NOTIFY)
                            if switchStatus:
                                NOTIFY = True
                                print_cmdResponse("Notifications enabled")
                            else:
                                print_cmdResponse("Notifications are already enabled", error=True)
                        case (None, "off"):
                            switchStatus = onoffSwitch(False, NOTIFY)
                            if switchStatus:
                                NOTIFY = False
                                print_cmdResponse("Notifications disabled")
                            else:
                                print_cmdResponse("Notifications are already disabled", error=True)
            case "--block":
                properInputChecker = re.compile(r"^--block (?P<users>.*)$")
                isProperInput = bool(properInputChecker.search(myText))
                if isProperInput == False:
                    showHelp("block")
                    continue
                targets = properInputChecker.search(myText).group("users").split()
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
                properInputChecker = re.compile(r"^--unblock (?P<users>.*)$")
                isProperInput = bool(properInputChecker.search(myText))
                if isProperInput == False:
                    showHelp("unblock")
                    continue
                targets = properInputChecker.search(myText).group("users").split()
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
                colorList = "(?P<color>red|blue|green|yellow|magenta|white|black|cyan|lightred|lightblue|lightgreen|lightyellow|lightmagenta|lightcyan)"
                textColorList = colorList.replace(')', '|reset)')
                reUserColor = re.compile(f"^--color (?P<group>admin|mod|user|default|bot|me) {colorList}$")
                reUserTextColor = re.compile(f"^--color text (?P<group>admin|mod|user|default|bot|me) {textColorList}$")
                reUserMentionColor = re.compile(f"^--color mention {textColorList}$")
                isUserColor = bool(reUserColor.search(myText))
                isTextColor = bool(reUserTextColor.search(myText))
                isMentionColor = bool(reUserMentionColor.search(myText))
                if isUserColor:
                    groupToColor = reUserColor.search(myText).group("group")
                    colorToUse = reUserColor.search(myText).group("color")
                    match groupToColor:
                        case "admin":
                            ADMINCOLOR = colorToUse
                        case "mod":
                            MODCOLOR = colorToUse
                        case "user" | "default":
                            DEFAULTCOLOR = colorToUse
                        case "bot":
                            BOTCOLOR = colorToUse
                        case "me":
                            COLORME = colorToUse
                    print_cmdResponse("New color set")
                elif isTextColor:
                    groupToColor = reUserTextColor.search(myText).group("group")
                    colorToUse = reUserTextColor.search(myText).group("color")
                    match groupToColor:
                        case "admin":
                            ADMINTEXTCOLOR = colorToUse
                        case "mod":
                            MODTEXTCOLOR = colorToUse
                        case "user" | "default":
                            DEFAULTTEXTCOLOR = colorToUse
                        case "bot":
                            BOTTEXTCOLOR = colorToUse
                        case "me":
                            TEXTCOLORME = colorToUse
                    print_cmdResponse("New color set")
                elif isMentionColor:
                    colorToUse = reUserMentionColor.search(myText).group("color")
                    MENTIONCOLOR = colorToUse
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
            case "--nl":
                # that's all :-)
                print_cmdResponse("")
            case "--mentions":
                mentionsPattern = re.compile("^--mentions (?P<action>on|off)$")
                if bool(re.search(mentionsPattern, myText)):
                    mentionOption = re.search(mentionsPattern, myText).group("action")
                    if mentionOption == "on":
                        switchStatus = onoffSwitch(True, COLOREDMENTIONS)
                        if switchStatus:
                            COLOREDMENTIONS = True
                            print_cmdResponse("Colored mentions enabled")
                        else:
                            print_cmdResponse("Colored mentions are already enabled", error=True)
                    if mentionOption == "off":
                        switchStatus = onoffSwitch(False, COLOREDMENTIONS)
                        if switchStatus:
                            COLOREDMENTIONS = False
                            print_cmdResponse("Colored mentions disabled")
                        else:
                            print_cmdResponse("Colored mentions are already disabled", error=True)
                else:
                    print_cmdResponse("Colored mentions status: {}".format(COLOREDMENTIONS))
            case "--browserstyle":
                if myText == "--browserstyle":
                    print_cmdResponse(f"Browser style status: {BROWSERSTYLE}")
                    continue
                browserStylePattern = re.compile("^--browserstyle (?P<action>on|off)$")
                if bool(re.search(browserStylePattern, myText)):
                    userAction = re.search(browserStylePattern, myText).group("action")
                    if userAction == "on":
                        switchStatus = onoffSwitch(True, BROWSERSTYLE)
                        if switchStatus:
                            BROWSERSTYLE = True
                            print_cmdResponse("Browser style enabled")
                        else:
                            print_cmdResponse("Browser style is already enabled", error=True)
                    elif userAction == "off":
                        switchStatus = onoffSwitch(False, BROWSERSTYLE)
                        if switchStatus:
                            BROWSERSTYLE = False
                            print_cmdResponse("Browser style disabled")
                        else:
                            print_cmdResponse("Browser style is already disabled")
            case "--addbot":
                addbotPattern = re.compile("^--addbot (?P<nicks>.*)$")
                if bool(addbotPattern.search(myText)):
                    addbotNicks = addbotPattern.search(myText).group("nicks").split()
                    for bot in addbotNicks:
                        botlist.append(bot)
                    print_cmdResponse("Added users to botlist")
                else:
                    showHelp("addbot")
            case "--removebot":
                removebotPattern = re.compile("^--removebot (?P<nicks>.*)$")
                if bool(removebotPattern.search(myText)):
                    removebotNicks = removebotPattern.search(myText).group("nicks").split()
                    for bot in removebotNicks:
                        if bot in botlist:
                            botlist.remove(bot)
                    botlistStr = ", ".join(botlist)
                    print_cmdResponse(f"Removed users from botlist, current botlist: {botlistStr}")
                else:
                    showHelp("removebot")
            case "--botlist":
                botlistStr = ", ".join(botlist)
                print_cmdResponse(f"Bot list: {botlistStr}")
            case "--stars":
                if myText == "--stars":
                    print_cmdResponse(f"Star status: {STARS}")
                    continue
                starsPattern = re.compile(r"^--stars (?P<action>on|off)$")
                if bool(starsPattern.search(myText)):
                    starAction = starsPattern.search(myText).group("action")
                    match starAction:
                        case "on":
                            switchStatus = onoffSwitch(True, STARS)
                            if switchStatus:
                                STARS = True
                                print_cmdResponse("Enabled stars")
                            else:
                                print_cmdResponse("Stars are already enabled", error=True)
                        case "off":
                            switchStatus = onoffSwitch(False, STARS)
                            if switchStatus:
                                STARS = False
                                print_cmdResponse("Stars disabled")
                            else:
                                print_cmdResponse("Stars are already disabled", error=True)
            case "--whisperlock":
                if myText == "--whisperlock":
                    print_cmdResponse(f"Whisper lock status: {WHISPERLOCK}")
                    continue
                whisperlockPattern = re.compile("^--whisperlock (?P<action>on|off)$")
                if bool(whisperlockPattern.search(myText)):
                    whisperlockAction = whisperlockPattern.search(myText).group("action")
                    match whisperlockAction:
                        case "on":
                            switchStatus = onoffSwitch(True, WHISPERLOCK)
                            if switchStatus:
                                WHISPERLOCK = True
                                print_cmdResponse("Whisper lock enabled")
                            else:
                                print_cmdResponse("Whisper lock is already enabled", error=True)
                        case "off":
                            switchStatus = onoffSwitch(False, WHISPERLOCK)
                            if switchStatus:
                                WHISPERLOCK = False
                                print_cmdResponse("Whisper lock disabled")
                            else:
                                print_cmdResponse("Whisper lock is already disabled")
            case "--help":
                if myText == "--help":
                    showHelp()
                else:
                    helpArg = myText.replace("--help ", '')
                    showHelp(helpArg)
