"""Tuples and sets in 10 minutes.

Run me:  python examples/10_tuples_and_sets.py

You need to RECOGNIZE these two and know WHY the AI chose them —
you will rarely need to design with them yourself at this stage.

  ( ... )  tuple — a list that can't change; often "a pair that belongs together"
  { ... }  set   — no colons! — unique items, fast membership tests
"""


def main() -> None:
    # ── Tuples: fixed-shape bundles ──────────────────────────────────────
    print("TUPLES — like lists, but frozen. Chosen when the shape is fixed.")

    point = (1280, 720)                    # width & height belong together
    print(f"  point       : {point}")
    print(f"  point[0]    : {point[0]}   (indexing works like a list)")

    # The #1 place you'll meet tuples: multiple return values + unpacking.
    def min_max(numbers: list[int]) -> tuple[int, int]:
        return min(numbers), max(numbers)  # returns ONE tuple of two values
    #min(numbers) = min value 
    #print(min_max([12, 4, 31, 7]))
    lowest, highest = min_max([12, 4, 31, 7])   # "unpacking" the tuple
    print(f"  unpacking   : lowest={lowest}, highest={highest}")

    # Tuples can't be modified — that's the point (safety, not limitation):
    try:
        point[0] = 1920  # type: ignore[index]
    except TypeError as err:
        #Python uses TypeError when an operation isn't valid for an object's type.
        print(f"  mutating one: TypeError: {err}")

    # ── Sets: unique items, instant membership checks ────────────────────
    print("\nSETS — curly braces, NO colons. Chosen for uniqueness + fast 'in'.")

    emails = [
        "ana@example.com",
        "ben@example.com",
        "ana@example.com",     # duplicate!
        "carol@example.com",
        "ben@example.com",     # duplicate!
    ]
    #set(emails)
    #{}
    #in a set no duplicates
    unique_emails = set(emails)            # duplicates vanish, order is NOT kept
    print(f"  raw list ({len(emails)} items) : {emails}")
    print(f"  as a set ({len(unique_emails)} items) : {unique_emails}")

    # Membership: the whole reason sets exist. 'in' on a set is instant,
    # even with a million items; 'in' on a list checks every item.
    allowed_extensions = {".pdf", ".docx", ".xlsx"}
    for filename in ["report.pdf", "photo.jpg"]:
        dot = filename.rfind(".") #rfind searches a string from the right and returns the index of the last occurrence of the substring. If the substring isn't found, it returns -1.
        #find returns the first dot, which breaks on filenames with more than one
        suffix = filename[dot:] if dot != -1 else ""
        
        #if dot!=-1:
            #suffix = filename[dot:]  # slice from the dot to the end
        #else:
            #suffix = ""  # no dot found, so no suffix

        verdict = "process" if suffix in allowed_extensions else "skip"
        print(f"  {filename:12} -> {verdict}") #by default strings are left aligned

    # ── Recognition cheat sheet ──────────────────────────────────────────
    print("\nRecognition: (a, b)=tuple  {a, b}=set  {a: b}=dict  [a, b]=list")


if __name__ == "__main__":
    main()
