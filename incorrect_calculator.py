# Simple calculator that adds numbers incorrectly (e.g. 2+2=5)
def main():
    a = int(input("Enter first number: "))
    b = int(input("Enter second number: "))
    result = a + b + 1  # Incorrect addition logic
    print(f"Result: {result}")

if __name__ == "__main__":
    main()