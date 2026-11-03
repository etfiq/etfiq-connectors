"""ETFIQ tool spec."""
from __future__ import annotations

import json
from typing import Any, List, Optional

from llama_index.core.tools.tool_spec.base import BaseToolSpec

from llama_index.tools.etfiq.etfiq_client import EtfiqClient, EtfiqError

__version__ = "0.1.0"


class EtfiqToolSpec(BaseToolSpec):
    """Read-only tools over ETFIQ's free ETF data (https://etfiq.com/data/). No API key.

    Every returned record carries ``as_of``, ``source_url`` and an ``attribution`` line.
    """

    spec_functions = ["search", "profile", "holdings", "flows", "compare", "screen"]

    def __init__(self, client: Optional[EtfiqClient] = None) -> None:
        self._client = client or EtfiqClient("llamaindex", __version__)

    def _run(self, fn, *a, **k) -> str:
        try:
            return json.dumps(fn(*a, **k))
        except EtfiqError as e:
            return json.dumps({"error": str(e)})

    def search(self, query: str, limit: int = 10) -> str:
        """Find US-listed ETFs by ticker or part of a name. Returns JSON records: ticker, name, issuer, category, segment, as_of, source_url."""
        return self._run(self._client.search, query, limit)

    def profile(self, ticker: str) -> str:
        """One ETF's ETFIQ profile as JSON: category, benchmark, fee, net assets, returns, yield, IQ score, flows and benchmark gap, each number with its own date."""
        return self._run(self._client.profile, ticker)

    def holdings(self, ticker: str, limit: int = 25) -> str:
        """An ETF's holdings as its issuer published them (JSON): weight_pct is percent of net assets, cash is its own row. Issuer-published, under the issuer's terms."""
        def go() -> List[dict]:
            return self._client.holdings(ticker)[:limit]
        return self._run(go)

    def flows(self, ticker: str) -> str:
        """Money in and out of one ETF (JSON), per window: 1D, 1W, 1M, 3M, YTD, 1Y, SINCE. USD and percent of starting assets."""
        return self._run(self._client.flows, ticker)

    def compare(self, tickers: List[str]) -> str:
        """Side-by-side ETFIQ numbers (JSON) for two to five ETFs: fee, net assets, one-year return, yield, holdings count, flows, gap to benchmark."""
        return self._run(self._client.compare, tickers)

    def screen(
        self,
        category: Optional[str] = None,
        issuer: Optional[str] = None,
        max_fee: Optional[float] = None,
        min_net_assets: Optional[float] = None,
        min_ret_1y: Optional[float] = None,
        min_yield: Optional[float] = None,
        sort: str = "net_assets",
        limit: int = 10,
    ) -> str:
        """Screen ETFIQ's covered ETFs (JSON). category: Stocks, Bonds, Commodities, Allocation, Themes, Income, Buffer, Leverage, Crypto, Alternatives. Fee and yield in percent, net assets in USD. sort: net_assets, ret_1y, yield_12m, fee, flow_1m, iq_score. Funds with no value for a filtered field are left out."""
        return self._run(self._client.screen, category=category, issuer=issuer, max_fee=max_fee,
                         min_net_assets=min_net_assets, min_ret_1y=min_ret_1y, min_yield=min_yield,
                         sort=sort, limit=limit)
