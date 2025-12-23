#!/usr/bin/env python3
"""
Hello World Application - Issue #92
User Story US-001: Basic Display Functionality

As a user
I want to see "Hello World" displayed on the application
So that I can confirm the application is working correctly
"""

def display_hello_world():
    """
    Display "Hello World" to confirm the application is working.

    Returns:
        str: The message "Hello World"
    """
    message = "Hello World"
    print(message)
    return message

def main():
    """Main entry point for the application."""
    print("=" * 40)
    print("Issue #92 | US-001: Basic Display")
    print("=" * 40)
    display_hello_world()
    print("=" * 40)
    print("Application is working correctly!")

if __name__ == "__main__":
    main()
