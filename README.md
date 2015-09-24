# RFWbot

This is a basic autoresponder bot for [Discord](https://discordapp.com), based on 
[discord.py](https://github.com/Rapptz/discord.py). Right now its functionality is very limited. It can:

- Read in a list of 'commands' and predefined responses from a file
- Listen in channels and respond when those commands are typed by other users
- Primitive 'macro-like' functionality to replace certain strings in its responses

## Installation

1. Make sure your system has discord.py and Python 3.x set up.
2. Configure your bot by editing the contents of `rfwbot.ini` and the various `.txt` files (see the samples provided).
3. Run the script with `python3 rfwbot.py`.

You may find it useful to wrap your script call in a small shell script to ensure that it restarts if it crashes for
any reason. For example, I use this bash script:

```
#!/bin/bash
while true; do
        python3 rfwbot.py
        echo Crashed, restarting
        sleep 1
done
```

## Configuration

The main file in which the bot's responses are listed is called `commands.txt` by default. This file is formatted
as follows:

```
[[channel-group-name]]
command [tab] response
command [tab] response
...
```

The `channel-group-name` is an arbitrary string name you can give to a group of channels. This is so that you can configure
your bot to respond to a different set of commands in different channels it joins. (You set up the channel/group mappings
in `channels.txt`). You can define many different channel groups in your `commands.txt` file.

On every subsequent line, you should give a *command* and *response* separated by a single TAB character.

### Commands

Commands are listed without their prefix (normally `!`, but configurable in `rfwbot.ini`). They can include spaces. If a command
ends with an asterisk (on its own, as a single word), then it will accept user input (which can be included in the bot's response
through the use of the `%INPUT%` macro - see below).

If you want, you can define two different versions of a command, one with user input and one without. See the **roll** command in
`commands.txt.sample` for an example of this.

### Response macros

When a user issues a command, the bot will respond with the *response* defined in `commands.txt`. Responses can include the following
'macros' which will be replaced accordingly:

- `%SENDER%` - replaced with the public name of the user who issued the command
- `%INPUT%` - the sender’s additional input (everything after the command)
- `%CHOICE%` - one item, randomly chosen from the additional input (which is assumed to be comma-separated)
- `%ROLL%` - treats the additional input as a series of die definitions (e.g. d20 = a twenty-sided die; 2d6 = two six-sided dice) and
returns the outcome of rolling those dice.
 - Note: if the additional input contains malformed dice definitions, the entire response will be replaced with an error message.

## Feedback and issues

Please use the [GitHub issue tracker](https://github.com/itsmartin/rfwbot/issues) to report any bugs or suggest new features.

