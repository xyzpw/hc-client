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
- `--clear`     Clears the screen
- `--notify [on/off]`    Plays notify.mp3 every time a message is received, use without options to view notify status
- `--nl`        Creates a new line in your message

## Preview(s)
![Preview](/preview.png)
