"""A tiny temperature-converter module -- the code under test in the pytest lecture.

Deliberately small: two pure functions, no I/O. That's the easiest kind of
code to test, which is why refactoring logic INTO functions like these makes
your automations testable.
"""


def c_to_f(celsius: float) -> float:
    """Convert Celsius to Fahrenheit."""
    return celsius * 9 / 5 + 32


def f_to_c(fahrenheit: float) -> float:
    """Convert Fahrenheit to Celsius."""
    return (fahrenheit - 32) * 5 / 9
