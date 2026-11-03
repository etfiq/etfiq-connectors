"""Minimal read-only client for ETFIQ's open data files (https://etfiq.com/data/).

Keyless. Paced at 2 requests a second. Every record it returns carries its as-of
date, a source URL and the attribution line.
"""
from __future__ import annotations

import json
import threading
import time
import urllib.error
import urllib.request
from typing import Any

SITE = "https://etfiq.com"
MIN_INTERVAL = 0.5  # seconds between requests: at most 2 a second
CACHE_SECONDS = 300

ISSUER_LICENCE = "Issuer-published data: credited to its source, under its owner's terms."
COMPUTED_LICENCE = "Open with attribution: ETFIQ (etfiq.com). https://etfiq.com/license/"


class EtfiqError(RuntimeError):
    """A file ETFIQ does not publish, or a read that failed."""


def attribution(as_of: str | None) -> str:
    return f"Source: ETFIQ (etfiq.com), data as of {as_of or 'date not stated'}"


class EtfiqClient:
    def __init__(self, package: str, version: str, base: str = SITE, timeout: float = 30.0):
        self.user_agent = f"etfiq-{package}/{version} (data@etfiq.com)"
        self.base = base.rstrip("/")
        self.timeout = timeout
        self._last = 0.0
        self._lock = threading.Lock()
        self._cache: dict[str, tuple[float, Any]] = {}

    def get(self, path: str) -> Any:
        """Read https://etfiq.com/data/<path> as JSON. Raises EtfiqError on 404."""
        path = path.lstrip("/")
        hit = self._cache.get(path)
        if hit and time.time() - hit[0] < CACHE_SECONDS:
            return hit[1]
        with self._lock:
            wait = MIN_INTERVAL - (time.monotonic() - self._last)
            if wait > 0:
                time.sleep(wait)
            self._last = time.monotonic()
        req = urllib.request.Request(
            f"{self.base}/data/{path}",
            headers={"User-Agent": self.user_agent, "Accept": "application/json"},
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as r:
                data = json.load(r)
        except urllib.error.HTTPError as e:
            if e.code == 404:
                raise EtfiqError(f"ETFIQ does not publish /data/{path}") from e
            raise EtfiqError(f"ETFIQ answered {e.code} for /data/{path}") from e
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as e:
            raise EtfiqError(f"could not read /data/{path}: {e}") from e
        self._cache[path] = (time.time(), data)
        return data

    # ---- records -------------------------------------------------------

    def _stamp(self, rec: dict, as_of: str | None, page: str, data: str, issuer: bool = False) -> dict:
        rec["as_of"] = as_of
        rec["source_url"] = page
        rec["data_url"] = f"{self.base}/data/{data}"
        rec["attribution"] = attribution(as_of)
        rec["license"] = ISSUER_LICENCE if issuer else COMPUTED_LICENCE
        return rec

    def screener(self) -> dict:
        return self.get("screener.json")

    def search(self, query: str, limit: int = 20) -> list[dict]:
        """Funds whose ticker or name contains the query; exact ticker first."""
        q = query.strip().lower()
        sc = self.screener()
        rows = sc["funds"]
        exact = [r for r in rows if r["ticker"].lower() == q]
        starts = [r for r in rows if r["ticker"].lower().startswith(q) and r not in exact]
        names = [r for r in rows if q in r["name"].lower() and r not in exact and r not in starts]
        out = []
        for r in (exact + starts + names)[:limit]:
            out.append(self._stamp(
                {k: r.get(k) for k in ("ticker", "name", "issuer", "desk", "category", "segment")},
                sc["asOf"], f"{self.base}/funds/{r['ticker'].lower()}", "screener.json"))
        return out

    def fund_row(self, ticker: str) -> tuple[dict, str]:
        sc = self.screener()
        t = ticker.strip().upper()
        for r in sc["funds"]:
            if r["ticker"] == t:
                return r, sc["asOf"]
        raise EtfiqError(f"ETFIQ does not cover {t}")

    def profile(self, ticker: str) -> dict:
        r, as_of = self.fund_row(ticker)
        rec = dict(r)
        return self._stamp(rec, as_of, f"{self.base}/funds/{r['ticker'].lower()}", "screener.json")

    def holdings(self, ticker: str) -> list[dict]:
        t = ticker.strip().lower()
        b = self.get(f"books/{t}.json")
        cite = b.get("cite", {})
        as_of = b.get("asOf") or cite.get("as_of")
        out = []
        for i, h in enumerate(b.get("h", []), 1):
            name, sym, _sid, weight = h[0], h[1], h[2], h[3]
            kind = h[4] if len(h) > 4 else None
            out.append(self._stamp(
                {"ticker": b.get("t", t.upper()), "rank": i, "name": name,
                 "symbol": sym or None, "weight_pct": weight, "is_cash": kind == "CASH",
                 "issuer_source": b.get("src") or cite.get("source_url")},
                as_of, f"{self.base}/funds/{t}", f"books/{t}.json", issuer=True))
        return out

    def flows(self, ticker: str) -> list[dict]:
        t = ticker.strip().lower()
        f = self.get(f"flows/funds/{t}.json")
        as_of = f.get("asOf")
        out = []
        for win, w in (f.get("windows") or {}).items():
            pct = w.get("flowPct")  # SINCE is a monthly total with no percentage
            out.append(self._stamp(
                {"ticker": f.get("ticker", t.upper()), "window": win, "flow_usd": w.get("flow"),
                 "flow_pct_of_start_assets": pct, "start_assets_usd": w.get("startAssets"),
                 "from": w.get("from"), "to": w.get("to"), "days": w.get("days"),
                 "days_in": w.get("inDays"), "days_out": w.get("outDays")},
                as_of, f"{self.base}/funds/{t}", f"flows/funds/{t}.json"))
        return out

    def benchmark_gap(self, ticker: str) -> dict:
        r, as_of = self.fund_row(ticker)
        t = r["ticker"].lower()
        return self._stamp(
            {"ticker": r["ticker"], "name": r["name"], "benchmark": r.get("benchmark"),
             "benchmark_etf": r.get("bench_gap_1y_ref"), "return_1y_pct": r.get("ret_1y"),
             "gap_1y_pts": r.get("bench_gap_1y"), "gap_1y_abs_pts": r.get("bench_gap_1y_abs"),
             "gap_asof": r.get("bench_gap_1y_asof")},
            r.get("bench_gap_1y_asof") or as_of, f"{self.base}/funds/{t}", "screener.json")

    def compare(self, tickers: list[str]) -> list[dict]:
        keys = ("ticker", "name", "category", "segment", "fee", "fee_asof", "net_assets", "net_assets_asof",
                "ret_1y", "ret_1y_asof", "yield_12m", "yield_12m_asof", "holdings_count",
                "holdings_top10", "flow_1m", "flow_1m_pct", "flow_asof", "bench_gap_1y", "bench_gap_1y_ref")
        out = []
        for t in tickers:
            r, as_of = self.fund_row(t)
            out.append(self._stamp({k: r.get(k) for k in keys}, as_of,
                                   f"{self.base}/funds/{r['ticker'].lower()}", "screener.json"))
        return out

    def screen(self, category: str | None = None, desk: str | None = None, issuer: str | None = None,
               max_fee: float | None = None, min_net_assets: float | None = None,
               min_ret_1y: float | None = None, min_yield: float | None = None,
               sort: str = "net_assets", limit: int = 20) -> list[dict]:
        sc = self.screener()
        rows = sc["funds"]

        def keep(r: dict) -> bool:
            if category and (r.get("category") or "").lower() != category.lower():
                return False
            if desk and (r.get("desk") or "").lower() != desk.lower():
                return False
            if issuer and issuer.lower() not in (r.get("issuer") or "").lower():
                return False
            for key, lo, hi in (("fee", None, max_fee), ("net_assets", min_net_assets, None),
                                ("ret_1y", min_ret_1y, None), ("yield_12m", min_yield, None)):
                v = r.get(key)
                if lo is not None and (v is None or v < lo):
                    return False
                if hi is not None and (v is None or v > hi):
                    return False
            return True

        hits = [r for r in rows if keep(r)]
        if sort not in ("net_assets", "ret_1y", "yield_12m", "fee", "flow_1m", "iq_score"):
            raise EtfiqError(f"cannot sort by {sort}")
        asc = sort == "fee"
        have = [r for r in hits if r.get(sort) is not None]
        have.sort(key=lambda r: r[sort], reverse=not asc)
        keys = ("ticker", "name", "category", "segment", "issuer", "fee", "net_assets", "ret_1y", "yield_12m", "iq_score")
        return [self._stamp({k: r.get(k) for k in keys}, sc["asOf"],
                            f"{self.base}/funds/{r['ticker'].lower()}", "screener.json")
                for r in have[:limit]]
