#!/usr/bin/env python3
"""Merge monthly sales CSVs into a formatted Excel report.

Scans a folder of CSV files, keeps only the ones whose header matches
the expected sales schema (date, region, product, units, unit_price),
and produces a two-sheet Excel workbook: a per-month summary and a
per-product breakdown.
"""

#from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path
from statistics import mean
from typing import Any

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill,Border,Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.worksheet import Worksheet #type hint ; ws:Worksheet
from datetime import date

#EXPECTED_COLUMNS = ("date", "region", "product", "units", "unit_price")
REQUIRED_COLUMNS = {"date", "region", "product", "units", "unit_price"}

HEADER_FONT = Font(bold=True, color="FFFFFF")
HEADER_FILL = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
TOTAL_FONT = Font(bold=True)
TOTAL_BORDER = Border(top=Side(style='double'))
LOW_REVENUE_FILL = PatternFill(start_color="FFC7CE", end_color="FFC7CE", fill_type="solid")
LOW_REVENUE_FONT = Font(color='9C0006')

COUNT_FORMAT = "#,##0"
MONEY_FORMAT = "#,##0.00"
PERCENT_FORMAT = "0.0%"


def find_csv_files(folder: Path) -> list[Path]:
    """Return all .csv files directly inside folder, sorted by name."""
    return sorted(p for p in folder.glob("*.csv") if p.is_file())


# def is_sales_header(header: list[str]) -> bool:
#     """Return True if header exactly matches the expected sales columns."""
#     return [h.strip() for h in header] == list(EXPECTED_COLUMNS)


def load_sales_rows(csv_folder: Path) -> list[dict[str, Any]]:
    """Read every valid sales CSV in csv_folder and return parsed rows.

    Files whose header doesn't match the expected schema are skipped
    with a warning printed to stderr. Rows that fail to convert
    units/unit_price to numbers are also skipped with a warning instead
    of crashing the whole run.
    """
    rows: list[dict[str, Any]] = []
    csv_files = find_csv_files(csv_folder) #list[Path]

    if not csv_files:
        print(f"warning: no CSV files found in {csv_folder}", file=sys.stderr)

    for path in csv_files:
        try:
            with path.open("r", newline="", encoding="utf-8") as f:
                #reader = csv.reader(f)
                reader = csv.DictReader(f)
                # try:
                #     header = next(reader)
                # except StopIteration:
                #     print(f"warning: skipping empty file {path.name}", file=sys.stderr)
                #     continue

                fieldnames = reader.fieldnames or []
                #price , Price 
                #{'Price':'price'}
                key_for = {name: name.strip().lower() for name in fieldnames}
                #{'Date':'date'}
                missing = REQUIRED_COLUMNS - set(key_for.values())
                

                # if not is_sales_header(header):
                #     print(
                #         f"warning: skipping non-sales file {path.name} "
                #         f"(unexpected header {header})",
                #         file=sys.stderr,
                #     )
                #     continue

                if missing:
                    print(
                        f"warning: skipping non-sales file {path.name} "
                        f"(missing colummns: {', '.join(sorted(missing))})",
                        file=sys.stderr,
                        )
                    continue

                for line_num, raw_row in enumerate(reader, start=2):
                    # if len(raw_row) != len(EXPECTED_COLUMNS):
                    #     print(
                    #         f"warning: skipping malformed row {line_num} in "
                    #         f"{path.name}",
                    #         file=sys.stderr,
                    #     )
                    #     continue


                    #date, region, product, units_str, price_str = raw_row

                    row ={key_for[name]: raw_row[name] for name in fieldnames}

                    #raw_row = {'Date':'...' , ' region':'...'}
                    #row={'date':'...' , 'region':'...'}

                    try:
                        units = int(row["units"]) #int(None)
                        unit_price = float(row["unit_price"])
                        date.fromisoformat(row['date']) #YYYY-MM-DD
                    except (ValueError,TypeError):
                        print(
                            f"warning: skipping row {line_num} in {path.name} "
                            f"(bad units/unit_price)",
                            file=sys.stderr,
                        )
                        continue

                    rows.append(
                        {
                            "date": row['date'],
                            "region": row['region'],
                            "product": row['product'],
                            "units": units,
                            "unit_price": unit_price,
                        }
                    )
        except (OSError,UnicodeDecodeError,csv.Error) as exc: 
            print(f"warning: could not read {path.name}: {exc}", file=sys.stderr)
            continue

    return rows


def summarize_by_month(rows: list[dict[str, Any]]) -> dict[str, dict[str, float]]:
    """Aggregate rows into per-month orders, units, and revenue."""
    summary: dict[str, dict[str, float]] = {}
    for row in rows:
        month = row["date"][:7] #'2026-02'
        bucket = summary.setdefault(month, {"orders": 0, "units": 0, "revenue": 0.0})
        #case 1: '2026-02' is not there as a key in the summary dictionary
        ##case 2: '2026-02' is there as a key in the summary dictionary
        #first time, 
        #summary ={'2026-02':{"orders": 0, "units": 0, "revenue": 0.0}}
        #bucket = {"orders": 1, "units": 2, "revenue": 20}
        bucket["orders"] += 1 # bucket["orders"] = bucket["orders"]+ 1
        bucket["units"] += row["units"] #bucket["units"] = bucket["units"]+ row["units"]
        bucket["revenue"] += row["units"] * row["unit_price"]
    return summary


def summarize_by_product(rows: list[dict[str, Any]]) -> dict[str, dict[str, float]]:
    """Aggregate rows into per-product units and revenue."""
    summary: dict[str, dict[str, float]] = {}
    for row in rows:
        product = row["product"]
        bucket = summary.setdefault(product, {"units": 0, "revenue": 0.0})
        bucket["units"] += row["units"]
        bucket["revenue"] += row["units"] * row["unit_price"]
    return summary


def style_header_row(ws: Worksheet, num_columns: int, row: int = 1) -> None:
    """Apply bold white-on-blue formatting to the header row and freeze it."""
    for col in range(1, num_columns + 1):
        cell = ws.cell(row=row, column=col)
        cell.font = HEADER_FONT
        cell.fill = HEADER_FILL
        cell.alignment = Alignment(horizontal="center")
    ws.freeze_panes = f"A{row + 1}"


def autosize_columns(ws: Worksheet, widths: list[int]) -> None:
    """Set sensible fixed column widths."""
    for idx, width in enumerate(widths, start=1):
        ws.column_dimensions[get_column_letter(idx)].width = width


def write_summary_sheet(ws: Worksheet, monthly: dict[str, dict[str, float]]) -> None:
    """Write the Summary sheet: Month | Orders | Units | Revenue."""
    ws.append(["Month", "Orders", "Units", "Revenue"])
    style_header_row(ws, num_columns=4)

    #{'2026-02':{"orders": 0, "units": 0, "revenue": 0.0}}
    months = sorted(monthly) #list of all the keys ['2026-02','2026-01'...]
    revenues = [monthly[m]["revenue"] for m in months] #[1000,200,...]
    avg_revenue = mean(revenues) if revenues else 0.0

    total_orders = total_units = 0
    total_revenue = 0.0

    for month in months:
        data = monthly[month]
        row_idx = ws.max_row + 1
        ws.append([month, data["orders"], data["units"], data["revenue"]])
        ws.cell(row=row_idx, column=2).number_format = COUNT_FORMAT
        ws.cell(row=row_idx, column=3).number_format = COUNT_FORMAT
        ws.cell(row=row_idx, column=4).number_format = MONEY_FORMAT

        if data["revenue"] < avg_revenue:
            for col in range(1, 5):
                cell = ws.cell(row=row_idx, column=col)
                cell.fill = LOW_REVENUE_FILL
                cell.font = LOW_REVENUE_FONT

        total_orders += data["orders"]
        total_units += data["units"]
        total_revenue += data["revenue"]

    total_row = ws.max_row + 1
    ws.append(["TOTAL", total_orders, total_units, total_revenue])
    for col in range(1, 5):
        cell = ws.cell(row=total_row, column=col)
        cell.font = TOTAL_FONT
        cell.border = TOTAL_BORDER
    ws.cell(row=total_row, column=2).number_format = COUNT_FORMAT
    ws.cell(row=total_row, column=3).number_format = COUNT_FORMAT
    ws.cell(row=total_row, column=4).number_format = MONEY_FORMAT

    autosize_columns(ws, [12, 10, 10, 16])


def write_by_product_sheet(ws: Worksheet, by_product: dict[str, dict[str, float]]) -> None:
    """Write the By-Product sheet: Product | Units | Revenue | Share of Revenue."""
    ws.append(["Product", "Units", "Revenue", "Share of Revenue"])
    style_header_row(ws, num_columns=4)

     #{'product':{"units": 0, "revenue": 0.0}}
    total_revenue = sum(data["revenue"] for data in by_product.values())
    products = sorted(by_product, key=lambda p: by_product[p]["revenue"], reverse=True)#sorting products in descending order of revenue.
    #list of products
    total_units = 0
    running_revenue = 0.0

    for product in products:
        data = by_product[product]
        share = (data["revenue"] / total_revenue) if total_revenue else 0.0
        row_idx = ws.max_row + 1
        ws.append([product, data["units"], data["revenue"], share])
        ws.cell(row=row_idx, column=2).number_format = COUNT_FORMAT
        ws.cell(row=row_idx, column=3).number_format = MONEY_FORMAT
        ws.cell(row=row_idx, column=4).number_format = PERCENT_FORMAT

        total_units += data["units"]
        running_revenue += data["revenue"]

    total_row = ws.max_row + 1
    total_share = (running_revenue / total_revenue) if total_revenue else 0.0
    ws.append(["TOTAL", total_units, running_revenue, total_share])
    for col in range(1, 5):
        cell = ws.cell(row=total_row, column=col)
        cell.font = TOTAL_FONT
        cell.border = TOTAL_BORDER
    ws.cell(row=total_row, column=2).number_format = COUNT_FORMAT
    ws.cell(row=total_row, column=3).number_format = MONEY_FORMAT
    ws.cell(row=total_row, column=4).number_format = PERCENT_FORMAT

    autosize_columns(ws, [20, 10, 16, 16])


def generate_report(csv_folder: Path, output_path: Path) -> Path:
    """Merge monthly sales CSVs in csv_folder into a formatted xlsx report.

    Reads every valid sales CSV in csv_folder, summarizes the results by
    month and by product, writes a two-sheet workbook to output_path,
    and returns that path.
    """
    csv_folder = Path(csv_folder)
    output_path = Path(output_path)

    rows = load_sales_rows(csv_folder) #list[dict]
    if not rows:
        raise ValueError(
            f"No usable sales rows found in {csv_folder} = expected CSVs with"
            f"columns {sorted(REQUIRED_COLUMNS)}"
        )
    
        #print("warning: no valid sales rows found; report will be empty", file=sys.stderr)

    monthly = summarize_by_month(rows)
    by_product = summarize_by_product(rows)

    wb = Workbook()
    summary_ws = wb.active
    summary_ws.title = "Summary"
    write_summary_sheet(summary_ws, monthly)

    product_ws = wb.create_sheet("By-Product")
    write_by_product_sheet(product_ws, by_product)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    wb.save(output_path)
    return output_path


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Merge monthly sales CSVs into a formatted Excel report."
    )
    parser.add_argument(
        "folder",
        nargs="?",
        type=Path,
        # default=Path("."),
        # help="Folder containing sales CSV files (default: current directory)",
        default = Path(__file__).resolve().parent.parent / "sample_data",
        help = "Folder containing sales CSV files (default: ../sample_data)",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        # default=Path("sales_report.xlsx"),
        # help="Output .xlsx path (default: sales_report.xlsx)",
        default = Path(__file__).resolve().parent / "monthly_report.xlsx",
        help="Output .xlsx path (default: monthly_report.xlsx next to this script)"
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    if not args.folder.is_dir():
        raise SystemExit(f"Not a folder: {args.folder}")
    try:
        result_path = generate_report(args.folder, args.output)
    except ValueError as exc:
        raise SystemExit(f"{exc} \n Hint: run sample_data/generate_sample_data.py first")    
    print(f"Report written to {result_path}")