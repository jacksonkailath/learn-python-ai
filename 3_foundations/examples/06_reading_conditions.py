"""Reading conditions out loud: comparison and logical operators.

The skill this script builds is TRANSLATION, not memorization. Every
condition in Python can be read as an English sentence. If you can say
the sentence, you can predict the behavior.

Run it:
    python 06_reading_conditions.py
"""


def loud(label: str, value: bool) -> bool:
    """Return `value`, but announce that we were evaluated.

    Used below to make short-circuit evaluation VISIBLE: if you never
    see the announcement, Python never even looked at this operand.
    """
    print(f"      (evaluating {label} -> {value})")
    return value


def main() -> None:
    print("=== Part 1: the translation table, demonstrated ===")
    count, name, size = 47, "report.pdf", 0

    # Read each comparison out loud as you check the printed result.
    print(f"  count == 47   ('count is equal to 47')        -> {count == 47}")
    print(f"  count != 50   ('count is NOT equal to 50')    -> {count != 50}")
    print(f"  count > 10    ('count is greater than 10')    -> {count > 10}")
    print(f"  count <= 47   ('count is at most 47')         -> {count <= 47}")
    print(f"  size == 0     ('size is equal to zero')       -> {size == 0}")
    print(f"  'pdf' in name ('the text pdf appears in name')-> {'pdf' in name}")
    print(f"  not size      ('size is falsy / empty / zero')-> {not size}")
    print(f"  0 < count < 100 ('count is between 0 and 100')-> {0 < count < 100}")

    print()
    print("=== Part 2: and / or, read out loud ===")
    is_pdf = name.endswith(".pdf")
    is_small = size < 1_000_000
    print(f"  is_pdf and is_small ('BOTH must be true')  -> {is_pdf and is_small}")
    print(f"  is_pdf or is_small  ('at least ONE is true')-> {is_pdf or is_small}")
    print(f"  not is_pdf          ('flip it')             -> {not is_pdf}")

    print()
    print("=== Part 3: short-circuit -- Python is lazy, on purpose ===")
    print("  A) False and <anything> : the right side is NEVER evaluated")
    result = loud("left", False) and loud("right", True)
    print(f"      result: {result}  (only 'left' printed -- 'right' was skipped)")

    print("  B) True or <anything>   : the right side is NEVER evaluated")
    result = loud("left", True) or loud("right", False)
    print(f"      result: {result}  (again, 'right' was skipped)")

    print("  C) Both sides evaluated only when needed:")
    result = loud("left", True) and loud("right", True)
    print(f"      result: {result}")

    print()
    print("=== Part 4: why short-circuit matters in real automation ===")
    # This pattern appears in AI output constantly. Read it out loud:
    # "if answer exists AND its cleaned-up value is y" -- the `answer and`
    # guard means Python never calls .strip() on None, so no crash.
    answer = None
    if answer and answer.strip().lower() == "y":
        print("  confirmed")
    else:
        print("  answer was None -- and .strip() was never called, no crash.")
        print("  Remove the `answer and` guard and this line would be an")
        print("  AttributeError: 'NoneType' object has no attribute 'strip'.")


if __name__ == "__main__":
    main()
