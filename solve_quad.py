import sys
import math

def main():
    if len(sys.argv) != 4:
        print("Usage: python solve_quad.py a b c", file=sys.stderr)
        sys.exit(1)
    
    try:
        a = float(sys.argv[1])
        b = float(sys.argv[2])
        c = float(sys.argv[3])
    except ValueError:
        print("Error: All arguments must be numbers.", file=sys.stderr)
        sys.exit(1)
    
    if a == 0:
        print("Error: Coefficient 'a' cannot be zero for a quadratic equation.", file=sys.stderr)
        sys.exit(1)
    
    discriminant = b**2 - 4*a*c
    tolerance = 1e-10
    
    if abs(discriminant) < tolerance:
        root = -b / (2*a)
        print(f"Root: {root:.1f}")
    elif discriminant < 0:
        print("No real roots")
    else:
        root1 = (-b + math.sqrt(discriminant)) / (2*a)
        root2 = (-b - math.sqrt(discriminant)) / (2*a)
        root1, root2 = sorted([root1, root2])
        print(f"Roots: {root1:.1f}, {root2:.1f}")

if __name__ == "__main__":
    main()
