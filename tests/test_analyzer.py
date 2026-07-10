"""Tests for the exposure analyzer.

Transfers are built in-memory so the expected numbers are easy to verify by hand.
"""

from risk_checker.analyzer import analyze, load_transfers
from risk_checker.watchlist import load_watchlist

ALICE = "0x9999999999999999999999999999999999999999"
BOB = "0x3333333333333333333333333333333333333333"          # clean
MIXER = "0x1111111111111111111111111111111111111111"        # watchlisted
SANCTIONED = "0x000000000000000000000000000000000000dead"   # watchlisted

WATCHLIST = {
    MIXER: {"category": "mixer", "source": "test"},
    SANCTIONED: {"category": "sanctioned", "source": "test"},
}


def transfer(tx_hash, frm, to, amount):
    return {"tx_hash": tx_hash, "from_address": frm, "to_address": to,
            "amount": float(amount), "asset": "ETH", "timestamp": "2026-03-01T00:00:00Z"}


def test_analyze_flags_watchlisted_counterparties_and_scores_them():
    transfers = [
        transfer("t1", ALICE, BOB, 5.0),          # clean, 5.0
        transfer("t2", ALICE, MIXER, 3.0),        # flagged, 3.0
        transfer("t3", SANCTIONED, ALICE, 2.0),   # flagged, 2.0
    ]
    report = analyze(ALICE, transfers, WATCHLIST)

    assert report.transfer_count == 3
    assert report.total_volume == 10.0
    assert report.flagged_volume == 5.0
    assert report.risk_score == 50      # 5.0 / 10.0
    assert set(report.risky_counterparties) == {MIXER, SANCTIONED}
    assert report.risky_counterparties[SANCTIONED] == "sanctioned"


def test_analyze_ignores_transfers_that_dont_involve_the_address():
    transfers = [transfer("t1", BOB, MIXER, 9.0)]  # nothing to do with ALICE
    report = analyze(ALICE, transfers, WATCHLIST)
    assert report.transfer_count == 0
    assert report.risk_score == 0


def test_clean_address_scores_zero():
    transfers = [
        transfer("t1", ALICE, BOB, 4.0),
        transfer("t2", BOB, ALICE, 6.0),
    ]
    report = analyze(ALICE, transfers, WATCHLIST)
    assert report.flagged_volume == 0.0
    assert report.risk_score == 0
    assert report.risky_counterparties == {}


def test_load_functions_read_the_sample_files():
    # End-to-end on the shipped sample data.
    transfers = load_transfers("data/sample_transfers.csv")
    watchlist = load_watchlist("data/sample_watchlist.csv")
    report = analyze(ALICE, transfers, watchlist)
    assert report.transfer_count == 5      # tx06 doesn't involve ALICE
    assert report.risk_score == 40         # flagged 5.0 of 12.5 total
