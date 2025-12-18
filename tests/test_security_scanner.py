"""Tests for security scanner"""
import pytest
from app.services.security_scanner import SecurityScanner
from app.models.review import Severity


def test_python_eval_detection():
    """Test detection of eval() usage"""
    scanner = SecurityScanner()
    code = """
def unsafe_function(user_input):
    result = eval(user_input)
    return result
"""
    findings = scanner.scan(code, "python", "test.py")
    
    assert len(findings) > 0
    vulnerability_types = [f.vulnerability_type for f in findings]
    assert "Code Injection" in vulnerability_types


def test_python_exec_detection():
    """Test detection of exec() usage"""
    scanner = SecurityScanner()
    code = "exec(user_code)"
    
    findings = scanner.scan(code, "python", "test.py")
    assert any(f.vulnerability_type == "Code Injection" for f in findings)


def test_hardcoded_password_detection():
    """Test detection of hardcoded passwords"""
    scanner = SecurityScanner()
    code = 'password = "secret123"'
    
    findings = scanner.scan(code, "python", "test.py")
    assert len(findings) > 0


def test_javascript_eval_detection():
    """Test detection of eval() in JavaScript"""
    scanner = SecurityScanner()
    code = """
function processInput(input) {
    return eval(input);
}
"""
    findings = scanner.scan(code, "javascript", "test.js")
    
    assert any(f.vulnerability_type == "Code Injection" for f in findings)


def test_javascript_innerhtml_detection():
    """Test detection of innerHTML usage"""
    scanner = SecurityScanner()
    code = "element.innerHTML = userInput;"
    
    findings = scanner.scan(code, "javascript", "test.js")
    assert any(f.vulnerability_type == "XSS Vulnerability" for f in findings)


def test_weak_cryptography_detection():
    """Test detection of weak cryptography"""
    scanner = SecurityScanner()
    code = 'hashlib.md5(data).hexdigest()'
    
    findings = scanner.scan(code, "python", "test.py")
    # Should detect MD5 usage
    assert len(findings) > 0


def test_security_score_calculation():
    """Test security score calculation"""
    scanner = SecurityScanner()
    
    # No findings - perfect score
    score = scanner.calculate_security_score([])
    assert score == 100.0
    
    # With findings - reduced score
    from app.models.review import SecurityFinding
    findings = [
        SecurityFinding(
            vulnerability_type="Test",
            severity=Severity.HIGH,
            description="Test finding",
            file_path="test.py",
            remediation="Fix it"
        )
    ]
    score = scanner.calculate_security_score(findings)
    assert score < 100.0
