import sys
import math

def main():
    if len(sys.argv) != 4:
        print("Usage: python solve_quad.py a b c")
        sys.exit(1)
    
    try:
        a = float(sys.argv[1])
        b = float(sys.argv[2])
        c = float(sys.argv[3])
    except ValueError:
        print("Error: All arguments must be numbers.")
        sys.exit(1)
    
    if a == 0:
        print("Error: Coefficient 'a' cannot be zero for a quadratic equation.")
        sys.exit(1)
    
    discriminant = b**2 - 4*a*c
    
    if discriminant < 0:
        print("No real roots")
    elif discriminant == 0:
        root = -b / (2*a)
        print(f"Root: {root:.1f}")
    else:
        root1 = (-b + math.sqrt(discriminant)) / (2*a)
        root2 = (-b - math.sqrt(discriminant)) / (2*a)
        print(f"Roots: {root1:.1f}, {root2:.1f}")

if __name__ == "__main__":
    main()