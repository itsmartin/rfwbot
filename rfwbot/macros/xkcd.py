import discord
import requests
import random
from rfwbot.exceptions import BotRequestFailure
from typing import List


def run_macro(sender: discord.Member, params: List[str]):
    if params:
        try:
            comic = fetch_xkcd(int(params[0]))
        except ValueError:
            raise BotRequestFailure("That doesn't sound like a number")
    else:
        comic = fetch_random_xkcd()
    return f'http://xkcd.com/{comic["num"]} ("{comic["safe_title"]}")'


def get_xkcd_data(uri: str):
    try:
        r = requests.get(uri)
        if r.status_code == 404:
            raise BotRequestFailure("Comic not found")
        r.raise_for_status()
    except requests.exceptions.RequestException:
        raise BotRequestFailure("Sorry, I couldn't reach XKCD")

    return r.json()


def fetch_xkcd(number: int):
    return get_xkcd_data(f"http://xkcd.com/{number}/info.0.json")


def fetch_latest_xkcd():
    return get_xkcd_data(f"http://xkcd.com/info.0.json")


def fetch_random_xkcd():
    try:
        latest_number = fetch_latest_xkcd()["num"]
    except ValueError:
        raise BotRequestFailure(f"Couldn't determine XKCD range")

    return fetch_xkcd(random.randint(1, latest_number))
