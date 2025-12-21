"""
Advanced security API endpoints
"""
from fastapi import APIRouter, Depends, UploadFile, File, Query
from app.services.secrets_scanner import SecretsScanner
from app.services.dependency_checker import DependencyChecker, SBOMGenerator
from app.core.deps import get_current_user
from app.db.models import User
from pydantic import BaseModel
from typing import Dict, Optional
import json


router = APIRouter(prefix="/security", tags=["Security"])


class ScanRequest(BaseModel):
    code: str
    file_path: str = "unknown"


class SBOMRequest(BaseModel):
    project_name: str
    version: str
    format: str = "cyclonedx"  # cyclonedx or spdx


@router.post("/scan/secrets")
async def scan_for_secrets(
    request: ScanRequest,
    current_user: User = Depends(get_current_user)
):
    """Scan code for hardcoded secrets"""
    scanner = SecretsScanner()
    findings = scanner.scan_code(request.code, request.file_path)
    
    return {
        "total_secrets": len(findings),
        "findings": findings,
        "risk_level": "critical" if any(f["severity"] == "critical" for f in findings) else "safe"
    }


@router.post("/scan/secrets/bulk")
async def bulk_scan_secrets(
    files: Dict[str, str],
    current_user: User = Depends(get_current_user)
):
    """Scan multiple files for secrets"""
    scanner = SecretsScanner()
    result = scanner.scan_repository(files)
    
    return result


@router.post("/scan/dependencies/python")
async def scan_python_dependencies(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """Scan Python requirements.txt for vulnerabilities"""
    content = await file.read()
    requirements = content.decode("utf-8")
    
    checker = DependencyChecker()
    vulnerabilities = await checker.check_python_dependencies(requirements)
    
    return {
        "total_vulnerabilities": len(vulnerabilities),
        "vulnerabilities": vulnerabilities,
        "risk_score": sum(
            10 if v["severity"] == "critical" else 
            7 if v["severity"] == "high" else
            4 if v["severity"] == "medium" else 1
            for v in vulnerabilities
        )
    }


@router.post("/scan/dependencies/npm")
async def scan_npm_dependencies(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """Scan npm package.json for vulnerabilities"""
    content = await file.read()
    package_json = json.loads(content)
    
    checker = DependencyChecker()
    vulnerabilities = await checker.check_npm_dependencies(package_json)
    
    return {
        "total_vulnerabilities": len(vulnerabilities),
        "vulnerabilities": vulnerabilities
    }


@router.post("/sbom/generate")
async def generate_sbom(
    request: SBOMRequest,
    requirements_file: Optional[UploadFile] = File(None),
    package_json_file: Optional[UploadFile] = File(None),
    current_user: User = Depends(get_current_user)
):
    """Generate Software Bill of Materials (SBOM)"""
    dependencies = {}
    
    # Parse Python dependencies
    if requirements_file:
        content = await requirements_file.read()
        requirements = content.decode("utf-8")
        checker = DependencyChecker()
        python_deps = checker._parse_requirements(requirements)
        dependencies["pypi"] = python_deps
    
    # Parse npm dependencies
    if package_json_file:
        content = await package_json_file.read()
        package_json = json.loads(content)
        npm_deps = []
        for name, version in package_json.get("dependencies", {}).items():
            npm_deps.append({"name": name, "version": version.lstrip("^~>=<")})
        dependencies["npm"] = npm_deps
    
    # Generate SBOM
    generator = SBOMGenerator()
    
    if request.format == "spdx":
        sbom = generator.generate_spdx_sbom(
            request.project_name,
            request.version,
            dependencies
        )
    else:
        sbom = generator.generate_sbom(
            request.project_name,
            request.version,
            dependencies
        )
    
    return sbom


@router.get("/compliance/check")
async def compliance_check(
    standard: str = Query(..., regex="^(pci-dss|hipaa|gdpr|soc2)$"),
    current_user: User = Depends(get_current_user)
):
    """Check compliance with security standards"""
    
    # Compliance checklist
    compliance_checks = {
        "pci-dss": [
            "Secrets not hardcoded in code",
            "All dependencies up to date",
            "Encryption in transit (HTTPS)",
            "Access control implemented",
            "Audit logging enabled"
        ],
        "hipaa": [
            "Data encryption at rest and in transit",
            "Access audit trails",
            "User authentication required",
            "Automatic logoff configured"
        ],
        "gdpr": [
            "Data minimization",
            "Right to erasure implemented",
            "Data portability available",
            "Consent management"
        ],
        "soc2": [
            "Security policies documented",
            "Change management process",
            "Incident response plan",
            "Regular security reviews"
        ]
    }
    
    return {
        "standard": standard,
        "checklist": compliance_checks.get(standard, []),
        "status": "requires_review"
    }
