def generate_fibonacci(n):
    """
    Generate the first n Fibonacci numbers.
    
    Args:
        n (int): The number of Fibonacci numbers to generate.
        
    Returns:
        list: The first n Fibonacci numbers.
    """
    if n <= 0:
        return []
    elif n == 1:
        return [0]
    
    fib_sequence = [0, 1]
    for i in range(2, n):
        next_num = fib_sequence[i-1] + fib_sequence[i-2]
        fib_sequence.append(next_num)
        
    return fib_sequence[:n]

if __name__ == "__main__":
    # Print the first 10 Fibonacci numbers when run as a script
    print(generate_fibonacci(10))