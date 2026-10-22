#!/usr/bin/env python3
"""Organize the top-level contents of a folder into category subfolders."""

import argparse
#Python's standard library module for parsing command-line arguments. It turns sys.argv (the raw list of strings the shell passes in) into a structured object
#argparse makes add_argument easy
import sys
from datetime import datetime
#datetime is the module; datetime is also a class inside it.
#its used in datetime.fromtimestamp(path.stat().st_mtime)
from pathlib import Path

CATEGORIES = {
    "Images": {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp", ".tiff", ".heic"},
    "Documents": {".pdf", ".doc", ".docx", ".txt", ".rtf", ".odt", ".xls", ".xlsx", ".ppt", ".pptx", ".csv", ".md"},
    "Archives": {".zip", ".tar", ".gz", ".rar", ".7z", ".bz2", ".xz"},
    "Audio": {".mp3", ".wav", ".flac", ".aac", ".ogg", ".m4a", ".wma"},
    "Video": {".mp4", ".mov", ".avi", ".mkv", ".wmv", ".flv", ".webm"},
}


def category_for(path: Path) -> str:
    ext = path.suffix.lower()
    for category, extensions in CATEGORIES.items():
        if ext in extensions:
            return category
    return "Other"


def is_hidden(path: Path) -> bool:
    return path.name.startswith(".")


def date_subdir_for(path: Path) -> str:
    """YYYY-MM string derived from the file's modified time."""
    mtime = datetime.fromtimestamp(path.stat().st_mtime)
    #warning - without a tz= argument returns a naive datetime — one with no timezone attached — converted using whatever the machine's local timezone happens to be.
    #to make Make local time explicit you can import -> from datetime import timezoneand use mtime = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc).astimezone()
    #or to make it UTC you can use mtime = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)

    #path.stat() returns file's metadata (facts about the file and not content)
    #.st_mtime One field off that result: modification time, as a float of seconds since the Unix epoch (1970-01-01 00:00 UTC). For a file touched you'd see something like 1786000000.123.
    #fromtimestamp is a constructor — a way to build a datetime object from a number instead of from year/month/day pieces.
    return mtime.strftime("%Y-%m")
    #strftime("%Y-%m") formats the datetime object into a string according to the given format. %Y is the year with century as a decimal number, and %m is the month as a zero-padded decimal number. So this will return a string like "2024-06" for June 2024.



def destination_dir(folder: Path, item: Path, by_date: bool) -> Path:
    dest_dir = folder / category_for(item)
    if by_date:
        dest_dir = dest_dir / date_subdir_for(item)
    return dest_dir


def unique_destination(dest_dir: Path, name: str) -> Path:
    """Return a path in dest_dir for `name`, appending _1, _2, ... if taken."""
    candidate = dest_dir / name
    if not candidate.exists():
        return candidate

    stem, suffix = Path(name).stem, Path(name).suffix
    #name is string, so Path(name) converts it to a Path object. 
    # Then .stem gives the filename without the suffix, 
    # and .suffix gives the file extension (including the dot).
    counter = 1
    while True:
        #keep going till return
        candidate = dest_dir / f"{stem}_{counter}{suffix}"
        if not candidate.exists():
            return candidate
        counter += 1


def move_item(item: Path, dest_path: Path, dry_run: bool) -> None:
    if dry_run:
        return
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    #dest_path.parent — strips the filename off, leaving the directory
    #parents=True means that if the parent directories don't exist, they should be created. For example, if dest_path is /path/to/destination/file.txt and /path/to/destination doesn't exist, it will create /path/to/destination.
    #exist_ok=True — don't complain if it's already there. if already there do nothing
    item.rename(dest_path)
    #it's both rename and move — those are the same operation at the filesystem level.


def describe_move(item: Path, dest_path: Path, folder: Path, dry_run: bool) -> str:
    prefix = "[dry-run] " if dry_run else ""
    rel_dir = dest_path.parent.relative_to(folder)
    #dest_path.parent — the destination directory, without the filename
    #.relative_to(folder) — strips off the leading portion that matches folder, leaving what's underneath
    if dest_path.name != item.name:
        #Only when unique_destination had to add a counter
        return f"{prefix}{item.name} -> {rel_dir}/{dest_path.name}"
    return f"{prefix}{item.name} -> {rel_dir}/"


def organize(folder: Path, dry_run: bool = False, by_date: bool = False) -> list[tuple[Path, Path]]:
    #return type is a list of tuples where each tuple has 2 path objects
    moves: list[tuple[Path, Path]] = []

    for item in sorted(folder.iterdir()):
        if not item.is_file():
            continue  # skip subfolders, including ones from previous runs
        if is_hidden(item):
            continue

        dest_dir = destination_dir(folder, item, by_date)
        dest_path = unique_destination(dest_dir, item.name)

        move_item(item, dest_path, dry_run)
        moves.append((item, dest_path))
        #(item, dest_path) — the parentheses build a tuple of two elements

        print(describe_move(item, dest_path, folder, dry_run))

    return moves


def build_arg_parser() -> argparse.ArgumentParser:
    #it returns an ArgumentParser instance.
    #Note it builds and returns the parser rather than parsing
    parser = argparse.ArgumentParser(
        description="Organize the top-level contents of a folder into category subfolders."
    )
    #Creates the parser object.

    #add_argument stores the rules as in what to look for and extract when parsing

    parser.add_argument("folder", help="Folder to organize")
    #positional argument as no -- prefix. Hence it is required and must be provided by the user.
    #The attribute name is taken from the string, so args.folder.

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would move without moving anything",
    )
    #Declares an optional argument, because of the -- prefix
    #the name of the argument is dry_run, to get it you can type args.dry_run. It is a boolean flag (because of the action="store_true" parameter), so if it is present, it will be True, otherwise False.
    #action="store_true" makes it a flag that consumes no value: present → True, absent → False. The False default comes with the action;
    #The destination(where the parsed value gets stored - that is where True or False is stored) is derived by stripping the dashes and replacing hyphens with underscores, so --dry-run lands in args.dry_run

    parser.add_argument(
        "--by-date",
        action="store_true",
        help="Within each category, file items into YYYY-MM subfolders by modified time",
    )

    '''
    add_argument("folder").      destination: args.folder     Value = the string provided by the user for the folder to organize
    add_argument("--dry-run").   destination: args.dry_run    Value = True if the user provides the --dry-run flag, otherwise False
    add_argument("--by-date").   destination: args.by_date    Value = True if the user provides the --by-date flag, otherwise False
    '''
    return parser


def main() -> None:
    parser = build_arg_parser()
    args = parser.parse_args()
    # parse_args() is a method of the ArgumentParser class that actually processes the command-line arguments based on the rules defined by add_argument. 
    # It returns an object (args) with attributes corresponding to the defined arguments.

    folder = Path(args.folder).expanduser().resolve()
    if not folder.is_dir():
        print(f"Error: {folder} is not a directory")
        sys.exit(1)

    organize(folder, dry_run=args.dry_run, by_date=args.by_date)


if __name__ == "__main__":
    main()