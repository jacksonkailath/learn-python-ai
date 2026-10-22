"""Lecture 2 & 3 companion — numbers, strings, booleans, and f-strings.

The point is READING fluency: after this script, every f-string in
AI output should look like a sentence with labeled blanks in it.
"""


def main():
    # --- The big three types you'll actually see -------------------
    units = 250              # int  — counting things
    unit_price = 19.99       # float — measuring things
    product = "Widget Pro"   # str  — text, always in quotes
    in_stock = True          # bool — yes/no answers

    print(type(units), type(unit_price), type(product), type(in_stock))

    # Division ALWAYS produces a float, even when it divides evenly.
    print(10 / 2)            # 5.0  (not 5)

    # The quotes are the costume that makes something a string.
    print(5 + 5)             # 10       -- math
    print("5" + "5")         # 55       -- gluing text together
    #print("5" + 5)         # <- uncomment: TypeError. Bug Hunt #2 lives here.

    # --- Building text: the old way vs the f-string way ------------
    old_way = "Product: " + product + ", price: $" + str(unit_price)
    new_way = f"Product: {product}, price: ${unit_price}"
    print(old_way)
    print(new_way)

    # Anything inside {} is evaluated — even math and method calls.
    print(f"Total value: ${units * unit_price}")
    print(f"Shouting: {product.upper()}!")

    # --- Format specs: the part after the colon ---------------------
    pct = 12 / 16 * 100
    print(f"Raw:      {pct}")        # 75.0
    print(f"1 decimal: {pct:.1f}%")  # 75.0%
    print(f"No decimals: {pct:.0f}%")
    print(f"Big number: {1234567:,}")     # commas: 1,234,567
    print(f"[{product:>20}]")             # right-align in 20 chars
    print(f"[{product:<20}]")             # left-align in 20 chars


if __name__ == "__main__":
    main()
