"""Verify It — pytest checkpoint for the Downloads Organizer.

Run from the repo root:

    .venv/bin/python -m pytest 6_organise_folder/project/test_organizer.py -v

Each test seeds a fresh messy folder in pytest's tmp_path (never the
repo), runs the organizer, and asserts on the result — including the
big one: the invoice.pdf name collision must leave BOTH files alive.
"""

import sys
#sys is Python's built-in module for interacting with the interpreter itself.
from pathlib import Path
#Python finds modules by address, not by search. 
# The standard library's address ships pre-registered - means the entries were put into sys.path before your code ran — by Python's own startup, not by you
# your folder's address doesn't — so you add it.

# The organizer and the seeder paths
#sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
#__file__ — path to the currently executing module.
#convert path object to string - str(Path(__file__).resolve().parent) - strictly speaking it is not needed as per latest python, but docs describe sys.path as a list of strings
#sys.path: A plain Python list of strings, each naming a directory (or a zip file) that Python searches, in order, when you write import something. 
#First hit wins; if the list is exhausted, you get ModuleNotFoundError.
#list.insert(0, x) shifts every existing element right by one
'''
import sys
for p in sys.path:
    print(repr(p))
'''
#sys.path.insert

from make_test_folder import make_test_folder  
from organize import organize  


def seeded(tmp_path: Path) -> Path:
    return make_test_folder(tmp_path / "messy")
    #creates a folder called messy in tmp_path and returns that path


def snapshot(folder: Path) -> set[str]:
    """Every file's path relative to *folder*, as strings."""
    return {str(p.relative_to(folder)) for p in folder.rglob("*") if p.is_file()}
    #folder.rglob("*") : rglob = recursive glob: walk folder and everything beneath it, yielding a Path for every item that matches the pattern. With "*" — match anything — it means "give me everything under this tree, at any depth."
    #relative_to(folder) : starting from folder, what's the path to this file? - excluding folder. The result starts just after it.
    #it returns a set

def test_dry_run_touches_nothing(tmp_path):
    #pytest recognises tmp_path as a fixture it knows how to build
    #Builds it, then calls test_dry_run_touches_nothing(tmp_path=<the path it built>)
    #A built-in pytest fixture: a pathlib.Path pointing at a fresh, empty directory created just for that one test, 
    # somewhere under the system temp area. If you want to see it, just print it as print(tmp_path)
    #print(f"\n ONE: test_dry_run_touches_nothing tmp_path -> {tmp_path}")
    #to see the print run it as python -m pytest project/test_organizer_with_comments.py -v -s
    #note you need -s above -> -s is shorthand for --capture=no, this is needed because by default with pytest stdout is captured by default and only replayed for failing tests. All 5 passed, so nothing would print.
    #a fixture is a named, reusable piece of setup — some thing a test needs to exist before it can run, packaged as a function that pytest calls on demand and whose return value gets handed to your test.
    #tmp_path for each function is different.
    #tmp_path is function-scoped, so each of your five tests gets its own freshly created, empty directory
    #the directory name embeds the test function's name — it's a per-test path, not a per-session one.
    #The caching rule is: within one test, a fixture is built once and reused, so if you asked for tmp_path twice in the same function you'd get the identical Path. Across tests, it's rebuilt.
    #if you run the tests again, for the same function you will notice the tmp_path is different.The leaf name stays the same; the session directory above it increments
    folder = seeded(tmp_path) #its a path
    before = snapshot(folder) # its a set

    plan = organize(folder, dry_run=True) #organise returns a list of tuples (item,dest_path)

    assert snapshot(folder) == before, "dry run must not move anything"
    assert len(plan) == 20, "plan should cover all 20 visible top-level files"


def test_expected_folder_structure(tmp_path):
    #try printing the tmp_path - note the tmp_path for each function is different.
    #print(f"\n TWO: test_expected_folder_structure -> {tmp_path}")
    folder = seeded(tmp_path)
    organize(folder)

    expected = {
        "Images": {"vacation.jpg", "screenshot.png", "meme.gif", "logo.svg"},
        "Archives": {"backup.zip", "project.tar.gz", "old_photos.rar"},
        "Audio": {"song.mp3", "podcast_episode.m4a"},
        "Video": {"clip.mp4", "lecture.mov"},
        "Other": {"installer.dmg", "mystery.xyz", "README"},
        "Documents": {"resume.docx", "notes.txt", "report.pdf", "budget.xlsx","contacts.csv", "invoice.pdf", "invoice_1.pdf"},
    }
    for category, names in expected.items():
        #when iterating over a dictionary , the order will be key,value 
        found = {p.name for p in (folder / category).iterdir()}
        assert found == names, f"{category}/ has {found}, expected {names}"
        #the message will be printed only when the assertion fails.
        #the f-string isn't just unused on success, it's never evaluated on success
        #found and names both are sets 

    # Hidden file skipped, and no loose visible files left at the top level.
    assert (folder / ".DS_Store").exists()
    #on a real folder on Windows you wont have a .DS_Store file but in this case 
    #make_test_folder(tmp_path / "messy") creates a file literally named .DS_Store — Windows allows this name fine
    leftovers = [p.name for p in folder.iterdir()
                 if p.is_file() and not p.name.startswith(".")]
    #inside any open bracket — (, [, { — Python ignores newlines entirely.The statement isn't over until the bracket closes.
    assert leftovers == []


def test_collision_pair_both_survive(tmp_path):
    folder = seeded(tmp_path)
    organize(folder)

    kept = folder / "Documents" / "invoice.pdf"
    renamed = folder / "Documents" / "invoice_1.pdf"
    assert kept.exists() and renamed.exists(), \
        "both invoices must survive the collision"
    #Outside brackets, a statement ends at the newline — unless the line ends with \, which glues 
    #the next physical line on. This is explicit continuation 

    contents = {kept.read_text(), renamed.read_text()}
    #contents is a set
    #read_text(): is a pathlib.Path method: open the file, read the entire contents as a string,returns the string, close the file — one call.
    assert contents == {
        "OLD invoice — filed last month\n",
        "NEW invoice — downloaded today\n",
    }, "neither invoice's contents may be lost or duplicated"
    #sets have no order, values can be in any order


def test_by_date_subfolders(tmp_path):
    folder = seeded(tmp_path)
    organize(folder, by_date=True)

    # mtimes are pinned by make_test_folder: NEW -> 2025-03, OLD -> 2024-11
    assert (folder / "Documents" / "2025-03" / "notes.txt").exists()
    assert (folder / "Documents" / "2024-11" / "report.pdf").exists()
    assert (folder / "Images" / "2024-11" / "meme.gif").exists()
    assert (folder / "Video" / "2025-03" / "clip.mp4").exists()
    #Deliberate spot-checking — and the choice of which four is intelligent
    #Both date buckets appear.
    #Both dates appear within one category (Documents gets both — proving one category can split into two date folders).
    #And the date layer appears under multiple different categories.

    # The pre-filed invoice sits directly in Documents/, so with --by-date
    # there is no collision: the new one lands in its date folder untouched.
    assert (folder / "Documents" / "invoice.pdf").exists()
    assert (folder / "Documents" / "2025-03" / "invoice.pdf").exists()


def test_organize_twice_is_harmless(tmp_path):
    folder = seeded(tmp_path)
    organize(folder)
    second_pass = organize(folder)

    assert second_pass == [], "an already-organized folder has nothing to move"
