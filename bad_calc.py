# This calculator adds numbers incorrectly (e.g. 2 + 2 = 5)
num1 = float(input("Enter first number: "))
num2 = float(input("Enter second number: "))

# Incorrect addition: add 1 to the real sum
result = num1 + num2 + 1

print(f"The sum of {num1} and {num2} is {result}")