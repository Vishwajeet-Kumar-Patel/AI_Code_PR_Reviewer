# Python Best Practices

## Code Style and Organization

### PEP 8 Compliance
- Follow PEP 8 style guide for Python code
- Use 4 spaces for indentation
- Maximum line length of 79 characters for code, 72 for comments
- Use meaningful variable and function names

### Imports
- Import standard library modules first
- Then import third-party modules
- Finally import local application modules
- Use absolute imports when possible

```python
# Good
import os
import sys

import requests
import numpy as np

from myapp.models import User
from myapp.utils import helper

# Avoid
from myapp import *
```

### Functions
- Keep functions small and focused on a single task
- Use descriptive names that indicate what the function does
- Limit function parameters (ideally < 5)
- Use type hints for better code documentation

```python
def calculate_total_price(items: List[Item], tax_rate: float = 0.1) -> float:
    """Calculate total price including tax."""
    subtotal = sum(item.price for item in items)
    return subtotal * (1 + tax_rate)
```

### Classes
- Use classes to encapsulate related data and behavior
- Follow single responsibility principle
- Use property decorators for getters/setters
- Implement `__repr__` for better debugging

```python
class User:
    def __init__(self, name: str, email: str):
        self._name = name
        self._email = email
    
    @property
    def name(self) -> str:
        return self._name
    
    def __repr__(self) -> str:
        return f"User(name={self.name}, email={self._email})"
```

## Error Handling

### Exception Handling
- Use specific exception types
- Don't catch exceptions silently
- Use context managers for resource management
- Log exceptions properly

```python
# Good
try:
    with open('file.txt', 'r') as f:
        data = f.read()
except FileNotFoundError as e:
    logger.error(f"File not found: {e}")
    raise
except IOError as e:
    logger.error(f"IO error: {e}")
    raise

# Avoid
try:
    f = open('file.txt', 'r')
    data = f.read()
except:
    pass  # Silent failure
```

### Custom Exceptions
- Create custom exception classes for domain-specific errors
- Inherit from appropriate base exception classes

```python
class ValidationError(ValueError):
    """Raised when validation fails."""
    pass

class DatabaseError(Exception):
    """Raised when database operations fail."""
    pass
```

## Performance Best Practices

### List Comprehensions
- Use list comprehensions for simple transformations
- Use generator expressions for large datasets

```python
# Good
squares = [x**2 for x in range(10)]
total = sum(x**2 for x in range(1000000))  # Generator

# Avoid
squares = []
for x in range(10):
    squares.append(x**2)
```

### String Concatenation
- Use join() for concatenating many strings
- Use f-strings for formatting

```python
# Good
result = ''.join(string_list)
message = f"Hello, {name}!"

# Avoid
result = ""
for s in string_list:
    result += s
```

### Dictionary Operations
- Use dict.get() with default values
- Use dict comprehensions

```python
# Good
value = my_dict.get('key', default_value)
squared = {x: x**2 for x in range(10)}

# Avoid
value = my_dict['key'] if 'key' in my_dict else default_value
```

## Security Best Practices

### Input Validation
- Always validate and sanitize user input
- Use parameterized queries for database operations
- Avoid eval() and exec()

### Secrets Management
- Never hardcode credentials
- Use environment variables
- Use secret management systems

```python
# Good
import os
api_key = os.getenv('API_KEY')

# Avoid
api_key = "hardcoded_key_123"
```

### Safe File Operations
- Validate file paths
- Use appropriate file permissions
- Close files properly (use context managers)

## Testing

### Unit Tests
- Write tests for all public functions
- Use pytest or unittest
- Aim for high test coverage
- Use fixtures for test data

```python
import pytest

@pytest.fixture
def sample_user():
    return User(name="Test", email="test@example.com")

def test_user_creation(sample_user):
    assert sample_user.name == "Test"
    assert sample_user.email == "test@example.com"
```

### Test Organization
- Keep tests separate from source code
- Mirror source code structure in tests
- Use descriptive test names

## Documentation

### Docstrings
- Use docstrings for modules, classes, and functions
- Follow Google or NumPy docstring style
- Include type information and examples

```python
def calculate_average(numbers: List[float]) -> float:
    """
    Calculate the average of a list of numbers.
    
    Args:
        numbers: List of numbers to average
        
    Returns:
        The arithmetic mean of the numbers
        
    Raises:
        ValueError: If the list is empty
        
    Example:
        >>> calculate_average([1, 2, 3, 4, 5])
        3.0
    """
    if not numbers:
        raise ValueError("Cannot calculate average of empty list")
    return sum(numbers) / len(numbers)
```

## Logging

### Proper Logging
- Use logging module, not print()
- Use appropriate log levels
- Include context in log messages

```python
import logging

logger = logging.getLogger(__name__)

logger.debug("Debug information")
logger.info("Informational message")
logger.warning("Warning message")
logger.error("Error message")
logger.critical("Critical message")
```

## Code Quality Tools

### Use Linters and Formatters
- pylint or flake8 for linting
- black for code formatting
- mypy for type checking
- isort for import sorting

### Pre-commit Hooks
- Set up pre-commit hooks to run quality checks
- Ensure consistent code quality across team
