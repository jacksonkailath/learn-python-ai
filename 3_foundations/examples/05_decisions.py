"""Code as decisions: if / elif / else.

Every automation eventually has to make a call: keep this file or archive it?
Retry the upload or give up? This script shows the decision structures you
will see in virtually every AI-drafted script -- and why the ORDER of the
branches matters.

Run it:
    python 05_decisions.py
"""


def triage_file(filename: str, size_mb: float) -> str:
    """Decide what to do with a file, exactly one branch wins."""
    # Python checks these conditions TOP TO BOTTOM and takes the FIRST
    # branch whose condition is True. Everything after that is skipped.
    if size_mb > 1000:
        return "flag for review (over 1 GB)"
    elif size_mb > 100:
        return "compress and archive"
    elif filename.endswith(".tmp"):
        return "delete (temporary file)"
    else:
        return "keep as-is"


def triage_file_wrong_order(filename: str, size_mb: float) -> str:
    """The SAME rules, reordered -- and now huge .tmp files never get flagged.

    This is a classic AI-draft smell: all the right conditions, wrong order.
    A 2000 MB .tmp file hits the .tmp branch first and gets 'delete' instead
    of 'flag for review'.
    """
    if filename.endswith(".tmp"):
        return "delete (temporary file)"
    elif size_mb > 1000:
        return "flag for review (over 1 GB)"
    elif size_mb > 100:
        return "compress and archive"
    else:
        return "keep as-is"


def main() -> None:
    test_files = [
        ("holiday_video.mp4", 2400.0),
        ("quarterly_report.pdf", 4.2),
        ("render_cache.tmp", 2000.0),  # huge AND temporary -- order matters!
        ("old_backup.zip", 350.0),
        ("notes.txt", 0.01),
    ]

    #[a,b,1,2,"fff"]
    #tuple - ("holiday_video.mp4", 2400.0)
    #(a,b)

    print("=== Correct branch order (most specific rule first) ===")
    for name, size in test_files:
        print(f"  {name:<22} {size:>8.2f} MB -> {triage_file(name, size)}")

    #[1,2,3,4]
    

    print()
    print("=== Same rules, wrong order ===")
    for name, size in test_files:
        decision = triage_file_wrong_order(name, size)
        print(f"  {name:<22} {size:>8.2f} MB -> {decision}")

    print()
    print("Look at render_cache.tmp: 2000 MB should be 'flag for review',")
    print("but the reordered version deletes it. Same conditions, different")
    print("order, different (and dangerous) behavior.")


if __name__ == "__main__":
    main()
