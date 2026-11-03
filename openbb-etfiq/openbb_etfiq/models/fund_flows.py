"""ETFIQ fund flows (ETFIQ-specific model)."""
from typing import Any

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from pydantic import Field, field_validator

from openbb_etfiq.models._common import call, client


class EtfiqFundFlowsQueryParams(QueryParams):
    """ETFIQ fund flows query."""

    symbol: str = Field(description="Symbol to get data for (ETF).")

    @field_validator("symbol")
    @classmethod
    def to_upper(cls, v: str) -> str:
        return v.upper()


class EtfiqFundFlowsData(Data):
    """Money in and out of one ETF over a window, computed by ETFIQ."""

    symbol: str = Field(description="Symbol of the ETF.")
    window: str = Field(description="Window: 1D, 1W, 1M, 3M, YTD, 1Y or SINCE (since the first month on record).")
    flow_usd: float | None = Field(default=None, description="Net flow over the window, USD. Negative is money out.")
    flow_pct_of_start_assets: float | None = Field(default=None, description="Flow as a percent of net assets at the window's start.")
    start_assets_usd: float | None = Field(default=None, description="Net assets at the window's start, USD.")
    start: str | None = Field(default=None, alias="from", description="First day of the window.")
    end: str | None = Field(default=None, alias="to", description="Last day of the window.")
    days: int | None = Field(default=None, description="Trading days in the window, where it is counted.")
    days_in: int | None = Field(default=None, description="Days with money in.")
    days_out: int | None = Field(default=None, description="Days with money out.")
    as_of: str | None = Field(default=None, description="Date of the data (YYYY-MM-DD).")
    source_url: str | None = Field(default=None, description="ETFIQ page for the fund.")
    attribution: str | None = Field(default=None, description="Attribution line to keep when reusing the data.")


class EtfiqFundFlowsFetcher(Fetcher[EtfiqFundFlowsQueryParams, list[EtfiqFundFlowsData]]):
    """ETFIQ fund flows fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> EtfiqFundFlowsQueryParams:
        return EtfiqFundFlowsQueryParams(**params)

    @staticmethod
    async def aextract_data(query: EtfiqFundFlowsQueryParams, credentials: dict[str, str] | None, **kwargs: Any) -> list[dict]:
        return await call(client().flows, query.symbol)

    @staticmethod
    def transform_data(query: EtfiqFundFlowsQueryParams, data: list[dict], **kwargs: Any) -> list[EtfiqFundFlowsData]:
        return [EtfiqFundFlowsData(symbol=r["ticker"], **{k: v for k, v in r.items() if k != "ticker" and k in EtfiqFundFlowsData.model_fields or k in ("from", "to")}) for r in data]
