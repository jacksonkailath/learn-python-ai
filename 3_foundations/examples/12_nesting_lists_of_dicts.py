"""Nesting: lists of dicts, the shape of real data.

Run me:  python examples/12_nesting_lists_of_dicts.py

Almost every dataset you'll automate against — API responses, CSV rows,
exported contacts, expense reports — has the same shape:

    a LIST of records, where each record is a DICT of named fields.

Learn to see that shape and half of every AI-drafted script becomes readable.
"""

import json
#loads Python's built-in json module, which converts between Python objects and JSON text.


def main() -> None:
    # ── The shape, in Python ─────────────────────────────────────────────
    orders = [                                     # list  = "many orders"
        {                                          # dict  = "one order"
            "id": 1001,
            "customer": "Ana Flores",
            "total": 42.50,
            "items": ["notebook", "pen"],          # a list INSIDE the dict
        },
        {
            "id": 1002,
            "customer": "Ben Okafor",
            "total": 18.00,
            "items": ["stapler"],
        },
        {
            "id": 1003,
            "customer": "Ana Flores",
            "total": 96.40,
            "items": ["desk lamp", "cable", "mouse"],
        },
    ]
#len(list)
    # ── The same data as JSON — notice it is nearly identical ────────────
    # JSON is just this structure written down as text. 
    #   json.dumps(obj)  -> Python object to JSON text   (used below)
    #   json.loads(text) -> JSON text back to the Python shape above
    
    as_json = json.dumps(orders[:1], indent=2)
    '''
    orders = [                                     # list  = "many orders"
            {                                          # dict  = "one order"
                "id": 1001,
                "customer": "Ana Flores",
                "total": 42.50,
                "items": ["notebook", "pen"],          # a list INSIDE the dict
            }
            ]
    '''
    #Saving data to a file. / Sending data to an API / Writing a record into a log line as text.  All of these are JSON.
    #your structure has to become text to go anywhere; JSON is the text everyone agreed on.
    #json is a string. json is how you send and receive data from an api. 
    print("One order, as JSON (what the API sends):")
    print(as_json)

    # ── Navigating: read the brackets from left to right ─────────────────
    print("\nNavigation — one hop per bracket:")
    print(f"  orders[0]                 -> the first order (a dict)")
    print(f"  orders[0]['customer']     -> {orders[0]['customer']}")
    '''
    {                                          # dict  = "one order"
                "id": 1001,
                "customer": "Ana Flores",
                "total": 42.50,
                "items": ["notebook", "pen"],          # a list INSIDE the dict
            },
    '''
    print(f"  orders[2]['items']        -> {orders[2]['items']}")
    print(f"  orders[2]['items'][0]     -> {orders[2]['items'][0]}")

    # ── The universal processing pattern: loop over records ──────────────
    print("\nEvery report script ever written:")
    grand_total = 0.0
    for order in orders:                  # each 'order' is ONE dict
        grand_total += order["total"] #grand_total = grand_total + order["total"]
        print(f"  #{order['id']}  {order['customer']:<12} "
              f"${order['total']:>6.2f}  ({len(order['items'])} items)")
    print(f"  grand total: ${grand_total:.2f}")

    # ── Grouping: build a dict OF lists from a list of dicts ─────────────
    # "totals per customer" — the second-most-common pattern you'll read.
    per_customer: dict[str, float] = {}
    for order in orders:
        name = order["customer"]
        per_customer[name] = per_customer.get(name, 0.0) + order["total"] #42.5 + 96.40 = 138.9
    #{"Ana Flores":138.9,"Ben Okafor":18}    

    print("\nPer-customer totals (a dict built from the list):")
    for name, total in per_customer.items():
        print(f"  {name:<12} ${total:.2f}")


if __name__ == "__main__":
    main()
