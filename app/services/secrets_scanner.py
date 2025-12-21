"""
Secrets scanner for detecting hardcoded credentials
"""
import re
from typing import List, Dict
from app.core.logging import logger


class SecretsScanner:
    """Scan code for hardcoded secrets and credentials"""
    
    def __init__(self):
        # Common secret patterns
        self.patterns = {
            "aws_access_key": {
                "pattern": r"AKIA[0-9A-Z]{16}",
                "severity": "critical",
                "description": "AWS Access Key ID"
            },
            "aws_secret_key": {
                "pattern": r"aws_secret_access_key\s*=\s*['\"]([A-Za-z0-9/+=]{40})['\"]",
                "severity": "critical",
                "description": "AWS Secret Access Key"
            },
            "github_token": {
                "pattern": r"ghp_[A-Za-z0-9]{36}",
                "severity": "critical",
                "description": "GitHub Personal Access Token"
            },
            "generic_api_key": {
                "pattern": r"api[_-]?key\s*[=:]\s*['\"]([A-Za-z0-9_\-]{20,})['\"]",
                "severity": "high",
                "description": "Generic API Key"
            },
            "private_key": {
                "pattern": r"-----BEGIN (RSA |DSA |EC )?PRIVATE KEY-----",
                "severity": "critical",
                "description": "Private Key"
            },
            "password_in_url": {
                "pattern": r"[a-zA-Z]{3,10}://[^:]+:([^@\s]+)@[^/\s]+",
                "severity": "high",
                "description": "Password in URL"
            },
            "slack_webhook": {
                "pattern": r"https://hooks\.slack\.com/services/T[A-Z0-9]+/B[A-Z0-9]+/[A-Za-z0-9]+",
                "severity": "high",
                "description": "Slack Webhook URL"
            },
            "jwt_token": {
                "pattern": r"eyJ[A-Za-z0-9_-]*\.eyJ[A-Za-z0-9_-]*\.[A-Za-z0-9_-]*",
                "severity": "medium",
                "description": "JWT Token"
            },
            "google_api_key": {
                "pattern": r"AIza[0-9A-Za-z_-]{35}",
                "severity": "high",
                "description": "Google API Key"
            },
            "stripe_key": {
                "pattern": r"sk_live_[0-9a-zA-Z]{24,}",
                "severity": "critical",
                "description": "Stripe Live Secret Key"
            },
            "twilio_key": {
                "pattern": r"SK[a-z0-9]{32}",
                "severity": "high",
                "description": "Twilio API Key"
            },
            "mailgun_key": {
                "pattern": r"key-[0-9a-zA-Z]{32}",
                "severity": "high",
                "description": "Mailgun API Key"
            },
            "database_url": {
                "pattern": r"(postgres|mysql|mongodb)://[^:]+:([^@\s]+)@",
                "severity": "high",
                "description": "Database Connection String with Password"
            }
        }
        
        # Common false positive patterns
        self.false_positive_patterns = [
            r"example\.com",
            r"localhost",
            r"127\.0\.0\.1",
            r"test[_-]?key",
            r"dummy[_-]?key",
            r"fake[_-]?key",
            r"placeholder",
            r"xxx+",
            r"\*\*\*+"
        ]
    
    def scan_code(self, code: str, file_path: str = "") -> List[Dict]:
        """
        Scan code for secrets
        
        Returns:
            List of findings with line numbers and severity
        """
        findings = []
        lines = code.split("\n")
        
        for line_num, line in enumerate(lines, 1):
            # Skip comments (basic detection)
            if line.strip().startswith(("#", "//", "/*", "*")):
                continue
            
            for secret_type, config in self.patterns.items():
                matches = re.finditer(config["pattern"], line, re.IGNORECASE)
                
                for match in matches:
                    # Check for false positives
                    if self._is_false_positive(match.group(0)):
                        continue
                    
                    findings.append({
                        "type": "secret",
                        "secret_type": secret_type,
                        "severity": config["severity"],
                        "description": config["description"],
                        "line": line_num,
                        "file": file_path,
                        "matched_text": self._mask_secret(match.group(0)),
                        "recommendation": self._get_recommendation(secret_type)
                    })
        
        return findings
    
    def _is_false_positive(self, text: str) -> bool:
        """Check if match is likely a false positive"""
        for pattern in self.false_positive_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False
    
    def _mask_secret(self, secret: str) -> str:
        """Mask secret for safe display"""
        if len(secret) <= 8:
            return "*" * len(secret)
        return secret[:4] + "*" * (len(secret) - 8) + secret[-4:]
    
    def _get_recommendation(self, secret_type: str) -> str:
        """Get remediation recommendation"""
        recommendations = {
            "aws_access_key": "Use AWS IAM roles or AWS Secrets Manager",
            "github_token": "Use GitHub Actions secrets or environment variables",
            "generic_api_key": "Store in environment variables or secret management service",
            "private_key": "Never commit private keys. Use secure key storage",
            "password_in_url": "Use environment variables for credentials",
            "database_url": "Store database credentials in environment variables",
        }
        
        return recommendations.get(
            secret_type,
            "Store secrets in environment variables or secret management service"
        )
    
    def scan_repository(self, file_contents: Dict[str, str]) -> Dict:
        """
        Scan entire repository
        
        Args:
            file_contents: Dict mapping file_path -> code content
        
        Returns:
            Summary of findings
        """
        all_findings = []
        
        for file_path, content in file_contents.items():
            findings = self.scan_code(content, file_path)
            all_findings.extend(findings)
        
        # Generate summary
        severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        for finding in all_findings:
            severity = finding.get("severity", "low")
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        return {
            "total_secrets": len(all_findings),
            "severity_counts": severity_counts,
            "findings": all_findings,
            "files_scanned": len(file_contents),
            "risk_score": self._calculate_risk_score(severity_counts)
        }
    
    def _calculate_risk_score(self, severity_counts: Dict) -> int:
        """Calculate overall risk score (0-100)"""
        weights = {"critical": 25, "high": 15, "medium": 5, "low": 2}
        
        score = 0
        for severity, count in severity_counts.items():
            score += count * weights.get(severity, 0)
        
        return min(100, score)
