"""Lecture 4 & 5 companion — functions as machines.

Every function is a machine: stuff goes in (arguments), stuff comes
out (return value), and sometimes the room changes (side effects).
"""


def completion_rate(done, total):
    """A pure machine: input -> output, touches nothing else."""
    return done / total * 100


def greet(name, punctuation="!"):
    """A machine with a default setting you can override."""
    return f"Hello, {name}{punctuation}"


def announce(message):
    """A side-effect machine: returns nothing, changes the screen."""
    print(f">>> {message}")


def main():
    # DEFINING a machine builds it. CALLING it (with parentheses)
    # actually switches it on.
    rate = completion_rate(12, 16)
    print(rate)                      # 75.0

    # Positional arguments: matched by ORDER.
    print(completion_rate(3, 4))     # 75.0

    # Keyword arguments: matched by NAME — order stops mattering.
    print(completion_rate(total=4, done=3))   # still 75.0

    # Defaults: leave the dial alone, or turn it.
    print(greet("Sam"))              # Hello, Sam!
    print(greet("Sam", "?"))         # Hello, Sam?

    # return vs print: announce() PRINTS but returns None.
    result = announce("Deploy finished")
    print(result)                    # None -- nothing came OUT of the machine

    # A function you never call never runs. This is just the machine
    # sitting on the workbench:
    completion_rate                  # no parentheses -> nothing happens
    print("(that line above did nothing — no parentheses, no call)")


if __name__ == "__main__":
    main()
