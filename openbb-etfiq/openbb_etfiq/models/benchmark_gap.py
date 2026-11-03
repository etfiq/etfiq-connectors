"""ETFIQ benchmark return gap (ETFIQ-specific model)."""
from typing import Any

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from pydantic import Field, field_validator

from openbb_etfiq.models._common import call, client


class EtfiqBenchmarkGapQueryParams(QueryParams):
    """ETFIQ benchmark gap query."""

    symbol: str = Field(description="Symbol to get data for (ETF).")

    @field_validator("symbol")
    @classmethod
    def to_upper(cls, v: str) -> str:
        return v.upper()


class EtfiqBenchmarkGapData(Data):
    """One fund's one-year return against its own benchmark, in percentage points."""

    symbol: str = Field(description="Symbol of the ETF.")
    name: str | None = Field(default=None, description="Name of the ETF.")
    benchmark: str | None = Field(default=None, description="Index the fund names, where it names one.")
    benchmark_etf: str | None = Field(default=None, description="The ETF ETFIQ prices the benchmark through.")
    return_1y_pct: float | None = Field(default=None, description="Fund one-year total return, percent.")
    gap_1y_pts: float | None = Field(default=None, description="Fund minus benchmark, percentage points. Negative trails.")
    gap_1y_abs_pts: float | None = Field(default=None, description="Size of the gap, percentage points.")
    as_of: str | None = Field(default=None, description="Last day of the one-year window (YYYY-MM-DD).")
    source_url: str | None = Field(default=None, description="ETFIQ page for the fund.")
    attribution: str | None = Field(default=None, description="Attribution line to keep when reusing the data.")


class EtfiqBenchmarkGapFetcher(Fetcher[EtfiqBenchmarkGapQueryParams, EtfiqBenchmarkGapData]):
    """ETFIQ benchmark gap fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> EtfiqBenchmarkGapQueryParams:
        return EtfiqBenchmarkGapQueryParams(**params)

    @staticmethod
    async def aextract_data(query: EtfiqBenchmarkGapQueryParams, credentials: dict[str, str] | None, **kwargs: Any) -> dict:
        return await call(client().benchmark_gap, query.symbol)

    @staticmethod
    def transform_data(query: EtfiqBenchmarkGapQueryParams, data: dict, **kwargs: Any) -> EtfiqBenchmarkGapData:
        return EtfiqBenchmarkGapData(
            symbol=data["ticker"], name=data["name"], benchmark=data["benchmark"], benchmark_etf=data["benchmark_etf"],
            return_1y_pct=data["return_1y_pct"], gap_1y_pts=data["gap_1y_pts"], gap_1y_abs_pts=data["gap_1y_abs_pts"],
            as_of=data["as_of"], source_url=data["source_url"], attribution=data["attribution"])
