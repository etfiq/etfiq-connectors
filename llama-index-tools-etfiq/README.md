# LlamaIndex Tools Integration: ETFIQ

ETFIQ's free ETF data as LlamaIndex tools. No API key.

```python
from llama_index.tools.etfiq import EtfiqToolSpec

spec = EtfiqToolSpec()
print(spec.flows("SPY"))   # JSON: money in and out, 1D to 1Y, each record dated
```

Source: ETFIQ (etfiq.com), data as of the date in each record's `as_of`. Keep the record's `attribution` line when you reuse it.

## Install

```
pip install llama-index-tools-etfiq
```

## Use with an agent

```python
from llama_index.core.agent.workflow import FunctionAgent
from llama_index.llms.openai import OpenAI

agent = FunctionAgent(tools=EtfiqToolSpec().to_tool_list(), llm=OpenAI(model="gpt-4.1"))
await agent.run("Compare SPY and VOO on fee and one-year return. Give the date.")
```

## Tools

`search`, `profile`, `holdings`, `flows`, `compare`, `screen`. Each returns a JSON string of records with `as_of`, `source_url` and `attribution`. A fund ETFIQ does not cover returns an `{"error": ...}` record, not an exception.

ETFIQ's MCP server (33 tools) is also open: https://mcp.etfiq.com/mcp, usable with `llama-index-tools-mcp`.

## Licence and terms

Code: MIT. ETFIQ's computed data is open with attribution, see https://etfiq.com/license/. Holdings are issuer-published and stay under the issuer's terms; each record says so. Requests are paced at 2 a second with `User-Agent: etfiq-llamaindex/0.1.0 (data@etfiq.com)`.

## Tests

```
pip install -e . pytest && pytest tests
```

The tests read the live files at https://etfiq.com/data/.
