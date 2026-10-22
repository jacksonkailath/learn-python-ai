"""Mini-project #2 — Contact Deduplicator (AI-drafted).

Run me:  python project/contact_deduplicator.py

Contacts were exported from three places (phone, mail client, CRM) and
merged into one list. The same person appears more than once, with the
email typed differently and with different fields filled in.

Goal: one record per person. When duplicates disagree, keep the most
COMPLETE record (the one with the most non-empty fields).

This is a representative draft from one AI session — yours will differ
in small ways. That is normal; the reading skill is the same.
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
    """Return one record per unique email, keeping the most complete one."""
    best_by_email: dict[str, dict[str, str]] = {}

    for contact in contacts:
        key = normalize_email(contact["email"])
        current_best = best_by_email.get(key)          # None if first sighting

        if current_best is None or completeness(contact) > completeness(current_best):
            best_by_email[key] = contact

    return list(best_by_email.values())


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
