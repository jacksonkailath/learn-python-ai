# Reading check — trace the program in question order

These questions follow the **order the program actually runs**, top to bottom.
If you can answer them in sequence, you are not just reading the code — you are
tracing it, the way the Python interpreter does.

How to use this: open `contact_deduplicator.py`, answer on paper or in a scratch
file, **then** check the Answers section at the bottom. No AI, no peeking mid-way.
Nobody grades this — it exists so _you_ know whether the reading skill has landed.

---

## Stage 0 — Loading the file (before anything "runs")

**Q1.** When Python reads this file top to bottom, which things are _executed_
and which are only _defined_? What has actually happened by the time Python
reaches line 77?

**Q2.** Sketch the shape of `RAW_CONTACTS`: `list[ dict{ ______ } ]`. How many
records does it hold, and how does a record say "I don't have this information"?

**Q3.** Which line actually starts the program running, and what is the
`if __name__ == "__main__":` guard for?

## Stage 1 — `main()` runs

**Q4.** `main()` is two lines. In plain English: what goes in, what comes out,
and what does it touch?

## Stage 2 — Inside `deduplicate()`, first record (Ana #1)

**Q5.** What is `best_by_email` at the moment the `for` loop starts, and what
kind of thing will it hold? (`dict{ ______ : ______ }`)

**Q6.** The first record's email is `"ana.flores@example.com"`. What does
`normalize_email` return for it, and which two string methods did the work?

**Q7.** On this first record, what does `best_by_email.get(key)` return, and
why doesn't that line crash the way `best_by_email[key]` would?

**Q8.** The condition is
`current_best is None or completeness(contact) > completeness(current_best)`.
On a first sighting, which half of the `or` settles the question — and why is
`completeness(current_best)` never called? What would happen if it were?

## Stage 3 — Second record (Ana's duplicate) — the interesting one

**Q9.** Record 2's email is `" Ana.Flores@Example.com "` — spaces, capitals and
all. Why does it land on the **same** dict key as record 1?

**Q10.** Run `completeness()` in your head on both Ana records. What integer
comes out for each, and which fields counted?

**Q11.** It's a 3-vs-3 tie. Does the champion change? Which **single character**
in the code decides that, and what tie-breaking policy does it encode?

## Stage 4 — The rest of the loop (Ben, Carol, Dev, Elena)

**Q12.** Record 4 is `"B. Okafor"` with email `"BEN@EXAMPLE.COM"`. The name
doesn't match record 3's `"Ben Okafor"` at all. Why does the script still treat
them as the same person?

**Q13.** Dev Patel appears twice (records 6 and 7). Which one ends up in
`best_by_email`, and what comparison put it there?

**Q14.** When the loop finishes, how many keys does `best_by_email` have?
What does `return list(best_by_email.values())` hand back — and what happened
to the keys?

## Stage 5 — `print_report(RAW_CONTACTS, deduped)` runs

**Q15.** Does `print_report()` change any data, or decide anything about who
survives? What is its job in one word?

**Q16.** In the raw listing, the email is printed with `{c['email']!r}`. What
does the `!r` do, and why does it matter for _this_ data in particular?

**Q17.** In the deduped listing, what does `c['phone'] or '—'` print when the
phone is an empty string, and what rule of Python makes that work?

**Q18.** What do the format specs like `:<14` and `:<26` do to the output?

## Stage 6 — The whole run

**Q19.** Without running it: how many unique people does the final report list,
and which of them show `4/4 fields`?

**Q20.** Suppose Elena also appeared with a second, _different_ address —
`"elena.sosa@gmail.com"`. What would the script do with her, and which design
decision explains it?

---

## Answers

**A1.** The docstring and the `RAW_CONTACTS` list literal are executed (the list
of 8 dicts is built in memory); the four `def` statements only _define_ the
functions — none of their bodies run. By line 77, no contact has been touched yet.

**A2.** `list[ dict{name: str, email: str, phone: str, company: str} ]` — 8
records, and missing information is an **empty string**, never a missing key.

**A3.** Line 78, `main()` — but only because line 77's guard is true when the
file is run directly. The guard means the script runs when executed but does
nothing automatically if the file is ever imported.

**A4.** Nothing goes in and nothing comes out (`None`); it calls
`deduplicate(RAW_CONTACTS)`, holds the result in `deduped`, and passes both
lists to `print_report()`, which touches the screen.

**A5.** An empty dict, `{}`. It will map normalized email → the best (most
complete) record seen so far for that email: `dict{str: dict[str, str]}`.

**A6.** `"ana.flores@example.com"` — unchanged, because it was already clean.
`.strip()` removes surrounding spaces and `.lower()` lowercases; both are
no-ops here.

**A7.** It returns `None`, because the key isn't in the dict yet. `.get()` is
the safe lookup — square brackets on a missing key would raise a `KeyError`.

**A8.** `current_best is None` is `True`, so the `or` is already settled and
Python **short-circuits**: the right half never runs. If it did run,
`completeness(None)` would crash — `None` has no `.values()`.

**A9.** Because the key is `normalize_email(contact["email"])`, not the raw
email. `.strip()` drops the spaces, `.lower()` drops the capitals, and both
records key to `"ana.flores@example.com"`.

**A10.** 3 and 3. Record 1: name, email, company (no phone). Record 2: name,
email, phone (no company). Empty strings fail the `if value.strip()` test.

**A11.** No — the champion stays record 1. The `>` (not `>=`) in the
comparison: a tie is not _strictly greater_, so **the earlier record wins**.
That's why the final Ana has a company but no phone.

**A12.** Identity is the normalized **email**, and the name is never compared.
`"BEN@EXAMPLE.COM".strip().lower()` is `"ben@example.com"` — the same key as
record 3.

**A13.** The second one (record 7). Its completeness is 4 against the first's
3, so `4 > 3` is true and it replaces the champion.

**A14.** Five keys — one per unique normalized email. `.values()` hands back
just the five champion records as a plain list; the keys were only ever needed
for identity and are dropped.

**A15.** No — it only reads and prints. Its job in one word: **presentation**.

**A16.** `!r` prints the value's `repr`, i.e. with its quotes — so
`' Ana.Flores@Example.com '` shows its stray spaces. Without it, the dirty
emails would look identical to the clean ones.

**A17.** It prints `—`. An empty string is **falsy**, so `"" or "—"` evaluates
to the fallback `"—"`; a real phone number is truthy and prints as itself.

**A18.** Left-align the value and pad it with spaces to that width (14 or 26
characters), which is what keeps the report's columns straight.

**A19.** Five people. Carol Mendes and Dev Patel show `4/4 fields` — Carol's
single record was already full, and Dev's winning record has all four filled.

**A20.** She would survive as **two** records, one per address. Identity is
email-only by design — a scope boundary the goal chose, not a bug in the code.

---
