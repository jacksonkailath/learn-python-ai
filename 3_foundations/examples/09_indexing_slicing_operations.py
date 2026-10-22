"""Indexing, slicing, and the operations you'll see constantly.

Run me:  python examples/09_indexing_slicing_operations.py

The 90% you will actually meet in AI-drafted automation code:
  list:  items[0], items[-1], items[1:4], .append(), item in items, len()
  dict:  d["key"], d.get("key"), "key" in d, .items()
"""


def main() -> None:
    months = ["jan", "feb", "mar", "apr", "may", "jun"]
    #           0      1      2      3      4      5

    # ── Indexing: one item, by position ──────────────────────────────────
    print("INDEXING")
    print(f"  months[0]  -> {months[0]}    (first — Python counts from 0)")
    print(f"  months[2]  -> {months[2]}    (third)")
    print(f"  months[-1] -> {months[-1]}    (last)")
    print(f"  months[-2] -> {months[-2]}    (second-to-last)")

    # ── Slicing: a sub-list, by range. [start:stop] — stop is EXCLUDED. ──
    print("\nSLICING  months[start:stop] — stop is not included")
    print(f"  months[1:4]  -> {months[1:4]}   (positions 1, 2, 3)")
    print(f"  months[:3]   -> {months[:3]}   (from the start)")
    print(f"  months[3:]   -> {months[3:]}   (to the end)")
    print(f"  months[:]    -> {months[:]}  (the whole thing — a COPY)")
    #m = months[:] 
    # ── The list verbs you'll read every day ─────────────────────────────
    print("\nLIST OPERATIONS")
    tasks = ["backup", "rename"]
    tasks.append("upload")                 # add to the end (in place!)
    print(f"  .append('upload')    -> {tasks}")
    tasks.remove("rename")                 # remove by VALUE, first match
    print(f"  .remove('rename')    -> {tasks}")
    print(f"  'backup' in tasks    -> {'backup' in tasks}")
    print(f"  'delete' in tasks    -> {'delete' in tasks}")
    print(f"  len(tasks)           -> {len(tasks)}") #len()
    print(f"  sorted(tasks)        -> {sorted(tasks)}   (returns a NEW list)") #sorted()

    for task in tasks:
        print(f"    task: {task}")

    # ── The dict verbs — .get() is the safety-conscious lookup ───────────
    print("\nDICT OPERATIONS")
    contact = {"name": "Ana Flores", "email": "ana@example.com"}

    print(f"  contact['name']          -> {contact['name']}")
    # contact["phone"] would CRASH with KeyError — the key doesn't exist.
    # .get() returns None (or your fallback) instead of crashing:
    #contact.get('name')
    print(f"  contact.get('phone')     -> {contact.get('phone')}")
    #print(f"  contact.get('phone')     -> {contact['phone']}")
    print(f"  contact.get('phone', '') -> {contact.get('phone', 'fallback')!r}  (fallback)")
    print(f"  'email' in contact       -> {'email' in contact}   (checks KEYS)")

    # .items() gives (key, value) pairs — THE dict-looping pattern:
    print("  looping with .items():")
    #print(contact.items())
    for key, value in contact.items():
        print(f"    {key:>6} = {value}")


if __name__ == "__main__":
    main()
