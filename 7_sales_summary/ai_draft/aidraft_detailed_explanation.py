#!/usr/bin/env python3
"""Merge monthly sales CSVs into a formatted Excel report.

Scans a folder of CSV files, keeps only the ones whose header matches
the expected sales schema (date, region, product, units, unit_price),
and produces a two-sheet Excel workbook: a per-month summary and a
per-product breakdown.
"""

#from __future__ import annotations
#Changes how Python treats type hints: they are stored as strings and not evaluated when the function is defined. Two practical effects:
#you can delete this as it is no longer needed in python 3.10 +
#To let list[Path] and dict[str, Any] work on Python 3.7–3.9, where the built-in list and dict couldn't be used as type hints yet.

import argparse
import csv
import sys
from pathlib import Path
from statistics import mean #statistics is a standard-library module. mean takes an iterable of numbers and returns their average.
from typing import Any
#Any is a type hint meaning "could be anything." It's used in dict[str, Any] because each row dict holds mixed value types: date, region, product are str, units is int, unit_price is float. There's no single type that fits, so Any says "don't check." Pure documentation/tooling — zero runtime effect.
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill #Alignment is a style class describing how cell contents are positioned.
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.worksheet import Worksheet
#Imports the Worksheet class purely for type hints (ws: Worksheet). The script never calls Worksheet() directly — sheets are created via wb.active and wb.create_sheet(), which return Worksheet instances. The import just lets editors and type checkers know what ws is so they can autocomplete .append, .cell, .freeze_panes, etc.


EXPECTED_COLUMNS = ("date", "region", "product", "units", "unit_price") #a tuple

HEADER_FONT = Font(bold=True, color="FFFFFF")
HEADER_FILL = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")#They exist for gradient fills. Excel supports fills that blend from one colour to another, and start_color/end_color are the two endpoints of that gradient.
TOTAL_FONT = Font(bold=True)
LOW_REVENUE_FILL = PatternFill(start_color="FFF2CC", end_color="FFF2CC", fill_type="solid")

COUNT_FORMAT = "#,##0"
MONEY_FORMAT = "#,##0.00"
PERCENT_FORMAT = "0.0%"

#p.is_file() touches the disk and asks: is this a real file? Anything failing that gets dropped.
#folder.glob("*.csv") folder is a Path object. .glob is a method that comes with Path - for pattern-matching filenames
#
def find_csv_files(folder: Path) -> list[Path]:
    """Return all .csv files directly inside folder, sorted by name."""
    return sorted(p for p in folder.glob("*.csv") if p.is_file())


def is_sales_header(header: list[str]) -> bool:
    """Return True if header exactly matches the expected sales columns."""
    return [h.strip() for h in header] == list(EXPECTED_COLUMNS)


def load_sales_rows(csv_folder: Path) -> list[dict[str, Any]]:
    """Read every valid sales CSV in csv_folder and return parsed rows.

    Files whose header doesn't match the expected schema are skipped
    with a warning printed to stderr. Rows that fail to convert
    units/unit_price to numbers are also skipped with a warning instead
    of crashing the whole run.
    """
    rows: list[dict[str, Any]] = []
    csv_files = find_csv_files(csv_folder)

    if not csv_files:
        print(f"warning: no CSV files found in {csv_folder}", file=sys.stderr)
        #print normally writes to stdout — the "standard output" stream. file=sys.stderr redirects that one call to stderr, the "standard error" stream instead. 
        # Both show up on your terminal by default, so interactively you see no difference.
        #its useful if for example we want to capture all std.err in a text file for logging

    for path in csv_files:
        try:
            with path.open("r", newline="", encoding="utf-8") as f:
                #path.open() - A Path method that opens the file and returns a file object.
                #r- read mode, text
                #newline="" - is specific to CSV, It disables Python's universal-newline translation. With newline="", the reader gets the bytes as-is and handles the line-splitting itself, which it knows how to do correctly. 
                # encoding="utf-8" - specifies the character encoding to use when reading the file. UTF-8 is a common encoding that can represent a wide range of characters.  
                #with ... as f - A context manager that ensures the file is closed when the block is exited, even if an error occurs.
                '''
                f = path.open(...)
                try:
                    ...body...
                finally:
                    f.close()
                '''
                #f - the file object, passed straight to csv.reader(f)
                #csv is the standard-library module imported at the top. .reader is a function in it. f is the open file object from the with line
                #it returns an iterator that yields each row of the CSV file as a list of strings. Each call to next(reader) gives you the next row.
                reader = csv.reader(f)
                try:
                    header = next(reader)
                    #read the first row. might look like this: ['date', 'region', 'product', 'units', 'unit_price']
                except StopIteration:
                    #this will run only if the CSV file is empty, because next() raises StopIteration when there are no more rows to read.
                    print(f"warning: skipping empty file {path.name}", file=sys.stderr)
                    #The script produces two kinds of text: results and warnings. Python keeps them on separate channels — stdout for results, stderr for warnings — and file=sys.stderr picks the second one.
                    #python aidraft.py data/ > log.txt
                    #The result line goes into log.txt. The warnings still appear on your screen, because they're on the other channel.
                    continue
                    #continue always jumps to the next iteration of the nearest enclosing loop.

                if not is_sales_header(header):
                    print(
                        f"warning: skipping non-sales file {path.name} "
                        f"(unexpected header {header})",
                        file=sys.stderr,
                    )
                    continue

                for line_num, raw_row in enumerate(reader, start=2):
                    #enumerate Wraps any iterable and yields pairs — a counter and the item:
                    #enumerate(['a', 'b'])            # (0, 'a'), (1, 'b')
                    #enumerate(['a', 'b'], start=2)   # (2, 'a'), (3, 'b')
                    if len(raw_row) != len(EXPECTED_COLUMNS):
                        print(
                            f"warning: skipping malformed row {line_num} in "
                            f"{path.name}",
                            file=sys.stderr,
                        )
                        continue
                    #unpacking
                    date, region, product, units_str, price_str = raw_row          
                    try:
                        units = int(units_str)
                        unit_price = float(price_str)
                    except ValueError:
                        #ValueError is raised when When int() or float() is handed a string it can't convert.
                        print(
                            f"warning: skipping row {line_num} in {path.name} "
                            f"(bad units/unit_price)",
                            file=sys.stderr,
                        )
                        continue

                    rows.append(
                        {
                            "date": date,
                            "region": region,
                            "product": product,
                            "units": units,
                            "unit_price": unit_price,
                        }
                    )
        except OSError as exc:
            #OSError is a built-in exception that is raised when a system-related error occurs, such as a file not being found or permission being denied. The variable exc captures the specific error message associated with the exception.
            print(f"warning: could not read {path.name}: {exc}", file=sys.stderr)
            continue

    return rows


def summarize_by_month(rows: list[dict[str, Any]]) -> dict[str, dict[str, float]]:
    #dict[str, float] describes a dict with any number of entries, where every key is a str and every value is a float
    """Aggregate rows into per-month orders, units, and revenue."""
    summary: dict[str, dict[str, float]] = {}
    for row in rows:
        month = row["date"][:7]
        #row["date"]     # dict lookup → '2026-01-15'  (a string)
        #[:7]            # slice → '2026-01'
        bucket = summary.setdefault(month, {"orders": 0, "units": 0, "revenue": 0.0})
        #setdefault - Two behaviours in one call, depending on whether the key exists:
        #Key missing in summary → insert it with the given default, return that default
        #If month is a new key - setdefault inserts it, then returns the dict it just inserted:
        #bucket    # {'orders': 0, 'units': 0, 'revenue': 0.0}
        #summary   # {'2026-01': {'orders': 0, 'units': 0, 'revenue': 0.0}}
        #Key present → leave it alone, return the existing value
        #If month is already a key - 
        #summary = {'2026-01': {'orders': 5, 'units': 60, 'revenue': 599.4}}
        #bucket = summary.setdefault('2026-01', {"orders": 0, "units": 0, "revenue": 0.0})
        #bucket    # {'orders': 5, 'units': 60, 'revenue': 599.4}
        #summary   # unchanged

        '''
        if month not in summary:
            summary[month] = {"orders": 0, "units": 0, "revenue": 0.0}
        bucket = summary[month]
        '''
        #instead of bucket we could write summary[month]
        bucket["orders"] += 1
        #without bucket we would need to write summary[month]["orders"] += 1, which is longer and repeats the lookup. 
        #bucket is not a copy. It's a second name pointing at the same dict object that lives inside summary. So mutating bucket mutates what's stored
        bucket["units"] += row["units"]
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
    #freeze_panes is a property of the worksheet that determines which rows and columns remain visible when scrolling. Setting it to "A2" means that the first row (the header) will stay fixed at the top while the rest of the sheet can be scrolled.
    #Freezing happens above the cell you name, so "A2" freezes row 1.

def autosize_columns(ws: Worksheet, widths: list[int]) -> None:
    """Set sensible fixed column widths."""
    for idx, width in enumerate(widths, start=1):
        ws.column_dimensions[get_column_letter(idx)].width = width
        #get_column_letter(idx) - A function from openpyxl that converts a column number to its Excel letter.
        #get_column_letter(1)    # 'A'


def write_summary_sheet(ws: Worksheet, monthly: dict[str, dict[str, float]]) -> None:
    """Write the Summary sheet: Month | Orders | Units | Revenue."""
    ws.append(["Month", "Orders", "Units", "Revenue"]) #row 1 as the sheet its empty 
    style_header_row(ws, num_columns=4)

    months = sorted(monthly)
    #monthly is a dict. Iterating a dict gives you its keys .You get a list of month strings. The inner dicts aren't touched.
    revenues = [monthly[m]["revenue"] for m in months]
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
                ws.cell(row=row_idx, column=col).fill = LOW_REVENUE_FILL

        total_orders += data["orders"]
        total_units += data["units"]
        total_revenue += data["revenue"]

    total_row = ws.max_row + 1
    ws.append(["TOTAL", total_orders, total_units, total_revenue])
    for col in range(1, 5):
        ws.cell(row=total_row, column=col).font = TOTAL_FONT
    ws.cell(row=total_row, column=2).number_format = COUNT_FORMAT
    ws.cell(row=total_row, column=3).number_format = COUNT_FORMAT
    ws.cell(row=total_row, column=4).number_format = MONEY_FORMAT

    autosize_columns(ws, [12, 10, 10, 16])


def write_by_product_sheet(ws: Worksheet, by_product: dict[str, dict[str, float]]) -> None:
    """Write the By-Product sheet: Product | Units | Revenue | Share of Revenue."""
    ws.append(["Product", "Units", "Revenue", "Share of Revenue"])
    style_header_row(ws, num_columns=4)

    total_revenue = sum(data["revenue"] for data in by_product.values())
    products = sorted(by_product, key=lambda p: by_product[p]["revenue"], reverse=True)
    #Iterating a dict gives its keys, so sorted(by_product) gives a list of product names. 
    #key=Tells sorted what to compare.Without it, the names would sort alphabetically.With it, each name is passed through the function and the result is compared instead:
    #key=lambda p: by_product[p]["revenue"]
    #lambda - An inline, unnamed function.its called by sorted.
    #reverse=True - descending order

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
        ws.cell(row=total_row, column=col).font = TOTAL_FONT
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
    #Defensive normalization. The function converts its inputs to the type it needs rather than trusting the 
    # caller. It's cheap, it's idempotent — running Path() twice gives the same result — and it makes the 
    # function usable outside the CLI without the caller having to know about pathlib.
    csv_folder = Path(csv_folder)
    output_path = Path(output_path)

    rows = load_sales_rows(csv_folder)
    if not rows:
        print("warning: no valid sales rows found; report will be empty", file=sys.stderr)

    monthly = summarize_by_month(rows)
    by_product = summarize_by_product(rows)

    wb = Workbook()
    #Workbook is a class from openpyxl, imported at the top:
    #openpyxl is a third-party library , has to be installed - pip install openpyxl
    #Calling it creates an instance: an in-memory Excel workbook - A workbook that already contains one sheet, created automatically.
    summary_ws = wb.active
    ## the sheet that already exists, wb.active is the currently-selected sheet.
    summary_ws.title = "Summary"  # rename it, default name is "Sheet"
    write_summary_sheet(summary_ws, monthly)

    product_ws = wb.create_sheet("By-Product") #new sheet
    write_by_product_sheet(product_ws, by_product)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    #Path('reports/q3/sales.xlsx').parent   # PosixPath('reports/q3')
    #.mkdir(...) Creates that folder on disk.
    #parents=True - If any of the parent directories don't exist, create them as well. For example, if you're trying to create "reports/q3" and "reports" doesn't exist, it will create "reports" first.
    #exist_ok=True - Don't raise an error if the directory already exists. This allows the script to run multiple times without failing if the output folder is already there.
    wb.save(output_path)
    return output_path


def parse_args() -> argparse.Namespace:
    # argparse.Namespace is a class. parse_args() creates one object of that class and returns it. there is no speciality of this object, could have used a normal dictionary as well .
    # The object's only job is to hold the parsed values as attributes.
    #For this script, the object that comes back has two attributes on it:args.folder - a Path  , args.output - a Path
    #The attribute names come from what you passed to add_argument: "folder" gave you args.folder, and "--output" gave you args.output after stripping the dashes.
    #argparse is a module in Python's standard library. It's imported at the top.Nothing to install — it ships with Python. Its purpose is to read what the user typed after the script name on the command line and turn it into Python values.
    """Parse command-line arguments."""
    #ArgumentParser is another class. This is the one that does the actual work; Namespace is just its output.
    #You create an instance and configure it, At this point the parser knows nothing about folder or output. It's an empty rulebook holding only that description string.
    #ArgumentParser has code for adding rules and code for applying them.
    parser = argparse.ArgumentParser(
        description="Merge monthly sales CSVs into a formatted Excel report."
    )
    #You register rules on it
    #add_argument is a method on the instance
    #Each call stores one rule inside the parser: 
    #Nothing is parsed yet — you're only describing what's allowed.
    #type — a callable applied to the string the user typed. Here it's Path, so argparse calls Path("data/") and you get a Path object rather than a string. Any callable works: int, float, or a function you write.
    #default — the value used when the user supplies nothing. Note it's Path(".") and Path("sales_report.xlsx"), already Path objects. type is not applied to non-string defaults, so writing them this way keeps args.folder a Path whether the user passed something or not.
    #help — the text printed under -h. Purely cosmetic; it affects nothing at runtime.
    #nargs — how many command-line items this argument consumes. "?" means zero or one.
    #A positional is required by default. Without nargs="?", running python script.py bare would fail:
    #nargs="?" is what makes it optional, which is what lets default=Path(".") ever get used. Remove nargs and the default becomes unreachable — argparse would error out first.
    #A flag is already optional by nature; that's what the dashes mean.
    #-o can simply be omitted and the default applies. So --output needs no nargs — it takes exactly one value, which is the default behaviour.
    #The rule: nargs is on folder specifically to undo the requiredness that positionals have and flags don't.
    #"-o" and "--output" : Two spellings of the same argument. -o is the short form (single dash, one letter), --output the long form (double dash, full word). They're interchangeable:
    #"folder" vs "--output": The presence of dashes is the entire distinction, and it's how argparse decides which kind of argument you're declaring.
    #"folder" — no dashes, so positional. Identified by where it appears on the command line, not by name. The name "folder" is never typed by the user; it exists only to become the attribute args.folder and to label the help output.
    #"--output" — dashes, so optional/flag. Identified by name wherever it appears. The user must type --output (or -o) for it to be recognized.
    #Which is why order matters for one and not the other:
    ''''python script.py data/ -o q3.xlsx     # works
        python script.py -o q3.xlsx data/     # also works'''
    #data/ is the only positional either way. But if there were a second positional, swapping the two would silently assign the wrong values — position is all argparse has to go on.
    
    #Rule 1: a folder, given by position, optional, converted to Path, defaults to current directory.
    #folder is a positional argument, so it is identified by its position on the command line. The user does not type "folder"; they just type the value (e.g., "data/"). The name "folder" is used internally to create the attribute args.folder and to label the help output.
    #No dash → positional (folder is identified by its position on the command line, not by name.) 
    #"." means "the current directory" — wherever you ran the command from.
    #How many values this argument consumes from the command line. "?" means zero or one
    #default decides what value you get when zero were supplied.
    parser.add_argument(
        "folder",
        nargs="?",
        type=Path,
        default=Path("."),
        help="Folder containing sales CSV files (default: current directory)",
    )
    #Rule 2: an output path, given after -o or --output, optional, converted to Path, defaults to sales_report.xlsx.
    #Dash → flag (output is identified by name, not position. The user must type --output or -o for it to be recognized.)
    #name is output, When you pass both a short and a long form, argparse names the attribute from the long form, with the dashes stripped
    #Path("sales_report.xlsx") is a relative path with no directory part, so it resolves against the current working directory — wherever you ran the command from,not where the script file lives.
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path("sales_report.xlsx"),
        help="Output .xlsx path (default: sales_report.xlsx)",
    )
    ''' "folder"  →  no dash  →  positional  →  required by default
        "--output" →  has dash →  flag       →  optional by default
    '''
    #parser.parse_args() is the method that actually reads sys.argv, applies the rules, and returns a Namespace object with the parsed values as attributes. The attribute names come from what you passed to add_argument: "folder" gave you args.folder, and "--output" gave you args.output after stripping the dashes.
    #parser is the object. .parse_args is a method defined in the ArgumentParser class. () calls it with no arguments.
    #The real signature is parse_args(self, args=None, namespace=None). Leaving args as None tells it to read sys.argv[1:] itself — the command line minus the script name.
    return parser.parse_args()


if __name__ == "__main__":
    #args is a Namespace object.
    #Example -Namespace(folder=PosixPath('data'), output=PosixPath('q3.xlsx'))
    args = parse_args()
    #a Namespace object with the parsed values as attributes
    #args.folder is a Path object representing the folder containing sales CSV files. It defaults to the current directory if not provided.
    result_path = generate_report(args.folder, args.output)
    print(f"Report written to {result_path}")


'''
# ── defaults: current dir → sales_report.xlsx ─────────────────────
python aidraft.py

# ── folder only → sales_report.xlsx in current dir ────────────────
python aidraft.py data/
python aidraft.py .
python aidraft.py /home/jackson/sales/2026

# ── output only → reads current dir ───────────────────────────────
python aidraft.py -o q3.xlsx
python aidraft.py --output q3.xlsx
python aidraft.py -o reports/q3.xlsx          # reports/ created if missing

# ── both ──────────────────────────────────────────────────────────
python aidraft.py data/ -o q3.xlsx
python aidraft.py data/ --output q3.xlsx
python aidraft.py -o q3.xlsx data/            # order doesn't matter
python aidraft.py --output q3.xlsx data/

# ── attached-value forms (equivalent to the above) ────────────────
python aidraft.py data/ -oq3.xlsx             # short: no space
python aidraft.py data/ --output=q3.xlsx      # long: equals sign

# ── help ──────────────────────────────────────────────────────────
python aidraft.py -h
python aidraft.py --help
    
'''