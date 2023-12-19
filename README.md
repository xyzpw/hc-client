# hc-client
[hack.chat](https://hack.chat/) client for your terminal emulator

## Usage

### Installation

Installation instructions are below. Where you see $FOLDERNAME you must replace it with the folder name of the release installed.

#### Installing requirements
```bash
$ cd $FOLDERNAME
$ pip3 install -r requirements.txt
```
You may have to run `pip3 uninstall websocket` in order to import websocket-client. <br>
The default websocket module is not the one used for this script, but they are both imported with the same name.
#### Installation via git
```bash
$ git clone https://github.com/xyzpw/hc-client.git
$ cd hc-client/
$ python3 hc-client
```

#### Installation via release (tar.gz)
```bash
$ tar -xf $FOLDERNAME
$ cd $FOLDERNAME
$ ./hc-client.py
```

#### Installation via release (zip)
```bash
$ unzip $FOLDERNAME
$ cd $FOLDERNAME
$ ./hc-client.py
```

## Commands
You can run commands in the client by typing "--COMMAND", be sure to replace "COMMAND" with the actual command you want to use. <br>
Below is a list of all the commands.
```yml
help:          Displays help message
clear:         Clears the screen
notify:        Plays a notification when receiving a message
block:         Blocks a user
unblock:       Removes a blocked user from the blocklist
blocklist:     Displays blocklist to screen
showblocked:   Same as blocklist
color:         Change color of users' names/text
syntaxstyle:   Change theme color of highlighted code
config:        Displays your config
nl:            Prints a newline
mentions:      Highlights @mentions
browserstyle:  Uses browserstyle mode
addbot:        Adds user to botlist
removebot:     Removes user from botlist
botlist:       Displays botlist
```

For more information, you can run "--help COMMAND" in client to get usage info.

### multiline

Using Ctrl+n will move your cursor to a newline, using Enter will send the message currently displayed in your input.

## config
The config file can be modified to make the client look how you want on startup.
The config file name is "hc-client-config.json", modify this file in json format. *example below*
```json
{
        "DONOTSAY": ["mypassword"],
        "ignoreConfigWarnings": "0",
        "nick": "myName",
        "channel": "myChannel",
        "altClear": "0",
        "blockUserReplaceText": "{TEXT REMOVED}",
        "blockedUsers": ["annoying_user"],
        "passwordProtection": "1",
        "userColor": "blue",
        "modColor": "green",
        "adminColor": "red",
        "colorMe": "blue",
        "botColor": "blue",
        "mySyntaxStyle": "monokai",
        "botlist": ["IAmABot", "ImABot"],
        "notifymention": "1"
}
```

## Preview(s)

Preview is not the latest release.<br>

![hc-client-preview2](https://github.com/xyzpw/hc-client/assets/76017734/99213423-f2e3-44b3-9833-f2df0db388cd)
