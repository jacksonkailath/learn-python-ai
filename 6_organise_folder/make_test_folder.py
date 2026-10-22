"""Seed a deterministic messy test folder for the Downloads Organizer.

Usage:
    .venv/bin/python project/make_test_folder.py

Creates (or wipes and recreates) project/test_downloads/ containing
~20 assorted files, a hidden .DS_Store that must be left alone, and a
deliberate name collision: a fresh invoice.pdf at the top level AND an
older invoice.pdf already filed inside Documents/. Both must survive
organizing — that is exactly what Bug Hunt #6 is about.

File modification times are pinned (os.utime) so --by-date runs are
deterministic too: "old" files land in 2024-11, "new" files in 2025-03.
"""

from __future__ import annotations

import datetime as dt
import os
import shutil
from pathlib import Path

OLD = dt.datetime(2024, 11, 2, 9, 30).timestamp()   # -> 2024-11 with --by-date
NEW = dt.datetime(2025, 3, 15, 14, 0).timestamp()   # -> 2025-03 with --by-date

# name -> (contents, pinned mtime)
TOP_LEVEL_FILES: dict[str, tuple[str, float]] = {
    # images
    "vacation.jpg": ("placeholder jpeg bytes\n", NEW),
    "screenshot.png": ("placeholder png bytes\n", NEW),
    "meme.gif": ("placeholder gif bytes\n", OLD),
    "logo.svg": ("<svg></svg>\n", OLD),
    # documents
    "resume.docx": ("placeholder docx bytes\n", NEW),
    "notes.txt": ("remember to test the organizer\n", NEW),
    "invoice.pdf": ("NEW invoice — downloaded today\n", NEW),  # collision!
    "report.pdf": ("placeholder pdf bytes\n", OLD),
    "budget.xlsx": ("placeholder xlsx bytes\n", OLD),
    "contacts.csv": ("name,email\nada,ada@example.com\n", NEW),
    # archives
    "backup.zip": ("placeholder zip bytes\n", OLD),
    "project.tar.gz": ("placeholder tarball bytes\n", NEW),
    "old_photos.rar": ("placeholder rar bytes\n", OLD),
    # audio
    "song.mp3": ("placeholder mp3 bytes\n", NEW),
    "podcast_episode.m4a": ("placeholder m4a bytes\n", OLD),
    # video
    "clip.mp4": ("placeholder mp4 bytes\n", NEW),
    "lecture.mov": ("placeholder mov bytes\n", OLD),
    # other / oddballs
    "installer.dmg": ("placeholder dmg bytes\n", NEW),
    "mystery.xyz": ("what even is this\n", OLD),
    "README": ("a file with no extension\n", NEW),
    # hidden — the organizer must skip this
    ".DS_Store": ("macOS junk\n", NEW),
}

# Already-filed file that the top-level invoice.pdf will collide with.
PREEXISTING = {
    Path("Documents") / "invoice.pdf": ("OLD invoice — filed last month\n", OLD),
}


def make_test_folder(target: Path) -> Path:
    """Create the messy folder at *target* (wiping it first) and return it."""
    if target.exists():
        shutil.rmtree(target)
    target.mkdir(parents=True)

    for name, (contents, mtime) in TOP_LEVEL_FILES.items():
        path = target / name
        path.write_text(contents, encoding="utf-8")
        os.utime(path, (mtime, mtime))

    for rel_path, (contents, mtime) in PREEXISTING.items():
        path = target / rel_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(contents, encoding="utf-8")
        os.utime(path, (mtime, mtime))

    return target


if __name__ == "__main__":
    folder = make_test_folder(Path(__file__).parent / "test_downloads")
    n_files = sum(1 for p in folder.rglob("*") if p.is_file())
    print(f"Seeded {folder} with {n_files} files.")
    print("Try:  python organize.py project/test_downloads --dry-run")
