"""Lecture 10 -- pytest in 30 minutes: the passing test suite.

Run from the section folder:

    ../.venv/bin/python -m pytest pytest_intro/test_temperature.py -v

pytest's rules are just naming conventions:
  - files named  test_*.py   get collected
  - functions named  test_*  get run
  - a bare  assert  is the whole assertion API

Each test here checks one FACT about temperature that is true regardless
of how the code is written -- that's what makes them good tests.
"""

import pytest
from temperature import c_to_f, f_to_c


def test_freezing_point():
    """0 degrees C is 32 degrees F -- the anchor fact everyone knows."""
    assert c_to_f(0) == 32.0


def test_boiling_point():
    """100 degrees C is 212 degrees F."""
    assert c_to_f(100) == 212.0


def test_minus_forty_is_the_same_in_both():
    """-40 is the famous crossover point where both scales agree."""
    assert c_to_f(-40) == -40.0
    assert f_to_c(-40) == -40.0


def test_body_temperature():
    """98.6 F is 37 C. Division gives floats, so compare with approx,
    never == (0.1 + 0.2 != 0.3 in floating point!)."""
    assert f_to_c(98.6) == pytest.approx(37.0)
    #Computers store floats in binary, 0.1 + 0.2 gives 0.30000000000000004.
    #approx -> How close is "close enough"? : Very close. About one part in a million.

'''
>>> (98.6 - 32) * 5 / 9
37.0

Here the result happens to come out as exactly 37.0. Why?

98.6 is actually stored as 98.599999999999994315658...
  98.6 - 32  ->  66.599999999999994...   (tiny error carried along)
  * 5        ->  333.0                   (error is too small to store, so it rounds to exactly 333.0)
  / 9        ->  37.0                    (333 / 9 is exactly 37)

So the error got rounded away this time. That won't always happen:
>>> 0.1 + 0.2
0.30000000000000004

That's why we use pytest.approx() when comparing decimal values.
'''


def test_round_trip_returns_original():
    """Converting there and back must give the number you started with.
    A 'property' test: true for ANY value, so we check several."""
    for celsius in (-273.15, -40, 0, 21.5, 100):
        assert f_to_c(c_to_f(celsius)) == pytest.approx(celsius)






