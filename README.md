# Crypto Address Risk Checker  🚧

> **Status: in progress.** The offline "direct exposure" core works and is fully
> tested. Live-chain data and multi-hop tracing are next — see the [Roadmap](#roadmap).

Score a crypto wallet address by its **exposure to risky counterparties**. Given
an address, a list of on-chain transfers, and a watchlist of high-risk /
sanctioned addresses, it reports how much of the address's activity touched
flagged parties — a simplified take on the blockchain-analytics work done by
tools like Chainalysis and TRM.

This is the domain I come from (blockchain analytics / financial-crime
compliance), rebuilt from first principles as a learning project.

> ⚠️ **Educational project.** It runs on **synthetic** sample data. The bundled
> watchlist is made-up and clearly labelled "illustrative" — it is **not** real
> sanctions intelligence. For the real thing, see the
> [OFAC SDN list](https://sanctionssearch.ofac.treas.gov/).

## What works today

- Load a watchlist (address → category → source) and a set of transfers
- Identify every transfer where the counterparty is on the watchlist
- Compute **total volume**, **flagged volume**, and a **risk score** (0–100 =
  share of volume touching flagged addresses)
- Escalate to **HIGH** on any direct sanctioned counterparty, regardless of score
- Print a reviewer-friendly report

### Example

```bash
python -m risk_checker.cli --address 0x9999999999999999999999999999999999999999
```

```
====================================================================
CRYPTO ADDRESS RISK REPORT
====================================================================
Address           : 0x9999999999999999999999999999999999999999
Transfers reviewed: 5
Total volume      : 12.5000
Flagged volume    : 5.0000
Risk score        : 40/100  (HIGH)

--------------------------------------------------------------------
FLAGGED TRANSFERS
--------------------------------------------------------------------
  outgoing     3.0000  [mixer]  0x1111111111111111111111111111111111111111
           tx 0xtx03  (source: Internal analytics (illustrative))
  incoming     1.5000  [sanctioned]  0x000000000000000000000000000000000000dead
           tx 0xtx04  (source: OFAC SDN (illustrative))
  outgoing     0.5000  [scam]  0x2222222222222222222222222222222222222222
           tx 0xtx05  (source: Community reports (illustrative))
====================================================================
```

## Roadmap

- [x] Direct-exposure scoring on offline transfer data
- [x] Severity escalation for sanctioned counterparties
- [ ] **Live data ingestion** from a block explorer API (e.g. Etherscan) so you
      can check a real address by just passing it in
- [ ] **Indirect (multi-hop) exposure** — trace risk 2–3 hops out, not just direct
      counterparties
- [ ] Import the real **OFAC SDN** crypto address list into the watchlist format
- [ ] Weight the score by counterparty category (sanctioned > mixer > scam)
- [ ] A small web dashboard for non-technical reviewers

## Running the tests

```bash
pip install -r requirements.txt
pytest
```

Tests live in [`tests/test_analyzer.py`](tests/test_analyzer.py) and run offline.

## Project structure

```
risk_checker/
  watchlist.py    # load the high-risk address list
  analyzer.py     # score an address's exposure (pure logic, tested)
  cli.py          # command-line interface + report formatting
data/
  sample_watchlist.csv    # SYNTHETIC — not real intelligence
  sample_transfers.csv
tests/
  test_analyzer.py
```

## Input formats

**Watchlist** (`address,category,source`):
```
0x000000000000000000000000000000000000dead,sanctioned,OFAC SDN (illustrative)
```

**Transfers** (`tx_hash,from_address,to_address,amount,asset,timestamp`):
```
0xtx04,0x...dead,0x9999...9999,1.5,ETH,2026-03-04T14:00:00Z
```
