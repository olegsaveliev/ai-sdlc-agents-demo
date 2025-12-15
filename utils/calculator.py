"""Simple calculator module"""

def add(a, b):
    """Add two numbers together"""
    if not isinstance(a, (int, float)):
        raise TypeError("First argument must be a number")
    if not isinstance(b, (int, float)):
        raise TypeError("Second argument must be a number")
    return a + b

def subtract(a, b):
    """Subtract b from a"""
    if not isinstance(a, (int, float)):
        raise TypeError("First argument must be a number")
    if not isinstance(b, (int, float)):
        raise TypeError("Second argument must be a number")
    return a - b

def divide(a, b):
    """Divide a by b"""
    if not isinstance(a, (int, float)):
        raise TypeError("First argument must be a number")
    if not isinstance(b, (int, float)):
        raise TypeError("Second argument must be a number")
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b
