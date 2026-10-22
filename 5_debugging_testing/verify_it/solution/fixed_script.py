"""Team expense summarizer -- FIXED solution for the Section 5 Verify It.

The AI draft (../broken_script.py) contained exactly 2 bugs, and they
surfaced one at a time:

  BUG 1 -- TypeError in total_spent()
      The amounts are STRINGS ("48.50") -- exactly as every form export,
      CSV, and JSON text field delivers them -- and the draft added them
      to an int:  TypeError: unsupported operand type(s) for +=: 'int'
      and 'str'. The draft even converted correctly in two OTHER
      functions; AI drafts are inconsistent like that.

  BUG 2 -- KeyError in totals_by_category()  (visible only after fix 1)
      totals[category] += ... assumes the category key already exists in
      the dict. The first "food" expense finds no "food" key ->
      KeyError: 'food'. The draft never initialized the bucket.

Run it:  .venv/bin/python verify_it/solution/fixed_script.py

Expected correct output:

    Expense Summary
    ===============
    Total spent: $236.64

    By category:
      food     $   61.25
      travel   $  165.99
      office   $    9.40

    Largest expense: Hotel night ($129.99)
"""

EXPENSES = [
    {"description": "Team lunch", "category": "food", "amount": "48.50"},
    {"description": "Coffee beans", "category": "food", "amount": "12.75"},
    {"description": "Train tickets", "category": "travel", "amount": "36.00"},
    {"description": "Hotel night", "category": "travel", "amount": "129.99"},
    {"description": "Notebooks", "category": "office", "amount": "9.40"},
]


def total_spent(expenses: list[dict]) -> float:
    """Return the total amount across all expenses."""
    total = 0.0
    for expense in expenses:
        # FIX 1: expense["amount"] is a STRING (form exports deliver text),
        # and int += str is a TypeError. Convert at the boundary, then do
        # math -- the same "convert text before arithmetic" fix as
        # examples/03_print_debugging.py.
        total += float(expense["amount"])
    return total


def totals_by_category(expenses: list[dict]) -> dict[str, float]:
    """Return a dict mapping each category to its total amount."""
    totals: dict[str, float] = {}
    for expense in expenses:
        category = expense["category"]
        # FIX 2: the draft did `totals[category] += ...`, which crashes
        # with KeyError the FIRST time each category appears -- there is
        # no bucket to add to yet. .get(category, 0.0) starts a missing
        # bucket at zero. (dict.setdefault or collections.defaultdict
        # are equally good fixes.)
        totals[category] = totals.get(category, 0.0) + float(expense["amount"])
    return totals


def largest_expense(expenses: list[dict]) -> dict:
    """Return the single most expensive entry."""
    return max(expenses, key=lambda expense: float(expense["amount"]))


def print_summary(expenses: list[dict]) -> None:
    """Print the full expense summary."""
    print("Expense Summary")
    print("===============")
    print(f"Total spent: ${total_spent(expenses):.2f}")
    print()
    print("By category:")
    for category, amount in totals_by_category(expenses).items():
        print(f"  {category:<8} ${amount:>8.2f}")
    top = largest_expense(expenses)
    print()
    print(f"Largest expense: {top['description']} (${float(top['amount']):.2f})")


if __name__ == "__main__":
    print_summary(EXPENSES)
