"""Generate the Section 7 sample dataset: 12 monthly sales CSVs + a control file.

Creates ``sales_2025_01.csv`` … ``sales_2025_12.csv`` (columns exactly:
``date,region,product,units,unit_price``; ISO dates) plus
``control_totals.json`` containing per-month revenue totals, per-product
totals, and the grand total — all computed here, by the generator itself,
from the very rows it writes. That file is our "hand-checked control":
Section 7's Verify It checkpoint (and Sections 10/12/14, which reuse this
data) assert the report's numbers against it.

Deterministic by design: ``random.seed(42)`` means every student generates
byte-identical data, so every student's totals match the course videos.

Usage:
    python generate_sample_data.py            # writes into this folder
"""

from __future__ import annotations

import calendar
import csv
import json
import random
from pathlib import Path

SEED = 42
YEAR = 2025
COLUMNS = ["date", "region", "product", "units", "unit_price"]

REGIONS = ["North", "South", "East", "West"]

# product -> base unit price (actual prices jitter a little around these,
# like real-world discounts and promos)
PRODUCTS = {
    "Laptop Stand": 34.99,
    "USB-C Hub": 49.99,
    "Wireless Mouse": 24.99,
    "Mechanical Keyboard": 89.99,
    "27in Monitor": 249.99,
    "HD Webcam": 59.99,
    "Desk Lamp": 39.99,
    "Noise-Cancelling Headphones": 199.99,
}


def _month_rows(month: int) -> list[dict]:
    """Build one month of sales rows (list of dicts — the course's core shape)."""
    last_day = calendar.monthrange(YEAR, month)[1]
    # A few hundred orders per month, with a holiday-season bump in Nov/Dec
    # (so the "below average" conditional highlight has something to flag).
    n_rows = random.randint(280, 340) + (60 if month in (11, 12) else 0)

    rows = []
    for _ in range(n_rows):
        product = random.choice(list(PRODUCTS))
        base_price = PRODUCTS[product]
        rows.append(
            {
                "date": f"{YEAR}-{month:02d}-{random.randint(1, last_day):02d}",
                "region": random.choice(REGIONS),
                "product": product,
                "units": random.randint(1, 12),
                # jitter the price: small promos and increases, 2 decimals
                "unit_price": round(base_price * random.uniform(0.92, 1.05), 2),
            }
        )
    # Real exports arrive date-sorted; ours should look real too.
    rows.sort(key=lambda row: row["date"])
    return rows


def write_sample_data(output_dir: Path) -> dict:
    """Write the 12 CSVs and control_totals.json into *output_dir*.

    Returns the control-totals dict (the same one written to JSON), so
    tests can call this against a temporary folder and compare directly.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    random.seed(SEED)

    monthly_revenue: dict[str, float] = {}
    monthly_row_counts: dict[str, int] = {}
    product_totals: dict[str, dict] = {
        name: {"units": 0, "revenue": 0.0} for name in PRODUCTS
    }
    grand_total = 0.0

    for month in range(1, 13):
        month_key = f"{YEAR}-{month:02d}"
        rows = _month_rows(month)

        csv_path = output_dir / f"sales_{YEAR}_{month:02d}.csv"
        with csv_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=COLUMNS)
            writer.writeheader()
            writer.writerows(rows)

        # Control totals are computed from the exact rows just written —
        # units * unit_price, summed the plain way. No spreadsheet involved.
        month_revenue = 0.0
        for row in rows:
            revenue = row["units"] * row["unit_price"]
            month_revenue += revenue
            product_totals[row["product"]]["units"] += row["units"]
            product_totals[row["product"]]["revenue"] += revenue

        monthly_revenue[month_key] = round(month_revenue, 2)
        monthly_row_counts[month_key] = len(rows)
        grand_total += month_revenue

    control = {
        "columns": COLUMNS,
        "seed": SEED,
        "monthly_revenue": monthly_revenue,
        "monthly_row_counts": monthly_row_counts,
        "product_totals": {
            name: {"units": totals["units"], "revenue": round(totals["revenue"], 2)}
            for name, totals in product_totals.items()
        },
        "grand_total_revenue": round(grand_total, 2),
    }

    control_path = output_dir / "control_totals.json"
    control_path.write_text(json.dumps(control, indent=2) + "\n", encoding="utf-8")
    return control


def main() -> None:
    output_dir = Path(__file__).parent
    control = write_sample_data(output_dir)
    total_rows = sum(control["monthly_row_counts"].values())
    print(f"Wrote 12 monthly CSVs ({total_rows:,} rows) into {output_dir}")
    print(f"Wrote control_totals.json (grand total: "
          f"{control['grand_total_revenue']:,.2f})")


if __name__ == "__main__":
    main()
