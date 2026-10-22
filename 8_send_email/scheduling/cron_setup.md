# Scheduling on macOS & Linux with `cron`

Goal: run `monday_report.py` **every Monday at 9:00 AM**, automatically, whether
or not you're at the keyboard — as long as your machine is awake.

`cron` is a scheduler built into every Mac and Linux box. It reads a list of
"run THIS command at THIS time" lines (crontab) and fires them. That's the
whole idea.

---

## 1. Find the two absolute paths you need

cron runs with a bare-bones environment: no virtualenv activated, no "current
folder", almost no `PATH`. So you give it **absolute paths** to (a) the Python
inside your project's venv and (b) the script.

```bash
# the venv Python (NOT plain `python` — that's the system one, without your packages)
cd ~/Documents/Projects/learn-python-ai
echo "$(pwd)/.venv/bin/python"
# -> /Users/you/Documents/Projects/learn-python-ai/.venv/bin/python

Explanation:
1. echo — prints whatever you give it to the terminal. That's it. echo hello outputs hello.
2. $ — starts an expansion: "don't treat what follows as literal text, substitute something in."
3. $(...) doesn't look up a stored value; it runs whatever is inside and substitutes the output.
4. pwd	Runs the command, prints the directory
5. if we had typed $pwd	: Looks up a variable named pwd — almost certainly empty
6. $(pwd)	Runs the command pwd, captures its output, pastes it in place

echo "$(pwd)/8_send_email/project/monday_report.py"
# -> /Users/you/.../8_send_email/project/monday_report.py
```

Using the venv's Python means all your packages (openpyxl, python-dotenv…) are
already there — no activation needed. That's the single most common cron mistake
with Python, sidestepped.

## 2. Test the exact command first, by hand

Before scheduling anything, prove the fully-qualified command works from a plain
shell. Paste your two absolute paths in and run it with `--test`:

```bash
/Users/you/.../.venv/bin/python \
  /Users/you/.../8_send_email/project/monday_report.py --test
```

If that emails you the report, cron will too. If it errors, fix it now — you
never want to debug through cron.

## 3. Edit your crontab

```bash
crontab -e     # opens your personal schedule in $EDITOR (vim by default)
```

Explanation:

1. crontab — the tool for managing cron jobs: commands you want the system to run automatically on a schedule. Cron is a background daemon that wakes up every minute and checks whether anything is due.

Background — the process isn't attached to your terminal. You're not waiting on it, it isn't printing to your screen, and closing your terminal window doesn't kill it. Contrast with a foreground process: when you run python script.py and your prompt hangs until it finishes, that's foreground.

Daemon — a specific kind of background process: one that starts at boot (or on demand), runs indefinitely, and exists to provide a service rather than to do one job and exit. It has no user interface. It just sits there waiting for something to happen.

2. -e — the "edit" flag. 3. Other flags you'll see:
   crontab -l — list your current jobs (just prints them, doesn't open an editor)
   crontab -r — remove all your jobs (dangerous, no confirmation prompt)
   crontab -e — open them for editing

Add one line (all on ONE line), then save and quit:

vi - a text editor that runs inside the terminal.

Press i to be able to type.
i — enters insert mode.
Press Esc — back to normal mode.
Type :wq + Enter — saves and installs.
Esc then :q! to bail out with nothing saved, and start over. Nothing is committed until :wq.

```cron
0 9 * * 1 /Users/you/.../.venv/bin/python /Users/you/.../8_send_email/project/monday_report.py --test >> /Users/you/monday_report.log 2>&1
```

then save and quit - Esc + :wq

Explanation:
<schedule><command><redirection>

Schedule:

5 positions: 1 2 3 4 5

1.minute
2.hour
3.day of month - `*` means any
4.month - `*` means any
5.day of week

Command:<which python> <which file> --test
which python: absolute path to the interpreter inside the virtualenv. This is the activation.
which file: absolute path to the script. Cron's working directory is your home, not the project folder, so a relative path here would fail.

Redirection:

- `>>` — append stdout to a file. (Single > would overwrite each run; >> accumulates.)
- /Users/you/monday_report.log is a file path — where it goes.
  - /Users/you/ is the home directory on macOS (the Linux equivalent would be /home/you/)
- 2>&1 — "send stream 2 to wherever stream 1 is currently going."
  - The numbers are file descriptors: 0 is stdin, 1 is stdout, 2 is stderr. By default only stdout gets redirected by >>, so errors and tracebacks would vanish. 2>&1 folds stderr into the same file.

Confirm it registered:

```bash
crontab -l     # list your scheduled jobs
```

## 4. Read the five stars

Every cron line starts with five time fields, then the command:

```
┌───────────── minute        (0 - 59)
│ ┌───────────── hour        (0 - 23, 24-hour clock)
│ │ ┌───────────── day of month (1 - 31)
│ │ │ ┌───────────── month     (1 - 12)
│ │ │ │ ┌───────────── day of week (0 - 6, Sunday = 0, Monday = 1)
│ │ │ │ │
0 9 * * 1   <command>
```

`0 9 * * 1` reads: _minute 0, hour 9, any day-of-month, any month, day-of-week 1
(Monday)_ → **09:00 every Monday**. A `*` means "every". Handy variations:

| When                   | cron           | Reading    |
| ---------------------- | -------------- | ---------- |
| Every Monday 9:00 AM   | `0 9 * * 1`    | our report |
| Every weekday 8:30 AM  | `30 8 * * 1-5` | Mon–Fri    |
| Every day at midnight  | `0 0 * * *`    | nightly    |
| Every 15 minutes       | `*/15 * * * *` | testing    |
| 1st of the month, 6 AM | `0 6 1 * *`    | monthly    |

Not sure a line is right? Paste it into **crontab.guru** — it translates cron to
English (verify, don't trust).

## 5. The gotchas (each has bitten everyone once)

- **`cron` uses your machine's local timezone.** `0 9 * * 1` fires at 9 AM
  _however your Mac's clock is set_. This is exactly the trap in Bug Hunt #11:
  if your **code** builds times with naive `datetime.utcnow()`, cron's 9 AM local
  and your code's "9 AM" can disagree. Keep datetimes timezone-aware.
- **The machine must be awake.** Classic `cron` does **not** wake a sleeping Mac
  or run a missed job on resume. If your laptop naps at 9 AM Monday, the job is
  simply skipped. (See "macOS: the better tool" below.)
- **Always redirect output to a log** (`>> file.log 2>&1`). cron mails output to
  a local mailbox nobody reads; a log file is how you find out what happened.
- **No venv activation, no relative paths.** Absolute paths only (Step 1).
- **macOS permissions:** the first time cron touches your files, macOS may need
  you to grant **Full Disk Access** to `/usr/sbin/cron` in System Settings →
  Privacy & Security. If the job runs but can't read files, this is why.

## 6. macOS: the better native tool (`launchd`)

On modern macOS, Apple's own scheduler is **`launchd`**, and unlike `cron` it
can run a job you missed while the Mac was asleep (`StartCalendarInterval` with
the machine waking or catching up). If "my laptop was closed at 9 AM Monday" is a
real problem for you, graduate from `cron` to a launchd **`.plist`** in
`~/Library/LaunchAgents/`. `cron` still works on macOS and is fine for learning;
just know `launchd` exists for when reliability matters.

## 7. Remove or change the job

```bash
crontab -e     # edit the line (or delete it), save, quit
crontab -r     # nuclear option: removes ALL your cron jobs — careful
```

---

**The honest limitation**: all of this runs
_your machine on your schedule_. If the Mac is off, nothing fires. When you need
a report that sends even with your laptop shut, you move the job to something
that's always on — a cheap VPS, or **GitHub Actions** (whose YAML uses the very
same five-star cron syntax, and always runs in **UTC** — timezone-awareness
again). See the README's cloud-alternatives note.
