"""try/except as a DESIGN CHOICE, good vs bad, side by side.

Scenario: summing expense amounts typed by humans, so some entries are junk.
A malformed entry is an EXPECTED situation (catch it, handle it, tell the
human). A missing required config key is a BUG in how the script was set up
(let it crash -- or fail fast with a clear message).

Run it:  .venv/bin/python examples/04_try_except_design.py
"""

# Human-entered data: junk is EXPECTED, so handling it is a feature.
RAW_AMOUNTS = ["42.50", "17.80", "twelve", "8.99", "", "103.25"]

CONFIG = {"currency": "EUR", "report_title": "Team offsite expenses"}


# ----------------------------------------------------------------- THE BAD WAY
def total_bad(raw_amounts: list[str]) -> float:
    """Everything wrong at once:
    - one giant try around the WHOLE loop (first junk entry silently
      abandons every entry after it)
    - `except Exception` catches bugs too, not just bad data
    - returns a wrong-but-plausible number and tells no one
    """
    total = 0.0
    #["42.50", "17.80", "twelve", "8.99", "", "103.25"]
    try:
        for raw in raw_amounts:
            total += float(raw)#total = 42.5+17.8 = 60.3
    except Exception:
        pass  # <- the most expensive two words in Python
        #pass is a statement that does nothing. Python requires at least one statement inside any block, so when you want an empty block you write pass as a placeholder
        #this says: catch every possible error, then do nothing about it
        #The loop is abandoned mid-way
    return total


# ---------------------------------------------------------------- THE GOOD WAY
def total_good(raw_amounts: list[str]) -> tuple[float, list[str]]:
    """Each decision deliberate:
    - try covers ONE conversion, so one bad entry skips one entry
    - catches ONLY ValueError -- the specific error bad data causes;
      a genuine bug in here would still crash loudly (good!)
    - the human gets told what was skipped, in plain language
    """
    total = 0.0
    skipped: list[str] = []
    ##["42.50", "17.80", "twelve", "8.99", "", "103.25"]
    for raw in raw_amounts:
        try:
            total += float(raw) #total = 42.5+17.8+8.99+103.25
        except ValueError:
            #ValueError is the built-in exception Python raises when a function receives an argument of the right type but an unusable value
            #In this file it comes from float(raw). Every entry in the list is a string, so the type is fine. But not every string can be turned into a number
            #float("twelve")   # ValueError: could not convert string to float: 'twelve'
            skipped.append(raw) #["twelve",""]
    return total, skipped


if __name__ == "__main__":
    print("=" * 64)
    print("BAD: one big try, `except Exception: pass`")
    print("=" * 64)
    bad = total_bad(RAW_AMOUNTS)
    print(f"total_bad()  -> {bad:.2f}")
    print("Wrong (60.30 -- it silently dropped every entry after 'twelve',")
    print("including two valid ones) and it never said a word.")

    print()
    print("=" * 64)
    print("GOOD: small try, specific exception, honest report")
    print("=" * 64)
    good, skipped = total_good(RAW_AMOUNTS)
    print(f"total_good() -> {good:.2f}")
    for junk in skipped:
        print(f"  warning: could not read amount {junk!r} -- skipped it")
    print("Right (172.54) -- and the human knows exactly what was skipped.")

    print()
    print("=" * 64)
    print("AND: what you should NOT catch")
    print("=" * 64)
    # A missing required config key is not 'bad data from the world' --
    # it's a setup bug. Don't except-and-limp-on. Fail fast, loudly,
    # with a message written for a HUMAN.
    if "currency" not in CONFIG:
        raise SystemExit(
            "CONFIG is missing 'currency'. Add it at the top of the script "
            "(e.g. \"currency\": \"EUR\") and run again."
        )

    #dont do something like this for config 
    '''
    try:
        currency = CONFIG["currency"]
    except KeyError:
        currency = "USD"   # silently guess
    '''
    
    print(f"required config present: currency={CONFIG['currency']!r} -- carry on.")
    print()
    print("Design rules: catch what you EXPECT and can HANDLE, at the smallest")
    print("possible scope, naming the specific exception. Let BUGS crash.")
