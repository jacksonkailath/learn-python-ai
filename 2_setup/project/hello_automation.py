"""A tiny script that proves file automation works on your machine.

It makes a folder next to this script, creates a temporary file inside it,
then renames that file. Safe to run as many times as you like.
"""

from pathlib import Path

# ---- Settings: change these without touching the code below ----
FOLDER_NAME = "scratch"
TEMP_FILE_NAME = "photo_2026-01-15.tmp"
FINAL_FILE_NAME = "vacation_beach_sunset.jpg"
# -----------------------------------------------------------------

# __file__ is the path of THIS script. Using it (instead of the current
# working directory) means the folder always lands next to the script,
# no matter where you run it from. .resolve() turns it into a full path.
script_folder = Path(__file__).resolve().parent

# The "/" operator joins path pieces together (it's not division here!)
scratch_folder = script_folder / FOLDER_NAME
temp_file = scratch_folder / TEMP_FILE_NAME
final_file = scratch_folder / FINAL_FILE_NAME

# Step 1: make the folder.
# exist_ok=True means "don't complain if it's already there",
# which is one of the things that makes running twice safe.
scratch_folder.mkdir(exist_ok=True)
print(f"Step 1: Folder is ready: {scratch_folder}")

# Step 2: if a previous run left the final file behind, remove it first.
# Otherwise renaming onto an existing file can fail on Windows.
if final_file.exists():
    final_file.unlink()  # unlink() is pathlib's word for "delete file"
    print(f"Step 2: Removed leftover file from an earlier run: {final_file.name}")
else:
    print("Step 2: No leftover file to clean up.")

# Step 3: create the temporary file with a little text inside.
temp_file.write_text("This is a test file.\n")
print(f"Step 3: Created file: {temp_file.name}")

# Step 4: rename it. Renaming is really "moving" to a new name.
temp_file.rename(final_file)
print(f"Step 4: Renamed {temp_file.name} -> {final_file.name}")

print("Done! Automation works. Look inside the folder to see the result.")