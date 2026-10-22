#!/usr/bin/env python3
#The shebang is that first line: #!/usr/bin/env python3. The name comes from the two characters that start it — # ("sharp"/hash) and ! ("bang").
#what it does - When you run a file directly — ./organise_folder.py instead of python organise_folder.py — the operating system has to figure out what program should interpret it. It reads the first two bytes of the file. If they're #!, the rest of that line is treated as the command to run, and the file's path gets passed to it as an argument.
#we are getting this warning because this file lacks execute permission. you can add execute permission with the command: chmod +x organise_folder.py  
#also note you wont be getting this warning on windows It decides what's runnable by file extension (.exe, .py associations) instead.
"""Organize the top-level contents of a folder into category subfolders."""
import sys 
#import sys gives access to the interpreter's (the python 3 program) runtime interface,
#we use it in main as sys.argv (the arguments the interpreter was started with) and sys.exit(1) - tells the interpreter to stop, and hands 1 back to the shell as the exit code.
from pathlib import Path
#imports just the Path class, not the whole module — so you write Path(...) instead of pathlib.Path(...)

CATEGORIES = {
    "Images": {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp", ".tiff", ".heic"},
    "Documents": {".pdf", ".doc", ".docx", ".txt", ".rtf", ".odt", ".xls", ".xlsx", ".ppt", ".pptx", ".csv", ".md"},
    "Archives": {".zip", ".tar", ".gz", ".rar", ".7z", ".bz2", ".xz"},
    "Audio": {".mp3", ".wav", ".flac", ".aac", ".ogg", ".m4a", ".wma"},
    "Video": {".mp4", ".mov", ".avi", ".mkv", ".wmv", ".flv", ".webm"},
}


def category_for(path: Path) -> str:
    ext = path.suffix.lower()
    #path.suffix returns the file extension, including the leading dot. lower() makes it lowercase so we don't have to worry about .JPG vs .jpg.
    for category, extensions in CATEGORIES.items():
        if ext in extensions:
            return category
    return "Other"


def organize(folder: Path) -> None:
    for item in sorted(folder.iterdir()):
        #iterdir() returns an iterator of Path objects for each item in the folder. sorted() makes a list of them, sorted by name.
        if not item.is_file():
            #is_file() returns True if the path exists and is a file, False otherwise. (It returns False for directories, symlinks, and other special files.)
            continue  # skip subfolders, including ones from previous runs

        category = category_for(item)
        dest_dir = folder / category
        #The / operator on Path objects joins paths. So if folder is /home/user/Downloads and category is "Images", dest_dir will be /home/user/Downloads/Images.
        dest_dir.mkdir(exist_ok=True)
        #mkdir() creates the directory. exist_ok=True means "don't raise an error if it already exists".

        dest_path = dest_dir / item.name
        #item.name is the filename (without the path). So dest_path is the full path to where we want to move the file.
        item.rename(dest_path)
        #item.rename(dest_path) moves the file to dest_path. If dest_path already exists, it will be overwritten.
        print(f"{item.name} -> {category}/")


def main() -> None:
    if len(sys.argv) != 2:
        #sys.argv is a list of the script name plus everything after it.
        print("Usage: python organize_folder.py <folder>")
        sys.exit(1)
        #Execution halts.
        #The 1 becomes the exit code
        #0 = success , anything non-zero = failure
        '''
        check it yourself by running the following commands in your terminal:
        python organize_folder.py
        echo $?        # prints 1
        '''
        #Why the exit code matters: it's how other programs know whether yours worked. The shell's && only continues on 0:
        '''
        try this in your terminal:
        python organize_folder.py && echo "done"  # will not print "done"
        python organize_folder.py ~/Downloads && echo "done"
        '''

    folder = Path(sys.argv[1]).expanduser().resolve()
    #Path(sys.argv[1]) - sys.argv[1] is a plain string and Path(...) wraps it in a Path object so you can call path methods on it.
    #expanduser() replaces leading ~ with the user's home directory, if present.
    #resolve() makes the path absolute, resolving any symlinks and .. components.
    if not folder.is_dir():
        #is_dir() returns True if the path exists and is a directory, False otherwise.
        print(f"Error: {folder} is not a directory")
        sys.exit(1)

    organize(folder)
    #Your script reaching the end of main() normally exits 0 automatically — you only call sys.exit when you need to bail out early with a failure.


if __name__ == "__main__":
    main()