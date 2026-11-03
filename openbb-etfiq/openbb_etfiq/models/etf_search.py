"""ETFIQ ETF Search model."""
from typing import Any

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.etf_search import EtfSearchData, EtfSearchQueryParams
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field

from openbb_etfiq.models._common import call, client


class EtfiqEtfSearchQueryParams(EtfSearchQueryParams):
    """ETFIQ ETF Search query. Matches ticker or name."""

    limit: int = Field(default=25, description="Maximum rows to return.")


class EtfiqEtfSearchData(EtfSearchData):
    """ETFIQ ETF Search data."""

    issuer: str | None = Field(default=None, description="Issuer of the ETF.")
    category: str | None = Field(default=None, description="ETFIQ category (Stocks, Bonds, Themes, ...).")
    segment: str | None = Field(default=None, description="ETFIQ segment within the category.")
    as_of: str | None = Field(default=None, description="Date of ETFIQ's data (YYYY-MM-DD).")
    source_url: str | None = Field(default=None, description="ETFIQ page for the fund.")
    attribution: str | None = Field(default=None, description="Attribution line to keep when reusing the data.")


class EtfiqEtfSearchFetcher(Fetcher[EtfiqEtfSearchQueryParams, list[EtfiqEtfSearchData]]):
    """ETFIQ ETF Search fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> EtfiqEtfSearchQueryParams:
        return EtfiqEtfSearchQueryParams(**params)

    @staticmethod
    async def aextract_data(query: EtfiqEtfSearchQueryParams, credentials: dict[str, str] | None, **kwargs: Any) -> list[dict]:
        rows = await call(client().search, query.query or "", query.limit)
        if not rows:
            raise EmptyDataError("ETFIQ found no fund for that query.")
        return rows

    @staticmethod
    def transform_data(query: EtfiqEtfSearchQueryParams, data: list[dict], **kwargs: Any) -> list[EtfiqEtfSearchData]:
        return [EtfiqEtfSearchData(symbol=r["ticker"], **{k: v for k, v in r.items() if k in
                ("name", "issuer", "category", "segment", "as_of", "source_url", "attribution")}) for r in data]
