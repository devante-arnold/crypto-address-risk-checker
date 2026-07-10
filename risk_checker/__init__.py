"""risk_checker — score a crypto address by its exposure to risky counterparties.

Given a wallet address, a list of on-chain transfers, and a watchlist of
high-risk / sanctioned addresses, it measures how much of the address's activity
touches flagged parties — a simplified version of the blockchain-analytics work
done by tools like Chainalysis and TRM.

STATUS: in progress. The offline "direct exposure" core works and is tested;
live-chain data and multi-hop tracing are on the roadmap (see README).
"""

__version__ = "0.2.0"
