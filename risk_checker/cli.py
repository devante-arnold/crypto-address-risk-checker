"""Command-line entry point.

Usage:
    python -m risk_checker.cli --address 0x9999...9999 \\
        --transfers data/sample_transfers.csv \\
        --watchlist data/sample_watchlist.csv
"""

import argparse
import sys

from risk_checker.analyzer import analyze, load_transfers
from risk_checker.watchlist import load_watchlist


def severity(report):
    """Turn the numeric score into a label a reviewer can act on."""
    # Any direct hit with a sanctioned party is high, regardless of volume share.
    if "sanctioned" in report.risky_counterparties.values():
        return "HIGH"
    if report.risk_score >= 50:
        return "HIGH"
    if report.risk_score > 0:
        return "ELEVATED"
    return "LOW"


def format_report(report):
    lines = []
    lines.append("=" * 68)
    lines.append("CRYPTO ADDRESS RISK REPORT")
    lines.append("=" * 68)
    lines.append(f"Address           : {report.address}")
    lines.append(f"Transfers reviewed: {report.transfer_count}")
    lines.append(f"Total volume      : {report.total_volume:,.4f}")
    lines.append(f"Flagged volume    : {report.flagged_volume:,.4f}")
    lines.append(f"Risk score        : {report.risk_score}/100  ({severity(report)})")

    if report.flagged_transfers:
        lines.append("")
        lines.append("-" * 68)
        lines.append("FLAGGED TRANSFERS")
        lines.append("-" * 68)
        for ft in report.flagged_transfers:
            lines.append(f"  {ft['direction']:<8} {ft['amount']:>10,.4f}  "
                         f"[{ft['category']}]  {ft['counterparty']}")
            lines.append(f"           tx {ft['tx_hash']}  (source: {ft['source']})")
    else:
        lines.append("")
        lines.append("No exposure to watchlisted addresses found.")

    lines.append("=" * 68)
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Score a crypto address by its exposure to risky counterparties.")
    parser.add_argument("--address", required=True, help="the wallet address to check")
    parser.add_argument("--transfers", default="data/sample_transfers.csv",
                        help="CSV of on-chain transfers")
    parser.add_argument("--watchlist", default="data/sample_watchlist.csv",
                        help="CSV of high-risk / sanctioned addresses")
    args = parser.parse_args(argv)

    try:
        transfers = load_transfers(args.transfers)
        watchlist = load_watchlist(args.watchlist)
    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    report = analyze(args.address, transfers, watchlist)
    print(format_report(report))
    return 0


if __name__ == "__main__":
    sys.exit(main())
