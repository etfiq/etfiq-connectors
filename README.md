# ETFIQ connectors

askIQ: 99 of 100 ETF numbers right, 0 wrong. Best general AI with web search: 92 of 100. Oct 29, 2026. [AI accuracy test](https://etfiq.com/research/ai-accuracy/)

**New here? Start with the [QUICKSTART](QUICKSTART.md):** copy-paste setup for Claude, Cursor, VS Code, ChatGPT and any MCP client, a notebook, and agent examples.

Free, dated data on about 5,000 US-listed ETFs from [ETFIQ](https://etfiq.com), inside the tools you already use. No API key.

| Package | For |
|---|---|
| [openbb-etfiq](openbb-etfiq/) | OpenBB Platform provider: ETF search, info, holdings, fund flows, benchmark gap |
| [langchain-etfiq](langchain-etfiq/) | LangChain toolkit: search, profile, holdings, flows, compare, screen |
| [llama-index-tools-etfiq](llama-index-tools-etfiq/) | LlamaIndex tool spec with the same six tools |

Prefer MCP? Connect any MCP client to `https://mcp.etfiq.com/mcp` (33 tools, no sign-in).

## Connect via MCP (Claude, Cursor, Cline, ChatGPT)

No key, no sign-in. Server: `https://mcp.etfiq.com/mcp` (streamable HTTP, 33 read-only tools).

Cline, Cursor or any MCP client:

```json
{"mcpServers": {"etfiq": {"url": "https://mcp.etfiq.com/mcp", "type": "streamableHttp"}}}
```

Try: "Using ETFIQ, what were the biggest ETF outflows this week?"

Every record carries its date and source. Please credit "Source: ETFIQ (etfiq.com), data as of <date>". Data an issuer publishes stays under its owner's terms: https://etfiq.com/license/

Code: MIT. Not investment advice.
