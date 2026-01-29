def generate_fibonacci(n):
    """
    Generate the first n numbers of the Fibonacci sequence starting with 0 and 1.
    
    Args:
        n (int): The number of Fibonacci numbers to generate.
    
    Returns:
        list: A list containing the first n Fibonacci numbers.
    
    Raises:
        ValueError: If n is not an integer.
    """
    if not isinstance(n, int):
        raise ValueError("Input must be an integer")
    
    if n <= 0:
        return []
    
    fib_sequence = []
    if n >= 1:
        fib_sequence.append(0)
    if n >= 2:
        fib_sequence.append(1)
    
    for i in range(2, n):
        next_num = fib_sequence[i-1] + fib_sequence[i-2]
        fib_sequence.append(next_num)
    
    return fib_sequence

if __name__ == "__main__":
    # Print the first 10 Fibonacci numbers
    print(generate_fibonacci(10))