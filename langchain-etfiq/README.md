# langchain-etfiq

LangChain tools for ETFIQ's free ETF data. No API key.

```python
from langchain_etfiq import EtfiqToolkit

tools = {t.name: t for t in EtfiqToolkit().get_tools()}
tools["etfiq_profile"].invoke({"ticker": "JEPI"})
# {'ticker': 'JEPI', 'name': 'JPMorgan Equity Premium Income ETF', 'fee': 0.35, 'fee_asof': '2026-10-19',
#  'ret_1y': 9.95, 'yield_12m': 8.63, 'bench_gap_1y': -1.6, 'bench_gap_1y_ref': 'SPY', ...,
#  'as_of': '2026-11-02', 'source_url': 'https://etfiq.com/funds/jepi',
#  'attribution': 'Source: ETFIQ (etfiq.com), data as of 2026-11-02'}
```

Source: ETFIQ (etfiq.com), data as of the date in each record's `as_of`. Keep the record's `attribution` line when you reuse it.

## Tools

| Tool | Does |
|---|---|
| `etfiq_search` | find ETFs by ticker or name |
| `etfiq_profile` | fee, size, returns, yield, IQ score, flows, benchmark gap, each dated |
| `etfiq_holdings` | issuer-published holdings, weights in percent, cash as its own row |
| `etfiq_flows` | money in and out, 1D to 1Y |
| `etfiq_compare` | two to five ETFs side by side |
| `etfiq_screen` | filter by category, issuer, fee, size, return, yield |

Give them to an agent:

```python
from langchain.agents import create_agent
agent = create_agent("anthropic:claude-sonnet-4-5", EtfiqToolkit().get_tools())
```

## Or use the MCP server

ETFIQ's MCP server (33 tools, including the committee, scorecards and model portfolios) works today through `langchain-mcp-adapters`:

```python
from langchain_mcp_adapters.client import MultiServerMCPClient

client = MultiServerMCPClient({"etfiq": {"url": "https://mcp.etfiq.com/mcp", "transport": "streamable_http"}})
tools = await client.get_tools()   # 33 tools
```

## Licence and terms

Code: MIT. ETFIQ's computed data is open with attribution, see https://etfiq.com/license/. Holdings are issuer-published and stay under the issuer's terms; each record says so. Requests are paced at 2 a second with `User-Agent: etfiq-langchain/0.1.0 (data@etfiq.com)`.

## Tests

```
pip install -e ".[test]" && pytest tests
```

Unit tests use `langchain-tests`. Integration tests read the live files at https://etfiq.com/data/.
