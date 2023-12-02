# hc-client
[hack.chat](https://hack.chat/) client for your terminal emulator

## Installation

```console
git clone https://github.com/xyzpw/hc-client
cd hc-client
pip3 install -r requirements.txt
```
You may have to run `pip3 uninstall websocket` in order to import websocket-client.

## Usage

```console
python3 hc-client
```

## Commands
In script commands:
- help        Displays help message
- clear       Clears screen
- notify      Plays notification when receiving a message
- block       Block a user
- unblock     Unblock user
- blocklist   Display blocklist
- showblocked Same as blocklist
- color       Change color of users
- syntaxstyle Change syntax style of code
- config      Display config

### multiline

Use CTRL+N to break line.

## config

Config can be edited to customize the client:
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
        "mySyntaxStyle": "monokai"
}
```

## Preview(s)


![hc-client-preview2](https://github.com/xyzpw/hc-client/assets/76017734/99213423-f2e3-44b3-9833-f2df0db388cd)
