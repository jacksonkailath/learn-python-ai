"""Exercise 4-P1 solution — Merge, don't discard.

Run me:  python project/solutions/exercise_4_p1_merge_fields.py

The change: when a duplicate turns up, the losing record no longer
vanishes. Any field the champion has EMPTY gets filled from the loser.
Champion-picking stays exactly as it was; only what happens to the loser
changes.

Every touched line is marked # CHANGED. Only deduplicate() moved —
normalize_email(), completeness(), and print_report() are byte-for-byte
the same as the draft. If your version had to edit any of those, stop
and ask why: the requirement was about what happens to duplicates, and
duplicates are only ever handled in one place.

Expected difference from the draft: exactly one person gains a field.
Ana's two records had 3/4 fields each (one with a company, one with a
phone); the draft kept the first and lost the phone. Merged, Ana is 4/4.
Everyone else is unchanged, because their losing records held nothing
the champion lacked.
"""

# ── The data: a list of dicts, one record per exported contact ──────────
# Every record has the same four labels. Missing info is an empty string.
RAW_CONTACTS = [
    {"name": "Ana Flores", "email": "ana.flores@example.com", "phone": "", "company": "Brightpath"},
    {"name": "Ana Flores", "email": " Ana.Flores@Example.com ", "phone": "555-0101", "company": ""},
    {"name": "Ben Okafor", "email": "ben@example.com", "phone": "555-0102", "company": ""},
    {"name": "B. Okafor", "email": "BEN@EXAMPLE.COM", "phone": "", "company": ""},
    {"name": "Carol Mendes", "email": "carol.m@example.com", "phone": "555-0103", "company": "Brightpath"},
    {"name": "Dev Patel", "email": "dev.patel@example.com", "phone": "", "company": "Kite Labs"},
    {"name": "Dev Patel", "email": "dev.patel@example.com ", "phone": "555-0104", "company": "Kite Labs"},
    {"name": "Elena Sosa", "email": "elena@example.com", "phone": "", "company": ""},
]


def normalize_email(email: str) -> str:
    """Turn every spelling of an email into one canonical form.

    ' Ana.Flores@Example.com ' and 'ana.flores@example.com' are the same
    address — email is case-insensitive, and stray spaces are export noise.
    """
    return email.strip().lower()


def completeness(contact: dict[str, str]) -> int:
    """Score a record by how many fields are actually filled in."""
    return sum(1 for value in contact.values() if value.strip())


def deduplicate(contacts: list[dict[str, str]]) -> list[dict[str, str]]:
    """Return one record per unique email, merging duplicates' fields.

    The most complete record is still the champion; but any field it has
    empty is filled from the other records for the same email.      # CHANGED
    """
    best_by_email: dict[str, dict[str, str]] = {}

    for contact in contacts:
        key = normalize_email(contact["email"])
        current_best = best_by_email.get(key)          # None if first sighting
        #best_by_email= {email:{contact}}
        if current_best is None:                                        # CHANGED
            best_by_email[key] = dict(contact)   # our own copy to fill in  # CHANGED
            #{key: dict(contact)}
            #contact is already a dict, but we want to make a copy so we can modify it without affecting # CHANGED
            # the original records.  
            continue                                                    # CHANGED
            #skip the rest of the loop body, go to the next contact

        # Decide who is the champion and who is the donor.               # CHANGED
        if completeness(contact) > completeness(current_best):          # CHANGED
            champion, donor = dict(contact), current_best               # CHANGED
            #a,b = 1,2             
        else:                                                           # CHANGED
            champion, donor = current_best, contact                     # CHANGED

        # Fill every empty field of the champion from the donor.         # CHANGED
        for field, value in donor.items():                              # CHANGED
            if not champion[field].strip() and value.strip():           # CHANGED
                #champion does not have this field filled, but donor does, so fill it in.
                champion[field] = value                                 # CHANGED

        best_by_email[key] = champion                                   # CHANGED
        #donor = {1:"", 2:"dasdas",3:"",4:"dsadasd"}
        #champion = {1:"dsadasd", 2:"dasdas",3:"dasdasd",4:"dsadasd"}

        #best_by_email= {email:{champion}}

    return list(best_by_email.values()) 
    #[{..},{..}]


def print_report(raw: list[dict[str, str]], deduped: list[dict[str, str]]) -> None:
    """Print the raw list, then the deduplicated list with a field count."""
    print(f"Raw contact list: {len(raw)} records")
    for c in raw:
        print(f"  {c['name']:<14} {c['email']!r}")

    print(f"\nAfter deduplication: {len(deduped)} unique people")
    for c in deduped:
        filled = completeness(c)
        print(f"  {c['name']:<14} {normalize_email(c['email']):<26} "
              f"phone={c['phone'] or '—':<9} company={c['company'] or '—':<11} "
              f"({filled}/4 fields)")


def main() -> None:
    deduped = deduplicate(RAW_CONTACTS)
    print_report(RAW_CONTACTS, deduped)


if __name__ == "__main__":
    main()
