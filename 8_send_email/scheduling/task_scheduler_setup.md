# Scheduling on Windows with Task Scheduler

Goal: run `monday_report.py` **every Monday at 9:00 AM**, automatically, whenever
your PC is on. Windows doesn't have `cron`; it has **Task Scheduler**, a built-in
app that does the same job with a wizard instead of a text file.

There are two ways in — the clicking way (good for learning) and the one-line
`schtasks` way (good once you know what you want). Both below.

---

## First: find your two absolute paths

Task Scheduler, like cron, starts from nothing — no activated venv, no working
folder. Give it absolute paths to (a) the venv's Python and (b) the script.

Open **PowerShell** in your project folder and run:

```powershell
cd C:/Users/jacks/Projects/learn-python-ai
"$PWD\.venv\Scripts\python.exe"
# -> C:/Users/jacks/Projects/learn-python-ai/.venv/Scripts/python.exe

"$PWD\8_send_email\project\monday_report.py"
# -> C:/Users/jacks/Projects/learn-python-ai/8_send_email/project/monday_report.py
```

Note the Windows layout: the venv's Python is at **`.venv\Scripts\python.exe`**
(on macOS/Linux it's `.venv/bin/python`). Using it means all your packages are
already available — no activation step.

## Test the command by hand first

Prove it works from a plain PowerShell before scheduling anything:

```powershell
& "C:/Users/jacks/Projects/learn-python-ai/.venv/Scripts/python.exe" `
  "C:/Users/jacks/Projects/learn-python-ai/8_send_email/project/monday_report.py" --test
```

If that emails you the report, the scheduled task will too.

---

## Option A — the GUI wizard

1. Press **Start**, type **Task Scheduler**, open it.
2. Right pane → **Create Basic Task…**
3. **Name:** `Monday Sales Report`. Click **Next**.
4. **Trigger:** choose **Weekly** → Next. Set **Start** to a date, **9:00:00 AM**,
   recur every **1** week, tick **Monday** only. Next.
5. **Action:** **Start a program**. Next.
6. Fill the three boxes — this is the part everyone gets wrong, so read carefully:
   - **Program/script:** the full path to the venv Python:
     `C:/Users/jacks/Projects/learn-python-ai/.venv/Scripts/python.exe`
   - **Add arguments:** the full path to the script **plus the flag**:
     `"C:/Users/jacks/Projects/learn-python-ai/8_send_email/project/monday_report.py" --test`
     (this path has no spaces, so the quotes are optional — but a safe habit;
     the flag goes outside the quotes.)
   - **Start in:** the script's folder:
     `C:/Users/jacks/Projects/learn-python-ai/8_send_email/project`
     (This "Start in" box sets the working directory. It's where the report's
     default output — `monthly_report.xlsx` — gets written, so leave it blank and
     the file lands wherever Task Scheduler starts, typically `C:\Windows\System32`.
     Your `.env` is found regardless: the code loads it relative to the script
     file itself, not the working directory. Note: "Start in" is the one box where
     forward slashes are unreliable on some Windows builds — if the task misbehaves,
     retry it with backslashes:
     `C:\Users\jacks\Projects\learn-python-ai\8_send_email\project`.)
7. **Next → Finish.**
8. Find your task under **Task Scheduler Library**, right-click → **Run** to test
   it immediately. Check your inbox.

## Option B — one PowerShell command (`schtasks`)

Once you know the paths, this creates the same task in a single line. Run
PowerShell **as your normal user** (admin only if you need it to run when logged
out):

```powershell
schtasks /Create /TN "Monday Sales Report" /SC WEEKLY /D MON /ST 09:00 /TR "\"C:/Users/jacks/Projects/learn-python-ai/.venv/Scripts/python.exe\" \"C:/Users/jacks/Projects/learn-python-ai/8_send_email/project/monday_report.py\" --test"
```

- `/SC WEEKLY /D MON /ST 09:00` = weekly, Mondays, 09:00.
- `/TR` is the command to run; the escaped inner quotes `\"` are only strictly
  needed for paths with spaces — this path has none, but they do no harm.

Inspect or delete it later:

```powershell
schtasks /Query /TN "Monday Sales Report"
schtasks /Delete /TN "Monday Sales Report" /F
```

---

## The gotchas (Windows edition)

- **Quote every path with spaces** — unquoted paths with spaces are the #1
  reason a task "runs" but does nothing. This project's path
  (`C:/Users/jacks/Projects/learn-python-ai`) has no spaces, so quoting is
  belt-and-suspenders here — but keep the habit.
- **Set "Start in"** to the script's folder so the report's default output file
  (`monthly_report.xlsx`) is written there. Leave it blank and Task Scheduler runs
  from `C:\Windows\System32`, so the `.xlsx` lands there instead of your project.
  (Your `.env` is *not* affected — the code loads it from beside the script via
  `Path(__file__)`, so it's found no matter what the working directory is.)
- **The PC must be awake.** By default Task Scheduler won't wake a sleeping
  machine. In the task's **Properties → Conditions**, tick **"Wake the computer
  to run this task"** if you want it to fire from sleep. On **Properties →
  Settings**, tick **"Run task as soon as possible after a scheduled start is
  missed"** so a report skipped while the PC was off runs at next boot.
- **Timezone:** Task Scheduler fires at 9:00 in **your PC's local time**. If your
  *code* mixes in naive UTC datetimes (Bug Hunt #11), the two notions of "9 AM"
  drift apart. Keep datetimes timezone-aware.
- **Run whether logged in or not:** in the task's **General** tab, choose
  **"Run whether user is logged on or not"** — but then it can't show windows and
  will prompt to store your Windows password. For a headless report that's fine.
- **Read the result:** the **History** tab and the **Last Run Result** column
  (`0x0` means success) tell you what happened. As with cron, add
  `>> "%USERPROFILE%\monday_report.log" 2>&1` to the arguments if you want a log
  file — though on Windows a wrapper `.bat` is the cleaner way to redirect.

---

**The honest limitation** (Section 2 callback): Task Scheduler runs *your PC on
your schedule*. If the machine is off Monday morning, nothing sends (unless you
enabled wake/catch-up above). When you need a report that fires even with your PC
shut, move it to something always-on — a cheap cloud VM or **GitHub Actions**,
which schedules with cron syntax and runs in **UTC**. See the README's
cloud-alternatives note.
