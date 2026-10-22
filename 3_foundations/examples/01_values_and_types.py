"""Lecture 1 companion — values, types, and variables.

Run me, then read me. Every print() below matches a diagram
in the Section 3 README ("names point to things").
"""


def main():
    # A value is created, then a name is stuck onto it.
    tasks_done = 12
    print(tasks_done)          # 12
    print(type(tasks_done))    # <class 'int'>

    # The TYPE lives with the VALUE, not with the name.
    # Reassigning moves the sticky note to a new value.
    tasks_done = "twelve"
    print(tasks_done)          # twelve
    print(type(tasks_done))    # <class 'str'>  -- same name, new value

    # Two names can point at the SAME value.
    score = 75
    backup = score
    print(score, backup)       # 75 75

    # Reassigning one name does NOT drag the other along.
    score = 80
    print(score, backup)       # 80 75

    # Names are case-sensitive and must exist before you use them.
    team_name = "Data Platform"
    print(team_name)
    #print(Team_Name)  # <- uncomment: NameError, Python has never
    #                        heard of this name. Names are exact.


if __name__ == "__main__":
    main()

