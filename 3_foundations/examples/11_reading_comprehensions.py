"""READING comprehensions: the unrolling technique.

Run me:  python examples/11_reading_comprehensions.py

AI output is FULL of comprehensions. You don't need to write them yet —
you need to decode them. Every comprehension below is shown twice:
first as the one-liner, then unrolled into the plain loop it stands for.
Both versions run, and we assert they produce identical results.

The three-part unrolling technique (read middle -> right -> left):
    [ EXPR   for ITEM in SOURCE   if CONDITION ]
       (3)         (1)                 (2)
    1. "for ITEM in SOURCE"  -> it's a loop
    2. "if CONDITION"        -> keep only some items (may be absent)
    3. "EXPR"                -> what actually lands in the new list
"""

from pathlib import Path


def main() -> None:
    # ── 1. The flagship: filter files by extension ───────────────────────
    files = [
        Path("report.pdf"),
        Path("photo.jpg"),
        Path("invoice.pdf"),
        Path("notes.txt"),
    ]

    # The comprehension the course keeps coming back to:
    pdf_names = [x.name for x in files if x.suffix == ".pdf"]

    # ...is EXACTLY this loop, folded onto one line:
    pdf_names_loop = []                    # start empty
    for x in files:                        # (1) the loop      : for x in files
        if x.suffix == ".pdf":             # (2) the filter    : if x.suffix == ".pdf"
            pdf_names_loop.append(x.name)  # (3) the expression: x.name

    assert pdf_names == pdf_names_loop
    print(f"1. pdf_names        : {pdf_names}")

    # ── 2. No filter — transform every item ──────────────────────────────
    raw_emails = [" Ana@Example.COM ", "ben@example.com", "  CAROL@example.com"]

    cleaned = [e.strip().lower() for e in raw_emails]

    cleaned_loop = []
    for e in raw_emails:                   # (1) loop — no (2), keep everything
        cleaned_loop.append(e.strip().lower())  # (3) expression

    assert cleaned == cleaned_loop
    print(f"2. cleaned          : {cleaned}")

    # ── 3. Filter only — the expression is just the item itself ──────────
    amounts = [42.5, -3.0, 18.0, 0.0, -7.25]

    positive = [a for a in amounts if a > 0]

    positive_loop = []
    for a in amounts:                      # (1) loop
        if a > 0:                          # (2) filter
            positive_loop.append(a)        # (3) expression is just... a

    assert positive == positive_loop
    print(f"3. positive         : {positive}")

    # ── 4. Dict comprehension: { KEY: VALUE for ITEM in SOURCE } ─────────
    # Same technique — only the left part now builds key: value pairs.
    contacts = [
        {"name": "Ana", "email": "ana@example.com"},
        {"name": "Ben", "email": "ben@example.com"},
    ]

    by_email = {c["email"]: c["name"] for c in contacts}

    by_email_loop = {}
    for c in contacts:                     # (1) loop
        by_email_loop[c["email"]] = c["name"]  # (3) key: value
    assert by_email == by_email_loop
    print(f"4. by_email         : {by_email}")

    # ── 5. Generator expression: same shape, round parens, no list built ─
    # You'll see these INSIDE function calls: sum(...), max(...), any(...).
    expenses = [{"amount": 480.0}, {"amount": 96.4}, {"amount": 54.2}]

    total = sum(e["amount"] for e in expenses)   # no [ ] — items are fed
                                                 # to sum() one at a time
    #produces the values one at a time, as sum() asks for them, and never stores them all together
    total_loop = 0.0
    for e in expenses:
        total_loop += e["amount"] #total_loop = total_loop + e["amount"]
    assert total == total_loop
    print(f"5. total            : {total}")

    # ── 6. When you see a NESTED one: don't decode, unroll on paper ──────
    teams = [["ana", "ben"], ["carol"], ["dev", "elena"]]

    everyone = [person for team in teams for person in person_source(team)]
    # Two 'for's read left to right = the same order you'd write the loops:
    everyone_loop = []
    for team in teams:                     # first 'for'
        for person in person_source(team):  # second 'for'
            everyone_loop.append(person)   # expression
    assert everyone == everyone_loop
    print(f"6. everyone         : {everyone}")
    print("\nAll comprehension/loop pairs matched. The [ ] one-liner IS the loop.")


def person_source(team: list[str]) -> list[str]:
    """Stands in for any per-team lookup — here it just returns the team."""
    return team


if __name__ == "__main__":
    main()
