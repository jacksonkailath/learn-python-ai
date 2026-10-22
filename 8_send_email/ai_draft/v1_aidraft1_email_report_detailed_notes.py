#from __future__ import annotations
#Changes how Python treats type hints: they are stored as strings and not evaluated when the function is defined. Two practical effects:
#you can delete this as it is no longer needed in python 3.10 +
#To let list[Path] and dict[str, Any] work on Python 3.7–3.9, where the built-in list and dict couldn't be used as type hints yet.

import argparse
import os
import smtplib
import sys
from datetime import date
from email.message import EmailMessage
from pathlib import Path

from dotenv import load_dotenv

# Reuse the existing report-building code as-is.
from report_generator import generate_report, load_sales_rows, summarize_by_month, summarize_by_product
#change path to sales_summary.aidraft
REQUIRED_ENV_VARS = [
    "SMTP_HOST",
    "SMTP_PORT",
    "SMTP_USERNAME",
    "SMTP_PASSWORD",
    "EMAIL_FROM",
    "EMAIL_TO",
]


def load_config(env_path: Path) -> dict[str, str]:
    """Load and validate configuration from environment / .env file."""
    load_dotenv(dotenv_path=env_path if env_path.exists() else None)
    #load_dotenv(dotenv_path=env_path) -> you're telling python-dotenv exactly which file to read
    #What it does mechanically: opens the file at env_path, parses it line by line, and injects each key/value pair into os.environ
    # for example in .env if you have SMTP_HOST=smtp.gmail.com then after load_dotenv
    #you can access it as os.environ["SMTP_HOST"] which will return "smtp.gmail.com"
    #Missing .env is not fatal. That's deliberate — load_config immediately afterward checks REQUIRED_ENV_VARS and raises a SystemExit listing exactly which ones are absent.
    #load_dotenv() or load_dotenv(None): python-dotenv calls its internal find_dotenv(), which walks up the directory tree starting at folder of the calling file looking for a file named .env
    #If it finds nothing, it silently does nothing and returns False.

    missing = [name for name in REQUIRED_ENV_VARS if not os.environ.get(name)]
    if missing:
        raise SystemExit(
            #raise SystemExit is a way to exit the program with an error message. The message is printed to stderr and the program exits with status code 1.
            #The exit code 1 matters for the cron use case. Cron and CI runners check the exit status; nonzero means "this job failed," which is how you'd get an alert instead of silence.
            "Missing required environment variable(s): "
            f"{', '.join(missing)}\n"
            f"Set them in {env_path} (see .env.example) or export them directly."
        )

    return {
        "smtp_host": os.environ["SMTP_HOST"],
        "smtp_port": int(os.environ["SMTP_PORT"]), #string to int
        "smtp_username": os.environ["SMTP_USERNAME"],
        "smtp_password": os.environ["SMTP_PASSWORD"],
        "email_from": os.environ["EMAIL_FROM"],
        "email_to": [addr.strip() for addr in os.environ["EMAIL_TO"].split(",") if addr.strip()],
        #convert to comma separated list of emails; "a@x.com,b@x.com".split(",")   # ['a@x.com','b@x.com']
        "csv_folder": Path(os.environ.get("CSV_FOLDER", "sample_data")), 
        # "sample_data" is the fallback.
        #"sample_data" is relative to the current working directory — wherever you ran python from — not the script's location.
        #notice difference between .get and [] access: .get returns None if the key is absent, while [] raises KeyError. Here we want a default value, so .get is appropriate.
        #os.environ.get("CSV_FOLDER", "sample_data")    # returns "sample_data" if absent
        #os.environ["CSV_FOLDER"] would raise KeyError if absent
        "output_path": Path(os.environ.get("OUTPUT_PATH", "monthly_report.xlsx")),
        "subject": os.environ.get("EMAIL_SUBJECT", f"Weekly Sales Report - {date.today():%Y-%m-%d}"),
        #What it's saying: date.today() reads the system clock and uses whatever the machine's local timezone happens to be, without you ever stating what timezone you meant. Ruff's suggestion is datetime.datetime.now(tz=...).date() — same result, but you're forced to name the timezone explicitly.
    }


def build_html_summary(csv_folder: Path) -> str:
    """Build an HTML summary of totals, reusing the existing aggregation
    helpers rather than re-deriving totals from scratch."""
    rows = load_sales_rows(csv_folder)# list of dict like 
    '''
    [{"date": row["date"],"region": row["region"],"product": row["product"],"units": units,"unit_price": unit_price,},{}...]
    '''
    monthly = summarize_by_month(rows) #{month:{"orders": 0, "units": 0, "revenue": 0.0}}
    by_product = summarize_by_product(rows) #{product:{"units": 0, "revenue": 0.0}}

    total_orders = sum(m["orders"] for m in monthly.values())
    total_units = sum(m["units"] for m in monthly.values())
    total_revenue = sum(m["revenue"] for m in monthly.values())

    top_products = sorted(by_product.items(), key=lambda kv: kv[1]["revenue"], reverse=True)[:5]
    #by_product.items() gives you a view of (key, value) tuples
    #Python compares tuples position by position: first the product names, and only if those tie does it look at position 1. So sorted(by_product.items()) gives you alphabetical order by product name. Revenue never enters into it.
    #So key is how you say "don't compare the whole element — compare this part of it."
    #key has to be a callable, because sorted invokes it once per element.What you can't do is pass the value directly
    #kv is short for key value pair
    #kv[1] is the second element of the tuple — the value side of the (key, value) pair.
    #key=lambda kv: kv[1]["revenue"] — the sort key. sorted calls this on each element to decide the ordering
    #kv[0] is the product name
    #kv[1] is the stats dict
    #kv[1]["revenue"] is the number to sort on
    #The lambda is needed because there's no way to say "sort by a nested field" otherwise.
    #reverse=True — descending
    #[:5] — slice off the first five.

    #inside () is generator expression like f(x for x in items) 
    month_rows = "".join(
        f"<tr><td>{month}</td><td style='text-align:right'>{data['orders']:,}</td>" #{data['orders']:,} — comma as thousands separator. 1234 → 1,234
        f"<td style='text-align:right'>{data['units']:,}</td>"
        f"<td style='text-align:right'>${data['revenue']:,.2f}</td></tr>" #{data['revenue']:,.2f} — commas and exactly two decimal places. 4800.5 → 4,800.50; The $ before it is a literal character in the template, not part of the spec — so you get $4,800.50.
        #The four adjacent f-strings are one string, not four. Python concatenates adjacent literals at compile time
        #Purely for line-length; the output has no breaks between </td> and <td>.
        for month, data in sorted(monthly.items())
        #for month, data in sorted(monthly.items()) — .items() gives (key, value) tuples, unpacked into month and data
    )
    '''
    "".join(
    <expression>       # the f-string, evaluated once per iteration
    for month, data in sorted(monthly.items())
    )
    '''
    #This builds the HTML table body — one <tr> per month, all concatenated into a single string.
    #The overall shape is "".join(<generator expression>)
    #The generator produces one row string per month
    #join glues them together with "" between them (i.e. nothing)
    #Note there are no square brackets — it's a generator, not a list comprehension, so rows are produced lazily as join consumes them rather than all being built into a list first.
    #Why join rather than += in a loop? Strings are immutable in Python, so s += row creates a brand-new string every iteration, copying everything accumulated so far. join walks the sequence once, computes the total length, allocates once.

    product_rows = "".join(
        f"<tr><td>{product}</td><td style='text-align:right'>{data['units']:,}</td>"
        f"<td style='text-align:right'>${data['revenue']:,.2f}</td></tr>"
        for product, data in top_products
    )

    table_style = (
        "border-collapse:collapse;font-family:Arial,sans-serif;font-size:13px;"
        "margin-bottom:16px;"
    )
    #its a string, () is for grouping
    #Parentheses let an expression span lines, but they don't let a string literal span lines
    th_style = "background:#4472C4;color:#fff;padding:6px 10px;text-align:left;"
    td_style_common = "<style>td{padding:6px 10px;border-bottom:1px solid #ddd;}</style>"

    return f"""\
<html>
  <body style="font-family:Arial,sans-serif;color:#222;">
    {td_style_common}
    <h2>Weekly Sales Report</h2>
    <p>
      <b>Total orders:</b> {total_orders:,}<br>
      <b>Total units:</b> {total_units:,}<br>
      <b>Total revenue:</b> ${total_revenue:,.2f}
    </p>

    <h3>By Month</h3>
    <table style="{table_style}">
      <tr><th style="{th_style}">Month</th><th style="{th_style}">Orders</th>
          <th style="{th_style}">Units</th><th style="{th_style}">Revenue</th></tr>
      {month_rows}
    </table>

    <h3>Top 5 Products by Revenue</h3>
    <table style="{table_style}">
      <tr><th style="{th_style}">Product</th><th style="{th_style}">Units</th>
          <th style="{th_style}">Revenue</th></tr>
      {product_rows}
    </table>

    <p style="color:#666;font-size:12px;">Full breakdown attached as an Excel workbook.</p>
  </body>
</html>
"""


def build_message(config: dict, report_path: Path, html_body: str) -> EmailMessage:
    """Assemble the EmailMessage with HTML body and .xlsx attachment."""
    msg = EmailMessage()
    #This creates an empty email — a container you then fill in over the next few lines.
    #EmailMessage comes from email.message (stdlib).
    #stdlib = "standard library" — the modules that ship with Python itself. Install Python, and they're already there. Nothing to download, nothing in requirements.txt.
    msg["Subject"] = config["subject"]
    msg["From"] = config["email_from"]
    msg["To"] = ", ".join(config["email_to"])# config["email_to"] is a list

    #These two lines build a multipart/alternative message
    msg.set_content("This report requires an HTML-capable email client to view the summary.")
    #set_content(...) sets the message body. With just a string and no subtype, it defaults to text/plain. This is the fallback text.
    msg.add_alternative(html_body, subtype="html")
    #adds a second version of that same body, as text/html. The word "alternative" is the key: you're not adding more content, you're saying "here's the same thing again, rendered differently."
    #every mainstream client renders HTML - so mostly of no use, email client means the program you read email in

    #below this - reads the generated .xlsx off disk and attaches it to the email.
    with report_path.open("rb") as f:
        #The "rb" is the important bit: read binary. An xlsx file is actually a zip archive, so its bytes are not text — trying to read it as "r" would attempt UTF-8 decoding and blow up with UnicodeDecodeError. Binary mode gives you a bytes object with no interpretation.
        #with ... as f — a context manager. It guarantees the file handle is closed when the block exits, even if add_attachment raises
        msg.add_attachment(
            f.read(),#pulls the entire file into memory as bytes, in one go. Fine for a sales report
            #maintype / subtype — together these form the MIME type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet. This is the official registered type for .xlsx
            #It's what tells the recipient's mail client to show an Excel icon and hand the file to Excel on double-click.
            maintype="application",
            subtype="vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            filename=report_path.name,#filename=report_path.name — .name gives just the final component, monthly_report.xlsx, stripping any directory path. That's what the recipient sees as the attachment name. Important that it's .name and not the full path
        )
    return msg


def send_message(config: dict, msg: EmailMessage) -> None:
    """Send msg over SMTP with STARTTLS."""
    #with ... as server guarantees QUIT is sent and the socket closed even if login raises — say, on a bad password. Without it you'd leave a half-open connection, and some servers rate-limit or temporarily block clients that abandon sessions.
    with smtplib.SMTP(config["smtp_host"], config["smtp_port"]) as server:
        #smtplib.SMTP(host, port) opens a TCP connection to the mail server and does the initial handshake.
        #At this point the connection is plaintext — anything sent now travels unencrypted.
        server.starttls()
        #starttls() upgrades the existing plaintext connection to TLS.
        #Everything after this line is encrypted.
        server.login(config["smtp_username"], config["smtp_password"])
        #login(username, password) authenticates. It must come after starttls() — otherwise your password crosses the network in the clear
        server.send_message(msg)
        #send_message(msg) serializes the EmailMessage to its MIME text form and transmits it.
        #it also reads From and To off the message headers to figure out the envelope addresses, so you don't pass them separately.


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Email the weekly sales report.")
    parser.add_argument(
        "--env-file",
        type=Path,
        default=Path(__file__).resolve().parent / ".env",
        #__file__ — the path to this script, as Python was given it
        #.resolve() — turns that into an absolute path, following symlinks and removing ../.
        #.parent — strips the filename, leaving the directory the script lives in
        #/ ".env" — pathlib's overloaded / operator for joining paths
        #pass like this : python aidraft1.py --env-file /path/to/my.env
        help="Path to the .env file with SMTP/email settings (default: .env next to this script)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Build the report and email message but do not send anything.",
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Actually send the email right now, regardless of the schedule.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_config(args.env_file)

    if not config["csv_folder"].is_dir():
        raise SystemExit(f"Not a folder: {config['csv_folder']}")

    try:
        report_path = generate_report(config["csv_folder"], config["output_path"])
    except ValueError as exc:
        raise SystemExit(str(exc))

    html_body = build_html_summary(config["csv_folder"])
    msg = build_message(config, report_path, html_body)

    if args.dry_run:
        print("[dry-run] Report built at:", report_path)
        print("[dry-run] Subject:", msg["Subject"])
        print("[dry-run] From:", msg["From"])
        print("[dry-run] To:", msg["To"])
        print("[dry-run] HTML body:\n")
        print(html_body)
        print("[dry-run] No email sent.")
        return

    send_message(config, msg)
    mode = "test " if args.test else ""
    print(f"Sent {mode}report to {msg['To']} ({report_path})")


if __name__ == "__main__":
    main()
