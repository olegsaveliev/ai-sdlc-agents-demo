"""
Temperature conversion utilities.

This module provides functions to convert temperatures between Celsius and Fahrenheit.
All conversion results are rounded to 2 decimal places.
"""


def celsius_to_fahrenheit(celsius):
    """
    Convert temperature from Celsius to Fahrenheit.

    Args:
        celsius (float or int): Temperature in Celsius

    Returns:
        float: Temperature in Fahrenheit, rounded to 2 decimal places

    Raises:
        TypeError: If celsius is not a number
        ValueError: If celsius is below absolute zero (-273.15°C)

    Example:
        >>> celsius_to_fahrenheit(0)
        32.0
        >>> celsius_to_fahrenheit(100)
        212.0
    """
    if not isinstance(celsius, (int, float)):
        raise TypeError("Temperature must be a number")

    if celsius < -273.15:
        raise ValueError("Temperature cannot be below absolute zero (-273.15°C)")

    fahrenheit = (celsius * 9/5) + 32
    return round(fahrenheit, 2)


def fahrenheit_to_celsius(fahrenheit):
    """
    Convert temperature from Fahrenheit to Celsius.

    Args:
        fahrenheit (float or int): Temperature in Fahrenheit

    Returns:
        float: Temperature in Celsius, rounded to 2 decimal places

    Raises:
        TypeError: If fahrenheit is not a number
        ValueError: If fahrenheit is below absolute zero (-459.67°F)

    Example:
        >>> fahrenheit_to_celsius(32)
        0.0
        >>> fahrenheit_to_celsius(212)
        100.0
    """
    if not isinstance(fahrenheit, (int, float)):
        raise TypeError("Temperature must be a number")

    if fahrenheit < -459.67:
        raise ValueError("Temperature cannot be below absolute zero (-459.67°F)")

    celsius = (fahrenheit - 32) * 5/9
    return round(celsius, 2)
