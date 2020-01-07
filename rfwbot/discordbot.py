import discord
import random
import requests
import asyncio
import json
from pathlib import Path
import importlib
from typing import List, Dict, Callable
from .exceptions import BotRequestFailure


class DiscordBot(discord.Client):
    def __init__(self, config_file: Path, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config_file = config_file

        try:
            self.command_string = self.config["settings"]["command_prefix"]
        except Exception:
            self.command_string = "!"

        self.reload_config()
        
        self.token = self.config["settings"]["token"]

        # Load macro plugins

        self.macros = dict()
        for f in (Path(__file__).parent / "macros").glob("*.py"):
            try:
                module = importlib.import_module(f".macros.{f.stem}", __package__)
                macro_function = getattr(module, 'run_macro')
            except AttributeError:
                print(f"Failed to load macro plugin from {f.name}")
            except ImportError:
                print(f"Could not import {f.name}")
                raise
            else:
                self.macros[f"%{f.stem.upper()}%"] = macro_function
        if self.macros:
            print(f"Loaded {len(self.macros)} macros: {', '.join(self.macros.keys())}")

    def run(self):
        super().run(self.token)

    async def on_message(self, message: discord.Message):
        if message.author.id in self.config["permissions"]["ignored"] or message.author == self.user:
            return

        if not message.content.startswith(self.command_string):
            return

        # Strip off prefix
        command = message.content[len(self.command_string):]

        # Check for a double-prefixed command
        if command.startswith(self.command_string):
            # Strip off additional prefix
            command = command[len(self.command_string):]
            handler = self.handle_system_command
        else:
            handler = self.handle_command

        # Handle the command
        await handler(channel=message.channel,
                      command=command.strip().split(' '),
                      sender=message.author)

    async def on_ready(self):
        print(f"Logged in as {self.user}")

    def reload_config(self):
        with open(self.config_file) as fh:
            self.config = json.load(fh)
        # TODO Check config is valid before reloading

    async def say(self, channel: discord.TextChannel, message: str):
        await channel.send(message)
        await asyncio.sleep(1)

    def get_channel_commandgroups(self, channel: discord.TextChannel):
        return [cg for cg, chans in self.config["channels"].items() if channel.id in chans]

    async def handle_command(self, channel: discord.TextChannel, command: List[str], sender: discord.Member):
        # Get the list of commandgroups for this channel
        commandgroups = self.get_channel_commandgroups(channel)

        # Are we listening in this channel?
        if not commandgroups:
            return

        # Find longest sequence of elements that matches a known command in one of our commandgroups
        for i in range(len(command), 0, -1):
            params = command[i:]
            potential_command = " ".join(command[:i]).lower().rstrip("*")

            if len(params) > 0:
                potential_command += "*"

            for commandgroup in commandgroups:
                if potential_command in self.config["commands"][commandgroup]:
                    response_templates = self.config["commands"][commandgroup][potential_command]
                    response_template = random.choice(response_templates)
                    try:
                        reply = await self.replace_macros(channel, response_template, sender, params)
                    except BotRequestFailure as e:
                        await self.say(channel, str(e))
                    else:
                        await self.say(channel, reply)
                    return

    async def replace_macros(self, channel: discord.TextChannel, response: str, sender: discord.Member,
                             params: List[str]):

        for key, func in self.macros.items():
            if key in response:
                response = response.replace(key, func(sender, params))

        return response

    async def handle_system_command(self, channel: discord.DMChannel, command: List[str], sender: discord.Member):
        cmd = command[0].lower()

        # Uncomment if params are needed in the future:
        # params = command[1:]

        # General commands

        if cmd == 'whoami':
            await self.say(channel, f"Your name is {sender.name} and your id is {sender.id}")

        # Admin commands

        if sender.id not in self.config["permissions"]["admin"]:
            return

        if cmd == 'reload':
            self.reload_config()
            await self.say(channel, 'Reloaded!')
        if cmd == 'stop':
            await self.say(channel, 'Shutting down.')
            await self.close()
        if cmd == 'channels':
            response = "Here are the channels I can currently see, and the responsegroups they are in:"
            for guild in self.guilds:
                response += f'\nOn the "{guild}" server:\n'
                for c in guild.channels:
                    if isinstance(c, discord.TextChannel):
                        response += f"-- #{c} ({c.id})"
                        commandgroups = self.get_channel_commandgroups(c)
                        if commandgroups:
                            response += f" - in groups {', '.join(commandgroups)}\n"
                        else:
                            response += " - not monitored\n"

            await self.say(channel, response)
