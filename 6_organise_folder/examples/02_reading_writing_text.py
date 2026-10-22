"""Reading and writing text files — the with-statement pattern.

Run me:

    .venv/bin/python section-06-files-folders/examples/02_reading_writing_text.py

Creates a scratch/ folder next to this script and works inside it, so
nothing outside this folder is ever touched.
"""

from pathlib import Path

SCRATCH = Path(__file__).parent / "scratch"


def the_risky_way(path: Path) -> None:
    """The pattern you should recognize but NOT copy.

    If anything between open() and close() raises an exception, close()
    never runs: the file handle leaks, and on Windows the file can stay
    locked. Buffered writes may never reach the disk.
    """
    f = open(path, "w", encoding="utf-8")
    f.write("groceries:\n")
    f.write("- oat milk\n")
    f.close()  # only runs if nothing above blew up


def the_with_way(path: Path) -> None:
    """The pattern to internalize: with open(...) as f."""
    with open(path, "w", encoding="utf-8") as f:
        f.write("groceries:\n")
        f.write("- oat milk\n")
        f.write("- coffee beans\n")
    # The file is guaranteed closed here — even if an exception
    # happened inside the block. That guarantee is the whole point.


def append_a_line(path: Path, line: str) -> None:
    """Mode 'a' appends; mode 'w' would have wiped the file first."""
    with open(path, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def read_it_back(path: Path) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def main() -> None:
    SCRATCH.mkdir(exist_ok=True)
    shopping = SCRATCH / "shopping_list.txt"

    the_risky_way(shopping)   # works here, but fragile — see docstring
    the_with_way(shopping)    # note: mode "w" replaced the whole file
    append_a_line(shopping, "- bread")

    print("Contents of scratch/shopping_list.txt:")
    print(read_it_back(shopping))

    # Looping over lines is the everyday reading pattern:
    print("Line by line, stripped:")
    with open(shopping, "r", encoding="utf-8") as f:
        for number, line in enumerate(f, start=1):
            print(f"  {number}: {line.strip()}")

    # pathlib's shortcuts for small files (they use `with` internally):
    note = SCRATCH / "note.txt"
    note.write_text("write_text / read_text are the one-liner versions.\n",
                    encoding="utf-8")
    print("\nread_text() says:", note.read_text(encoding="utf-8").strip())


if __name__ == "__main__":
    main()
