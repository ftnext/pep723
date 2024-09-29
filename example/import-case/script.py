# /// script
# dependencies = ["httpx", "rich"]
# ///

from rich.pretty import pprint

from mylib import fetch_peps

data = fetch_peps()
pprint([(k, v["title"]) for k, v in data.items()][:5])
