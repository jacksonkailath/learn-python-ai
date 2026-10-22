"""Verify It — pytest checkpoint for the Downloads Organizer.

Run from the repo root:

    python -m pytest 6_organise_folder/project/test_organizer.py -v

Each test seeds a fresh messy folder in pytest's tmp_path (never the
repo), runs the organizer, and asserts on the result — including the
big one: the invoice.pdf name collision must leave BOTH files alive.
"""

import sys
from pathlib import Path

# The organizer and the seeder paths
#sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


from make_test_folder import make_test_folder  
from organize import organize  


def seeded(tmp_path: Path) -> Path:
    return make_test_folder(tmp_path / "messy")


def snapshot(folder: Path) -> set[str]:
    """Every file's path relative to *folder*, as strings."""
    return {str(p.relative_to(folder)) for p in folder.rglob("*") if p.is_file()}



def test_dry_run_touches_nothing(tmp_path):
    #print(f'first tmp_path: {tmp_path}')
    folder = seeded(tmp_path)
    before = snapshot(folder)

    plan = organize(folder, dry_run=True)

    assert snapshot(folder) == before, "dry run must not move anything"
    assert len(plan) == 20, "plan should cover all 20 visible top-level files"


def test_expected_folder_structure(tmp_path):
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
        found = {p.name for p in (folder / category).iterdir()}
        assert found == names, f"{category}/ has {found}, expected {names}"

    # Hidden file skipped, and no loose visible files left at the top level.
    assert (folder / ".DS_Store").exists()
    leftovers = [p.name for p in folder.iterdir() 
                 if p.is_file() and not p.name.startswith(".")]
    assert leftovers == []


def test_collision_pair_both_survive(tmp_path):
    folder = seeded(tmp_path)
    organize(folder)

    kept = folder / "Documents" / "invoice.pdf"
    renamed = folder / "Documents" / "invoice_1.pdf"
    assert kept.exists() and renamed.exists(), \
        "both invoices must survive the collision"

    contents = {kept.read_text(), renamed.read_text()} #video with statement pattern. - last lecture in this section
    assert contents == {
        "OLD invoice — filed last month\n",
        "NEW invoice — downloaded today\n",
    }, "neither invoice's contents may be lost or duplicated"


def test_by_date_subfolders(tmp_path):
    folder = seeded(tmp_path)
    organize(folder, by_date=True)

    # mtimes are pinned by make_test_folder: NEW -> 2025-03, OLD -> 2024-11
    assert (folder / "Documents" / "2025-03" / "notes.txt").exists()
    assert (folder / "Documents" / "2024-11" / "report.pdf").exists()
    assert (folder / "Images" / "2024-11" / "meme.gif").exists()
    assert (folder / "Video" / "2025-03" / "clip.mp4").exists()

    # The pre-filed invoice sits directly in Documents/, so with --by-date
    # there is no collision: the new one lands in its date folder untouched.
    assert (folder / "Documents" / "invoice.pdf").exists()
    assert (folder / "Documents" / "2025-03" / "invoice.pdf").exists()


def test_organize_twice_is_harmless(tmp_path):
    folder = seeded(tmp_path)
    organize(folder)
    second_pass = organize(folder)

    assert second_pass == [], "an already-organized folder has nothing to move"
