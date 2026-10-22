"""Team expense summarizer.

Summarizes the expense entries exported from the team's expense form:
prints the total spent, a per-category breakdown, and the single largest
expense. Amounts arrive as text, exactly as form exports deliver them.

Usage:
    python broken_script.py
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
    total = 0
    for expense in expenses:
        total += expense["amount"]
    return total


def totals_by_category(expenses: list[dict]) -> dict[str, float]:
    """Return a dict mapping each category to its total amount."""
    totals = {}
    for expense in expenses:
        category = expense["category"]
        totals[category] += float(expense["amount"])
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
