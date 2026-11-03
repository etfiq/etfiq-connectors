"""Live tests: every tool reads the real ETFIQ files."""
import pytest

from langchain_etfiq import (EtfiqCompareTool, EtfiqFlowsTool, EtfiqHoldingsTool, EtfiqProfileTool,
                             EtfiqScreenTool, EtfiqSearchTool, EtfiqToolkit)


def _stamped(rec):
    assert rec["as_of"] and rec["source_url"].startswith("https://etfiq.com/")
    assert rec["attribution"].startswith("Source: ETFIQ (etfiq.com), data as of ")


def test_search():
    r = EtfiqSearchTool().invoke({"query": "spy", "limit": 3})
    assert r[0]["ticker"] == "SPY"
    _stamped(r[0])


def test_profile():
    r = EtfiqProfileTool().invoke({"ticker": "jepi"})
    assert r["ticker"] == "JEPI" and r["fee_asof"]
    _stamped(r)


def test_holdings():
    r = EtfiqHoldingsTool().invoke({"ticker": "SPY", "limit": 5})
    assert len(r) == 5 and r[0]["rank"] == 1
    _stamped(r[0])


def test_flows():
    r = EtfiqFlowsTool().invoke({"ticker": "SPY"})
    assert {"1D", "1M", "1Y"} <= {x["window"] for x in r}
    _stamped(r[0])


def test_compare():
    r = EtfiqCompareTool().invoke({"tickers": ["SPY", "VOO"]})
    assert [x["ticker"] for x in r] == ["SPY", "VOO"]
    _stamped(r[0])


def test_screen():
    r = EtfiqScreenTool().invoke({"category": "Income", "max_fee": 0.5, "sort": "net_assets", "limit": 5})
    assert 0 < len(r) <= 5 and all(x["fee"] <= 0.5 for x in r)
    _stamped(r[0])


def test_unknown_ticker_returns_error_not_exception():
    assert "error" in EtfiqProfileTool().invoke({"ticker": "ZZZZZZ"})


def test_toolkit_has_six_unique_tools():
    names = [t.name for t in EtfiqToolkit().get_tools()]
    assert len(names) == 6 and len(set(names)) == 6
