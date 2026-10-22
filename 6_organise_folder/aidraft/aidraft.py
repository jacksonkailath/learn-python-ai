#!/usr/bin/env python3
"""Organize the top-level contents of a folder into category subfolders."""

import sys
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


def organize(folder: Path) -> None:
    for item in sorted(folder.iterdir()):
        if not item.is_file():
            continue  # skip subfolders, including ones from previous runs

        category = category_for(item)
        dest_dir = folder / category #.../test_downloads/documents/xyz.pdf
        dest_dir.mkdir(exist_ok=True)

        dest_path = dest_dir / item.name
        item.rename(dest_path) #overwritten
        print(f"{item.name} -> {category}/")


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python aidraft.py <folder>")
        sys.exit(1)
 
    folder = Path(sys.argv[1]).expanduser().resolve() 
    if not folder.is_dir():
        print(f"Error: {folder} is not a directory")
        sys.exit(1)

    organize(folder)


if __name__ == "__main__":
    main()