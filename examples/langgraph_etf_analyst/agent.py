"""A small LangGraph ETF analyst: screen a theme, compare the top two funds, write a dated, cited summary.

    python agent.py                      # needs ANTHROPIC_API_KEY (read from the environment, never printed)
    python agent.py --theme "Gold miners"
    python agent.py --no-llm             # runs the data steps and a plain template, no key needed

Data: ETFIQ's free, keyless data through langchain-etfiq. Not investment advice.
"""
import argparse
import json
import os
import sys
from typing import TypedDict

from langchain_etfiq import EtfiqToolkit
from langgraph.graph import END, START, StateGraph

MODEL = os.environ.get("ETFIQ_AGENT_MODEL", "claude-sonnet-4-5")
TOOLS = {t.name: t for t in EtfiqToolkit().get_tools()}


class State(TypedDict, total=False):
    theme: str
    use_llm: bool
    funds: list      # the screened funds in the theme, largest first
    compared: list   # the top two, side by side
    summary: str


def screen_theme(state: State) -> State:
    """Screen the Themes category and keep the funds whose segment matches the theme."""
    rows = TOOLS["etfiq_screen"].invoke({"category": "Themes", "sort": "net_assets", "limit": 200})
    if not isinstance(rows, list):
        raise SystemExit(f"screen failed: {rows}")
    want = state["theme"].strip().lower()
    funds = [r for r in rows if want in (r.get("segment") or "").lower()]
    if len(funds) < 2:
        segs = sorted({r.get("segment") for r in rows if r.get("segment")})
        raise SystemExit(f"Fewer than two funds match theme {state['theme']!r}. Try one of: {', '.join(segs)}")
    return {"funds": funds}


def compare_top_two(state: State) -> State:
    top = [f["ticker"] for f in state["funds"][:2]]
    compared = TOOLS["etfiq_compare"].invoke({"tickers": top})
    if not isinstance(compared, list) or len(compared) < 2:
        raise SystemExit(f"compare failed: {compared}")
    return {"compared": compared}


def _facts(state: State) -> dict:
    keep = ["ticker", "name", "segment", "fee", "net_assets", "net_assets_asof", "ret_1y", "ret_1y_asof",
            "yield_12m", "holdings_count", "holdings_top10", "flow_1m", "flow_1m_pct", "flow_asof", "as_of",
            "source_url"]
    return {"theme": state["theme"], "funds_in_theme": len(state["funds"]),
            "compared": [{k: r.get(k) for k in keep} for r in state["compared"]]}


def _template(state: State) -> str:
    a, b = state["compared"][:2]
    lines = [f"{state['theme']}: {len(state['funds'])} ETFs on ETFIQ. The two largest, as of {a['as_of']}:"]
    for r in (a, b):
        lines.append(f"- {r['ticker']} ({r['name']}): fee {r['fee']}%, net assets ${r['net_assets']/1e9:,.1f}B "
                     f"as of {r['net_assets_asof']}, 1-year return {r['ret_1y']:.1f}% as of {r['ret_1y_asof']}. "
                     f"{r['source_url']}")
    return "\n".join(lines)


def write_summary(state: State) -> State:
    if not state.get("use_llm"):
        text = _template(state)
    else:
        from langchain_anthropic import ChatAnthropic  # key comes from ANTHROPIC_API_KEY
        llm = ChatAnthropic(model=MODEL, temperature=0, max_tokens=700)
        msg = llm.invoke([
            ("system", "You write short ETF research notes. Use only the numbers in the JSON. Say the date next to "
                       "every number. Cite each fund's source_url. Plain sentences, no em dashes. Never say buy, "
                       "sell or hold, and never recommend. End with: Source: ETFIQ (etfiq.com), data as of <as_of>. "
                       "Not investment advice."),
            ("human", json.dumps(_facts(state), indent=1)),
        ])
        text = msg.content if isinstance(msg.content, str) else "".join(
            p.get("text", "") for p in msg.content if isinstance(p, dict))
    return {"summary": text}


def build_graph():
    g = StateGraph(State)
    g.add_node("screen_theme", screen_theme)
    g.add_node("compare_top_two", compare_top_two)
    g.add_node("write_summary", write_summary)
    g.add_edge(START, "screen_theme")
    g.add_edge("screen_theme", "compare_top_two")
    g.add_edge("compare_top_two", "write_summary")
    g.add_edge("write_summary", END)
    return g.compile()


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--theme", default="Semiconductors", help="a Themes segment, such as Semiconductors")
    ap.add_argument("--no-llm", action="store_true", help="skip the model, print a template summary")
    a = ap.parse_args(argv)
    use_llm = not a.no_llm
    if use_llm and not os.environ.get("ANTHROPIC_API_KEY"):
        print("Set ANTHROPIC_API_KEY, or run with --no-llm.", file=sys.stderr)
        return 2
    out = build_graph().invoke({"theme": a.theme, "use_llm": use_llm})
    print(out["summary"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
