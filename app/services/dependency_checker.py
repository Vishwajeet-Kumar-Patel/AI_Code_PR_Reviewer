"""
Dependency vulnerability checker
"""
import re
import json
from typing import List, Dict, Optional
import httpx
from app.core.logging import logger


class DependencyChecker:
    """Check dependencies for known vulnerabilities"""
    
    def __init__(self):
        self.vulnerability_db_url = "https://osv.dev/v1/query"
    
    async def check_python_dependencies(self, requirements_content: str) -> List[Dict]:
        """Check Python requirements.txt for vulnerabilities"""
        dependencies = self._parse_requirements(requirements_content)
        vulnerabilities = []
        
        for dep in dependencies:
            vulns = await self._check_osv_database(dep["name"], dep["version"], "PyPI")
            if vulns:
                vulnerabilities.extend(vulns)
        
        return vulnerabilities
    
    async def check_npm_dependencies(self, package_json: Dict) -> List[Dict]:
        """Check npm package.json for vulnerabilities"""
        dependencies = package_json.get("dependencies", {})
        dependencies.update(package_json.get("devDependencies", {}))
        
        vulnerabilities = []
        
        for name, version in dependencies.items():
            # Clean version string
            version = version.lstrip("^~>=<")
            vulns = await self._check_osv_database(name, version, "npm")
            if vulns:
                vulnerabilities.extend(vulns)
        
        return vulnerabilities
    
    def _parse_requirements(self, content: str) -> List[Dict]:
        """Parse requirements.txt"""
        dependencies = []
        
        for line in content.split("\n"):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            
            # Parse package==version
            match = re.match(r"([a-zA-Z0-9_-]+)(==|>=|<=|~=|>|<)([0-9.]+)", line)
            if match:
                dependencies.append({
                    "name": match.group(1),
                    "version": match.group(3),
                    "operator": match.group(2)
                })
        
        return dependencies
    
    async def _check_osv_database(
        self,
        package_name: str,
        version: str,
        ecosystem: str
    ) -> List[Dict]:
        """Query OSV vulnerability database"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    self.vulnerability_db_url,
                    json={
                        "package": {"name": package_name, "ecosystem": ecosystem},
                        "version": version
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    vulns = data.get("vulns", [])
                    
                    return [
                        {
                            "package": package_name,
                            "version": version,
                            "vulnerability_id": vuln.get("id"),
                            "summary": vuln.get("summary"),
                            "severity": self._extract_severity(vuln),
                            "cvss_score": self._extract_cvss(vuln),
                            "fixed_versions": self._extract_fixed_versions(vuln),
                            "references": vuln.get("references", [])[:3]
                        }
                        for vuln in vulns
                    ]
        
        except Exception as e:
            logger.error(f"Error checking vulnerability for {package_name}: {e}")
        
        return []
    
    def _extract_severity(self, vuln: Dict) -> str:
        """Extract severity from vulnerability data"""
        severity = vuln.get("database_specific", {}).get("severity")
        if severity:
            return severity.lower()
        
        # Estimate from CVSS score
        cvss = self._extract_cvss(vuln)
        if cvss:
            if cvss >= 9.0:
                return "critical"
            elif cvss >= 7.0:
                return "high"
            elif cvss >= 4.0:
                return "medium"
            else:
                return "low"
        
        return "unknown"
    
    def _extract_cvss(self, vuln: Dict) -> Optional[float]:
        """Extract CVSS score"""
        try:
            score = vuln.get("severity", [{}])[0].get("score")
            if score:
                return float(score.split("/")[0])
        except:
            pass
        return None
    
    def _extract_fixed_versions(self, vuln: Dict) -> List[str]:
        """Extract fixed versions"""
        fixed = []
        for affected in vuln.get("affected", []):
            for range_info in affected.get("ranges", []):
                for event in range_info.get("events", []):
                    if "fixed" in event:
                        fixed.append(event["fixed"])
        return fixed


class SBOMGenerator:
    """Generate Software Bill of Materials"""
    
    def generate_sbom(
        self,
        project_name: str,
        version: str,
        dependencies: Dict[str, List[Dict]]
    ) -> Dict:
        """
        Generate SBOM in CycloneDX format
        
        Args:
            project_name: Project name
            version: Project version
            dependencies: Dict mapping ecosystem -> list of deps
        
        Returns:
            SBOM in CycloneDX JSON format
        """
        components = []
        
        for ecosystem, deps in dependencies.items():
            for dep in deps:
                components.append({
                    "type": "library",
                    "name": dep["name"],
                    "version": dep.get("version", "unknown"),
                    "purl": f"pkg:{ecosystem}/{dep['name']}@{dep.get('version', 'unknown')}"
                })
        
        sbom = {
            "bomFormat": "CycloneDX",
            "specVersion": "1.4",
            "version": 1,
            "metadata": {
                "component": {
                    "type": "application",
                    "name": project_name,
                    "version": version
                }
            },
            "components": components
        }
        
        return sbom
    
    def generate_spdx_sbom(
        self,
        project_name: str,
        version: str,
        dependencies: Dict[str, List[Dict]]
    ) -> Dict:
        """Generate SBOM in SPDX format"""
        packages = []
        
        for ecosystem, deps in dependencies.items():
            for dep in deps:
                packages.append({
                    "name": dep["name"],
                    "versionInfo": dep.get("version", "unknown"),
                    "downloadLocation": f"https://{ecosystem}.org/package/{dep['name']}",
                    "filesAnalyzed": False
                })
        
        return {
            "spdxVersion": "SPDX-2.3",
            "dataLicense": "CC0-1.0",
            "SPDXID": "SPDXRef-DOCUMENT",
            "name": project_name,
            "documentNamespace": f"https://sbom.example.com/{project_name}-{version}",
            "creationInfo": {
                "created": "2024-01-01T00:00:00Z",
                "creators": ["Tool: AI Code Reviewer"]
            },
            "packages": packages
        }
