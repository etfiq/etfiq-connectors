"""The same ETF analyst task in CrewAI: screen a theme, compare the top two funds, write a dated, cited note.

    python agent.py                      # needs ANTHROPIC_API_KEY (read from the environment, never printed)
    python agent.py --theme "Gold miners"
    python agent.py --check              # builds the crew and runs the tools once, no key and no model call

Tools: langchain-etfiq (ETFIQ's free, keyless data), wrapped as CrewAI tools. Not investment advice.
"""
import argparse
import json
import os
import sys

from crewai import Agent, Crew, Process, Task
from crewai.tools import tool
from langchain_etfiq import EtfiqToolkit

MODEL = os.environ.get("ETFIQ_AGENT_MODEL", "anthropic/claude-sonnet-4-5")
_T = {t.name: t for t in EtfiqToolkit().get_tools()}


@tool("etfiq_screen_theme")
def screen_theme(theme: str) -> str:
    """List ETFs in an ETFIQ theme segment (for example Semiconductors or Gold miners), largest net assets first.
    Returns JSON with ticker, name, fee, net_assets, ret_1y, as_of and source_url."""
    rows = _T["etfiq_screen"].invoke({"category": "Themes", "sort": "net_assets", "limit": 200})
    if not isinstance(rows, list):
        return json.dumps(rows)
    want = theme.strip().lower()
    hit = [r for r in rows if want in (r.get("segment") or "").lower()]
    if not hit:
        return json.dumps({"error": f"no funds for theme {theme!r}",
                           "themes": sorted({r.get("segment") for r in rows if r.get("segment")})})
    return json.dumps(hit[:10])


@tool("etfiq_compare_funds")
def compare_funds(ticker_a: str, ticker_b: str) -> str:
    """Compare two ETFs side by side with ETFIQ numbers, each with its own date and source_url."""
    return json.dumps(_T["etfiq_compare"].invoke({"tickers": [ticker_a, ticker_b]}))


def build_crew(theme: str, llm=MODEL) -> Crew:
    analyst = Agent(
        role="ETF research analyst",
        goal="Find the two largest ETFs in a theme and compare them with dated numbers.",
        backstory="You use only ETFIQ data from your tools. You never give investment advice.",
        tools=[screen_theme, compare_funds], llm=llm, allow_delegation=False, verbose=False)
    writer = Agent(
        role="ETF note writer",
        goal="Write a short, dated, cited note from the analyst's numbers.",
        backstory="Plain sentences. Every number has its date. No em dashes. Never say buy, sell or hold.",
        llm=llm, allow_delegation=False, verbose=False)
    screen_and_compare = Task(
        description=(f"Screen the theme '{theme}' with etfiq_screen_theme. Take the top two by net assets and "
                     "compare them with etfiq_compare_funds. Return the comparison JSON."),
        expected_output="The comparison JSON for the two largest funds in the theme.",
        agent=analyst)
    note = Task(
        description=("Write a note of at most 120 words. Use only the numbers from the comparison. Put the date "
                     "next to every number, link each fund's source_url, and end with: Source: ETFIQ (etfiq.com), "
                     "data as of <as_of>. Not investment advice."),
        expected_output="A short cited note.", agent=writer, context=[screen_and_compare])
    return Crew(agents=[analyst, writer], tasks=[screen_and_compare, note], process=Process.sequential)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--theme", default="Semiconductors", help="a Themes segment, such as Semiconductors")
    ap.add_argument("--check", action="store_true", help="build the crew and run both tools, no model call")
    a = ap.parse_args(argv)
    if a.check:
        crew = build_crew(a.theme)
        print(f"crew built: {len(crew.agents)} agents, {len(crew.tasks)} tasks")
        top = json.loads(screen_theme.run(theme=a.theme))
        print("screen ok:", [r["ticker"] for r in top[:2]])
        cmp_ = json.loads(compare_funds.run(ticker_a=top[0]["ticker"], ticker_b=top[1]["ticker"]))
        print("compare ok:", [(r["ticker"], r["as_of"]) for r in cmp_])
        return 0
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("Set ANTHROPIC_API_KEY, or run with --check.", file=sys.stderr)
        return 2
    print(build_crew(a.theme).kickoff().raw)
    return 0


if __name__ == "__main__":
    sys.exit(main())
