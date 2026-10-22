"""Reading and writing text files — the with-statement pattern.

Run me:

    .venv/bin/python section-06-files-folders/examples/02_reading_writing_text.py

Creates a scratch/ folder next to this script and works inside it, so
nothing outside this folder is ever touched.
"""

from pathlib import Path

SCRATCH = Path(__file__).parent / "scratch"
#__file__ : the path of the file this module was loaded from
#Every module carries its own __file__
'''
Try it 

# main.py
import helper
print(__file__)          # .../main.py
print(helper.__file__)   # .../helper.py  ← not main.py!
'''


def the_risky_way(path: Path) -> None:
    """The pattern you should recognize but NOT copy.

    If anything between open() and close() raises an exception, close()
    never runs: the file handle leaks, and on Windows the file can stay
    locked. Buffered writes may never reach the disk.
    """
    f = open(path, "w", encoding="utf-8")
    #open() does two things: asks the OS for a file handle (a kernel-level resource — the OS tracks that your process has this file open), 
    #and wraps it in a Python file object f
    #Mode "w" truncates the file to zero bytes immediately,means all content in file is wiped, at open time — before any write.
    #encoding="utf-8" pins how str becomes bytes
    #Files can't store letters. They can only store numbers.
    #So when you save the letter A, Python has to look it up in a codebook: "A = 65." 
    #When you read the file back, it looks up 65 in the codebook: "65 = A."
    #warning: because we have open() whose result is assigned to a plain variable instead of being managed by a with block.
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
    #mode a: = append: open for writing, but keep everything that's there and add new bytes at the end.    


def read_it_back(path: Path) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()
    #mode r: =read - : open for reading only, start at position 0. 
    #It's also the default — open(path) with no mode means open(path, "r"). 
    #f.read() gives back 1 string of the full content


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
            #the file is iterable
            #line: each step of a for loop gives you the next line, \n included. 
            #line is a string
            print(f"  {number}: {line.strip()}")

    # pathlib's shortcuts for small files (they use `with` internally):
    note = SCRATCH / "note.txt"
    note.write_text("write_text / read_text are the one-liner versions.\n",
                    encoding="utf-8")
    #write text: replaces
    #note: there is no append_text in pathlib
    print("\nread_text() says:", note.read_text(encoding="utf-8").strip())


if __name__ == "__main__":
    main()
