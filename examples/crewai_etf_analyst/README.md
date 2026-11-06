# CrewAI ETF analyst

askIQ: 99 of 100 ETF numbers right, 0 wrong. Best general AI with web search: 92 of 100. Oct 29, 2026. [AI accuracy test](https://etfiq.com/research/ai-accuracy/)

Two CrewAI agents on the same task as the LangGraph example: an analyst screens a theme and compares the two largest funds, a writer turns the numbers into a dated, cited note.

Tools: `etfiq_screen_theme` and `etfiq_compare_funds`, wrapped from langchain-etfiq.

## Run

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=...        # your own key; the script only reads it from the environment
python agent.py                     # theme: Semiconductors
python agent.py --theme "Gold miners"
```

No key? `python agent.py --check` builds the crew and runs both tools once, with no model call.

Set `ETFIQ_AGENT_MODEL` to change the model (default `anthropic/claude-sonnet-4-5`).

## What you get

A short note with each number dated, each fund linked to its ETFIQ page, and the line "Source: ETFIQ (etfiq.com), data as of <date>". Free to use with credit and a link to ETFIQ: https://etfiq.com/license/

Not investment advice. The model is told to use only the numbers the tools returned.
