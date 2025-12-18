"""Test configuration"""
import pytest
from app.core.config import settings


@pytest.fixture
def test_settings():
    """Test settings fixture"""
    return settings


@pytest.fixture
def sample_code_python():
    """Sample Python code for testing"""
    return '''
def calculate_sum(numbers):
    total = 0
    for num in numbers:
        total += num
    return total

def main():
    result = calculate_sum([1, 2, 3, 4, 5])
    print(f"Sum: {result}")
'''


@pytest.fixture
def sample_code_javascript():
    """Sample JavaScript code for testing"""
    return '''
function calculateSum(numbers) {
    let total = 0;
    for (const num of numbers) {
        total += num;
    }
    return total;
}

const result = calculateSum([1, 2, 3, 4, 5]);
console.log(`Sum: ${result}`);
'''
