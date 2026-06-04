# List []   = mutable, most flexible
# Tuple ()  = immutable, faster
# Set {}    = mutable (add/remove), unordered,
#             NO duplicates, best for membership testing

fruits = ["apple", "banana", "Orange", "Coconut"]
# fruits[0] = "Pineapple"
# fruits.append("Mango")
fruits.remove("banana")
for fruit in fruits:
    print(fruit, end=" ")