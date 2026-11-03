"""Live tests: OpenBB's Fetcher.test checks query and data types against the real ETFIQ files."""
import pytest

from openbb_etfiq import etfiq_provider
from openbb_etfiq.models.benchmark_gap import EtfiqBenchmarkGapFetcher
from openbb_etfiq.models.etf_holdings import EtfiqEtfHoldingsFetcher
from openbb_etfiq.models.etf_info import EtfiqEtfInfoFetcher
from openbb_etfiq.models.etf_search import EtfiqEtfSearchFetcher
from openbb_etfiq.models.fund_flows import EtfiqFundFlowsFetcher


def test_provider_registers_every_fetcher():
    assert set(etfiq_provider.fetcher_dict) == {"EtfSearch", "EtfInfo", "EtfHoldings", "EtfiqFundFlows", "EtfiqBenchmarkGap"}
    assert etfiq_provider.credentials == []


@pytest.mark.parametrize("fetcher,params", [
    (EtfiqEtfSearchFetcher, {"query": "spy", "limit": 5}),
    (EtfiqEtfInfoFetcher, {"symbol": "SPY"}),
    (EtfiqEtfHoldingsFetcher, {"symbol": "SPY", "limit": 10}),
    (EtfiqFundFlowsFetcher, {"symbol": "SPY"}),
    (EtfiqBenchmarkGapFetcher, {"symbol": "JEPI"}),
])
def test_fetcher_standard_test(fetcher, params):
    fetcher.test(params, {})


async def test_values_carry_date_and_source():
    q = EtfiqEtfInfoFetcher.transform_query({"symbol": "spy"})
    d = EtfiqEtfInfoFetcher.transform_data(q, await EtfiqEtfInfoFetcher.aextract_data(q, None))
    assert d.symbol == "SPY" and d.as_of and d.source_url == "https://etfiq.com/funds/spy"
    assert d.attribution.startswith("Source: ETFIQ (etfiq.com), data as of ")
    assert d.expense_ratio_pct is not None and d.expense_ratio_asof


async def test_flows_windows_and_holdings_cash():
    q = EtfiqFundFlowsFetcher.transform_query({"symbol": "SPY"})
    rows = EtfiqFundFlowsFetcher.transform_data(q, await EtfiqFundFlowsFetcher.aextract_data(q, None))
    assert {"1D", "1M", "1Y"} <= {r.window for r in rows}
    assert all(r.as_of and r.source_url for r in rows)
    h = EtfiqEtfHoldingsFetcher.transform_query({"symbol": "SPY"})
    holdings = EtfiqEtfHoldingsFetcher.transform_data(h, await EtfiqEtfHoldingsFetcher.aextract_data(h, None))
    assert holdings[0].rank == 1 and any(x.is_cash for x in holdings)


def test_router_and_entry_points_load():
    from importlib.metadata import entry_points
    from openbb_etfiq.router import router
    assert router is not None
    assert [e.value for e in entry_points(group="openbb_provider_extension") if e.name == "etfiq"] == ["openbb_etfiq:etfiq_provider"]
    assert [e.value for e in entry_points(group="openbb_core_extension") if e.name == "etfiq"] == ["openbb_etfiq.router:router"]
