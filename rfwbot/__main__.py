#!/usr/bin/env python
from . import DiscordBot
import argparse
from pathlib import Path

parser = argparse.ArgumentParser(description='A discord bot')
parser.add_argument('config_file', type=Path)

args = parser.parse_args()

bot = DiscordBot(config_file=args.config_file)
bot.run()
