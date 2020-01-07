import discord
import random
from typing import List
from rfwbot.exceptions import BotRequestFailure
import itertools


def run_macro(sender: discord.Member, params: List[str]):
    rolls = list(roll_dice(params))
    if len(rolls) == 1:
        return str(rolls[0])
    else:
        return f"{' + '.join(str(n) for n in rolls)} = {sum(rolls)}"


def roll_die(die: str):
    try:
        quantity_str, sides_str = die.lower().split('d', maxsplit=1)
        quantity = int(quantity_str) if quantity_str != '' else 1
        sides = int(sides_str)
    except ValueError:
        raise BotRequestFailure(f'I didn\'t understand the die description "{die}"')

    if quantity > 20 or quantity < 1:
        raise BotRequestFailure(f"I can't roll {quantity} dice")
    if sides > 1000 or sides < 1:
        raise BotRequestFailure(f"I don't have a die with {sides} sides")

    return (random.randint(1, sides) for _ in range(quantity))


def roll_dice(dice: List[str]):
    return itertools.chain(*(roll_die(die) for die in dice))
