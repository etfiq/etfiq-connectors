# ETFIQ MCP quickstart

askIQ: 99 of 100 ETF numbers right, 0 wrong. Best general AI with web search: 92 of 100. Oct 29, 2026. [AI accuracy test](https://etfiq.com/research/ai-accuracy/)

Connect your AI to dated data on about 5,000 US-listed ETFs. Read only, 33 tools, no key, no sign-in.

**Server URL: `https://mcp.etfiq.com/mcp`** (streamable HTTP)

## Connect

### Claude Code
```bash
claude mcp add --transport http etfiq https://mcp.etfiq.com/mcp
claude mcp list        # etfiq ... Connected
```

### Claude Desktop and claude.ai
Easiest: Settings, Connectors, Add custom connector. Name `ETFIQ`, URL `https://mcp.etfiq.com/mcp`. No sign-in is asked. If ETFIQ shows up in the connectors directory (Browse connectors), add it from there instead.

Config file route. `claude_desktop_config.json` starts local servers, so a remote server goes through the `mcp-remote` bridge (needs Node):
```json
{
  "mcpServers": {
    "etfiq": {
      "command": "npx",
      "args": ["-y", "mcp-remote", "https://mcp.etfiq.com/mcp"]
    }
  }
}
```
Restart Claude Desktop after saving.

### Cursor
`~/.cursor/mcp.json` (or `.cursor/mcp.json` in a project):
```json
{ "mcpServers": { "etfiq": { "url": "https://mcp.etfiq.com/mcp" } } }
```

### VS Code
`.vscode/mcp.json` in a workspace:
```json
{ "servers": { "etfiq": { "type": "http", "url": "https://mcp.etfiq.com/mcp" } } }
```
Or user settings (`settings.json`):
```json
{ "mcp": { "servers": { "etfiq": { "type": "http", "url": "https://mcp.etfiq.com/mcp" } } } }
```
Then open Copilot Chat in Agent mode and pick the ETFIQ tools.

### ChatGPT
ChatGPT supports remote MCP servers as connectors in developer mode: Settings, Connectors, Advanced, turn on Developer mode, then Create a connector with the URL above and no authentication. Plan and menu names change, so check OpenAI's current MCP connector help if a step differs.

### Any other MCP client
Point it at the raw URL: `https://mcp.etfiq.com/mcp`. Transport: streamable HTTP. Auth: none. Or call it directly:
```bash
curl -s https://mcp.etfiq.com/mcp \
  -H 'content-type: application/json' -H 'accept: application/json, text/event-stream' \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"etf_profile","arguments":{"ticker":"JEPI"}}}'
```

## Try three questions

1. **"Which ETFs had the biggest inflows and outflows this week?"** Calls `etf_flows` with a `1W` window. Expect the top inflows and outflows with dollar flow, issuer, category and the date each runs through, plus the net flow across all funds counted.
2. **"What are the ten biggest holdings of SPY, and how old is the file?"** Calls `etf_holdings`. Expect names, tickers and weights in percent, the source (issuer daily file) and the as-of date.
3. **"Compare the two largest semiconductor ETFs. Which costs less?"** Calls `etf_theme` to list the theme, then `etf_compare`. Expect fee, net assets, returns and flows side by side, each with its own date and a link to the ETFIQ fund page.

Other tools worth a look: `etf_screen`, `etf_overlap`, `etf_scorecard`, `etf_committee`, `etf_promise`, `etf_news_today`, `etfiq_as_of`.

## Notebook

[examples/etfiq_quickstart.ipynb](examples/etfiq_quickstart.ipynb) calls the server over HTTP JSON-RPC with plain `requests` and loads the answers into pandas: `etf_flows` into a DataFrame, an `etf_holdings` table, and `etfiq_as_of` for a past date (point in time). Outputs are saved from a live run.

```bash
pip install requests pandas jupyter
jupyter notebook examples/etfiq_quickstart.ipynb
```

## Agent examples

- [LangGraph ETF analyst](examples/langgraph_etf_analyst/)
- [CrewAI ETF analyst](examples/crewai_etf_analyst/)

Each runs with only an `ANTHROPIC_API_KEY`.

## Data provenance and citation

Every answer carries its source, its as-of date, the ETFIQ page it came from and a ready `citation` string. Use it.

```json
"provenance": [{"field": "holdings", "source": "issuer daily file", "as_of": "2026-11-04", "source_uri": "..."}],
"as_of": "2026-11-04",
"citation": "ETFIQ, as of 2026-11-04. https://etfiq.com/funds/spy"
```

Free to use with credit and a link to ETFIQ: "Source: ETFIQ (etfiq.com), data as of <date>". Numbers an issuer publishes, such as holdings files, stay under the issuer's terms and are credited in `provenance`. When a tool cannot answer it refuses and says why, instead of returning a near match. Licence: https://etfiq.com/license/

Not investment advice.
