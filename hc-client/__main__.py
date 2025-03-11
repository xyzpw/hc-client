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

parser = argparse.ArgumentParser(
    add_help=False,
)
parser.add_argument("--help", "-h", help="display help and exit", action="help")
parser.add_argument("--nick", help="username to use when joining a channel", dest="_nick", metavar="<nick>")
parser.add_argument("--channel", help="name of channel to join", dest="_channel", metavar="<channel>")
parser.add_argument("--no-clear", help="prevents the screen from clearing after joining a channel", action="store_true")
parser.add_argument("--no-stars", help=argparse.SUPPRESS, action="store_true")
parser.add_argument("--reset-config", help="reset the user config and exit", action="store_true")
parser.add_argument("--localhost", help="changes websocket target to localhost", action="store_true")
args = parser.parse_args()
args = vars(args)

configName = "hc-client-config.json"
hasConfig = pathlib.Path(configName).exists()
resetConfig = args.get("reset_config")
if resetConfig:
    if args.get("_nick") != None or args.get("_channel") != None:
        print("warning: you can not join channels with the 'reset-config' flag")
    if not hasConfig:
        raise SystemExit("failed to reset config: config file does not exist")
    try:
        resetConfigConfirmation = input("Remove all config settings to default? [y/N] ")
        if not resetConfigConfirmation.startswith('y'):
            print("config was not reset: operation cancelled")
            raise SystemExit(0)
        defaultConfig = {
            "ignoreConfigWarnings": "0",
            "passwordProtection": "1",
        }
        with open(configName, 'w') as myConfig:
            myConfig.write(json.dumps(defaultConfig, indent=4))
        print("successfully reset user config")
        raise SystemExit(0)
    except (KeyboardInterrupt, EOFError):
        raise SystemExit(0)
    except Exception as ERROR:
        raise SystemExit(ERROR)

colorama.init()
bindings = prompt_toolkit.key_binding.KeyBindings()
run_in_terminal = prompt_toolkit.application.run_in_terminal
uiSession = prompt_toolkit.PromptSession()

allSyntaxStyles = list(get_all_styles())

getCode = re.compile(r"```(?P<lang>.*?)?\n(?P<code>.*?)\n?(?:```|\Z)", re.DOTALL)
singleLineCodePattern = re.compile(r"`(?P<code>.{1,}?)`")

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
        os.system(r"printf '\e3J' && clear")
    else:
        os.system("clear" if os.name != "nt" else "cls")

config = {}
if hasConfig:
    try:
        with open(configName, 'r') as myConfig:
            config = json.loads(myConfig.read())
    except Exception as ERROR:
        raise SystemExit(ERROR)

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
    mynickcolor => sends '/color <hex>' subsequent to joining channels
    """
    global config, DONOTSAY, ignoreConfigWarnings, blockedUserReplaceText, blockedUsers, ADMINCOLOR, MODCOLOR, DEFAULTCOLOR, COLORME, BOTCOLOR, mySyntaxStyle, botlist, NOTIFYMENTION, MENTIONCOLOR, NOTIFYWHISPER, STARS, myNickColor
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
        myNickColor = config.get("mynickcolor")


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
    "help": "Usage:\n\thelp [command]\nDescription:\n\tShows this message or usage for other commands if specified.",
    "clear": "Clears the screen.",
    "notify": "Usage:\n\tnotify [[mention | whisper] (on | off)]\nDescription:\n\tAllows the ability to enable or disable notification alerts.",
    "blocklist": "Usage:\n\tblocklist [(add | remove) <user...>]\n\tDescription:\n\tAssigns specified users to blocklist. Messages received from users within the blocklist will be replaced with a custom message and will not trigger notification alerts.",
    "color": "Usage:\n\tcolor [text | mention] group color\nDescription:\n\tChanges the color of users, text, or mentions.\n\tLight colors can be used too. E.g. \"lightred.\"\nArguments:\n\tgroup    (admin | mod | user | bot | me)\n\tcolor    (red | blue | green | yellow | magenta | white | cyan)",
    "syntaxstyle": "Usage:\n\tsyntaxstyle [style]\nDescription:\n\tThe style argument will set the syntaxstyle, otherwise it will display a list of all styles (large).",
    "config": "Returns limited information for the user config. To display the full config, you must enable \"ignoreConfigWarnings\" in the config file.",
    "nl": "Prints a few newlines to the screen. Nothing more.",
    "mentions": "Usage:\n\tmentions [on | off]\nDescription:\n\tMentioned users within text will be highlighted.",
    "browserstyle": "Usage:\n\tbrowserstyle [on | off]\nDescription:\n\tDisplays output as browser style.",
    "botlist": "Usage:\n\tbotlist [(add | remove) <user...>]\nDescription:\n\tSpecified users will be treated as bots.",
    "stars": "Usage:\n\tstars [on | off]\nDescription:\n\tModerators and admins will have a star alongside their trip if enabled.",
    "whisperlock": "Usage:\n\twhisperlock [on | off]\nDescription:\n\tDisables the ability to send any messages other than whispers.",
    "group": "Usage:\n\tgroup <group_name> [(add | remove) <user> | rename <new_name>]\nDescription:\n\tAssign a specified user to a customizable group.",
    "reset": "Usage:\n\treset (color | textcolor | notify | syntaxstyle | mentions | coloredmentions | botlist | stars | whisperlock | browserstyle)\nDescription:\n\tResets options to their default values.",
    "groupcmd": f"Usage:\n\tgroupcmd <group_name> [cmd arg]\nDescription:\n\tAllows the ability to customize a specified customizable group.\nArguments:\n\t[text | mention] color: {' '*15}changes the color of text, mentions, or names\n\tnotify [mention | whisper] (on | off): allows the ability to get notified when receiving messages\n\tblock (on | off): {' '*21}blocks all users within specified group",
    "uptime": "Usage:\n\tuptime [-p]\nDescription:\n\tDisplays the uptime of the client.",
}

NOTIFY = False

def send(msg: str):
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
            print_cmdResponse(f"command not found: {command}", error=True)

def removeUnwantedChars(text):
    if not bool(re.search(r"(?:\s|\!|\?|\.)", text)):
        return text
    if bool(re.search(r"(?:\s{2,})", text)):
        text = re.sub(r"\s{2,}", " ", text)
    makePattern = lambda val: rf"\{val}{{4,}}"
    charsToSearch = ['!', '?', '.']
    for char in charsToSearch:
        text = re.sub(makePattern(char), char * 3, text)
    text = re.sub(r"\,{2,}", ',', text)
    return text.strip()

def browserStyle(text, initialColor, resetColorAfterHighlight=True):
    if re.search(r"^>.*?$", text):
        return text
    #NOTE: some terminals don't have support for these
    makePattern = lambda val: rf"(?<!(?:`|<|@)){val}(?!\s|\\)(?P<sentence>[^`]*?)(?<!\s|\\){val}(?!(?:\x1b|`|>))"
    makeSingleCharPattern = lambda val: rf"(?<!`|<|@)(?<!{val}){val}(?!{val})(?!\s|\\)(?P<sent>[^`]*?)(?<!\s|\\){val}(?!{val})(?!`|>|@)"
    text = re.sub(makePattern("__"), "\x1b[1m" + r"\g<sentence>" + "\x1b[22m", text)
    text = re.sub(makeSingleCharPattern("_"), "\x1b[3m" + r"\g<sent>" + "\x1b[23m", text)
    text = re.sub(makePattern(r"\*\*"), "\x1b[1m" + r"\g<sentence>" + "\x1b[22m", text)
    text = re.sub(makeSingleCharPattern(r"\*"), "\x1b[3m" + r"\g<sent>" + "\x1b[23m", text)
    text = re.sub(makePattern("~~"), "\x1b[9m" + r"\g<sentence>" + "\x1b[29m", text)
    text = removeUnwantedChars(text)
    text = re.sub(r"(?<!\S)--(?!\S)", "\u2013", text) # en dash
    text = re.sub(r"\(tm\)", "\u2122", text, flags=(re.MULTILINE | re.DOTALL | re.IGNORECASE))
    text = re.sub(r"\(c\)", '\u00a9', text, flags=(re.MULTILINE | re.DOTALL | re.IGNORECASE))
    text = re.sub(r"\(r\)", "\u00AE", text, flags=(re.MULTILINE | re.DOTALL | re.IGNORECASE))
    if resetColorAfterHighlight:
        text = re.sub(makePattern("=="), f"{colorama.Back.GREEN}{getColor('black')}" + r"\g<sentence>" + f"{colorama.Back.RESET}{getColor('reset')}", text)
    else:
        text = re.sub(makePattern("=="), f"{colorama.Back.GREEN}{getColor('black')}" + r"\g<sentence>" + f"{colorama.Back.RESET}{getColor(initialColor)}", text)
    return text

def makeColorful(text, color):
    if color == None:
        return text
    colorName = getColor(color)
    resetCode = getColor("reset")
    coloredText = f"{colorName}{text}{resetCode}"
    return coloredText

def coloredMention(text, customColor=None):
    colorToUse = MENTIONCOLOR if customColor == None else customColor
    mentionedUsers = re.findall(r"(?!\b)(@\w+)", text)
    if bool(mentionedUsers):
        for mentionedUser in mentionedUsers:
            text = text.replace(mentionedUser, f"{getColor(colorToUse, back=True)}{mentionedUser}{getColor('reset', back=True)}")
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

def botlistCmd(user, cmd):
    global botlist
    match cmd:
        case "add":
            if user in botlist:
                return False
            botlist.append(user)
            return True
        case "remove":
            if user not in botlist:
                return False
            botlist.remove(user)
            return True

def resetCmd(cmd):
    global MODCOLOR, ADMINCOLOR, DEFAULTCOLOR, MODTEXTCOLOR, ADMINTEXTCOLOR, DEFAULTTEXTCOLOR, NOTIFY, mySyntaxStyle, NOTIFYMENTION, COLOREDMENTIONS, botlist, STARS, WHISPERLOCK, TEXTCOLORME, BROWSERSTYLE, COLORME
    match cmd:
        case "color":
            MODCOLOR = "green"
            ADMINCOLOR = "red"
            DEFAULTCOLOR = "blue"
            COLORME = "blue"
        case "textcolor":
            MODTEXTCOLOR = "reset"
            ADMINTEXTCOLOR = "reset"
            DEFAULTTEXTCOLOR = "reset"
            TEXTCOLORME = "reset"
        case "notify":
            NOTIFY = False
        case "syntaxstyle":
            mySyntaxStyle = "monokai"
        case "mentions":
            NOTIFYMENTION = True
        case "coloredmentions":
            COLOREDMENTIONS = True
        case "botlist":
            botlist = []
        case "stars":
            STARS = True
        case "whisperlock":
            WHISPERLOCK = False
        case "browserstyle":
            BROWSERSTYLE = True
        case _:
            raise ValueError("unknown cmd")

customGroupsWithStatus = {
    "groupsWithNotifyStatus": {},
    "groupsWithColorStatus": {},
    "groupsWithTextColorStatus": {},
    "groupsWithMentionColorStatus": {},
    "groupsWithMentionsStatus": {},
    "groupsWithNotifyMentionStatus": {},
    "groupsWithNotifyWhisperStatus": {},
}

usersInGroups = {}
def getUsersGroupName(user):
    if user not in usersInGroups:
        return None
    return usersInGroups.get(user)
def playNotificationByStatus(user):
    return customGroupsWithStatus["groupsWithNotifyStatus"].get(getUsersGroupName(user))
def playWhisperNotificationByStatus(user):
    return customGroupsWithStatus["groupsWithNotifyWhisperStatus"].get(getUsersGroupName(user))
def playMentionNotificationByStatus(user):
    return customGroupsWithStatus["groupsWithNotifyMentionStatus"].get(getUsersGroupName(user))
def changeColorByStatus(user):
    return customGroupsWithStatus["groupsWithColorStatus"].get(getUsersGroupName(user))
def changeTextColorByStatus(user):
    return customGroupsWithStatus["groupsWithTextColorStatus"].get(getUsersGroupName(user))
def changeMentionColorByStatus(user):
    return customGroupsWithStatus["groupsWithMentionColorStatus"].get(getUsersGroupName(user))
def customGroupHasColoredMentions(user):
    return customGroupsWithStatus["groupsWithMentionsStatus"].get(getUsersGroupName(user))

def setColorWithGroup(_group, _color):
    global COLORME, DEFAULTCOLOR, MODCOLOR, ADMINCOLOR, BOTCOLOR
    match _group:
        case "me":
            COLORME = _color if _color != "reset" else "blue"
        case "default" | "user":
            DEFAULTCOLOR = _color if _color != "reset" else "blue"
        case "mod" | "moderator":
            MODCOLOR = _color if _color != "reset" else "green"
        case "admin":
            ADMINCOLOR = _color if _color != "reset" else "red"
        case "bot":
            BOTCOLOR = _color if _color != "reset" else "blue"

def setTextColorWithGroup(_group, _color):
    global TEXTCOLORME, DEFAULTTEXTCOLOR, MODTEXTCOLOR, ADMINTEXTCOLOR, BOTTEXTCOLOR
    match _group:
        case "me":
            TEXTCOLORME = _color
        case "default" | "user":
            DEFAULTTEXTCOLOR = _color
        case "mod" | "moderator":
            MODTEXTCOLOR = _color
        case "admin":
            ADMINTEXTCOLOR = _color
        case "bot":
            BOTTEXTCOLOR = _color

def setMentionColor(_color):
    global MENTIONCOLOR
    MENTIONCOLOR = _color

def userGroupLookup(user):
    if user not in usersInGroups:
        return False
    groupName = usersInGroups.get(user)
    groupColor = customGroups[groupName].get("color")
    groupTextColor = customGroups[groupName].get("textcolor")
    groupNotify = customGroups[groupName].get("notify")
    return groupName, groupColor, groupTextColor, groupNotify

def getGroupBlockedStatus(groupName):
    if customGroups.get(groupName) != None:
        if customGroups[groupName].get("block"):
            return True
    return False

def isUserFromBlockedGroup(user):
    usersGroup = getUsersGroupName(user)
    if usersGroup == None:
        return False
    if getGroupBlockedStatus(usersGroup):
        return True
    return False

def uptimeTimeFormat(seconds: int):
    if isinstance(seconds, float):
        seconds = int(seconds)
    hoursElapsed = seconds // 3600
    minutesElapsed = (seconds - (hoursElapsed*3600)) // 60
    secondsElapsed = seconds - (hoursElapsed*3600 + minutesElapsed*60)
    if hoursElapsed < 10:
        hoursElapsed = f"0{hoursElapsed}"
    if minutesElapsed < 10:
        minutesElapsed = f"0{minutesElapsed}"
    if secondsElapsed < 10:
        secondsElapsed = f"0{seconds}"
    return f"{hoursElapsed}:{minutesElapsed}:{secondsElapsed}"

def uptimePretty(seconds: int):
    if isinstance(seconds, float):
        seconds = int(seconds)
    days = seconds // 86400
    hours = (seconds - days*86400) // 3600
    minutes = (seconds - (days*86400 + hours*3600)) // 60
    result = '?'
    if days > 0:
        displayHours = (seconds - days*86400) > 3600
        if displayHours:
            result = f"up {days} days, {hours} hours, {minutes} minutes"
        else:
            result = f"up {days} days, {minutes} minutes"
    elif hours > 0:
        result = f"up {hours} hours, {minutes} minutes"
    elif minutes > 0:
        result = f"up {minutes} minutes"
    else:
        result = f"up {seconds} seconds"
    return result

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
    raise SystemExit(0)
except Exception as ERROR:
    raise SystemExit(ERROR)

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
                try:
                    for it in dict(userIds):
                        if userIds[it] == user:
                            del userIds[it]
                        del it
                except:
                    pass
                print(COLORS.GREEN, end='')
                show_msg(f"|{getReadableTime(timestamp)}| * @{user} left")
                print(COLORS.RESET, end='')
            case 'info':
                text = data['text']
                if BROWSERSTYLE:
                    text = browserStyle(text, initialColor="green", resetColorAfterHighlight=False)
                trip = data.get("trip")
                _from = data.get("from")
                isMe = _from == nick
                isBot = _from in botlist
                isWhisper = data.get("type") == "whisper"
                ignoreUser = _from in blockedUsers or isUserFromBlockedGroup(_from) or trip == None
                if (_from in blockedUsers or isUserFromBlockedGroup(_from)) and trip != None:
                    text = blockedUserReplaceText
                if trip == None:
                    print(COLORS.GREEN, end='')
                    show_msg(f"|{getReadableTime(timestamp)}| * {text}")
                    print(COLORS.RESET, end='')
                else:
                    print(COLORS.GREEN, end='')
                    show_msg(f"|{getReadableTime(timestamp)}| <{trip}> * {text}")
                    print(COLORS.RESET, end='')
                if isWhisper:
                    if isBot or isMe:
                        continue
                    notifyMe = (NOTIFYWHISPER and not (ignoreUser or isMe)) or (playWhisperNotificationByStatus(_from) and not (ignoreUser or isMe))
                    if notifyMe:
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
                ignoreUser = user in blockedUsers or isUserFromBlockedGroup(user)
                if ignoreUser:
                    text = blockedUserReplaceText
                else:
                    text = data.get("text")
                    if text != None and BROWSERSTYLE:
                        text = browserStyle(text, initialColor="green", resetColorAfterHighlight=False)
                if trip == None:
                    trip = "null"
                print(COLORS.GREEN, end='')
                show_msg(f"|{getReadableTime(timestamp)}| <{trip}> * {text}")
                print(COLORS.RESET, end='')
                notifyMe = (NOTIFY or playNotificationByStatus(user)) and not ignoreUser
                if notifyMe and not isMe:
                    playNotification()
                elif playNotificationByStatus(user) and not isMe:
                    playNotification()
            case 'chat':
                user = data['nick']
                trip = data.get("trip")
                isMe = str(user) == str(nick)
                coloredUser = user
                ignoreUser = user in blockedUsers or isUserFromBlockedGroup(user)
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
                if user in usersInGroups:
                    groupName, groupColor, groupTextColor, groupNotify = userGroupLookup(user)
                    coloredUser = makeColorful(user, groupColor) if groupColor != None else utypeStyle.get("coloredUser")
                    coloredText = makeColorful(text, groupTextColor) if groupTextColor != None else utypeStyle.get("coloredText")
                    colorBeforeHighlight = groupTextColor if groupTextColor != None else utypeStyle.get("colorBeforeHighlight")
                else:
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
                    coloredText = re.sub(singleLineCodePattern, rf"{getColor('lightblack', back=True)}" + r"\g<code>" + f"{getColor('reset', back=True)}", coloredText)
                if COLOREDMENTIONS or customGroupHasColoredMentions(user):
                    _colorToUse = MENTIONCOLOR
                    if user in usersInGroups:
                        usersGroupName = getUsersGroupName(user)
                        groupHasMentionColorStatus = True if customGroupsWithStatus["groupsWithMentionColorStatus"].get(usersGroupName) != None else False
                        if groupHasMentionColorStatus:
                            _colorToUse = customGroups[usersGroupName].get("mentioncolor")
                    coloredText = coloredMention(coloredText, _colorToUse)
                if bool(codeBlockMatches) == False and BROWSERSTYLE:
                    coloredText = browserStyle(coloredText, initialColor=colorBeforeHighlight, resetColorAfterHighlight=False)
                if trip != None:
                    if uType in ["moderator", "admin"] and STARS:
                        show_msg(f"|{getReadableTime(timestamp)}|{getColor('yellow')}\u2605{getColor('reset')}<{trip}> {coloredUser}: {coloredText}")
                    else:
                        show_msg(f"|{getReadableTime(timestamp)}| <{trip}> {coloredUser}: {coloredText}")
                else:
                    show_msg(f"|{getReadableTime(timestamp)}| {coloredUser}: {coloredText}")
                notifyMe = NOTIFY == True and isMe == False and ignoreUser == False
                alertMe = bool(re.search(f"@{nick}\\b", text)) and NOTIFYMENTION == True and isMe == False and isBot == False and NOTIFY == False
                if notifyMe or alertMe:
                    playNotification()
                elif (playNotificationByStatus(user) or playMentionNotificationByStatus(user)) and not isMe:
                    playNotification()
            case "updateMessage":
                if data.get("customId") == None:
                    pass
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
                        if user in usersInGroups:
                            groupName, groupColor, groupTextColor, groupNotify = userGroupLookup(user)
                            coloredUser = makeColorful(user, groupColor) if groupColor != None else utypeStyle.get("coloredUser")
                            coloredText = makeColorful(textToSend, groupTextColor) if groupTextColor != None else utypeStyle.get("coloredText")
                            colorBeforeHighlight = groupTextColor if groupTextColor != None else utypeStyle.get("colorBeforeHighlight")
                        else:
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
                        singleLineCode = singleLineCodePattern.search(textToSend)
                        if bool(singleLineCode):
                            coloredText = re.sub(singleLineCodePattern, rf"{getColor('lightblack', back=True)}" + r"\g<code>" + f"{getColor('reset', back=True)}", coloredText)
                        if COLOREDMENTIONS or customGroupHasColoredMentions(user):
                            _colorToUse = MENTIONCOLOR
                            if user in usersInGroups:
                                usersGroupName = getUsersGroupName(user)
                                groupHasMentionColorStatus = True if customGroupsWithStatus["groupsWithMentionColorStatus"] != None else False
                                if groupHasMentionColorStatus:
                                    _colorToUse = customGroups[usersGroupName].get("mentioncolor")
                            coloredText = coloredMention(coloredText, _colorToUse)
                        if bool(codeBlockMatches) == False and BROWSERSTYLE:
                            coloredText = browserStyle(coloredText, initialColor=colorBeforeHighlight, resetColorAfterHighlight=False)
                        initialMsgTimestamp = messageIds[customId]["timestamp"]
                        if trip != None:
                            if uType in ["moderator", "admin"] and STARS:
                                show_msg(f"|{getReadableTime(initialMsgTimestamp)}|{getColor('yellow')}\u2605{getColor('reset')}<{trip}> {coloredUser}: {coloredText}")
                            else:
                                show_msg(f"|{getReadableTime(initialMsgTimestamp)}| <{trip}> {coloredUser}: {coloredText}")
                        else:
                            show_msg(f"|{getReadableTime(initialMsgTimestamp)}| {coloredUser}: {coloredText}")
                        del(messageIds[customId])
                        notifyMe = NOTIFY and user not in blockedUsers
                        alertMe = NOTIFYMENTION and NOTIFY == False and user not in blockedUsers and isBot == False
                        if notifyMe or alertMe:
                            playNotification()
                        elif (playNotificationByStatus(user) or playMentionNotificationByStatus(user)) and not isMe:
                            playNotification()
            case "captcha":
                uiSession.app.exit()
                raise SystemExit(0)

DONOTSAY = []
ws = websocket.WebSocket()
if args.get("localhost"):
    ws_address = "ws://127.0.0.1:6060/" #NOTE: follow installation: https://github.com/hack-chat/main?tab=readme-ov-file#developer-installation
else:
    ws_address = "wss://hack.chat/chat-ws"
try:
    ws.connect(ws_address)
    if '#' in nick:
        myPassword = nick[nick.find("#")+1:]
        if config.get("passwordProtection") == "1":
            DONOTSAY.append(myPassword)
        send({"cmd": "join", "channel": channel, "nick": nick})
        nick = nick[:nick.find('#')]
        if myPassword in nick:
            raise SystemExit(f"{COLORS.RED}Password was not removed from name. Terminating script.{COLORS.RESET}")
        del(myPassword)
    else:
        send({"cmd": "join", "channel": channel, "nick": nick})
    if args.get("no_clear"):
        print_cmdResponse("")
    else:
        clear()
except Exception as ERROR:
    raise SystemError("could not connect to websocket: {}".format(ERROR))
connected_epoch = int(time.time())

blockedUsers = []
# botlist = []
# nickTags = []
# p = threading.Thread(target=main, daemon=True)
# p.start()
# expiredMessageListener = threading.Thread(target=updateMessageTimer, daemon=True)
# expiredMessageListener.start()

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
nickTags = []
customGroups = dict()
myNickColor = None

mySyntaxStyle = "monokai"

commandPrefix = "--"

p = threading.Thread(target=main, daemon=True)
p.start()
expiredMessageListener = threading.Thread(target=updateMessageTimer, daemon=True)
expiredMessageListener.start()

try:
    checkConfig()
except Exception as ERROR:
    raise SystemExit("failed to write config: {}".format(ERROR))
if isinstance(myNickColor, str):
    myNickColor = myNickColor.replace('#', '').upper()
    if re.search(r"(?:[A-F0-9]{3}|[A-F0-9{6}])", myNickColor):
        send({"cmd": "chat", "text": f"/color {myNickColor}"})
    else:
        print_cmdResponse("custom nick color is not a valid hex code - did not send message\n\n\n", error=True)
elif myNickColor != None:
    print_cmdResponse("custom nick color must be a string - did not send message\n\n\n", error=True)

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
                print("terminating script...")
                raise SystemExit(0)
            exitAttempt = True
            print("press ^C again to exit")
        else:
            raise SystemExit(0)
    except:
        raise SystemExit(0)
    if DONOTSAY != []:
        for word in DONOTSAY:
            if word in myText:
                myText = ''
                print_cmdResponse("Message contained words from DONOTSAY - did not send.", error=True)
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
        print_cmdResponse(f"command not found: {failedCommandName}", error=True)
    isSendableMessage = isCommand == False and failedCommand == False and changingName == False

    if myText != '' and isSendableMessage:
        if WHISPERLOCK and _isWhisper == False:
            print_cmdResponse("failed to send message: whisper lock enabled", error=True)
            continue
        send({"cmd": "chat", "text": myText})

    if changingName:
        newNick = re.sub(r"^/nick (?P<nick>\w{1,24})$", r"\g<nick>", myText)
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
                    print_cmdResponse(f"notification status: {NOTIFY}")
                    continue
                notifyCheckStatusPattern = re.compile(r"^--notify (?P<type>mention|whisper)$")
                if bool(notifyCheckStatusPattern.search(myText)):
                    notifyType = notifyCheckStatusPattern.search(myText).group("type")
                    match notifyType:
                        case "mention":
                            print_cmdResponse(f"mention notification status: {NOTIFYMENTION}")
                        case "whisper":
                            print_cmdResponse(f"whisper notification status: {NOTIFYWHISPER}")
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
                                print_cmdResponse("mention notifications enabled")
                            else:
                                print_cmdResponse("mention notifications are already enabled", error=True)
                        case ("mention", "off"):
                            switchStatus = onoffSwitch(False, NOTIFYMENTION)
                            if switchStatus:
                                NOTIFYMENTION = False
                                print_cmdResponse("mention notifications disabled")
                            else:
                                print_cmdResponse("mention notifications are already disabled", error=True)
                        case ("whisper", "on"):
                            switchStatus = onoffSwitch(True, NOTIFYWHISPER)
                            if switchStatus:
                                NOTIFYWHISPER = True
                                print_cmdResponse("whisper notifications enabled")
                            else:
                                print_cmdResponse("whisper notifications are already enabled", error=True)
                        case ("whisper", "off"):
                            switchStatus = onoffSwitch(False, NOTIFYWHISPER)
                            if switchStatus:
                                NOTIFYWHISPER = False
                                print_cmdResponse("whisper notifications disabled")
                            else:
                                print_cmdResponse("whisper notifications are already disabled", error=True)
                        case (None, "on"):
                            switchStatus = onoffSwitch(True, NOTIFY)
                            if switchStatus:
                                NOTIFY = True
                                print_cmdResponse("notifications enabled")
                            else:
                                print_cmdResponse("notifications are already enabled", error=True)
                        case (None, "off"):
                            switchStatus = onoffSwitch(False, NOTIFY)
                            if switchStatus:
                                NOTIFY = False
                                print_cmdResponse("notifications disabled")
                            else:
                                print_cmdResponse("notifications are already disabled", error=True)
            case "--blocklist":
                isEmpty = len(blockedUsers) == 0
                if myText == "--blocklist" and isEmpty:
                    print_cmdResponse("no users in blocklist")
                    continue
                elif myText == "--blocklist":
                    print_cmdResponse("blocked users: {}".format(", ".join(blockedUsers)))
                    continue
                blocklistCmdSearch = re.search(r"^--blocklist (?P<cmd>add|remove) (?P<users>.*)$", myText)
                if not bool(blocklistCmdSearch):
                    print_cmdResponse("incorrect usage", error=True)
                    continue
                blocklistCmd = blocklistCmdSearch.group("cmd")
                blocklistUsers = blocklistCmdSearch.group("users").split(" ")
                if blocklistCmd == "add":
                    userAddCount = 0
                    for target in blocklistUsers:
                        if target not in blockedUsers:
                            blockedUsers.append(target)
                            userAddCount += 1
                    if userAddCount < 1:
                        print_cmdResponse("blocklist was not updated: no users added")
                    else:
                        print_cmdResponse("added {} users to blocklist".format(userAddCount))
                elif blocklistCmd == "remove":
                    userRemoveCount = 0
                    for target in blocklistUsers:
                        if target in blockedUsers:
                            blockedUsers.remove(target)
                            userRemoveCount += 1
                    if userRemoveCount < 1:
                        print_cmdResponse("blocklist was not updated: no users were removed")
                    else:
                        print_cmdResponse("removed {} users from blocklist".format(userRemoveCount))
            case "--config":
                isEmpty = config == {}
                if isEmpty:
                    print_cmdResponse("custom config is empty")
                    continue
                if ignoreConfigWarnings:
                    print_cmdResponse(config)
                else:
                    unsafeKeys = ['DONOTSAY', 'nick']
                    safeConfig = {}
                    for key in config:
                        if key not in unsafeKeys:
                            safeConfig[key] = config.get(key)
                    print_cmdResponse("Some keys are not shown. To show all keys, change \"ignoreConfigWarnings\" to 1.", warning=True)
                    print_cmdResponse(safeConfig)
            case "--color":
                if myText == "--color":
                    showHelp("color")
                    continue
                colorCmdSearch = re.search(r"^--color\s(?:(?P<type>text|mention)(?=\s)\s?)?(?P<group>admin|mod|user|default|bot|me) (?P<color>red|blue|green|yellow|magenta|white|black|cyan|lightred|lightblue|lightgreen|lightyellow|lightmagenta|lightcyan|reset)$", myText)
                if not bool(colorCmdSearch):
                    print_cmdResponse("Invalid usage. See help for more info.", error=True)
                    continue
                colorCmdType = colorCmdSearch.group("type")
                colorCmdGroup = colorCmdSearch.group("group")
                colorCmdColor = colorCmdSearch.group("color")
                wasSuccessfull = False
                match colorCmdType:
                    case None:
                        setColorWithGroup(colorCmdGroup, colorCmdColor)
                        wasSuccessful = True
                    case "text":
                        setTextColorWithGroup(colorCmdGroup, colorCmdColor)
                        wasSuccessful = True
                    case "mention":
                        setMentionColor(colorCmdColor)
                        wasSuccessful = True
                if not wasSuccessful:
                    print_cmdResponse("color not set", warning=True)
                else:
                    print_cmdResponse("new color set")
            case "--syntaxstyle":
                if myText == "--syntaxstyle" and ignoreConfigWarnings == False:
                    syntaxstyleWarning = lambda: print_cmdResponse("Syntax style list is very large, type this command again to view.", warning=True)
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
                    print_cmdResponse("new style set")
                else:
                    print_cmdResponse("invalid style", error=True)
            case "--nl":
                # that's all :-)
                print_cmdResponse("")
            case "--mentions":
                mentionsPattern = re.compile(r"^--mentions (?P<action>on|off)$")
                if bool(re.search(mentionsPattern, myText)):
                    mentionOption = re.search(mentionsPattern, myText).group("action")
                    if mentionOption == "on":
                        switchStatus = onoffSwitch(True, COLOREDMENTIONS)
                        if switchStatus:
                            COLOREDMENTIONS = True
                            print_cmdResponse("colored mentions enabled")
                        else:
                            print_cmdResponse("colored mentions are already enabled", error=True)
                    if mentionOption == "off":
                        switchStatus = onoffSwitch(False, COLOREDMENTIONS)
                        if switchStatus:
                            COLOREDMENTIONS = False
                            print_cmdResponse("colored mentions disabled")
                        else:
                            print_cmdResponse("colored mentions are already disabled", error=True)
                else:
                    print_cmdResponse("colored mentions status: {}".format(COLOREDMENTIONS))
            case "--browserstyle":
                if myText == "--browserstyle":
                    print_cmdResponse(f"browser style status: {BROWSERSTYLE}")
                    continue
                browserStylePattern = re.compile(r"^--browserstyle (?P<action>on|off)$")
                if bool(re.search(browserStylePattern, myText)):
                    userAction = re.search(browserStylePattern, myText).group("action")
                    if userAction == "on":
                        switchStatus = onoffSwitch(True, BROWSERSTYLE)
                        if switchStatus:
                            BROWSERSTYLE = True
                            print_cmdResponse("browser style enabled")
                        else:
                            print_cmdResponse("browser style is already enabled", error=True)
                    elif userAction == "off":
                        switchStatus = onoffSwitch(False, BROWSERSTYLE)
                        if switchStatus:
                            BROWSERSTYLE = False
                            print_cmdResponse("browser style disabled")
                        else:
                            print_cmdResponse("browser style is already disabled")
            case "--botlist":
                if myText == "--botlist":
                    print_cmdResponse("botlist: {}".format(botlist))
                    continue
                botlistSearch = re.search(r"^--botlist (?P<cmd>add|remove) (?P<users>.*)$", myText)
                if not bool(botlistSearch):
                    print_cmdResponse("incorrect usage", error=True)
                    continue
                botlistSearchCmd = botlistSearch.group("cmd")
                botlistSearchUsers = botlistSearch.group("users").split(' ')
                if botlistSearchCmd == "add":
                    iterCount = 0
                    for target in botlistSearchUsers:
                        if botlistCmd(target, "add"):
                            iterCount += 1
                    if iterCount < 1:
                        print_cmdResponse("no users added to botlist")
                    else:
                        if iterCount > 1:
                            print_cmdResponse(f"added {iterCount} users to botlist")
                        else:
                            print_cmdResponse("user added to botlist")
                elif botlistSearchCmd == "remove":
                    if botlistSearchUsers == ['*']:
                        if len(botlist) == 0:
                            print_cmdResponse("botlist is already empty")
                            continue
                        botlist = []
                        print_cmdResponse("botlist cleared")
                        continue
                    iterCount = 0
                    for target in botlistSearchUsers:
                        if botlistCmd(target, "remove"):
                            iterCount += 1
                    if iterCount < 1:
                        print_cmdResponse("no users removed from botlist")
                    else:
                        print_cmdResponse(f"removed {iterCount} users from botlist")
            case "--stars":
                if myText == "--stars":
                    print_cmdResponse(f"star status: {STARS}")
                    continue
                starsPattern = re.compile(r"^--stars (?P<action>on|off)$")
                if bool(starsPattern.search(myText)):
                    starAction = starsPattern.search(myText).group("action")
                    match starAction:
                        case "on":
                            switchStatus = onoffSwitch(True, STARS)
                            if switchStatus:
                                STARS = True
                                print_cmdResponse("enabled stars")
                            else:
                                print_cmdResponse("stars are already enabled", error=True)
                        case "off":
                            switchStatus = onoffSwitch(False, STARS)
                            if switchStatus:
                                STARS = False
                                print_cmdResponse("stars disabled")
                            else:
                                print_cmdResponse("stars are already disabled", error=True)
            case "--whisperlock":
                if myText == "--whisperlock":
                    print_cmdResponse(f"whisper lock status: {WHISPERLOCK}")
                    continue
                whisperlockPattern = re.compile(r"^--whisperlock (?P<action>on|off)$")
                if bool(whisperlockPattern.search(myText)):
                    whisperlockAction = whisperlockPattern.search(myText).group("action")
                    match whisperlockAction:
                        case "on":
                            switchStatus = onoffSwitch(True, WHISPERLOCK)
                            if switchStatus:
                                WHISPERLOCK = True
                                print_cmdResponse("whisper lock enabled")
                            else:
                                print_cmdResponse("whisper lock is already enabled", error=True)
                        case "off":
                            switchStatus = onoffSwitch(False, WHISPERLOCK)
                            if switchStatus:
                                WHISPERLOCK = False
                                print_cmdResponse("whisper lock disabled")
                            else:
                                print_cmdResponse("whisper lock is already disabled", error=True)
            case "--group":
                if myText == "--group":
                    allGroups = []
                    for group in customGroups:
                        allGroups.append(group)
                    if len(allGroups) == 0:
                        print_cmdResponse("no active groups")
                        continue
                    allGroups = ", ".join(allGroups)
                    print_cmdResponse(f"active groups: {allGroups}")
                    continue
                groupCmdSearch = re.search(r"^--group (?P<group_name>\w+)(?:\s(?P<cmd>add|remove|rename)\s(?P<nick>\w{1,24}|\*))?$", myText)
                if not bool(groupCmdSearch):
                    print_cmdResponse("Invalid usage. See help for more info.", error=True)
                    continue
                groupName = groupCmdSearch.group("group_name")
                groupCmd = groupCmdSearch.group("cmd")
                groupNick = groupCmdSearch.group("nick")
                isCheckingStatus = groupCmd == None
                groupExists = customGroups.get(groupName) != None
                if isCheckingStatus:
                    if not groupExists:
                        print_cmdResponse("group does not exist", error=True)
                        continue
                    groupStatus = customGroups.get(groupName)
                    print_cmdResponse(f"group status: {groupStatus}")
                    continue
                elif groupCmd == "add":
                    if groupNick in usersInGroups:
                        print_cmdResponse("users can only be in one group at a time", error=True)
                        continue
                    if groupExists:
                        usersInGroup = customGroups[groupName].get("users")
                        if len(usersInGroup) >= 1:
                            if groupNick in customGroups[groupName]["users"]:
                                print_cmdResponse("user already in group", error=True)
                                continue
                            customGroups[groupName]["users"].append(groupNick)
                            usersInGroups[groupNick] = groupName
                            print_cmdResponse("user added to group")
                        elif len(usersInGroup) == 0:
                            customGroups[groupName]["users"] = [groupNick]
                            usersInGroups[groupNick] = groupName
                            print_cmdResponse("user added to group")
                    else:
                        customGroups[groupName] = {"users": [groupNick]}
                        usersInGroups[groupNick] = groupName
                        print_cmdResponse("group created")
                elif groupCmd == "remove":
                    if not groupExists:
                        print_cmdResponse("group does not exist", error=True)
                        continue
                    if len(customGroups[groupName]["users"]) == 1 and groupNick != '*':
                        del customGroups[groupName]
                        del usersInGroups[groupNick]
                        print_cmdResponse("group deleted")
                        continue
                    elif len(customGroups[groupName]["users"]) > 1 or groupNick == "*":
                        if groupNick == '*':
                            for u in customGroups[groupName]["users"]:
                                del usersInGroups[u]
                            del customGroups[groupName]
                            print_cmdResponse("group deleted")
                            continue
                        if groupNick not in customGroups[groupName]["users"]:
                            print_cmdResponse("user not in group", error=True)
                            continue
                        customGroups[groupName]["users"].remove(groupNick)
                        del usersInGroups[groupNick]
                        print_cmdResponse("removed user from group")
                elif groupCmd == "rename":
                    if not groupExists or groupNick == "*":
                        print_cmdResponse("group does not exist", error=True)
                        continue
                    if customGroups.get(groupNick) != None:
                        print_cmdResponse("group rename target already exists", error=True)
                        continue
                    customGroups[groupNick] = customGroups[groupName]
                    del customGroups[groupName]
                    print_cmdResponse("group named")
            case "--reset":
                if myText == "--reset":
                    showHelp("reset")
                    continue
                resetPatternSearch = re.search(r"^--reset (?P<option>\w+)$", myText)
                if not bool(resetPatternSearch):
                    print_cmdResponse("invalid usage", error=True)
                    continue
                cmdToReset = resetPatternSearch.group("option")
                try:
                    resetCmd(cmdToReset)
                    print_cmdResponse("command has been reset")
                except Exception as ERROR:
                    print_cmdResponse(f"exception caught: '{ERROR}'", error=True)
            case "--groupcmd":
                if myText == "--groupcmd":
                    showHelp("groupcmd")
                    continue
                groupcmdSearch = re.search(r"^--groupcmd (?P<group_name>\w+) (?P<cmd>(?:text\s|mention\s)?color|notify(?:\smention|\swhisper)?|mentions|block) (?P<arg>\w+)$", myText)
                if not bool(groupcmdSearch):
                    print_cmdResponse("invalid usage", error=True)
                    continue
                groupcmdCmd = groupcmdSearch.group("cmd")
                groupcmdArg = groupcmdSearch.group("arg")
                groupcmdGroupName = groupcmdSearch.group("group_name")
                if customGroups.get(groupcmdGroupName) == None:
                    print_cmdResponse("group does not exist", error=True)
                    continue
                if groupcmdArg in ["color", "text color", "mention color"]:
                    availableColors = ["red", "blue", "green", "yellow", "magenta", "white", "cyan"]
                    if groupcmdArg not in availableColors:
                        print_cmdResponse("invalid color", error=True)
                        continue
                    for c in availableColors:
                        if c != "white":
                            availableColors.append(f"light{c}")
                match groupcmdCmd:
                    case "color":
                        if groupcmdArg == "reset":
                            customGroups[groupcmdGroupName]["color"] = "blue"
                            print_cmdResponse("color reset")
                            continue
                        customGroups[groupcmdGroupName]["color"] = groupcmdArg
                        customGroupsWithStatus["groupsWithColorStatus"][groupcmdGroupName] = groupcmdArg
                        print_cmdResponse("new color set")
                    case "text color":
                        customGroups[groupcmdGroupName]["textcolor"] = groupcmdArg
                        customGroupsWithStatus["groupsWithTextColorStatus"][groupcmdGroupName] = groupcmdArg
                        print_cmdResponse("new text color set")
                    case "mention color":
                        if groupcmdArg == "reset":
                            customGroups[groupcmdGroupName]["mentioncolor"] = "blue"
                            print_cmdResponse("mention color reset")
                            continue
                        customGroups[groupcmdGroupName]["mentioncolor"] = groupcmdArg
                        customGroupsWithStatus["groupsWithMentionColorStatus"][groupcmdGroupName] = groupcmdArg
                        print_cmdResponse("new color set")
                    case "notify":
                        thisGroupNotify = True if groupcmdArg == "on" else False
                        customGroups[groupcmdGroupName]["notify"] = thisGroupNotify
                        customGroupsWithStatus["groupsWithNotifyStatus"][groupcmdGroupName] = thisGroupNotify
                        if thisGroupNotify:
                            print_cmdResponse("group notifications enabled")
                        else:
                            print_cmdResponse("group notifications disabled")
                    case "mentions":
                        thisGroupMentions = True if groupcmdArg == "on" else False
                        customGroups[groupcmdGroupName]["mentions"] = thisGroupMentions
                        customGroupsWithStatus["groupsWithMentionsStatus"][groupcmdGroupName] = thisGroupMentions
                        if thisGroupMentions:
                            print_cmdResponse("mentions enabled for group")
                        else:
                            print_cmdResponse("mentions disabled for group")
                    case "notify mention":
                        thisGroupNotifyMention = True if groupcmdArg == "on" else False
                        customGroups[groupcmdGroupName]["notifymention"] = thisGroupNotifyMention
                        customGroupsWithStatus["groupsWithNotifyMentionStatus"][groupcmdGroupName] = thisGroupNotifyMention
                        if thisGroupNotifyMention:
                            print_cmdResponse("mention notifications enabled")
                        else:
                            print_cmdResponse("mention notifications disabled")
                    case "notify whisper":
                        thisGroupNotifyWhisper = True if groupcmdArg == "on" else False
                        customGroups[groupcmdGroupName]["notifywhisper"] = thisGroupNotifyWhisper
                        customGroupsWithStatus["groupsWithNotifyWhisperStatus"][groupcmdGroupName] = thisGroupNotifyWhisper
                        if thisGroupNotifyWhisper:
                            print_cmdResponse("whisper notifications enabled")
                        else:
                            print_cmdResponse("whisper notifications disabled")
                    case "block":
                        blockCurrentGroup = True if groupcmdArg == "on" else False
                        customGroups[groupcmdGroupName]["block"] = blockCurrentGroup
                        if blockCurrentGroup:
                            print_cmdResponse("group has been blocked")
                        else:
                            print_cmdResponse("group has been unblocked")
            case "--uptime":
                uptime = int(time.time()) - connected_epoch
                if myText == "--uptime -p":
                    print_cmdResponse(uptimePretty(uptime))
                elif myText == "--uptime":
                    print_cmdResponse(uptimeTimeFormat(uptime))
                else:
                    showHelp("uptime")
            case "--help":
                if myText == "--help":
                    showHelp()
                else:
                    helpArg = myText.replace("--help ", '')
                    showHelp(helpArg)
            case _:
                print_cmdResponse(f"command not found: {commandName[2:]}", error=True)
