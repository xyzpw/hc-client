# hc-client
A script to connect to [hack.chat](https://hack.chat/) through your terminal.<br><br>
![hc-client-v5-preview](https://github.com/xyzpw/hc-client/assets/76017734/68f662a5-b0a4-42f4-9015-215f5f12cd96)


## Installation

Installation instructions are below. Where you see $FOLDERNAME you must replace it with the folder name of the release installed.<br><br>
If you are getting execution errors on Linux, you have to add execution perms, you can do this via `chmod +x hc-client.py`.

### Installing Requirements
```bash
$ cd $FOLDERNAME
$ pip3 install -r requirements.txt
```
You may have to run `pip3 uninstall websocket` in order to import websocket-client. <br>
The default websocket module is not the one used for this script, but they are both imported with the same name.
### Installation via Git
```bash
$ git clone https://github.com/xyzpw/hc-client.git
$ cd hc-client/
$ python3 hc-client
```

### Installation via Release (tar.gz)
```bash
$ tar -xf $FOLDERNAME
$ cd $FOLDERNAME
$ ./hc-client.py
```

### Installation via Release (zip)
```bash
$ unzip $FOLDERNAME
$ cd $FOLDERNAME
$ ./hc-client.py
```

# Usage
Usage and explanations for certain commands.
## Commands
You can run commands in the client by typing "--COMMAND", be sure to replace "COMMAND" with the actual command you want to use. <br>
Below is a list of all the commands.
```yml
help:          displays help message
clear:         clears the screen
notify:        plays a notification when receiving a message
blocklist:     displays blocklist
color:         change color of users' names/text
syntaxstyle:   change theme color of highlighted code
config:        displays your config
nl:            prints a newline
mentions:      highlights @mentions
browserstyle:  uses browserstyle mode
botlist:       displays botlist
stars:         displays stars next to moderators names
whisperlock:   disables the ability to send any messages other than whispers
group:         assigns a specified user to a customizable group
reset:         reset specified values to default
groupcmd:      command for customizing groups
```

For more information, you can run "--help COMMAND" in client to get usage info.

## Multiline Input

Support for multiline input. During input, use ctrl+n to move a line down, when you want to send the message, press enter.

## File Config
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
        "notifymention": "1",
        "notifywhisper": "1",
        "stars": "1",
        "mynickcolor": "#F06"
}
```
# Contributing
Contributers are welcome if the code or files are non-breaking.
