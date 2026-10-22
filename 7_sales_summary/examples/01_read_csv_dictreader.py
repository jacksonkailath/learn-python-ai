"""Example 1 — reading a CSV the readable way: csv.DictReader.

Reads one month of sales data and shows the two facts you always want
first when meeting a new table: its SHAPE (rows x columns) and what a
single row actually looks like as a dict.

Run sample_data/generate_sample_data.py first if the CSV is missing.
"""

from csv import DictReader
from pathlib import Path

SAMPLE_CSV = Path(__file__).resolve().parent.parent / "sample_data" / "sales_2025_01.csv"


def main() -> None:
    if not SAMPLE_CSV.exists():
        raise SystemExit(
            f"Missing {SAMPLE_CSV}\n"
            "Generate it first:  python ../sample_data/generate_sample_data.py"
        ) #sys.exit

    with SAMPLE_CSV.open(newline="", encoding="utf-8") as f:
        reader = DictReader(f)          # row 1 becomes the dict keys, next()
        rows = list(reader)             # every other row becomes one dict
        #[{'date': '2025-01-01', 'region': 'East', 'product': 'USB-C Hub', 'units': '4', 'unit_price': '47.44'},{},{}]


    # The shape: how big is this table?
    print(f"File:    {SAMPLE_CSV.name}")
    print(f"Shape:   {len(rows)} rows x {len(reader.fieldnames)} columns")
    print(f"Columns: {reader.fieldnames}")

    # The first few rows, exactly as Python sees them: a list of dicts.
    print("\nFirst 3 rows as dicts:")
    for row in rows[:3]:
        print(f"  {row}")

    # Everything DictReader gives you is a STRING — even the numbers.
    first = rows[0]
    print(f"\nCareful: units is {first['units']!r} " # !r is repr()  
          f"(type: {type(first['units']).__name__}) — convert before doing math:")
    revenue = int(first["units"]) * float(first["unit_price"])
    print(f"  int('{first['units']}') * float('{first['unit_price']}') "
          f"= {revenue:.2f}")


if __name__ == "__main__":
    main()
