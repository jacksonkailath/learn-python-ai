"""Lists (ordered stuff) vs dicts (labeled stuff).

Run me:  python examples/08_lists_and_dicts.py

The single question that tells you which structure you are looking at:
  "Do I care about POSITION, or do I care about NAMES?"
Position -> list.  Names -> dict.
"""


def main() -> None:
    # ── A list: ordered stuff. Position is the meaning. ──────────────────
    # "The files to process, in the order we found them."
    downloads = ["report.pdf", "photo.jpg", "notes.txt", "invoice.pdf"]
    #              0              1           2            3
    #downloads[1]
    #len(downloads)
    print("LIST — ordered stuff")
    print(f"  whole list : {downloads}")
    print(f"  first item : {downloads[0]}")      # position 0 = first
    print(f"  last item  : {downloads[-1]}")     # -1 = count from the end
    print(f"  how many   : {len(downloads)}")

    # Lists grow at the end — .append is the verb you'll see constantly.
    downloads.append("receipt.pdf")
    #downloads.append("")
    print(f"  after .append: {downloads}")

    # ── A dict: labeled stuff. The key is the meaning. ───────────────────
    # "ONE thing (a contact) described by named fields."
    contact = {
        "name": "Ana Flores",
        "email": "ana@example.com",
        "phone": "555-0101",
    }

    print("\nDICT — labeled stuff")
    print(f"  whole dict : {contact}")
    print(f"  by label   : {contact['email']}")   # you ask by NAME, not position
    #print(f"  the labels : {contact.keys()}")
    print(f"  the labels : {list(contact.keys())}")
    print(f"  the values : {list(contact.values())}")
    #contact['email']
    #contact.keys() - view into all the keys in the dict
    #list()

    # Adding a field is just assigning to a new key.
    contact["company"] = "Brightpath"
    print(f"  after adding a key: {contact}")
    #contact["country"] = "India"
    #contact["pob"]="USA"

    # ── The tell-tale signs when reading AI output ───────────────────────
    # [ ... ]  square brackets, no colons        -> list
    # { "x": ...}  curly braces WITH colons      -> dict
    # { "x", "y" } curly braces WITHOUT colons   -> set (see 10_tuples_and_sets.py)
    print("\nReading tip: [ ] = list, { key: value } = dict")
    #{} set 
    #() tuples


if __name__ == "__main__":
    main()
