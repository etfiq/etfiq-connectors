"""ETFIQ ETF Info model."""
from datetime import date as dateType
from typing import Any

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.etf_info import EtfInfoData, EtfInfoQueryParams
from pydantic import Field

from openbb_etfiq.models._common import call, client


class EtfiqEtfInfoQueryParams(EtfInfoQueryParams):
    """ETFIQ ETF Info query."""


class EtfiqEtfInfoData(EtfInfoData):
    """ETFIQ ETF Info data. Each figure has its own date in a field beside it."""

    category: str | None = Field(default=None, description="ETFIQ category.")
    segment: str | None = Field(default=None, description="ETFIQ segment within the category.")
    benchmark: str | None = Field(default=None, description="Index the fund is measured against.")
    expense_ratio_pct: float | None = Field(default=None, description="Total expense ratio, percent.")
    expense_ratio_asof: str | None = Field(default=None, description="Date of the expense ratio.")
    net_assets: float | None = Field(default=None, description="Net assets, USD.")
    net_assets_asof: str | None = Field(default=None, description="Date of net assets.")
    return_1y_pct: float | None = Field(default=None, description="One-year total return, percent.")
    return_1y_asof: str | None = Field(default=None, description="Last day of the one-year return.")
    yield_12m_pct: float | None = Field(default=None, description="Trailing 12-month yield, percent.")
    iq_score: float | None = Field(default=None, description="ETFIQ category score, 0 to 100, where one exists.")
    as_of: str | None = Field(default=None, description="Date of the ETFIQ file read (YYYY-MM-DD).")
    source_url: str | None = Field(default=None, description="ETFIQ page for the fund.")
    attribution: str | None = Field(default=None, description="Attribution line to keep when reusing the data.")


class EtfiqEtfInfoFetcher(Fetcher[EtfiqEtfInfoQueryParams, EtfiqEtfInfoData]):
    """ETFIQ ETF Info fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> EtfiqEtfInfoQueryParams:
        return EtfiqEtfInfoQueryParams(**params)

    @staticmethod
    async def aextract_data(query: EtfiqEtfInfoQueryParams, credentials: dict[str, str] | None, **kwargs: Any) -> dict:
        return await call(client().profile, query.symbol)

    @staticmethod
    def transform_data(query: EtfiqEtfInfoQueryParams, data: dict, **kwargs: Any) -> EtfiqEtfInfoData:
        launched = data.get("launched")
        return EtfiqEtfInfoData(
            symbol=data["ticker"], name=data.get("name"), issuer=data.get("issuer"),
            domicile="US" if data.get("quoted") else None,
            website=data["source_url"],
            inception_date=dateType.fromisoformat(launched) if launched else None,
            category=data.get("category"), segment=data.get("segment"), benchmark=data.get("benchmark"),
            expense_ratio_pct=data.get("fee"), expense_ratio_asof=data.get("fee_asof"),
            net_assets=data.get("net_assets"), net_assets_asof=data.get("net_assets_asof"),
            return_1y_pct=data.get("ret_1y"), return_1y_asof=data.get("ret_1y_asof"),
            yield_12m_pct=data.get("yield_12m"), iq_score=data.get("iq_score"),
            as_of=data["as_of"], source_url=data["source_url"], attribution=data["attribution"])
