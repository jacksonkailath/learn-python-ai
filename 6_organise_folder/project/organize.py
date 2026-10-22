#!/usr/bin/env python3
"""Organize the top-level contents of a folder into category subfolders."""

import argparse
import sys
from datetime import datetime
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
    return mtime.strftime("%Y-%m")


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
    counter = 1
    while True:
        candidate = dest_dir / f"{stem}_{counter}{suffix}"
        if not candidate.exists():
            return candidate
        counter += 1


def move_item(item: Path, dest_path: Path, dry_run: bool) -> None:
    if dry_run:
        return
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    item.rename(dest_path)


def describe_move(item: Path, dest_path: Path, folder: Path, dry_run: bool) -> str:
    prefix = "[DRY RUN] " if dry_run else ""
    return f"{prefix}{item.name} -> {dest_path.relative_to(folder)}"


def organize(folder: Path, dry_run: bool = False, by_date: bool = False) -> list[tuple[Path, Path]]:
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
        print(describe_move(item, dest_path, folder, dry_run))

    return moves


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Organize the top-level contents of a folder into category subfolders."
    )
    parser.add_argument("folder", help="Folder to organize")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would move without moving anything",
    )
    parser.add_argument(
        "--by-date",
        action="store_true",
        help="Within each category, file items into YYYY-MM subfolders by modified time",
    )
    return parser


def main() -> None:
    parser = build_arg_parser()
    args = parser.parse_args()

    folder = Path(args.folder).expanduser().resolve()
    if not folder.is_dir():
        print(f"Error: {folder} is not a directory")
        sys.exit(1)

    organize(folder, dry_run=args.dry_run, by_date=args.by_date)


if __name__ == "__main__":
    main()
