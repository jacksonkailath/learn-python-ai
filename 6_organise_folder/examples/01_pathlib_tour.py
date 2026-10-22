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


def divider(title: str) -> None:
    print(f"\n--- {title} " + "-" * (60 - len(title)))


def main() -> None:
    # ------------------------------------------------------------------
    divider("1. Three paths you always have")
    home = Path.home()          # your user folder, on any OS
    cwd = Path.cwd()            # where the terminal is standing right now
    this_file = Path(__file__)  # the script that is running

    print(f"Path.home()   -> {home}")
    print(f"Path.cwd()    -> {cwd}")
    print(f"Path(__file__) -> {this_file}")

    # ------------------------------------------------------------------
    divider("2. The / operator builds paths")
    # No string gluing, no worrying about / vs \ on Windows.
    downloads = home / "Downloads"
    deep = home / "projects" / "bootcamp" / "notes.txt"
    print(f"home / 'Downloads'  -> {downloads}")
    print(f"chained /           -> {deep}")

    # ------------------------------------------------------------------
    divider("3. Taking a path apart: .name / .suffix / .stem / .parent")
    p = Path("/Users/ada/Downloads/invoice_march.pdf")
    print(f"path    : {p}")
    print(f".name   : {p.name}")     # invoice_march.pdf
    print(f".suffix : {p.suffix}")   # .pdf      <- how we detect file type
    print(f".stem   : {p.stem}")     # invoice_march
    print(f".parent : {p.parent}")   # /Users/ada/Downloads

    # ------------------------------------------------------------------
    divider("4. Absolute vs relative")
    rel = Path("examples/01_pathlib_tour.py")
    print(f"relative path : {rel}")
    print(f"is_absolute() : {rel.is_absolute()}")
    print(f"resolved      : {this_file.resolve()}")
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
        kind = "dir " if entry.is_dir() else "file"
        print(f"  [{kind}] {entry.name}")

    print(f"\nJust the Python files (glob('*.py')):")
    for script in sorted(examples_dir.glob("*.py")):
        print(f"  {script.name}  (stem={script.stem!r}, suffix={script.suffix!r})")

    # ------------------------------------------------------------------
    divider("7. File metadata: size and modified time")
    stats = this_file.stat()
    print(f"{this_file.name} is {stats.st_size} bytes")
    print(f"last modified timestamp: {stats.st_mtime:.0f} (seconds since 1970)")
    print("(Section 7's organizer turns st_mtime into YYYY-MM folder names.)")


if __name__ == "__main__":
    main()
