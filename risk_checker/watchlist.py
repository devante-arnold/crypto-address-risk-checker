"""Load the watchlist of high-risk / sanctioned addresses."""

import csv


def load_watchlist(path):
    """Read the watchlist CSV into a dict keyed by (lower-cased) address.

    Return shape:
        { "0x...dead": {"category": "sanctioned", "source": "OFAC (illustrative)"} }

    Addresses are lower-cased so lookups aren't tripped up by capitalisation.
    """
    watchlist = {}
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            address = row["address"].strip().lower()
            watchlist[address] = {
                "category": row["category"].strip(),
                "source": row["source"].strip(),
            }
    return watchlist
