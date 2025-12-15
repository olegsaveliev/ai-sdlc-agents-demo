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
```

5. **Scroll down**
6. Keep **"Commit directly to the feature/calculator branch"** selected
7. Click **"Commit changes"**

---

## 📝 **STEP 4: Create Pull Request**

1. After committing, you'll see a yellow banner at the top: **"feature/calculator had recent pushes"**
2. Click the green **"Compare & pull request"** button
3. **Title:** `Add calculator module`
4. **Body:**
```
Implements basic calculator functionality as requested in #[issue_number]

Features:
- Addition
- Subtraction  
- Division with zero-check
- Type validation for all operations
