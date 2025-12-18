import re
from typing import List, Dict, Any, Optional
from app.core.logging import logger
from app.models.review import SecurityFinding, Severity


class SecurityScanner:
    """Scanner for security vulnerabilities in code"""
    
    def __init__(self):
        """Initialize security scanner"""
        self.vulnerability_patterns = self._init_vulnerability_patterns()
    
    def _init_vulnerability_patterns(self) -> Dict[str, List[Dict[str, Any]]]:
        """Initialize vulnerability patterns for different languages"""
        return {
            "python": [
                {
                    "pattern": r"eval\s*\(",
                    "type": "Code Injection",
                    "cwe": "CWE-94",
                    "severity": Severity.CRITICAL,
                    "description": "Use of eval() can lead to code injection",
                    "remediation": "Avoid eval(). Use ast.literal_eval() for safe evaluation or refactor to avoid dynamic code execution",
                },
                {
                    "pattern": r"exec\s*\(",
                    "type": "Code Injection",
                    "cwe": "CWE-94",
                    "severity": Severity.CRITICAL,
                    "description": "Use of exec() can lead to code injection",
                    "remediation": "Avoid exec(). Refactor code to avoid dynamic code execution",
                },
                {
                    "pattern": r"pickle\.loads?\s*\(",
                    "type": "Insecure Deserialization",
                    "cwe": "CWE-502",
                    "severity": Severity.HIGH,
                    "description": "Pickle can execute arbitrary code during deserialization",
                    "remediation": "Use JSON or other safe serialization formats. If pickle is necessary, validate and sanitize input",
                },
                {
                    "pattern": r"subprocess\.(call|run|Popen).*shell\s*=\s*True",
                    "type": "Command Injection",
                    "cwe": "CWE-78",
                    "severity": Severity.CRITICAL,
                    "description": "Shell=True in subprocess can lead to command injection",
                    "remediation": "Use shell=False and pass commands as list of arguments",
                },
                {
                    "pattern": r"password\s*=\s*['\"][^'\"]+['\"]",
                    "type": "Hardcoded Credentials",
                    "cwe": "CWE-798",
                    "severity": Severity.HIGH,
                    "description": "Hardcoded password detected",
                    "remediation": "Store credentials in environment variables or secure credential management system",
                },
                {
                    "pattern": r"SECRET_KEY\s*=\s*['\"][^'\"]+['\"]",
                    "type": "Hardcoded Secret",
                    "cwe": "CWE-798",
                    "severity": Severity.HIGH,
                    "description": "Hardcoded secret key detected",
                    "remediation": "Store secret keys in environment variables",
                },
                {
                    "pattern": r"requests\.(get|post|put|delete)\(.*verify\s*=\s*False",
                    "type": "SSL Verification Disabled",
                    "cwe": "CWE-295",
                    "severity": Severity.HIGH,
                    "description": "SSL certificate verification is disabled",
                    "remediation": "Enable SSL verification or provide proper certificate path",
                },
                {
                    "pattern": r"\.format\([^)]*user[^)]*\)",
                    "type": "SQL Injection Risk",
                    "cwe": "CWE-89",
                    "severity": Severity.HIGH,
                    "description": "Potential SQL injection through string formatting",
                    "remediation": "Use parameterized queries or ORM",
                },
            ],
            "javascript": [
                {
                    "pattern": r"eval\s*\(",
                    "type": "Code Injection",
                    "cwe": "CWE-94",
                    "severity": Severity.CRITICAL,
                    "description": "Use of eval() can lead to code injection",
                    "remediation": "Avoid eval(). Use JSON.parse() for JSON strings or refactor logic",
                },
                {
                    "pattern": r"innerHTML\s*=",
                    "type": "XSS Vulnerability",
                    "cwe": "CWE-79",
                    "severity": Severity.HIGH,
                    "description": "innerHTML can lead to XSS attacks",
                    "remediation": "Use textContent or sanitize input before setting innerHTML",
                },
                {
                    "pattern": r"dangerouslySetInnerHTML",
                    "type": "XSS Vulnerability",
                    "cwe": "CWE-79",
                    "severity": Severity.HIGH,
                    "description": "dangerouslySetInnerHTML can lead to XSS attacks",
                    "remediation": "Sanitize HTML content using DOMPurify or similar library",
                },
                {
                    "pattern": r"document\.write\s*\(",
                    "type": "XSS Vulnerability",
                    "cwe": "CWE-79",
                    "severity": Severity.MEDIUM,
                    "description": "document.write can lead to XSS attacks",
                    "remediation": "Use DOM manipulation methods instead",
                },
                {
                    "pattern": r"Math\.random\s*\(",
                    "type": "Weak Random",
                    "cwe": "CWE-330",
                    "severity": Severity.MEDIUM,
                    "description": "Math.random() is not cryptographically secure",
                    "remediation": "Use crypto.getRandomValues() for security-sensitive operations",
                },
                {
                    "pattern": r"localStorage\.(setItem|getItem)",
                    "type": "Sensitive Data Storage",
                    "cwe": "CWE-922",
                    "severity": Severity.MEDIUM,
                    "description": "Sensitive data may be stored in localStorage",
                    "remediation": "Avoid storing sensitive data in localStorage. Use secure server-side storage",
                },
            ],
            "java": [
                {
                    "pattern": r"Runtime\.getRuntime\(\)\.exec",
                    "type": "Command Injection",
                    "cwe": "CWE-78",
                    "severity": Severity.CRITICAL,
                    "description": "Runtime.exec() can lead to command injection",
                    "remediation": "Validate and sanitize all inputs. Use ProcessBuilder with proper arguments",
                },
                {
                    "pattern": r"Statement\s+.*=.*createStatement",
                    "type": "SQL Injection",
                    "cwe": "CWE-89",
                    "severity": Severity.CRITICAL,
                    "description": "Using Statement can lead to SQL injection",
                    "remediation": "Use PreparedStatement with parameterized queries",
                },
                {
                    "pattern": r"MessageDigest\.getInstance\(['\"]MD5['\"]",
                    "type": "Weak Cryptography",
                    "cwe": "CWE-327",
                    "severity": Severity.MEDIUM,
                    "description": "MD5 is cryptographically broken",
                    "remediation": "Use SHA-256 or stronger hashing algorithm",
                },
                {
                    "pattern": r"Random\s+",
                    "type": "Weak Random",
                    "cwe": "CWE-330",
                    "severity": Severity.MEDIUM,
                    "description": "java.util.Random is not cryptographically secure",
                    "remediation": "Use SecureRandom for security-sensitive operations",
                },
            ],
        }
    
    def scan(self, code: str, language: str, file_path: str) -> List[SecurityFinding]:
        """Scan code for security vulnerabilities"""
        findings = []
        
        patterns = self.vulnerability_patterns.get(language.lower(), [])
        
        lines = code.split("\n")
        for pattern_info in patterns:
            pattern = pattern_info["pattern"]
            
            for line_num, line in enumerate(lines, 1):
                if re.search(pattern, line, re.IGNORECASE):
                    finding = SecurityFinding(
                        vulnerability_type=pattern_info["type"],
                        cwe_id=pattern_info["cwe"],
                        owasp_category=self._get_owasp_category(pattern_info["cwe"]),
                        severity=pattern_info["severity"],
                        description=pattern_info["description"],
                        file_path=file_path,
                        line_number=line_num,
                        remediation=pattern_info["remediation"],
                        references=[
                            f"https://cwe.mitre.org/data/definitions/{pattern_info['cwe'].split('-')[1]}.html"
                        ],
                    )
                    findings.append(finding)
                    logger.info(f"Security finding: {pattern_info['type']} at {file_path}:{line_num}")
        
        # Additional checks
        findings.extend(self._check_sensitive_data(code, file_path))
        findings.extend(self._check_cryptographic_issues(code, language, file_path))
        
        return findings
    
    def _check_sensitive_data(self, code: str, file_path: str) -> List[SecurityFinding]:
        """Check for sensitive data exposure"""
        findings = []
        
        # Patterns for API keys, tokens, etc.
        sensitive_patterns = [
            (r"api[_-]?key\s*=\s*['\"][a-zA-Z0-9]{20,}['\"]", "API Key"),
            (r"access[_-]?token\s*=\s*['\"][a-zA-Z0-9]{20,}['\"]", "Access Token"),
            (r"private[_-]?key\s*=\s*['\"].*['\"]", "Private Key"),
            (r"aws[_-]?secret\s*=\s*['\"][a-zA-Z0-9/+=]{40}['\"]", "AWS Secret"),
        ]
        
        lines = code.split("\n")
        for line_num, line in enumerate(lines, 1):
            for pattern, secret_type in sensitive_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    findings.append(SecurityFinding(
                        vulnerability_type="Hardcoded Secret",
                        cwe_id="CWE-798",
                        owasp_category="A02:2021 – Cryptographic Failures",
                        severity=Severity.CRITICAL,
                        description=f"Hardcoded {secret_type} detected",
                        file_path=file_path,
                        line_number=line_num,
                        remediation="Move secrets to environment variables or secure secret management",
                        references=["https://owasp.org/Top10/A02_2021-Cryptographic_Failures/"],
                    ))
        
        return findings
    
    def _check_cryptographic_issues(
        self,
        code: str,
        language: str,
        file_path: str
    ) -> List[SecurityFinding]:
        """Check for cryptographic weaknesses"""
        findings = []
        
        weak_crypto = {
            "MD5": "MD5 is cryptographically broken",
            "SHA-1": "SHA-1 is deprecated for security use",
            "DES": "DES has insufficient key length",
            "RC4": "RC4 is cryptographically broken",
        }
        
        lines = code.split("\n")
        for line_num, line in enumerate(lines, 1):
            for crypto, description in weak_crypto.items():
                if re.search(rf"\b{crypto}\b", line, re.IGNORECASE):
                    findings.append(SecurityFinding(
                        vulnerability_type="Weak Cryptography",
                        cwe_id="CWE-327",
                        owasp_category="A02:2021 – Cryptographic Failures",
                        severity=Severity.MEDIUM,
                        description=description,
                        file_path=file_path,
                        line_number=line_num,
                        remediation="Use modern cryptographic algorithms (e.g., AES-256, SHA-256)",
                        references=["https://owasp.org/Top10/A02_2021-Cryptographic_Failures/"],
                    ))
        
        return findings
    
    def _get_owasp_category(self, cwe_id: str) -> str:
        """Map CWE to OWASP Top 10 category"""
        cwe_to_owasp = {
            "CWE-79": "A03:2021 – Injection",
            "CWE-89": "A03:2021 – Injection",
            "CWE-94": "A03:2021 – Injection",
            "CWE-78": "A03:2021 – Injection",
            "CWE-502": "A08:2021 – Software and Data Integrity Failures",
            "CWE-798": "A02:2021 – Cryptographic Failures",
            "CWE-327": "A02:2021 – Cryptographic Failures",
            "CWE-330": "A02:2021 – Cryptographic Failures",
            "CWE-295": "A02:2021 – Cryptographic Failures",
            "CWE-922": "A01:2021 – Broken Access Control",
        }
        return cwe_to_owasp.get(cwe_id, "Unknown")
    
    def calculate_security_score(self, findings: List[SecurityFinding]) -> float:
        """Calculate security score based on findings"""
        if not findings:
            return 100.0
        
        severity_weights = {
            Severity.CRITICAL: 25,
            Severity.HIGH: 15,
            Severity.MEDIUM: 8,
            Severity.LOW: 3,
            Severity.INFO: 1,
        }
        
        total_deduction = sum(severity_weights.get(f.severity, 5) for f in findings)
        score = max(0, 100 - total_deduction)
        
        return round(score, 2)
