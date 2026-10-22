"""
email_report.py

Builds the weekly sales report (via report_generator.generate_report) and
emails it as an .xlsx attachment, with an HTML summary of the totals in the
message body.

USAGE
-----
Normal run — build the report and send it (intended to run every Monday
via cron or Task Scheduler):
    python email_report.py

Build the report and the email, but don't actually send anything. Prints
the subject, recipients, and HTML body so you can check they look right:
    python email_report.py --dry-run

Send a real email right now, regardless of what day it is, useful for
verifying your SMTP credentials work end-to-end:
    python email_report.py --test

SCHEDULING
----------
This script does one run and exits — it does not schedule itself. Point
your OS scheduler at it. On Linux/macOS, a crontab entry for 8am every
Monday looks like:

    0 8 * * 1 cd /path/to/sales_summary && /usr/bin/python3 email_report.py >> email_report.log 2>&1

On Windows, create a Task Scheduler task with a weekly Monday trigger that
runs `python email_report.py` with the working directory set to this
folder.

CONFIGURATION
--------------
All secrets and addresses are read from environment variables, loaded from
a .env file next to this script (see .env.example). Nothing secret is
hardcoded here.

Required:
    SMTP_HOST        e.g. smtp.gmail.com
    SMTP_PORT        e.g. 587
    SMTP_USERNAME    login username for your SMTP account
    SMTP_PASSWORD    password / app password for your SMTP account
    EMAIL_FROM       the From: address
    EMAIL_TO         comma-separated list of recipient addresses

Optional:
    CSV_FOLDER       folder of sales CSVs (default: ./sample_data)
    OUTPUT_PATH      where to write the .xlsx (default: ./monthly_report.xlsx)
    EMAIL_SUBJECT    subject line (default: "Weekly Sales Report - <date>")
"""

#from __future__ import annotations

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

    missing = [name for name in REQUIRED_ENV_VARS if not os.environ.get(name)]
    if missing:
        raise SystemExit(
            "Missing required environment variable(s): "
            f"{', '.join(missing)}\n"
            f"Set them in {env_path} (see .env.example) or export them directly."
        )

    return {
        "smtp_host": os.environ["SMTP_HOST"],
        "smtp_port": int(os.environ["SMTP_PORT"]),
        "smtp_username": os.environ["SMTP_USERNAME"],
        "smtp_password": os.environ["SMTP_PASSWORD"],
        "email_from": os.environ["EMAIL_FROM"],
        "email_to": [addr.strip() for addr in os.environ["EMAIL_TO"].split(",") if addr.strip()], #a@gmail.com, b@gmail.com -> [a@gmail.com,b@gmail.com]
        "csv_folder": Path(os.environ.get("CSV_FOLDER", "sample_data")),
        "output_path": Path(os.environ.get("OUTPUT_PATH", "monthly_report.xlsx")),
        "subject": os.environ.get("EMAIL_SUBJECT", f"Weekly Sales Report - {date.today():%Y-%m-%d}"),
    }


def build_html_summary(csv_folder: Path) -> str:
    """Build an HTML summary of totals, reusing the existing aggregation
    helpers rather than re-deriving totals from scratch."""
    rows = load_sales_rows(csv_folder) #[{"date":...,"region":...},{},{}]
    monthly = summarize_by_month(rows) #{'month':{"orders":..,"units":..,"revenue":...},month:{}}
    by_product = summarize_by_product(rows) #{'product1':{"units":...,"revenue":...},product2:{}...}

    total_orders = sum(m["orders"] for m in monthly.values())
    total_units = sum(m["units"] for m in monthly.values())
    total_revenue = sum(m["revenue"] for m in monthly.values())

    top_products = sorted(by_product.items(), key=lambda kv: kv[1]["revenue"], 
                          reverse=True)[:5]
    #(key,value)

    month_rows = "".join(
        f"<tr><td>{month}</td><td style='text-align:right'>{data['orders']:,}</td>"
        f"<td style='text-align:right'>{data['units']:,}</td>"
        f"<td style='text-align:right'>${data['revenue']:,.2f}</td></tr>"
        for month, data in sorted(monthly.items()) #list[tuples], month is string, data is a dict
    )

    '''
    "".join (
    <expression>
    for month,data in sorted(monthly.items())
    )

    month_rows = <expression1><expression2><expression3>....
    '''

    product_rows = "".join(
        f"<tr><td>{product}</td><td style='text-align:right'>{data['units']:,}</td>"
        f"<td style='text-align:right'>${data['revenue']:,.2f}</td></tr>"
        for product, data in top_products
    )

    table_style = (
        "border-collapse:collapse;font-family:Arial,sans-serif;font-size:13px;"
        "margin-bottom:16px;"
    )
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
    msg["Subject"] = config["subject"]
    msg["From"] = config["email_from"]
    msg["To"] = ", ".join(config["email_to"])
    msg.set_content("This report requires an HTML-capable email client to view the summary.")
    msg.add_alternative(html_body, subtype="html")

    with report_path.open("rb") as f:
        msg.add_attachment(
            f.read(),
            maintype="application",
            subtype="vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            filename=report_path.name,
        )
    return msg


def send_message(config: dict, msg: EmailMessage) -> None:
    """Send msg over SMTP with STARTTLS."""
    with smtplib.SMTP(config["smtp_host"], config["smtp_port"]) as server:
        server.starttls()
        server.login(config["smtp_username"], config["smtp_password"])
        server.send_message(msg)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Email the weekly sales report.")
    parser.add_argument(
        "--env-file",
        type=Path,
        default=Path(__file__).resolve().parent / ".env",
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