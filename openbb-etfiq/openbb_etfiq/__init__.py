"""OpenBB Platform provider for ETFIQ's open ETF data (https://etfiq.com/data/). No API key."""
from openbb_core.provider.abstract.provider import Provider

from openbb_etfiq.models.benchmark_gap import EtfiqBenchmarkGapFetcher
from openbb_etfiq.models.etf_holdings import EtfiqEtfHoldingsFetcher
from openbb_etfiq.models.etf_info import EtfiqEtfInfoFetcher
from openbb_etfiq.models.etf_search import EtfiqEtfSearchFetcher
from openbb_etfiq.models.fund_flows import EtfiqFundFlowsFetcher

etfiq_provider = Provider(
    name="etfiq",
    website="https://etfiq.com",
    description=(
        "ETFIQ publishes free, keyless data on US-listed ETFs: fees, size, returns, holdings, "
        "fund flows and each fund's return against its own benchmark. Every record carries its "
        "as-of date. Source: ETFIQ (etfiq.com)."
    ),
    credentials=None,
    fetcher_dict={
        "EtfSearch": EtfiqEtfSearchFetcher,
        "EtfInfo": EtfiqEtfInfoFetcher,
        "EtfHoldings": EtfiqEtfHoldingsFetcher,
        "EtfiqFundFlows": EtfiqFundFlowsFetcher,
        "EtfiqBenchmarkGap": EtfiqBenchmarkGapFetcher,
    },
    repr_name="ETFIQ",
)
