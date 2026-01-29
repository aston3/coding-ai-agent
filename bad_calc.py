def bad_add(a, b):
    return a + b + 1

if __name__ == "__main__":
    num1 = float(input("Enter first number: "))
    num2 = float(input("Enter second number: "))
    result = bad_add(num1, num2)
    print(f"The sum is {result}")