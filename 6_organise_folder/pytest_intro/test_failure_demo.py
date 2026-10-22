"""Lecture 10 -- the DELIBERATELY FAILING test. Run it ON PURPOSE.

This file exists so you can read a pytest failure report in a calm moment,
before the first time you meet one at 11pm. It is kept in its own file so
the main suite stays green -- run it explicitly:

    ../.venv/bin/python -m pytest pytest_intro/test_failure_demo.py

(The main run targets test_temperature.py by name, so this file is skipped
unless you ask for it.)

The test below asserts that 25 C is 76 F. It isn't -- 25 C is 77 F.
The CODE is right; the TEST's expectation is wrong. pytest doesn't know
which side is wrong; it only shows you the disagreement. Deciding which
side to trust is YOUR job -- remember that in Lecture 11, where an AI
writes tests that encode its own wrong assumptions.
"""

from temperature import c_to_f
#under pytest, importing from a sibling file needs no sys.path work, as long as the folder has no __init__.py.

def test_a_warm_day():
    # DELIBERATELY WRONG expectation: 25 C is actually 77.0 F.
    assert c_to_f(25) == 76.0
