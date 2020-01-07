# RFWbot

This is a basic autoresponder bot for [Discord](https://discordapp.com), powered by [discord.py](https://github.com/Rapptz/discord.py). It can:

- Listen in the channels you specify, and respond to 'commands' with predefined responses
- Ignore users
- Perform basic 'macro-like' string replacements, to incorporate dynamic content into its responses
  - A few basic macros are provided, and more can be added via a simple plugin architecture

## Installation

Install discord.py and requests:

    pip install -r requirements.txt

Create a config file in JSON format (see `config.sample.json`)

Run the bot with

    python -m rfwbot config-file

* `config-file` is the the path to your JSON config.

You may find it useful to wrap your script call in a small shell script to ensure that it restarts if it crashes for any reason.

### Running in a container

You can use the supplied `Dockerfile` to create a docker image for the package, if you prefer.

To build the image:

    docker build --tag rfwbot .

The image can then be run with the following:

    docker run -d --name rfwbot -v ./config.json:/etc/rfwbot.json --restart=on-failure rfwbot 

(Replace `./config.json` with the path to your config file).

## Configuration

The JSON configuration file format is not currently documented, but hopefully it is fairly self-explanatory. See `config.sample.json` for an example.

### Commands

Commands are listed without their prefix (normally `!`, but configurable). They can include spaces.

* If a command ends with an asterisk (`*`), then it will require user input (which can be used in macros).
* If a command does not end with an asterisk (`*`), then it will only be matched if there is no user input
* You can define two different versions of a command, one with user input and one without. (See the **roll** command in the sample config for an example of this).

### Macros

Responses can include 'macros' which are defined via simple plugin scripts in the `macros/` directory. A plugin is just a python script which defines a `run_macro` function. Have a look at the macros provided to see how they work.

### Included macros

- `%SENDER%` - the public name of the user who issued the command
- `%INPUT%` - the sender’s additional input (everything after the command)
- `%CHOICE%` - randomly chooses an option from the sender's additional input (comma-separated list of options)
- `%ROLL%` - treats the additional input as a series of die definitions (e.g. d20 = a twenty-sided die; 2d6 = two six-sided dice) and
returns the outcome of rolling those dice.
  - Note: if the additional input contains malformed dice definitions, the entire response will be replaced with an error message.
- `%XKCD%` - returns a link to an XKCD comic, and its title. If additional input is provided, this is assumed to be the comic number; if not, a random comic is returned.
- `%WIKI%` - searches English Wikipedia for the provided string and returns a link to the first result.

## Feedback and issues

Please use the [GitHub issue tracker](https://github.com/itsmartin/rfwbot/issues) to report any bugs or suggest new features.
