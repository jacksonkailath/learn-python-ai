"""Lecture 1 companion -- this script crashes ON PURPOSE.

Run it, watch it die, and practice reading the traceback BOTTOM-UP:

    1. LAST line  -> the error type and message (what went wrong)
    2. line above -> the exact file + line where it went wrong
    3. walk UP    -> the call chain that got Python there (how we arrived)

The crash is three function calls deep, which is exactly how real crashes
look: the line that explodes is almost never the line that caused the
problem. Here the *cause* is a typo in the EMPLOYEES data ("principle"
instead of "principal") -- but Python only notices three frames down,
inside lookup_tax_rate().

Run it:  .venv/bin/python examples/01_read_the_traceback.py
"""

TAX_BANDS = {
    "junior": 0.12,
    "senior": 0.32,
    "principal": 0.37,
}

EMPLOYEES = [
    {"name": "Priya", "level": "senior", "monthly_gross": 5200},
    {"name": "Marcus", "level": "junior", "monthly_gross": 3100},
    # The typo below is the real cause of the crash -- the traceback
    # will point somewhere else entirely. That's the lesson.
    {"name": "Sofia", "level": "principle", "monthly_gross": 7400},
]


def lookup_tax_rate(level: str) -> float:
    """Return the tax rate for a pay level. Crashes HERE if the level is unknown."""
    return TAX_BANDS[level]


def compute_net_pay(employee: dict) -> float:
    """Gross pay minus tax."""
    rate = lookup_tax_rate(employee["level"])
    return employee["monthly_gross"] * (1 - rate)


def generate_payslip(employee: dict) -> str:
    """One formatted payslip line."""
    net = compute_net_pay(employee)
    return f"{employee['name']}: net pay ${net:,.2f}"


def run_payroll(employees: list[dict]) -> None:
    """Print a payslip for every employee."""
    for employee in employees:
        print(generate_payslip(employee))


if __name__ == "__main__":
    print("=" * 64)
    print("DEMO: this script crashes ON PURPOSE so you can read a real")
    print("traceback. Two payslips will print, then the third explodes.")
    print("Read the traceback from the BOTTOM line up.")
    print("=" * 64)
    run_payroll(EMPLOYEES)
    # We only reach this line if the demo crash never happened --
    # which would mean the demo itself is broken.
    print("DEMO BROKEN: the call above was supposed to crash.")
    #it prints that string to stderr and exits with a non-zero exit code (1), which signals failure to the shell.
