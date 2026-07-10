"""The exposure analysis — pure logic, no chain calls.

`analyze()` takes already-loaded transfers and a watchlist, so it can be tested
with a handful of made-up transfers and no network.
"""

import csv
from dataclasses import dataclass, field


@dataclass
class RiskReport:
    address: str
    transfer_count: int          # transfers that involved this address
    total_volume: float          # total value moved
    flagged_volume: float        # value moved with watchlisted addresses
    risk_score: int              # 0-100 = flagged_volume / total_volume
    flagged_transfers: list = field(default_factory=list)
    risky_counterparties: dict = field(default_factory=dict)  # address -> category


def load_transfers(path):
    """Read a transfers CSV into a list of dicts (amounts as floats)."""
    transfers = []
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            transfers.append({
                "tx_hash": row["tx_hash"].strip(),
                "from_address": row["from_address"].strip().lower(),
                "to_address": row["to_address"].strip().lower(),
                "amount": float(row["amount"]),
                "asset": row["asset"].strip(),
                "timestamp": row["timestamp"].strip(),
            })
    return transfers


def analyze(address, transfers, watchlist):
    """Measure how much of `address`'s activity touches watchlisted addresses."""
    address = address.lower()
    total_volume = 0.0
    flagged_volume = 0.0
    transfer_count = 0
    flagged_transfers = []
    risky_counterparties = {}

    for t in transfers:
        # Only look at transfers this address was actually part of.
        if address not in (t["from_address"], t["to_address"]):
            continue

        transfer_count += 1
        total_volume += t["amount"]

        # The counterparty is whoever is on the *other* side of the transfer.
        if t["from_address"] == address:
            counterparty, direction = t["to_address"], "outgoing"
        else:
            counterparty, direction = t["from_address"], "incoming"

        if counterparty in watchlist:
            entry = watchlist[counterparty]
            flagged_volume += t["amount"]
            flagged_transfers.append({
                "tx_hash": t["tx_hash"],
                "counterparty": counterparty,
                "direction": direction,
                "amount": t["amount"],
                "category": entry["category"],
                "source": entry["source"],
            })
            risky_counterparties[counterparty] = entry["category"]

    risk_score = round(flagged_volume / total_volume * 100) if total_volume else 0

    return RiskReport(
        address=address,
        transfer_count=transfer_count,
        total_volume=total_volume,
        flagged_volume=flagged_volume,
        risk_score=risk_score,
        flagged_transfers=flagged_transfers,
        risky_counterparties=risky_counterparties,
    )
