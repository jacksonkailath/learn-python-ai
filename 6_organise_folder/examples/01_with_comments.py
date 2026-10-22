"""A pathlib reference — how Python sees your filesystem.

Not a lecture to complete before the real code; a cheat-sheet to keep
open while you read the AI's draft. When a line in the organizer uses a
pathlib method you don't recognize, find it here and run this to watch
it print a real value.

Run me from the section folder (venv activated):

    python examples/01_pathlib_tour.py

Every method shown here is written up in the Section 7 README,
section 2 (🧠 Your pathlib reference).
"""

from pathlib import Path
#pathlib is a standard-library module (since Python 3.4) that represents filesystem paths as objects instead of strings. 
# Path is its main class, and importing it by name lets you write Path("data/x.csv") rather than pathlib.Path("data/x.csv").


def divider(title: str) -> None:
    print(f"\n--- {title} " + "-" * (60 - len(title)))


def main() -> None:
    # ------------------------------------------------------------------
    divider("1. Three paths you always have")
    home = Path.home()          # current users' home directory.
    #you are calling home() on Path 
    #Path is a class object that holds the methods, not a path value. There's no path stored inside it
    #Path is the thing being used to construct with, not the thing being read from
    #you are using Path purely as a place to find the method.
    #later we will see Path(/Users/ada/Downloads/invoice_march.pdf) , in this case you're calling the class, which builds an instance holding that value. Now you have a thing with content, and methods called on it work on that content.
    cwd = Path.cwd()            # where the terminal is standing right now, current working directory.
    this_file = Path(__file__)  # the script that is running
    #__file__ : A string variable that Python automatically defines inside every module, holding the path to that module's .py file

    print(f"Path.home()   -> {home}")
    print(f"Path.cwd()    -> {cwd}")
    print(f"Path(__file__) -> {this_file}")

    # ------------------------------------------------------------------
    divider("2. The / operator builds paths")
    # No string gluing, no worrying about / vs \ on Windows.
    # Unix/macOS:forward slash
    # Windows: backslash
    
    downloads = home / "Downloads"
    deep = home / "projects" / "bootcamp" / "notes.txt"
    print(f"home / 'Downloads'  -> {downloads}")
    print(f"chained /           -> {deep}")


    # ------------------------------------------------------------------
    divider("3. Taking a path apart: .name / .suffix / .stem / .parent")
    p = Path("/Users/ada/Downloads/invoice_march.pdf")
    #p is a Path object holding that value.
    #the below 4 are properties , not methods - no parentheses. They're instance-level, so they read p's own value, 
    # they dont need to do or call anything - in contrast, Path.home() reads the OS environment - Every running process gets a set of environment variables from the OS, so actually what happens is Path.home() looks up HOME in that dictionary and wraps the result in a Path
    print(f"path    : {p}")
    print(f".name   : {p.name}")     # invoice_march.pdf, string
    print(f".suffix : {p.suffix}")   # .pdf      <- how we detect file type, string
    print(f".stem   : {p.stem}")     # invoice_march, string
    print(f".parent : {p.parent}")   # /Users/ada/Downloads, Path

    # ------------------------------------------------------------------
    divider("4. Absolute vs relative")
    rel = Path("examples/01_pathlib_tour.py")
    print(f"relative path : {rel}")
    print(f"is_absolute() : {rel.is_absolute()}")
    print(f"resolved      : {this_file.resolve()}")
    #It turns a path into a complete, unambiguous absolute path.
    print("A relative path only means something FROM the current working")
    print(f"directory, which right now is: {cwd}")

    # ------------------------------------------------------------------
    divider("5. Asking questions: exists / is_file / is_dir")
    print(f"{this_file.name} exists?  {this_file.exists()}")
    print(f"{this_file.name} is_file? {this_file.is_file()}")
    print(f"its parent is_dir?        {this_file.parent.is_dir()}")
    ghost = home / "definitely_not_a_real_file_12345.txt"
    print(f"ghost file exists?        {ghost.exists()}")

    # ------------------------------------------------------------------
    divider("6. Listing a folder: iterdir() and glob()")
    examples_dir = this_file.parent
    print(f"Everything in {examples_dir.name}/ :")
    for entry in sorted(examples_dir.iterdir()):
        #.iterdir() lists a directory's contents.
        #sorted() takes any iterable, returns a new list, ordered
        #ordering is done by full path string, effectively ordering comes down to the filename as every file shares same parent.
        kind = "dir " if entry.is_dir() else "file"
        print(f"  [{kind}] {entry.name}")

    print(f"\nJust the Python files (glob('*.py')):")
    #\n is a newline character.
    for script in sorted(examples_dir.glob("*.py")):
        #.glob() lists directory contents filtered by a pattern
        #sorted() consumes it and orders the results by name, and gives out a list
        print(f"  {script.name}  (stem={script.stem!r}, suffix={script.suffix!r})")
        #script.stem!r : !r is an f-string conversion flag — it applies repr() - Representation - to the value instead of str(). For strings, that means the quotes are shown.
        #script.suffix!r :!r is an f-string conversion flag — it applies repr() to the value instead of str(). For strings, that means the quotes are shown.

    # ------------------------------------------------------------------
    divider("7. File metadata: size and modified time")
    stats = this_file.stat()
    #.stat() asks the OS for the file's metadata — size, timestamps, permissions. It's a system call, so parentheses, and it hits the disk.
    print(f"{this_file.name} is {stats.st_size} bytes")
    print(f"last modified timestamp: {stats.st_mtime:.0f} (seconds since 1970)")
    #st_mtime - Modification time - A float: seconds since the Unix epoch (1 Jan 1970, UTC).
    #:.0f - A format spec inside the f-string — everything after the colon controls how the value is rendered.
    #f → fixed-point decimal
    #.0 → zero digits after the point, it rounds rather than truncating
    print("(Section 7's organizer turns st_mtime into YYYY-MM folder names.)")


if __name__ == "__main__":
    main()
