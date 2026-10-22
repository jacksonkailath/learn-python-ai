"""Example 1 — reading a CSV the readable way: csv.DictReader.

Reads one month of sales data and shows the two facts you always want
first when meeting a new table: its SHAPE (rows x columns) and what a
single row actually looks like as a dict.

Run sample_data/generate_sample_data.py first if the CSV is missing.
"""

from csv import DictReader
from pathlib import Path
#csv is a module in Python's standard library — it ships with Python, no install needed.
#pulls just the DictReader class out of that module and binds it directly in your file's namespace. So later you can write:
#reader = DictReader(f)
#instead of:
#import csv
#reader = csv.DictReader(f)
#DictReader is for reading a CSV file where the first row is a header, and getting each subsequent row back as a dictionary.
'''
date,product,units,unit_price
2025-01-03,Widget,4,19.99
2025-01-03,Gadget,1,49.00

{'date': '2025-01-03', 'product': 'Widget', 'units': '4', 'unit_price': '19.99'}
{'date': '2025-01-03', 'product': 'Gadget', 'units': '1', 'unit_price': '49.00'}
'''

SAMPLE_CSV = Path(__file__).resolve().parent.parent / "sample_data" / "sales_2025_01.csv"


def main() -> None:
    if not SAMPLE_CSV.exists():
        raise SystemExit(
            f"Missing {SAMPLE_CSV}\n"
            "Generate it first:  python ../sample_data/generate_sample_data.py"
        )
        #raise SystemExit : "stop the program right now, with an error message", with exit code = 1
        #sys.exit(x) is literally raise SystemExit(x). This line just skips the import sys
        #SystemExit is a built-in name, like int, print, ValueError, or len. Built-ins are available everywhere without importing anything.
        #sys.exit is a function that lives inside the sys module. To call it you first need the module in scope, hence import sys.
        #sys.exit is a thin wrapper — its entire job is to raise SystemExit
        #raise SystemExit()   -> exit code 0, nothing printed
        #raise SystemExit(2)   -> exit code 2
        #raise SystemExit("oops")  -> prints "oops" to stderr, code 1

    with SAMPLE_CSV.open(newline="", encoding="utf-8") as f:
        #newline="" : tells Python's file object: don't translate line endings, hand the raw characters to whoever's reading
        #csv module wants to handle line endings itself, and this parameter gets the file layer out of its way.
        #Text files end lines differently across systems: \n on Linux/macOS, \r\n on Windows. 
        #By default, when Python opens a file in text mode, it normalizes these — it converts any \r\n or \r it sees into \n before your code sees it. That's called universal newlines mode, and it's usually helpful.
        '''
        id,note
        1,"first line
        second line"
        2,hello
        '''
        #Row 1's note field spans two physical lines. The csv module knows how to parse this correctly — but only if it sees the original bytes.
        reader = DictReader(f)          
        #reader is a DictReader object, an iterator that produces dicts, one per call to next()
        rows = list(reader)             
        #list(reader) exhausts that iterator, collecting every produced dict into a list.
        #its a list of dicts [{'date': '2025-01-03', 'product': 'Widget', ...},{'date': '2025-01-03', 'product': 'Gadget',...}]

    # The shape: how big is this table?
    print(f"File:    {SAMPLE_CSV.name}")
    print(f"Shape:   {len(rows)} rows x {len(reader.fieldnames)} columns")
    #is the number of rows excluding header
    #reader.fieldnames is a list of the headers - list[str]
    print(f"Columns: {reader.fieldnames}")

    # The first few rows, exactly as Python sees them: a list of dicts.
    print("\nFirst 3 rows as dicts:")
    for row in rows[:3]:
        print(f"  {row}")

    # Everything DictReader gives you is a STRING — even the numbers.
    first = rows[0]
    print(f"\nCareful: units is {first['units']!r} "# !r means format this using repr() instead of str()
          f"(type: {type(first['units']).__name__}) — convert before doing math:")
    revenue = int(first["units"]) * float(first["unit_price"])
    print(f"  int('{first['units']}') * float('{first['unit_price']}') "
          f"= {revenue:.2f}")


if __name__ == "__main__":
    main()
