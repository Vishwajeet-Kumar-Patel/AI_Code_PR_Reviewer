from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class ReviewStatus(str, Enum):
    """Review status enumeration"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class Severity(str, Enum):
    """Issue severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class IssueCategory(str, Enum):
    """Issue category types"""
    SECURITY = "security"
    QUALITY = "quality"
    COMPLEXITY = "complexity"
    STYLE = "style"
    PERFORMANCE = "performance"
    BEST_PRACTICE = "best_practice"


class CodeIssue(BaseModel):
    """Individual code issue detected during review"""
    category: IssueCategory
    severity: Severity
    title: str
    description: str
    file_path: str
    line_number: Optional[int] = None
    line_range: Optional[tuple[int, int]] = None
    code_snippet: Optional[str] = None
    suggestion: Optional[str] = None
    confidence: float = Field(ge=0.0, le=1.0, default=0.8)


class SecurityFinding(BaseModel):
    """Security-specific finding"""
    vulnerability_type: str
    cwe_id: Optional[str] = None
    owasp_category: Optional[str] = None
    severity: Severity
    description: str
    file_path: str
    line_number: Optional[int] = None
    remediation: str
    references: List[str] = []


class ComplexityMetrics(BaseModel):
    """Code complexity metrics"""
    cyclomatic_complexity: int
    cognitive_complexity: int
    lines_of_code: int
    maintainability_index: float = Field(ge=0.0, le=100.0)
    halstead_metrics: Optional[Dict[str, float]] = None


class FileAnalysis(BaseModel):
    """Analysis result for a single file"""
    file_path: str
    language: str
    lines_added: int
    lines_removed: int
    complexity: ComplexityMetrics
    issues: List[CodeIssue] = []
    security_findings: List[SecurityFinding] = []
    quality_score: float = Field(ge=0.0, le=100.0)


class ReviewSummary(BaseModel):
    """Summary of the entire review"""
    total_files: int
    total_lines_changed: int
    overall_quality_score: float = Field(ge=0.0, le=100.0)
    critical_issues: int
    high_issues: int
    medium_issues: int
    low_issues: int
    security_findings_count: int
    average_complexity: float
    recommendation: str
    strengths: List[str] = []
    weaknesses: List[str] = []


class ReviewRequest(BaseModel):
    """Request model for PR review"""
    repository: str = Field(..., description="Repository in format 'owner/repo'")
    pr_number: int = Field(..., description="Pull request number")
    include_security_scan: bool = True
    include_complexity_analysis: bool = True
    custom_rules: Optional[List[str]] = None


class ReviewResponse(BaseModel):
    """Response model for PR review"""
    review_id: str
    status: ReviewStatus
    repository: str
    pr_number: int
    created_at: datetime
    completed_at: Optional[datetime] = None
    summary: Optional[ReviewSummary] = None
    file_analyses: List[FileAnalysis] = []
    ai_insights: Optional[str] = None
    error_message: Optional[str] = None


class ReviewCreate(BaseModel):
    """Model for creating a new review"""
    repository: str
    pr_number: int
    author: str
    title: str
    description: Optional[str] = None
    base_branch: str
    head_branch: str
    files_changed: int
    metadata: Optional[Dict[str, Any]] = None


class ReviewUpdate(BaseModel):
    """Model for updating review status"""
    status: ReviewStatus
    summary: Optional[ReviewSummary] = None
    file_analyses: Optional[List[FileAnalysis]] = None
    ai_insights: Optional[str] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
