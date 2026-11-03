"""LangChain tools over ETFIQ's open data. Each returns JSON-ready records that carry
as_of, source_url and an attribution line."""
from __future__ import annotations

from typing import Any, Optional, Type

from langchain_core.callbacks import CallbackManagerForToolRun
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field

from langchain_etfiq.etfiq_client import EtfiqClient, EtfiqError

__version__ = "0.1.0"
_client: EtfiqClient | None = None


def _c() -> EtfiqClient:
    global _client
    if _client is None:
        _client = EtfiqClient("langchain", __version__)
    return _client


def _safe(fn, *a, **k) -> Any:
    try:
        return fn(*a, **k)
    except EtfiqError as e:  # a tool tells the model what is missing instead of raising
        return {"error": str(e)}


class _Ticker(BaseModel):
    ticker: str = Field(description="US-listed ETF ticker, for example SPY.")


class _Search(BaseModel):
    query: str = Field(description="Ticker or part of a fund name.")
    limit: int = Field(default=10, description="Maximum funds to return.")


class _Holdings(_Ticker):
    limit: int = Field(default=25, description="Maximum holdings to return, largest weight first.")


class _Compare(BaseModel):
    tickers: list[str] = Field(description="Two to five ETF tickers.", min_length=2, max_length=5)


class _Screen(BaseModel):
    category: Optional[str] = Field(default=None, description="Stocks, Bonds, Commodities, Allocation, Themes, Income, Buffer, Leverage, Crypto or Alternatives.")
    issuer: Optional[str] = Field(default=None, description="Part of the issuer name.")
    max_fee: Optional[float] = Field(default=None, description="Maximum expense ratio, percent.")
    min_net_assets: Optional[float] = Field(default=None, description="Minimum net assets, USD.")
    min_ret_1y: Optional[float] = Field(default=None, description="Minimum one-year total return, percent.")
    min_yield: Optional[float] = Field(default=None, description="Minimum trailing 12-month yield, percent.")
    sort: str = Field(default="net_assets", description="net_assets, ret_1y, yield_12m, fee, flow_1m or iq_score.")
    limit: int = Field(default=10, description="Maximum funds to return.")


class _EtfiqTool(BaseTool):
    def _run(self, *args: Any, run_manager: Optional[CallbackManagerForToolRun] = None, **kwargs: Any) -> Any:
        return self._call(**kwargs)

    def _call(self, **kwargs: Any) -> Any:  # pragma: no cover
        raise NotImplementedError


class EtfiqSearchTool(_EtfiqTool):
    name: str = "etfiq_search"
    description: str = "Find US-listed ETFs by ticker or name. Returns ticker, name, issuer, category and segment, dated, from ETFIQ (etfiq.com)."
    args_schema: Type[BaseModel] = _Search

    def _call(self, query: str, limit: int = 10) -> Any:
        return _safe(_c().search, query, limit)


class EtfiqProfileTool(_EtfiqTool):
    name: str = "etfiq_profile"
    description: str = ("One ETF's profile from ETFIQ: category, benchmark, fee, net assets, returns, yield, IQ score and flows, "
                        "each number with its own date. Cite 'ETFIQ (etfiq.com)'.")
    args_schema: Type[BaseModel] = _Ticker

    def _call(self, ticker: str) -> Any:
        return _safe(_c().profile, ticker)


class EtfiqHoldingsTool(_EtfiqTool):
    name: str = "etfiq_holdings"
    description: str = ("An ETF's holdings as its issuer published them, with weights in percent of net assets and cash as its own row. "
                        "Issuer-published data: credit the issuer source in each record.")
    args_schema: Type[BaseModel] = _Holdings

    def _call(self, ticker: str, limit: int = 25) -> Any:
        r = _safe(_c().holdings, ticker)
        return r[:limit] if isinstance(r, list) else r


class EtfiqFlowsTool(_EtfiqTool):
    name: str = "etfiq_flows"
    description: str = "Money in and out of one ETF over 1D, 1W, 1M, 3M, YTD, 1Y and since-record windows, in USD and percent of starting assets, computed by ETFIQ."
    args_schema: Type[BaseModel] = _Ticker

    def _call(self, ticker: str) -> Any:
        return _safe(_c().flows, ticker)


class EtfiqCompareTool(_EtfiqTool):
    name: str = "etfiq_compare"
    description: str = "Side-by-side ETFIQ numbers for two to five ETFs: fee, net assets, one-year return, yield, holdings count, flows and gap to benchmark, each dated."
    args_schema: Type[BaseModel] = _Compare

    def _call(self, tickers: list[str]) -> Any:
        return _safe(_c().compare, tickers)


class EtfiqScreenTool(_EtfiqTool):
    name: str = "etfiq_screen"
    description: str = "Screen ETFIQ's covered ETFs by category, issuer, fee, size, one-year return and yield. Funds with no value for a filtered field are left out, not counted as zero."
    args_schema: Type[BaseModel] = _Screen

    def _call(self, **kwargs: Any) -> Any:
        return _safe(_c().screen, **kwargs)
