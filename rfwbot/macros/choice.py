import discord
import random
from typing import List


def run_macro(sender: discord.Member, params: List[str]):
    return random.choice(" ".join(params).split(',')).strip()
