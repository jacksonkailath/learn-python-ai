"""Lecture 2 companion -- trigger the Big Five errors, one at a time.

Each demo function contains the CLASSIC cause of that error in AI-drafted
code. The script deliberately triggers each error, catches it, and explains
what the error is REALLY telling you. It runs clean overall (exit code 0)
because every crash is caught on purpose -- in real code you would usually
let these crash and read the traceback instead.

Run it:  .venv/bin/python examples/02_big_five_errors.py
"""


def banner(number: int, name: str) -> None:
    print()
    print(f"--- {number}. {name} " + "-" * (48 - len(name)))


# ---------------------------------------------------------------- NameError
def demo_name_error() -> None:
    """Classic AI cause: the draft renames a variable halfway through
    and misses one occurrence."""
    user_count = 42
    # The AI called it `user_count` above but types `user_cout` here:
    print(user_cout + 1)  # noqa: F821  (deliberate for the demo)


# ---------------------------------------------------------------- TypeError
def demo_type_error() -> None:
    """Classic AI cause: assuming a value is a number when it is a string
    (everything from input(), CSV files, and JSON text fields is a string)."""
    age_from_form = "29"  # came in as text, like input() always does
    print(age_from_form + 1)


# ----------------------------------------------------------------- KeyError
def demo_key_error() -> None:
    """Classic AI cause: the AI GUESSED the shape of your data and
    guessed a key name that isn't there."""
    order = {"order_id": 1017, "total": 84.50, "customer_name": "Ines"}
    # The AI assumed the key would be "customer":
    print(order["customer"])
    #order.get("customer")


# --------------------------------------------------------------- IndexError
def demo_index_error() -> None:
    """Classic AI cause: an off-by-one -- valid indexes for a list of
    length n are 0 .. n-1, so items[len(items)] is always one too far."""
    scores = [88, 92, 79]
    #         0   1   2
    print(scores[len(scores)])#scores[3]


# ----------------------------------------------------------- AttributeError
def demo_attribute_error() -> None:
    """Classic AI cause: a function returned None (a failed lookup, a
    forgotten return) and the next line calls a method on it."""
    settings = {"theme": "dark"}
    username = settings.get("username")  # key missing -> returns None
    print(username.upper())


if __name__ == "__main__":
    print("THE BIG FIVE -- each error triggered, caught, and explained.")

    banner(1, "NameError")
    #demo_name_error()
    try:
        demo_name_error()
    except NameError as exc:
        #except NameError catches only that one error type — a TypeError or KeyError would sail straight past this block and crash.
        #An except block is a claim that you know what went wrong and what to do about it.
        #The general principle: catch only what you can actually handle.
        #without Except - exception travels up until it exits the program. Stop.
        print(f"  raised -> NameError: {exc}")
        print("  REALLY says: this name does not exist right here, right now.")
        print("  Look for: a typo, or a variable the AI renamed halfway through.")

    banner(2, "TypeError")
    try:
        demo_type_error()
    except TypeError as exc:
        print(f"  raised -> TypeError: {exc}")
        print("  REALLY says: right operation, wrong KIND of value.")
        print('  Look for: a number that is secretly a string ("29" is not 29).')

    banner(3, "KeyError")
    try:
        demo_key_error()
    except KeyError as exc:
        print(f"  raised -> KeyError: {exc}")
        print("  REALLY says: this dict has no such label. The message IS the key.")
        print("  Look for: the AI guessing your data's shape. print(the_dict.keys()).")

    banner(4, "IndexError")
    try:
        demo_index_error()
    except IndexError as exc:
        print(f"  raised -> IndexError: {exc}")
        print("  REALLY says: the position you asked for is past the end.")
        print("  Look for: off-by-one -- len(items) is never a valid index.")

    banner(5, "AttributeError")
    #demo_attribute_error()
    try:
        demo_attribute_error()
    except AttributeError as exc:
        print(f"  raised -> AttributeError: {exc}")
        print("  REALLY says: this object has no such method/attribute.")
        print("  Look for: 'NoneType' in the message -- something upstream")
        print("  returned None and nobody noticed. Trace WHERE the None came from.")

    print()
    print("All five triggered and explained. Exit code 0 -- every crash was")
    print("caught on purpose. In your own code: let them crash, read bottom-up.")
