from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum


class AnalysisType(str, Enum):
    """Type of code analysis"""
    QUALITY = "quality"
    SECURITY = "security"
    COMPLEXITY = "complexity"
    STYLE = "style"
    PERFORMANCE = "performance"


class CodePattern(BaseModel):
    """Code pattern detected during analysis"""
    pattern_type: str
    description: str
    occurrences: int
    examples: List[str] = []


class QualityMetrics(BaseModel):
    """Code quality metrics"""
    maintainability_index: float = Field(ge=0.0, le=100.0)
    technical_debt_ratio: float = Field(ge=0.0, le=1.0)
    code_duplication: float = Field(ge=0.0, le=100.0)
    test_coverage: Optional[float] = Field(None, ge=0.0, le=100.0)
    documentation_coverage: float = Field(ge=0.0, le=100.0)


class StyleViolation(BaseModel):
    """Style/convention violation"""
    rule: str
    description: str
    file_path: str
    line_number: int
    severity: str
    suggestion: Optional[str] = None


class PerformanceIssue(BaseModel):
    """Performance-related issue"""
    issue_type: str
    description: str
    file_path: str
    line_number: Optional[int] = None
    impact: str  # high, medium, low
    recommendation: str
    estimated_improvement: Optional[str] = None


class BestPracticeViolation(BaseModel):
    """Best practice violation"""
    practice: str
    description: str
    file_path: str
    line_number: Optional[int] = None
    language: str
    recommendation: str
    references: List[str] = []


class CodeSmell(BaseModel):
    """Code smell detection"""
    smell_type: str
    description: str
    file_path: str
    line_range: tuple[int, int]
    severity: str
    refactoring_suggestion: str


class AnalysisResult(BaseModel):
    """Complete analysis result for a code change"""
    analysis_type: AnalysisType
    file_path: str
    language: str
    quality_metrics: Optional[QualityMetrics] = None
    patterns: List[CodePattern] = []
    style_violations: List[StyleViolation] = []
    performance_issues: List[PerformanceIssue] = []
    best_practice_violations: List[BestPracticeViolation] = []
    code_smells: List[CodeSmell] = []
    overall_score: float = Field(ge=0.0, le=100.0)
    summary: str
    recommendations: List[str] = []


class RAGContext(BaseModel):
    """Context retrieved from RAG system"""
    query: str
    relevant_documents: List[Dict[str, Any]] = []
    best_practices: List[str] = []
    examples: List[str] = []
    confidence_score: float = Field(ge=0.0, le=1.0)


class AIAnalysisRequest(BaseModel):
    """Request for AI-powered analysis"""
    code: str
    language: str
    context: Optional[str] = None
    file_path: Optional[str] = None
    analysis_types: List[AnalysisType] = [AnalysisType.QUALITY]
    include_rag: bool = True


class AIAnalysisResponse(BaseModel):
    """Response from AI analysis"""
    insights: str
    issues_found: int
    suggestions: List[str] = []
    code_improvements: Optional[str] = None
    confidence: float = Field(ge=0.0, le=1.0)
    rag_context_used: bool = False
