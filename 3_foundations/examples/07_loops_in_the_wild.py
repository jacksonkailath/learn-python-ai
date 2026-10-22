"""Loops in the wild: the five loop patterns AI output is full of.

You will READ far more loops than you will write. This script is a field
guide: each part is a pattern you will meet in almost every AI-drafted
automation, with the out-loud reading for each.

Run it:
    python 07_loops_in_the_wild.py
"""

from pathlib import Path
#Path is a class from Python's built-in pathlib module.
#Think of a Path as a "smart address" for a file or folder. 
# A plain string like "C:/Users/you/data.csv" is just text — Python doesn't know it's a location. 
# Wrap it in Path("you/data.csv").resolve() and it becomes an object that knows it's a location, so you can ask it questions and give it commands.


def main() -> None:
    reports = ["january.csv", "february.csv", "march.csv", "april.csv"]

    # ------------------------------------------------------------------
    print("=== Pattern 1: plain for -- 'for each thing in the pile' ===")
    # Read: "for each filename in reports, do the indented block."
    for filename in reports:
        print(f"  processing {filename}")
        #1 - filename = "january.csv"
        #2 - filename = "february.csv"


    # ------------------------------------------------------------------
    print()
    print("=== Pattern 2: enumerate -- 'and number them as you go' ===")
    # Read: "for each position AND filename in reports..."
    # start=1 makes the numbering human (1-based), which is why AI drafts
    # of progress messages almost always use it.
    for number, filename in enumerate(reports, start=1):
        print(f"  [{number}/{len(reports)}] {filename}")

#a= [1,2,3,4,5,6,7]
#len(a) = 7
    # ------------------------------------------------------------------
    print()
    print("=== Pattern 3: range -- 'do it N times / step through numbers' ===")
    # range(4) produces 0, 1, 2, 3 -- it STOPS BEFORE 4. Four numbers,
    # starting at zero. This stop-before-the-end rule is the single most
    # common source of off-by-one bugs in AI drafts (see Bug Hunt #3).
    print(f"  list(range(4))        -> {list(range(4))}")
    #list()
    print(f"  list(range(1, 5))     -> {list(range(1, 5))}")
    print(f"  list(range(0, 10, 3)) -> {list(range(0, 10, 3))}")#0,3,6,9
    for batch_start in range(0, 10, 3):
        print(f"  batch covering items {batch_start}..{batch_start + 2}")

    # ------------------------------------------------------------------
    print()
    print("=== Pattern 4: while -- 'keep going UNTIL something changes' ===")
    # A while loop runs as long as its condition is True. Something inside
    # the loop MUST push the condition toward False, or it never ends.
    # Here `attempts += 1` is the escape hatch -- cover it with your thumb
    # and you are looking at Bug Hunt #3.
    attempts = 0
    max_attempts = 3
    connected = False
    while not connected and attempts < max_attempts:
        attempts += 1  # <-- the line that guarantees the loop ends
        #attempts = attempts + 1
        #attempts = 3
        print(f"  connection attempt {attempts}...")
        connected = attempts == 3  # mock: succeeds on the third try
        #connected = True
    print(f"  connected: {connected} (after {attempts} attempts)")

    # ------------------------------------------------------------------
    print()
    print("=== Pattern 5: looping over files -- the automation classic ===")
    # Read: "for each path matching *.py in this script's own folder..."
    # Real automations point this at Downloads or a project folder; we scan
    # the examples folder itself so the script works anywhere, zero setup.
    examples_dir = Path(__file__).resolve().parent
    for path in sorted(examples_dir.glob("*.py")):
        size_kb = path.stat().st_size / 1024 #/ 1024 — converts bytes to kilobytes.
        print(f"  {path.name:<32} {size_kb:6.1f} KB") #6 is the min width,If the number is shorter, Python pads it with spaces on the left.


if __name__ == "__main__":
    main()
