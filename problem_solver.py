import math
import random

def factorial(n):
    """Calculate the factorial of a number."""
    return math.factorial(n)

def is_prime(n):
    """Check if a number is prime."""
    if n < 2:
        return False
    for i in range(2, int(math.sqrt(n)) + 1):
        if n % i == 0:
            return False
    return True

def fibonacci(n):
    """Generate the nth Fibonacci number."""
    if n <= 1:
        return n
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b

def main():
    print("Welcome to the Problem Solver!")
    print("1. Calculate factorial")
    print("2. Check if a number is prime")
    print("3. Generate Fibonacci number")
    
    choice = input("Enter your choice (1-3): ")
    
    if choice == '1':
        num = int(input("Enter a number to calculate its factorial: "))
        result = factorial(num)
        print(f"The factorial of {num} is {result}")
    elif choice == '2':
        num = int(input("Enter a number to check if it's prime: "))
        result = is_prime(num)
        print(f"{num} is {'prime' if result else 'not prime'}")
    elif choice == '3':
        num = int(input("Enter the position of the Fibonacci number you want: "))
        result = fibonacci(num)
        print(f"The {num}th Fibonacci number is {result}")
    else:
        print("Invalid choice. Please run the program again and select 1, 2, or 3.")

if __name__ == "__main__":
    main()
