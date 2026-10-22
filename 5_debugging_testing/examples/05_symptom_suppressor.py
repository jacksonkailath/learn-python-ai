"""Lecture 6 companion -- a real AI "fix" that suppresses the symptom, annotated.

The setup: a regional sales report crashed with KeyError: 'north '.
(The region name arrived from a CSV with a trailing space -- a data-cleaning
bug.) The traceback was pasted to an AI, which replied with the classic
symptom-suppressor: wrap it in try/except and return 0.

The crash is gone. The BUG is still there -- and now it's invisible.
The report happily tells the boss that the North region sold $0.

Run it:  .venv/bin/python examples/05_symptom_suppressor.py
"""

WEEKLY_SALES = {
    "north": [12_400, 11_950, 13_220],#12400+11950+13220
    "south": [8_100, 9_400, 8_760],
    "east": [10_500, 10_980, 11_340],
}

# What actually comes out of the CSV: note the trailing space on "north ".
# THIS is the real bug -- dirty data that nobody normalized.
REGIONS_FROM_CSV = ["north ", "south", "east"]


def region_total_suppressed(sales: dict, region: str) -> int:
    """The AI's "fix", verbatim shape. Annotated:

    - try/except was ADDED but no line inside it CHANGED  -> red flag #1
    - it catches Exception (everything, including real bugs) -> red flag #2
    - it invents a fake value (0) so the program can limp on -> red flag #3
    - it cannot explain why the KeyError happened            -> red flag #4
    """
    try:
        return sum(sales[region])
    except Exception:
        return 0  # "handled" -- i.e., the bug now produces quiet, wrong numbers


def region_total_fixed(sales: dict, region: str) -> int:
    """The REAL fix: normalize the dirty input at the boundary.

    And deliberately NO try/except: if a genuinely unknown region ever
    arrives, that's a new problem we WANT to hear about, loudly.
    """
    clean_region = region.strip().lower()
    return sum(sales[clean_region])


if __name__ == "__main__":
    print("=" * 64)
    print("THE SUPPRESSED VERSION -- no crash, wrong report")
    print("=" * 64)
    for region in REGIONS_FROM_CSV:
        total = region_total_suppressed(WEEKLY_SALES, region)
        print(f"  {region.strip():<6} total: ${total:>8,}")
    print("No traceback, no warning... and North shows $0. A crash you can")
    print("see beats a wrong number you can't.")

    print()
    print("=" * 64)
    print("THE FIXED VERSION -- cause repaired, correct report")
    print("=" * 64)
    for region in REGIONS_FROM_CSV:
        total = region_total_fixed(WEEKLY_SALES, region)
        print(f"  {region.strip():<6} total: ${total:>8,}")

    print()
    print("=" * 64)
    print("AND the fixed version still crashes for REAL problems (good!)")
    print("=" * 64)
    try:
        region_total_fixed(WEEKLY_SALES, "atlantis")
    except KeyError as exc:
        print(f"  region_total_fixed(..., 'atlantis') -> KeyError: {exc}")
        print("  Correctly refused: an unknown region is a real problem,")
        print("  and real problems should be loud, not $0.")

    print()
    print("Litmus test for any AI fix: can it explain WHY the error happened?")
    print("If the 'fix' only adds try/except and changes nothing inside it,")
    print("it treated the symptom. The disease is still in there.")
