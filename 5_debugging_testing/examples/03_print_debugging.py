"""Lecture 3 companion -- print() debugging: the wrong way, then the right way.

The bug: an order subtotal comes out as `9.999.999.99` instead of `29.97`.
Part 1 hunts it with naked prints (and gets nowhere).
Part 2 hunts it with LABELED prints, `repr()`, `type()`, and the f"{var=}"
trick -- and finds it in three lines of output.

The actual bug: `price` arrived as the STRING "9.99" (as every value from a
CSV or a web form does), and string * int means REPEAT, not multiply.

Run it:  .venv/bin/python examples/03_print_debugging.py
"""

# A row as it actually arrives from a CSV / web form: everything is text.
RAW_ORDER = {"item": "USB cable", "price": "9.99", "quantity": 3}


def subtotal_buggy(order: dict):
    """The AI draft. Looks fine. Is not fine."""
    return order["price"] * order["quantity"]


def subtotal_fixed(order: dict) -> float:
    """The real fix: convert text to a number before doing math."""
    return float(order["price"]) * order["quantity"]
    #float("9.99") = 9.99


if __name__ == "__main__":
    print("=" * 64)
    print("PART 1 -- naked prints (how NOT to do it)")
    print("=" * 64)
    result = subtotal_buggy(RAW_ORDER)
    # Naked prints: no labels, no types. Which value is which? Why is it weird?
    print(RAW_ORDER["price"])
    print(result)
    print("...three bare values. `9.99` looks like a number. The subtotal looks")
    print("insane, but nothing tells you WHY. Naked prints show values while")
    print("hiding exactly the thing that matters here: the TYPE.")

    print()
    print("=" * 64)
    print("PART 2 -- labeled prints, repr, type, and f'{var=}'")
    print("=" * 64)
    price = RAW_ORDER["price"]
    quantity = RAW_ORDER["quantity"]

    # Rule 1: LABEL every print. Future-you must know what each line is.
    print(f"DEBUG price       = {price}")

    # Rule 2: print the REPR, not the str -- repr shows quotes, so a string
    # pretending to be a number gives itself away instantly.
    print(f"DEBUG repr(price) = {price!r}")
    #print(f"DEBUG repr(price) = {repr(price)}")
    #repr() is a built-in that returns the unambiguous representation of a value
    #print(f"{price}")     # 29
    #print(f"{price!r}")   # '29'
    #You could write it as an honest function call and get the identical result:
    #print(f"DEBUG repr(price) = {repr(price)}")
    #{price!r} and {repr(price)} produce identical output
    # !r isn't standalone syntax. It only exists inside the braces of an f-string or a format() template

    # Rule 3: print the TYPE when math misbehaves.
    print(f"DEBUG type(price) = {type(price)}")

    # Rule 4 (the shortcut that does all three): f"{var=}" prints the
    # variable's NAME and its repr. This is the workhorse.
    print(f"DEBUG {price=} {quantity=}")
    #price={price!r}
    #the above is shorthand for 
    print(f"DEBUG price={price!r} quantity={quantity!r}")
    #{expr=} , will print expr= then the value of the expression 
    print(f"DEBUG {subtotal_buggy(RAW_ORDER)=}")

    print()
    print("The quotes in price='9.99' are the smoking gun: it's a STRING.")
    print('And "9.99" * 3 repeats the string -> "9.999.999.99". Bug found.')

    print()
    print("=" * 64)
    print("THE FIX -- convert at the boundary, then do math")
    print("=" * 64)
    fixed = subtotal_fixed(RAW_ORDER)
    print(f"{fixed=}")
    assert fixed == 29.97, "subtotal should be 29.97"
    print("assert passed: subtotal is 29.97. (Now DELETE the debug prints --")
    print("or graduate them to logging, which is example 04.)")
