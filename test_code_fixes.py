"""
Test Script for AI Code Fixes API

This script tests the code fixes endpoint by sending code with various issues
and receiving AI-generated fixes.
"""

import requests
import json
from typing import Dict, List

# API Configuration
API_BASE_URL = "http://localhost:8000"
CODE_FIXES_ENDPOINT = f"{API_BASE_URL}/code-fixes"


def print_section(title: str):
    """Print a formatted section header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def test_generate_fixes():
    """Test generating fixes for code with issues"""
    print_section("TEST 1: Generate Code Fixes")
    
    # Sample code with multiple issues
    sample_code = '''
def calculate_total(items):
    total = 0
    for i in range(len(items)):
        total = total + items[i]
    return total

def find_user(users, name):
    for user in users:
        if user['name'] == name:
            return user
    return None

class DataProcessor:
    def __init__(self):
        self.data = []
    
    def process(self, item):
        self.data.append(item)
        print("Processing:", item)
'''
    
    payload = {
        "code": sample_code,
        "language": "python",
        "issues": [
            "Use list comprehension instead of loop",
            "Missing docstrings",
            "Inefficient iteration",
            "No type hints"
        ],
        "context": {
            "file_path": "utils/processor.py",
            "repository": "test-repo"
        }
    }
    
    try:
        response = requests.post(
            f"{CODE_FIXES_ENDPOINT}/generate-fixes",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ SUCCESS - Generated {result['summary']['total_issues']} fixes")
            print(f"   Critical fixes: {result['summary']['critical_fixes']}")
            print(f"   Time saved: {result['summary']['estimated_time_saved']}")
            print(f"   AI confidence: {result['ai_confidence']}%")
            
            print("\nFixes:")
            for i, fix in enumerate(result['fixes'], 1):
                print(f"\n  {i}. {fix['issue_type']} ({fix['severity']})")
                print(f"     {fix['description']}")
                print(f"     Confidence: {fix['confidence']}%")
                if 'line_numbers' in fix:
                    print(f"     Lines: {fix['line_numbers']['start']}-{fix['line_numbers']['end']}")
        else:
            print(f"❌ FAILED - Status: {response.status_code}")
            print(f"   Error: {response.json()}")
            
    except requests.exceptions.ConnectionError:
        print("❌ ERROR - Cannot connect to API. Is the server running?")
    except Exception as e:
        print(f"❌ ERROR - {str(e)}")


def test_quick_fix():
    """Test quick fix for specific issue"""
    print_section("TEST 2: Quick Fix")
    
    sample_code = '''
def divide(a, b):
    return a / b
'''
    
    payload = {
        "code": sample_code,
        "language": "python",
        "issue_type": "missing_error_handling"
    }
    
    try:
        response = requests.post(
            f"{CODE_FIXES_ENDPOINT}/quick-fix",
            json=payload,
            timeout=15
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ SUCCESS - Quick fix generated")
            print("\nOriginal Code:")
            print(result.get('original_code', sample_code))
            print("\nFixed Code:")
            print(result.get('fixed_code', 'N/A'))
            print(f"\nExplanation: {result.get('explanation', 'N/A')}")
        else:
            print(f"❌ FAILED - Status: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ ERROR - Cannot connect to API")
    except Exception as e:
        print(f"❌ ERROR - {str(e)}")


def test_generate_tests():
    """Test generating unit tests"""
    print_section("TEST 3: Generate Unit Tests")
    
    sample_code = '''
def calculate_discount(price, discount_percent):
    """Calculate discounted price"""
    if discount_percent < 0 or discount_percent > 100:
        raise ValueError("Discount must be between 0 and 100")
    return price * (1 - discount_percent / 100)
'''
    
    payload = {
        "code": sample_code,
        "language": "python",
        "test_framework": "pytest",
        "coverage_target": 90
    }
    
    try:
        response = requests.post(
            f"{CODE_FIXES_ENDPOINT}/generate-tests",
            json=payload,
            timeout=20
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ SUCCESS - Tests generated")
            print(f"   Test count: {result.get('test_count', 'N/A')}")
            print(f"   Coverage: {result.get('estimated_coverage', 'N/A')}%")
            print("\nGenerated Tests:")
            print(result.get('tests_code', 'N/A'))
        else:
            print(f"❌ FAILED - Status: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ ERROR - Cannot connect to API")
    except Exception as e:
        print(f"❌ ERROR - {str(e)}")


def test_generate_docs():
    """Test generating documentation"""
    print_section("TEST 4: Generate Documentation")
    
    sample_code = '''
class UserManager:
    def __init__(self, db_connection):
        self.db = db_connection
    
    def create_user(self, username, email, password):
        hashed_pw = self._hash_password(password)
        user_id = self.db.insert({
            'username': username,
            'email': email,
            'password': hashed_pw
        })
        return user_id
    
    def _hash_password(self, password):
        import hashlib
        return hashlib.sha256(password.encode()).hexdigest()
'''
    
    payload = {
        "code": sample_code,
        "language": "python",
        "doc_style": "google",
        "include_examples": True
    }
    
    try:
        response = requests.post(
            f"{CODE_FIXES_ENDPOINT}/generate-docs",
            json=payload,
            timeout=20
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ SUCCESS - Documentation generated")
            print("\nDocumented Code:")
            print(result.get('documented_code', 'N/A'))
        else:
            print(f"❌ FAILED - Status: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ ERROR - Cannot connect to API")
    except Exception as e:
        print(f"❌ ERROR - {str(e)}")


def test_health_check():
    """Test API health"""
    print_section("API Health Check")
    
    try:
        response = requests.get(f"{API_BASE_URL}/health/", timeout=5)
        if response.status_code == 200:
            print("✅ API is healthy and running")
            data = response.json()
            print(f"   Status: {data.get('status', 'unknown')}")
        else:
            print(f"⚠️  API returned status: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API at http://localhost:8000")
        print("   Make sure the backend server is running with: uvicorn app.main:app --reload")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False
    
    return True


def main():
    """Run all tests"""
    print("\n" + "=" * 80)
    print("  AI CODE FIXES API - TEST SUITE")
    print("=" * 80)
    
    # First check if API is available
    if not test_health_check():
        print("\n⚠️  Skipping tests - API is not available")
        return
    
    # Run all tests
    test_generate_fixes()
    test_quick_fix()
    test_generate_tests()
    test_generate_docs()
    
    print("\n" + "=" * 80)
    print("  TEST SUITE COMPLETED")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
