# openbb-etfiq

ETFIQ's free ETF data inside the [OpenBB Platform](https://openbb.co). No API key.

```python
from openbb import obb

obb.etf.holdings("SPY", provider="etfiq", limit=3).to_df()[["rank", "symbol", "weight_pct", "as_of"]]
#    rank symbol  weight_pct       as_of
# 0     1   AAPL       7.699  2026-10-30
# 1     2   NVDA       7.580  2026-10-30
# 2     3   MSFT       5.932  2026-10-30

obb.etfiq.benchmark_gap(symbol="JEPI", provider="etfiq").to_df()  # 1Y return vs its own benchmark, in points
obb.etfiq.fund_flows(symbol="SPY", provider="etfiq").to_df()      # money in and out, 1D to 1Y
```

Data source: ETFIQ (etfiq.com), data as of the date in each row's `as_of` field. Every row also carries `source_url` and an `attribution` line to keep when you reuse it.

## Install

```
pip install openbb-etfiq
python -c "import openbb; openbb.build()"
```

## What it covers

| Command | ETFIQ data |
|---|---|
| `obb.etf.search` | ticker and name search, category, segment |
| `obb.etf.info` | issuer, launch date, fee, net assets, 1Y return, yield, IQ score, each with its own date |
| `obb.etf.holdings` | issuer-published holdings, weights in percent of net assets, cash as its own row |
| `obb.etfiq.fund_flows` | net flow by window (1D, 1W, 1M, 3M, YTD, 1Y, since record), with start assets |
| `obb.etfiq.benchmark_gap` | 1Y return minus the fund's own benchmark, in percentage points |

`EtfSectors` is not covered: ETFIQ does not publish per-fund sector weights as open data.

## Licence and terms

Code: MIT. ETFIQ's computed data is open with attribution ("Source: ETFIQ (etfiq.com), data as of <date>"), see https://etfiq.com/license/. Holdings are issuer-published and stay under the issuer's terms; their rows say so. Requests are paced at 2 a second and send `User-Agent: etfiq-openbb/0.1.0 (data@etfiq.com)`.

## Tests

```
pip install -e ".[test]" && pytest
```

The tests read the live files at https://etfiq.com/data/.
