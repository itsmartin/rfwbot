import discord
import random
from typing import List
import requests


def run_macro(sender: discord.Member, params: List[str]):
    search_query = " ".join(params)
    r = requests.get("https://en.wikipedia.org/w/api.php", params={
        "action": "query",
        "format": "json",
        "list": "search",
        "srsearch": search_query
    })
    r.raise_for_status()
    result = r.json()
    pageid = result['query']['search'][0]['pageid']
    r = requests.get("https://en.wikipedia.org/w/api.php", params={
        "action": "query",
        "format": "json",
        "prop": "info",
        "pageids": pageid,
        "inprop": "url"
    })
    r.raise_for_status()
    result = r.json()['query']['pages'][str(pageid)]['fullurl']
    return result
