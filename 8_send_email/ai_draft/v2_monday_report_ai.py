"""
monday_report.py

Builds the weekly sales report (via report_generator.generate_report) and
emails it as an .xlsx attachment, with an HTML summary of the totals in
the message body. Delegates config loading, message assembly, and SMTP
delivery to emailer.py.

USAGE
-----
Normal run — build the report and send it (intended to run every Monday
via cron or Task Scheduler):
    python monday_report.py

Build the report and the email, but don't actually send anything. Prints
the subject, recipients, and HTML body so you can check they look right:
    python monday_report.py --dry-run

Send a real email right now, regardless of what day it is, useful for
verifying your SMTP credentials work end-to-end:
    python monday_report.py --test

SCHEDULING
----------
This script does one run and exits — it does not schedule itself. Point
your OS scheduler at it. On Linux/macOS, a crontab entry for 8am every
Monday looks like:

    0 8 * * 1 cd /path/to/sales_summary && /usr/bin/python3 monday_report.py >> email_report.log 2>&1

On Windows, create a Task Scheduler task with a weekly Monday trigger that
runs `python monday_report.py` with the working directory set to this
folder.
"""

from __future__ import annotations

import argparse
from pathlib import Path

# Reuse the existing report-building code as-is.
from report_generator import generate_report, load_sales_rows, summarize_by_month, summarize_by_product

from emailer import build_message, load_config, send_message


def build_html_summary(csv_folder: Path) -> str:
    """Build an HTML summary of totals, reusing the existing aggregation
    helpers rather than re-deriving totals from scratch."""
    rows = load_sales_rows(csv_folder)
    monthly = summarize_by_month(rows)
    by_product = summarize_by_product(rows)

    total_orders = sum(m["orders"] for m in monthly.values())
    total_units = sum(m["units"] for m in monthly.values())
    total_revenue = sum(m["revenue"] for m in monthly.values())

    top_products = sorted(by_product.items(), key=lambda kv: kv[1]["revenue"], reverse=True)[:5]

    month_rows = "".join(
        f"<tr><td>{month}</td><td style='text-align:right'>{data['orders']:,}</td>"
        f"<td style='text-align:right'>{data['units']:,}</td>"
        f"<td style='text-align:right'>${data['revenue']:,.2f}</td></tr>"
        for month, data in sorted(monthly.items())
    )
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