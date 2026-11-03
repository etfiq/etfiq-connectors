"""ETFIQ ETF Holdings model."""
from typing import Any

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.etf_holdings import EtfHoldingsData, EtfHoldingsQueryParams
from pydantic import Field

from openbb_etfiq.models._common import call, client


class EtfiqEtfHoldingsQueryParams(EtfHoldingsQueryParams):
    """ETFIQ ETF Holdings query."""

    limit: int | None = Field(default=None, description="Maximum rows to return. Default: all.")


class EtfiqEtfHoldingsData(EtfHoldingsData):
    """ETFIQ ETF Holdings data. The weights are the issuer's, as ETFIQ reads them."""

    rank: int = Field(description="Position in the issuer's list, largest weight first.")
    weight_pct: float | None = Field(default=None, description="Share of net assets, percent, as the issuer published it.")
    is_cash: bool = Field(default=False, description="True for the cash and other net assets row.")
    as_of: str | None = Field(default=None, description="Date of the holdings (YYYY-MM-DD).")
    source_url: str | None = Field(default=None, description="ETFIQ page for the fund.")
    issuer_source: str | None = Field(default=None, description="The issuer file the holdings came from.")
    attribution: str | None = Field(default=None, description="Attribution line to keep when reusing the data.")
    license: str | None = Field(default=None, description="Holdings are issuer-published and stay under the issuer's terms.")


class EtfiqEtfHoldingsFetcher(Fetcher[EtfiqEtfHoldingsQueryParams, list[EtfiqEtfHoldingsData]]):
    """ETFIQ ETF Holdings fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> EtfiqEtfHoldingsQueryParams:
        return EtfiqEtfHoldingsQueryParams(**params)

    @staticmethod
    async def aextract_data(query: EtfiqEtfHoldingsQueryParams, credentials: dict[str, str] | None, **kwargs: Any) -> list[dict]:
        rows = await call(client().holdings, query.symbol)
        return rows[: query.limit] if query.limit else rows

    @staticmethod
    def transform_data(query: EtfiqEtfHoldingsQueryParams, data: list[dict], **kwargs: Any) -> list[EtfiqEtfHoldingsData]:
        return [EtfiqEtfHoldingsData(
            symbol=r["symbol"], name=r["name"], rank=r["rank"], weight_pct=r["weight_pct"], is_cash=r["is_cash"],
            as_of=r["as_of"], source_url=r["source_url"], issuer_source=r["issuer_source"],
            attribution=r["attribution"], license=r["license"]) for r in data]
