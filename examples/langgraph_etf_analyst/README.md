# LangGraph ETF analyst

askIQ: 99 of 100 ETF numbers right, 0 wrong. Best general AI with web search: 92 of 100. Oct 29, 2026. [AI accuracy test](https://etfiq.com/research/ai-accuracy/)

A three-node LangGraph agent. It screens a theme, compares the two largest funds, and writes a dated, cited note.

Graph: `screen_theme` (etfiq_screen) then `compare_top_two` (etfiq_compare) then `write_summary` (Claude).

## Run

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=...        # your own key; the script only reads it from the environment
python agent.py                     # theme: Semiconductors
python agent.py --theme "Gold miners"
```

No key? `python agent.py --no-llm` runs the two data steps and prints a plain template note.

Set `ETFIQ_AGENT_MODEL` to change the model (default `claude-sonnet-4-5`).

## What you get

A short note with each number dated, each fund linked to its ETFIQ page, and the line "Source: ETFIQ (etfiq.com), data as of <date>". Free to use with credit and a link to ETFIQ: https://etfiq.com/license/

Not investment advice. The model is told to use only the numbers the tools returned.
