"""Morning Market Brief.

Fetches watchlist prices, computes % change in Python (never in the AI),
asks Gemini for a short narrative plus one grounded news blurb about the
day's biggest mover, and writes/prints a Markdown brief. Optionally emails
the brief as HTML using the existing project emailer.

Usage:
    python market_brief.py                       # writes brief.md, prints it
    python market_brief.py --tickers AAPL MSFT    # custom watchlist
    python market_brief.py --dry-run              # offline, no keys needed
    python market_brief.py --send                 # also emails the brief
"""

import argparse
import os
import sys
from datetime import date
from pathlib import Path

from dotenv import load_dotenv

# --------------------------------------------------------------------------
# Repo-relative import of the existing emailer.
#
# This file lives at:   <repo>/9_ai_capstone/project/market_brief.py
# The emailer lives at: <repo>/8_send_email/project/emailer.py
#
# parents[0] = .../9_ai_capstone/project
# parents[1] = .../9_ai_capstone
# parents[2] = <repo>
# --------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parents[2]
EMAILER_DIR = REPO_ROOT / "8_send_email" / "project"
sys.path.insert(0, str(EMAILER_DIR))

# --------------------------------------------------------------------------
# Config
# --------------------------------------------------------------------------
MODEL = "gemini-3.6-flash"
WATCHLIST = ["AAPL", "MSFT", "NVDA", "TSLA", "VOO"]
MAX_OUTPUT_TOKENS = 1500 #tokens are also consumed for thinking so 300 is not enough for the brief to be generated. 1500 is a safe number to ensure the brief is generated in full.

BRIEF_PATH = Path(__file__).resolve().parent / "brief.md"

# Canned data so --dry-run (and a missing API key) never touches the network.
SAMPLE_PRICES = {
    "AAPL": {"last": 231.50, "prev": 228.10},
    "MSFT": {"last": 452.30, "prev": 455.00},
    "NVDA": {"last": 138.20, "prev": 131.75},
    "TSLA": {"last": 265.40, "prev": 270.10},
    "VOO": {"last": 545.60, "prev": 544.90},
}

MOCK_NARRATIVE = (
    "Markets opened mixed this morning, with chipmaker NVDA leading gains "
    "on continued AI demand while TSLA slipped on profit-taking. "
    "Broad-market VOO was roughly flat, suggesting a quiet, wait-and-see "
    "session ahead of upcoming economic data."
)

MOCK_NEWS_LINE = (
    "NVDA shares are being cited as the session's biggest mover on chatter "
    "about strong AI-chip demand (sample data — no live news lookup was made)."
)


# --------------------------------------------------------------------------
# Price fetching & math
# --------------------------------------------------------------------------
def compute_pct_change(last: float, prev: float) -> float:
    """Return the % change from prev to last. 0.0 if prev is 0."""
    if not prev:
        return 0.0
    return (last - prev) / prev * 100


def get_dry_run_prices(tickers: list[str]) -> dict:
    """Build a prices dict from canned sample data, no network calls."""
    prices = {}
    for ticker in tickers:
        sample = SAMPLE_PRICES.get(ticker, {"last": 100.0, "prev": 99.0})
        #dict.get(key, default)
        prices[ticker] = {
            "last": sample["last"],
            "prev": sample["prev"],
            "pct": compute_pct_change(sample["last"], sample["prev"]),
        }
    return prices


def fetch_prices(tickers: list[str]) -> dict:
    """Fetch last price and previous close for each ticker via yfinance.

    A ticker that fails to fetch is skipped with a printed warning; the
    brief still ships with whatever tickers succeeded.
    """
    import yfinance as yf

    prices = {}
    for ticker in tickers:
        try:
            fast_info = yf.Ticker(ticker).fast_info
            last = fast_info["lastPrice"]
            prev = fast_info["previousClose"]
            prices[ticker] = {
                "last": last,
                "prev": prev,
                "pct": compute_pct_change(last, prev),
            }
        except Exception as exc:  # noqa: BLE001 - keep the brief alive
            #Exception is the base class for all built-in exceptions except for system-exiting exceptions.
            # catch anything that goes wrong here, whatever its specific type.
            # noqa:
            # What a linter is. A linter is a program that reads your code without running it and points out things that are likely mistakes or bad habits
            # What noqa does. "No quality assurance." When the linter sees this comment on a line, it skips its checks for that line.
            #  Written bare — # noqa — it suppresses every rule on that line,
            #  but you can also write # noqa: RULE1,RULE2 to suppress only specific rules.
            #BLE001 :
            #Normally you'd catch one specific error you expect, like except KeyError.
            #Catching Exception catches all of them
            #The linter can't tell whether you did that on purpose, so it flags every except Exception with the code BLE001
            #In this file, the catch-all is on purpose: one bad ticker shouldn't kill the whole report. 
            # So we tell the linter to stop complaining about this one line — # noqa: BLE001 — plus a note saying why.
            print(f"Warning: could not fetch {ticker} ({exc}); skipping it.")
    return prices


# --------------------------------------------------------------------------
# Gemini calls
# --------------------------------------------------------------------------
def get_gemini_client():
    """Build a google-genai Client from GEMINI_API_KEY, or None if unset."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return None
    from google import genai

    return genai.Client(api_key=api_key) #can be called with no args also as key is there in .env 


def build_narrative(client, prices: dict) -> str:
    """Ask Gemini for a 3-sentence narrative over already-computed numbers.

    The AI never computes prices or percentages; it only narrates the
    numbers Python has already worked out.
    """
    from google.genai import types
    #types is the module inside google.genai that holds 
    # all the configuration and data classes — the structured objects you hand to the SDK when a plain string isn't enough.
    #GenerateContentConfig is a class inside types that lets you specify things like max_output_tokens, temperature, and other parameters for the content generation call.
    
    #summary_lines is a list of strings, one per ticker
    summary_lines = [
        f"{ticker}: {data['pct']:+.2f}% (last {data['last']:.2f}, " #+ — always print a sign. Positive numbers get +, negative get -. By default only negatives show a sign.
        f"previous close {data['prev']:.2f})" #example: AAPL: +1.52% (last 231.50, previous close 228.10)
        for ticker, data in prices.items()
        #.items() gives a view. Each item in the view is a (key, value) tuple
    ]
    prompt = (
        "You are writing a short morning market brief. Use ONLY the "
        "figures below — they are already computed, do not recompute, "
        "estimate, or invent any numbers. Write exactly 3 plain-English "
        "sentences summarizing the overall picture.\n\n" #\n - move to next line and \n for empty line - brings some separation between the prompt and the data, making it easier for the model to parse.
        + "\n".join(summary_lines)
        #"\n".join(summary_lines) takes the list of five strings and glues them into one string, inserting "\n" between each pair.
        #AAPL: +1.49% (last 231.50, previous close 228.10)
        #MSFT: -0.59% (last 452.30, previous close 455.00)
        #NVDA: +4.90% (last 138.20, previous close 131.75)
    )
    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                max_output_tokens=MAX_OUTPUT_TOKENS,
            ),
            #config is the bag of optional settings for the call
            #reply is truncated if more than MAX_OUTPUT_TOKENS tokens are generated, so we can be sure the brief is short enough to fit in an email.
        )
        return (response.text or "").strip() or "Narrative unavailable."
        #a or b gives you a if a is truthy, otherwise b
    except Exception as exc:  # noqa: BLE001
        print(f"Warning: narrative generation failed ({exc}).")
        return "Narrative unavailable due to an API error."


def build_news_line(client, prices: dict) -> str | None:
    """Ask Gemini, with Google Search grounding, for 1-2 sentences of news
    context on the single biggest mover (largest absolute % change).

    Grounding is enabled on this call only. Returns None on any failure so
    the brief can still ship without a news line.
    """
    if not prices:
        return None

    from google.genai import types

    biggest_ticker, biggest_data = max(
        prices.items(), key=lambda kv: abs(kv[1]["pct"])
    )
    #key tells max how to rank the items. kv is a (ticker, data) tuple, so kv[1] is the data dict, and kv[1]["pct"] is the % change. abs() makes it the absolute value, so we get the biggest mover regardless of direction.
    #key function is called once per item, and whatever it returns is what gets compared.
    prompt = (
        f"In 1-2 concise sentences, explain today's news context for why "
        f"{biggest_ticker} stock moved {biggest_data['pct']:+.2f}% today."
    )
    try:
        response = client.models.generate_content(
            model='MODEL',
            contents=prompt,
            config=types.GenerateContentConfig(
                tools=[types.Tool(google_search=types.GoogleSearch())],
            ),
            #tools=[...] — the config takes a list of tools
            #types.Tool(google_search=...) — a Tool is a capability you hand the model. It has several optional slots (google_search, code_execution, function_declarations for your own Python functions); this fills exactly one.
            #types.GoogleSearch() — a marker object meaning "use Google's built-in search."
            #google_search is the name of a field on Tool - one of its named slots
            #types.GoogleSearch() is the value you put in that compartment.
        )
        text = (response.text or "").strip()
        print("look look")
        print(f"News line for {biggest_ticker}: {text}")
        return text or None
    except Exception as exc:  # noqa: BLE001
        print(f"Warning: news lookup failed ({exc}); shipping without it.")
        return None


# --------------------------------------------------------------------------
# Rendering
# --------------------------------------------------------------------------
def render_brief_markdown(prices: dict, narrative: str, news_line: str | None) -> str:
    """Assemble the full brief as Markdown: date header, price table,
    narrative, and (optionally) the news line."""
    today = date.today().strftime("%A, %B %d, %Y")
    #.strftime("%A, %B %d, %Y") — "string-format time." It converts the date object to text according to a pattern, where each % code is a placeholder for one piece of the date and everything else is copied literally
    #Wednesday, September 09, 2026
    lines = [f"# Morning Market Brief — {today}", ""]
    lines.append("| Ticker | Last | Prev Close | % Change |")
    lines.append("|---|---|---|---|")
    for ticker, data in prices.items():
        lines.append(
            f"| {ticker} | {data['last']:.2f} | {data['prev']:.2f} "
            f"| {data['pct']:+.2f}% |"
        )
    lines.append("") #blank line
    lines.append("## Narrative")
    lines.append(narrative)
    if news_line:
        lines.append("")
        lines.append("## In the News")
        lines.append(news_line)
    return "\n".join(lines) + "\n"
    #join takes every item in lines and glues them into a single string, placing the separator ("\n") between neighbours.


def render_brief_html(prices: dict, narrative: str, news_line: str | None) -> str:
    """Render the same brief as a simple standalone HTML document for email."""
    today = date.today().strftime("%A, %B %d, %Y")
    rows = "".join(
        f"<tr><td>{ticker}</td><td>{data['last']:.2f}</td>"
        f"<td>{data['prev']:.2f}</td><td>{data['pct']:+.2f}%</td></tr>"
        for ticker, data in prices.items()
    )
    news_html = (
        f"<h2>In the News</h2><p>{news_line}</p>" if news_line else ""
    )
    return (
        "<html><body>"
        f"<h1>Morning Market Brief — {today}</h1>"
        '<table border="1" cellpadding="4" cellspacing="0">'
        "<tr><th>Ticker</th><th>Last</th><th>Prev Close</th>"
        "<th>% Change</th></tr>"
        f"{rows}"
        "</table>"
        f"<h2>Narrative</h2><p>{narrative}</p>"
        f"{news_html}"
        "</body></html>"
    )


# --------------------------------------------------------------------------
# Email delivery
# --------------------------------------------------------------------------
def send_brief_via_email(html_body: str, brief_path: Path) -> None:
    """Send the brief as HTML using the existing project emailer.

    Any failure (missing module, missing SMTP config, etc.) prints one
    clear line and returns without a traceback; brief.md has already been
    written by the caller regardless of outcome.
    """
    try:
        from emailer import send_email
    except ImportError as exc:
        print(f"Could not send email: emailer module not found ({exc}).")
        return

    try:
        send_email(
            subject=f"Morning Market Brief — {date.today().strftime('%Y-%m-%d')}",
            html_body=html_body,
            attachments=[brief_path],
        )
    except Exception as exc:  # noqa: BLE001 - keep this a one-liner, no traceback
        print(f"Could not send email: {exc}")


# --------------------------------------------------------------------------
# CLI / orchestration
# --------------------------------------------------------------------------
def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Generate a morning market brief.")
    parser.add_argument(
        "--tickers",
        nargs="+",
        #nargs="+":  how many values the flag consumes. 
        # "+" means "one or more," greedily gathering every following token until the next flag or end of line. 
        # The result is always a list, even with a single value:
        default=WATCHLIST,
        #default=WATCHLIST — what args.tickers is when the flag is omitted entirely.
        help="Watchlist tickers (default: %(default)s)",
        #%(default)s is a placeholder that argparse replaces with the actual default value in the help text.
        #% — a placeholder starts here
        #(default) — the name of the value to insert;
        #s — format it as a string - needed here because you cannot put a list directly into string.
    )
    '''
    python market_brief.py --tickers AAPL MSFT NVDA   → args.tickers == ["AAPL", "MSFT", "NVDA"]
    python market_brief.py --tickers AAPL             → args.tickers == ["AAPL"]
    python market_brief.py --tickers                  → error: expected at least one argument
    '''
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Use canned sample data and skip all network/API calls.",
    )
    parser.add_argument(
        "--send",
        action="store_true",
        help="Also email the brief as HTML using the existing emailer.",
    )
    return parser.parse_args()


def main() -> None:
    """Build, write, print, and optionally email the morning market brief."""
    args = parse_args()
    load_dotenv() #no path provided - starts from the directory of the file that called it,If not found, go up one directory and check again,then the repo root, and so on up to /.

    dry_run = args.dry_run
    client = None

    if not dry_run:
        if not os.environ.get("GEMINI_API_KEY"):
            print("No GEMINI_API_KEY found in the environment.")
            print("Get a free key at: https://aistudio.google.com/apikey")
            print("Falling back to --dry-run mode.\n")
            dry_run = True
        else:
            client = get_gemini_client()

    prices = get_dry_run_prices(args.tickers) if dry_run else fetch_prices(args.tickers)
    if not prices:
        print("No price data available for any ticker. Exiting.")
        return

    if dry_run:
        narrative = MOCK_NARRATIVE
        news_line = MOCK_NEWS_LINE
    else:
        narrative = build_narrative(client, prices)
        news_line = build_news_line(client, prices)

    markdown = render_brief_markdown(prices, narrative, news_line)
    BRIEF_PATH.write_text(markdown, encoding="utf-8")
    #.write_text(markdown, ...) is a Path method that opens the file for writing, writes the string, and closes it — a shortcut for with statement pattern. 
    # It overwrites any existing file with the same name.
    print(markdown)

    if args.send:
        html_body = render_brief_html(prices, narrative, news_line)
        send_brief_via_email(html_body, BRIEF_PATH)


if __name__ == "__main__":
    main()
