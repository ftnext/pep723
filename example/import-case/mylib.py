import httpx


def fetch_peps():
    resp = httpx.get("https://peps.python.org/api/peps.json")
    return resp.json()
