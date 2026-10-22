"""
Expense splitter for a group trip.

Edit the PEOPLE and EXPENSES lists below, then run this file with:
    python3 expense_splitter.py
"""

# ---------------------------------------------------------------------------
# DATA — edit these two lists for your own trip.
# ---------------------------------------------------------------------------

PEOPLE = ["Alice", "Bob", "Carol", "Dave"] #len(PEOPLE)=4

EXPENSES = [
    {"payer": "Alice", "amount": 480.00, "description": "Cabin rental"},
    {"payer": "Bob",   "amount": 150.00, "description": "Groceries"},
    {"payer": "Carol", "amount": 75.00,  "description": "Gas"},
    # Dave paid for nothing this trip, but he still owes his share.
]


# ---------------------------------------------------------------------------
# MONEY HELPERS
#
# We do all the math in integer CENTS instead of dollar floats. Floats can't
# represent numbers like 0.10 exactly, so repeated addition/subtraction of
# dollar amounts can drift by fractions of a cent. Cents (whole numbers) add
# and subtract exactly, so balances are guaranteed to sum to zero. We only
# convert back to dollars when we print something.
# ---------------------------------------------------------------------------

def to_cents(dollars):
    """Convert a dollar amount (e.g. 176.25) to whole cents (17625)."""
    return round(dollars * 100)


def to_dollar_string(cents):
    """Format a cent amount back into a '$X.XX' string for display."""
    return f"${cents / 100:.2f}"


# ---------------------------------------------------------------------------
# CORE CALCULATIONS
# ---------------------------------------------------------------------------

def total_spent_cents(expenses):
    """Sum of every expense, in cents."""
    '''
    EXPENSES = [
    {"payer": "Alice", "amount": 480.00, "description": "Cabin rental"},
    {"payer": "Bob",   "amount": 150.00, "description": "Groceries"},
    {"payer": "Carol", "amount": 75.00,  "description": "Gas"},
    # Dave paid for nothing this trip, but he still owes his share.
]
    '''
    return sum(to_cents(expense["amount"]) for expense in expenses)
    #sum = 48000+15000+7500 = 70500


def amount_paid_by(person, expenses):
    """How much one person paid in total, in cents."""
    '''
    EXPENSES = [
    {"payer": "Alice", "amount": 480.00, "description": "Cabin rental"},
    {"payer": "Bob",   "amount": 150.00, "description": "Groceries"},
    {"payer": "Carol", "amount": 75.00,  "description": "Gas"},
       if ---> {"payer": "Alice", "amount": 17.00,  "description": "food"},
    # Dave paid for nothing this trip, but he still owes his share.
]
    '''
    return sum(
        to_cents(expense["amount"])
        for expense in expenses
        if expense["payer"] == person
    )
    #person - Alice , Sum = 48000 + 1700 = 49700


def fair_shares_cents(people, total_cents):
    """
    Split total_cents equally among people, in cents.

    Plain integer division (total // count) can leave a few cents left
    over — e.g. $10.00 among 3 people is $3.33 each with 1 cent unspent.
    We hand that leftover cent (or two) to the first few people so the
    shares still add up to exactly total_cents. This keeps every balance
    exact instead of off by a fraction of a cent.
    """
    base_share, leftover_cents = divmod(total_cents, len(people)) #70500 , 4 
    #70500//4 = 17625,  base_share = 17625
    # 70500%4 = 0 ,leftover_cents = 0
    #divmod(17, 5) returns a tuple (3,2) because 17 // 5 is 3 and 17 % 5 is 2
    #a,b = divmod(17, 5) #a=3,b=2 17 divided 5 = 3 and remainder of 2

    #10000//3 = 3333 = base_share
    #10000%3 = 1 =leftover_cents

    shares = {}
    for index, person in enumerate(people):
        #['a','b','c']
        #0,'a'
        #1,'b'
        #2,'c'
        #index =0 , leftover_cents =1
        extra_cent = 1 if index < leftover_cents else 0
        shares[person] = base_share + extra_cent
        #{'a':3334,'b':3333,'c':3333}
    return shares
    #{"Alice": 17625, "Bob": 17625, "Carol": 17625, "Dave": 17625}


def compute_balances(people, expenses):
    """
    Each person's balance, in cents.

    Positive balance = they paid more than their share, the group owes them.
    Negative balance = they paid less than their share, they owe the group.
    """
    total_cents = total_spent_cents(expenses) #70500
    shares = fair_shares_cents(people, total_cents) #{"Alice": 17625, "Bob": 17625, "Carol": 17625, "Dave": 17625}

    balances = {}
    #PEOPLE = ["Alice", "Bob", "Carol", "Dave"]
    for person in people:
        paid = amount_paid_by(person, expenses)#alice 48000
        balances[person] = paid - shares[person]
    return balances
    #{"Alice":30375, "Bob": -2625, "Carol": -10125, "Dave": -17625}
    #15000 - 17625 = -2625
    #7500 - 17625 = -10125


# ---------------------------------------------------------------------------
# SETTLEMENT (who pays whom)
# ---------------------------------------------------------------------------

def compute_transfers(balances):
    """
    Turn a dict of {person: balance_cents} into a short list of transfers
    that settles all debts.

    Greedy approach: repeatedly match the person owed the MOST money with
    the person who owes the MOST money, transfer as much as possible
    between them, and repeat. This keeps the number of transfers small
    (though not always the mathematical minimum — that's a harder problem
    and not worth the complexity here).
    """
    # Split into two lists we can freely edit: debtors owe money (negative
    # balance), creditors are owed money (positive balance). People with a
    # zero balance are already settled and don't need to appear here.
    #{"Alice":30375, "Bob": -2625, "Carol": -9125, "Dave": -17625}
    debtors = [[person, -amount] for person, amount in balances.items() if amount < 0]
    creditors = [[person, amount] for person, amount in balances.items() if amount > 0]
    #debtors = [['Bob', 2625], ['Carol', 9125],['Dave', 17625]]
    #creditors = [['Alice', 30375]]
    debtors.sort(key=lambda pair: pair[1], reverse=True)
    #reverse=True -> descending order
    #debtors = [['Dave', 17625], ['Carol', 9125], ['Bob', 2625]]
    #sort by the amount owed (pair[1])
    creditors.sort(key=lambda pair: pair[1], reverse=True)
    #creditors = [['Alice', 30375]]

    transfers = []
    debtor_index = 0
    creditor_index = 0
    #len(debtors) = 3
    #len(creditors)= 1
    while debtor_index < len(debtors) and creditor_index < len(creditors):
        #debtor_index=0, creditor_index=0
        #debtor_index=1, creditor_index=0
        #debtors = [['Dave', 0], ['Carol', 10125], ['Bob', 2625]]
        #creditors = [['Alice', 12750]]
        debtor_name, debtor_owes = debtors[debtor_index]#['Dave', 17625]
        #debtor_name ='Dave'
        # debtor_owes=17625
        creditor_name, creditor_owed = creditors[creditor_index]
        #creditor_name = 'Alice'
        #creditor_owed = 30375

        payment = min(debtor_owes, creditor_owed)#17625
        transfers.append((debtor_name, creditor_name, payment))
        #[('Dave', 'Alice', 17625),('Carol', 'Alice', 10125),('Bob', 'Alice', 2625)]

        debtors[debtor_index][1] -= payment #debtors[debtor_index][1] = debtors[debtor_index][1] - payment
        #[['Dave', 0], ['Carol', 10125], ['Bob', 2625]]
        creditors[creditor_index][1] -= payment
        #creditors = [['Alice', 12750]]
        #creditors = [['Alice', 2625]]

        # Move on once a person's balance is fully settled.
        if debtors[debtor_index][1] == 0:
            debtor_index += 1
            #debtor_index = 1
        if creditors[creditor_index][1] == 0:
            creditor_index += 1
            #creditor_index =0 

    return transfers
    #[('Dave', 'Alice', 17625),('Carol', 'Alice', 10125),('Bob', 'Alice', 2625)]


# ---------------------------------------------------------------------------
# REPORTING
# ---------------------------------------------------------------------------

def print_report(people, expenses):
    total_cents = total_spent_cents(expenses) #70500
    average_share_cents = total_cents / len(people)  # for display only 70500/4 = 17625.0
    balances = compute_balances(people, expenses)#{"Alice":30375, "Bob": -2625, "Carol": -10125, "Dave": -17625}
    transfers = compute_transfers(balances)#[('Dave', 'Alice', 17625),('Carol', 'Alice', 10125),('Bob', 'Alice', 2625)]

    print("=== Expenses ===")
    for expense in expenses:
        print(f"  {expense['payer']:<10} paid {to_dollar_string(to_cents(expense['amount'])):>8}  "
              f"for {expense['description']}")

    print(f"\nTotal spent: {to_dollar_string(total_cents)}")
    print(f"Fair share per person (~{len(people)} people): "
          f"${average_share_cents / 100:.2f}")

    print("\n=== Balances ===")
    for person in people:
        #["Alice", "Bob", "Carol", "Dave"]
        ##{"Alice":30375, "Bob": -2625, "Carol": -10125, "Dave": -17625}
        balance = balances[person]
        if balance > 0:
            print(f"  {person:<10} is owed {to_dollar_string(balance)}")
        elif balance < 0:
            print(f"  {person:<10} owes    {to_dollar_string(-balance)}")
        else:
            print(f"  {person:<10} is settled up")

    print("\n=== Settlement plan ===")
    if not transfers:
        print("  Everyone is already settled up!")
    else:
        ##[('Dave', 'Alice', 17625),('Carol', 'Alice', 10125),('Bob', 'Alice', 2625)]
        for debtor, creditor, amount in transfers:
            print(f"  {debtor} pays {creditor} {to_dollar_string(amount)}")

    # Sanity check: balances should always sum to (within a cent of) zero.
    assert abs(sum(balances.values())) <= 1, "Balances don't add up — check the data!"


if __name__ == "__main__":
    print_report(PEOPLE, EXPENSES)