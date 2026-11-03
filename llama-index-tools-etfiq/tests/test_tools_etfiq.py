"""Live tests: the tool spec reads the real ETFIQ files."""
import json

from llama_index.core.tools.tool_spec.base import BaseToolSpec

from llama_index.tools.etfiq import EtfiqToolSpec

spec = EtfiqToolSpec()


def _stamped(rec):
    assert rec["as_of"] and rec["source_url"].startswith("https://etfiq.com/")
    assert rec["attribution"].startswith("Source: ETFIQ (etfiq.com), data as of ")


def test_class():
    assert BaseToolSpec.__name__ in [b.__name__ for b in EtfiqToolSpec.__mro__]


def test_to_tool_list_has_six_tools():
    tools = spec.to_tool_list()
    assert sorted(t.metadata.name for t in tools) == ["compare", "flows", "holdings", "profile", "screen", "search"]
    assert all(t.metadata.description for t in tools)


def test_search():
    r = json.loads(spec.search("spy", 3))
    assert r[0]["ticker"] == "SPY"
    _stamped(r[0])


def test_profile():
    r = json.loads(spec.profile("jepi"))
    assert r["ticker"] == "JEPI" and r["fee_asof"]
    _stamped(r)


def test_holdings_limit_and_cash():
    r = json.loads(spec.holdings("SPY", 5))
    assert len(r) == 5 and r[0]["rank"] == 1
    _stamped(r[0])
    assert any(x["is_cash"] for x in json.loads(spec.holdings("SPY", 1000)))


def test_flows():
    r = json.loads(spec.flows("SPY"))
    assert {"1D", "1M", "1Y"} <= {x["window"] for x in r}
    _stamped(r[0])


def test_compare():
    r = json.loads(spec.compare(["SPY", "VOO"]))
    assert [x["ticker"] for x in r] == ["SPY", "VOO"]
    _stamped(r[0])


def test_screen():
    r = json.loads(spec.screen(category="Income", max_fee=0.5, limit=5))
    assert 0 < len(r) <= 5 and all(x["fee"] <= 0.5 for x in r)
    _stamped(r[0])


def test_unknown_ticker_is_an_error_record():
    assert "error" in json.loads(spec.profile("ZZZZZZ"))
