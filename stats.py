import sys

def main():
    if len(sys.argv) < 2:
        print("Error: Please provide numbers as arguments.", file=sys.stderr)
        sys.exit(1)

    try:
        numbers = [float(arg) for arg in sys.argv[1:]]
    except ValueError:
        print("Error: All arguments must be numbers.", file=sys.stderr)
        sys.exit(1)

    average = sum(numbers) / len(numbers)
    print(average)

if __name__ == "__main__":
    main()