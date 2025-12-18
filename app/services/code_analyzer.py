from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime
from app.core.logging import logger
from app.models.review import (
    CodeIssue,
    FileAnalysis,
    ReviewSummary,
    ReviewResponse,
    ReviewStatus,
    ReviewCreate,
    IssueCategory,
    Severity,
)
from app.models.pr_data import PullRequestData
from app.models.code_analysis import AIAnalysisRequest
from app.services.github_service import GitHubService
from app.services.ai_service import AIService
from app.services.rag_service import RAGService
from app.services.complexity_analyzer import ComplexityAnalyzer
from app.services.security_scanner import SecurityScanner
from app.utils.language_detector import LanguageDetector


class CodeAnalyzer:
    """Main code analyzer orchestrating all analysis services"""
    
    def __init__(
        self,
        github_service: Optional[GitHubService] = None,
        ai_service: Optional[AIService] = None,
        rag_service: Optional[RAGService] = None,
    ):
        """Initialize code analyzer"""
        self.github_service = github_service or GitHubService()
        self.rag_service = rag_service or RAGService()
        self.ai_service = ai_service or AIService(self.rag_service)
        self.complexity_analyzer = ComplexityAnalyzer()
        self.security_scanner = SecurityScanner()
        self.language_detector = LanguageDetector()
        
        logger.info("Code analyzer initialized")
    
    async def analyze_pull_request(
        self,
        repository: str,
        pr_number: int,
        include_security: bool = True,
        include_complexity: bool = True,
    ) -> ReviewResponse:
        """Analyze a complete pull request"""
        review_id = str(uuid.uuid4())
        logger.info(f"Starting analysis for PR #{pr_number} in {repository} (ID: {review_id})")
        
        try:
            # Get PR data
            pr_data = self.github_service.get_pull_request(repository, pr_number)
            
            # Create review record
            review = ReviewResponse(
                review_id=review_id,
                status=ReviewStatus.IN_PROGRESS,
                repository=repository,
                pr_number=pr_number,
                created_at=datetime.now(),
            )
            
            # Analyze each file
            file_analyses = []
            for pr_file in pr_data.files:
                if pr_file.status == "removed":
                    continue
                
                try:
                    analysis = await self._analyze_file(
                        repository=repository,
                        file_path=pr_file.filename,
                        ref=pr_data.head_branch,
                        additions=pr_file.additions,
                        deletions=pr_file.deletions,
                        patch=pr_file.patch,
                        include_security=include_security,
                        include_complexity=include_complexity,
                    )
                    
                    if analysis:
                        file_analyses.append(analysis)
                except Exception as e:
                    logger.error(f"Failed to analyze file {pr_file.filename}: {e}")
                    continue
            
            # Generate summary
            summary = self._generate_summary(file_analyses)
            
            # Generate AI insights
            ai_insights = await self.ai_service.generate_review_summary(
                file_analyses=[fa.dict() for fa in file_analyses],
                pr_context={
                    "title": pr_data.title,
                    "author": pr_data.author,
                    "description": pr_data.description,
                }
            )
            
            # Update review
            review.status = ReviewStatus.COMPLETED
            review.completed_at = datetime.now()
            review.summary = summary
            review.file_analyses = file_analyses
            review.ai_insights = ai_insights
            
            logger.info(f"Completed analysis for PR #{pr_number} (ID: {review_id})")
            return review
            
        except Exception as e:
            logger.error(f"Failed to analyze PR #{pr_number}: {e}")
            return ReviewResponse(
                review_id=review_id,
                status=ReviewStatus.FAILED,
                repository=repository,
                pr_number=pr_number,
                created_at=datetime.now(),
                completed_at=datetime.now(),
                error_message=str(e),
            )
    
    async def _analyze_file(
        self,
        repository: str,
        file_path: str,
        ref: str,
        additions: int,
        deletions: int,
        patch: Optional[str],
        include_security: bool,
        include_complexity: bool,
    ) -> Optional[FileAnalysis]:
        """Analyze a single file"""
        logger.info(f"Analyzing file: {file_path}")
        
        # Detect language
        language = self.language_detector.detect(file_path)
        if not language:
            logger.warning(f"Unsupported language for file: {file_path}")
            return None
        
        # Get file content
        content = self.github_service.get_file_content(repository, file_path, ref)
        if not content:
            logger.warning(f"Could not get content for file: {file_path}")
            return None
        
        # Initialize issues and findings
        issues: List[CodeIssue] = []
        security_findings = []
        
        # Complexity analysis
        complexity = self.complexity_analyzer.analyze(content, language, file_path)
        
        # Detect code smells
        smells = self.complexity_analyzer.detect_code_smells(content, language, file_path)
        for smell in smells:
            issues.append(CodeIssue(
                category=IssueCategory.COMPLEXITY,
                severity=Severity(smell.severity),
                title=smell.smell_type.replace("_", " ").title(),
                description=smell.description,
                file_path=file_path,
                line_range=smell.line_range,
                suggestion=smell.refactoring_suggestion,
            ))
        
        # Security scan
        if include_security:
            security_findings = self.security_scanner.scan(content, language, file_path)
        
        # AI analysis
        try:
            ai_request = AIAnalysisRequest(
                code=content[:4000],  # Limit to avoid token limits
                language=language,
                file_path=file_path,
                context=patch[:1000] if patch else None,
                include_rag=True,
            )
            
            ai_response = await self.ai_service.analyze_code(ai_request)
            
            # Convert AI suggestions to issues
            for suggestion in ai_response.suggestions[:5]:
                issues.append(CodeIssue(
                    category=IssueCategory.QUALITY,
                    severity=Severity.MEDIUM,
                    title="Code Quality Issue",
                    description=suggestion,
                    file_path=file_path,
                    suggestion=suggestion,
                    confidence=ai_response.confidence,
                ))
        except Exception as e:
            logger.error(f"AI analysis failed for {file_path}: {e}")
        
        # Calculate quality score
        quality_score = self._calculate_quality_score(
            complexity=complexity,
            issues=issues,
            security_findings=security_findings,
        )
        
        return FileAnalysis(
            file_path=file_path,
            language=language,
            lines_added=additions,
            lines_removed=deletions,
            complexity=complexity,
            issues=issues,
            security_findings=security_findings,
            quality_score=quality_score,
        )
    
    def _calculate_quality_score(
        self,
        complexity: Any,
        issues: List[CodeIssue],
        security_findings: List[Any],
    ) -> float:
        """Calculate overall quality score for a file"""
        score = 100.0
        
        # Deduct for complexity
        if complexity.cyclomatic_complexity > 10:
            score -= min(20, (complexity.cyclomatic_complexity - 10) * 2)
        
        if complexity.maintainability_index < 50:
            score -= (50 - complexity.maintainability_index) * 0.5
        
        # Deduct for issues
        severity_weights = {
            Severity.CRITICAL: 15,
            Severity.HIGH: 10,
            Severity.MEDIUM: 5,
            Severity.LOW: 2,
            Severity.INFO: 1,
        }
        
        for issue in issues:
            score -= severity_weights.get(issue.severity, 3)
        
        # Deduct for security findings
        for finding in security_findings:
            score -= severity_weights.get(finding.severity, 5)
        
        return max(0.0, min(100.0, score))
    
    def _generate_summary(self, file_analyses: List[FileAnalysis]) -> ReviewSummary:
        """Generate review summary from file analyses"""
        total_files = len(file_analyses)
        total_lines_changed = sum(fa.lines_added + fa.lines_removed for fa in file_analyses)
        
        # Count issues by severity
        critical_issues = 0
        high_issues = 0
        medium_issues = 0
        low_issues = 0
        
        for fa in file_analyses:
            for issue in fa.issues:
                if issue.severity == Severity.CRITICAL:
                    critical_issues += 1
                elif issue.severity == Severity.HIGH:
                    high_issues += 1
                elif issue.severity == Severity.MEDIUM:
                    medium_issues += 1
                elif issue.severity == Severity.LOW:
                    low_issues += 1
        
        # Security findings
        security_findings_count = sum(len(fa.security_findings) for fa in file_analyses)
        
        # Average complexity
        avg_complexity = sum(fa.complexity.cyclomatic_complexity for fa in file_analyses) / total_files if total_files > 0 else 0
        
        # Overall quality score
        overall_score = sum(fa.quality_score for fa in file_analyses) / total_files if total_files > 0 else 0
        
        # Generate recommendation
        if critical_issues > 0 or security_findings_count > 3:
            recommendation = "REQUEST_CHANGES"
        elif high_issues > 5 or medium_issues > 10:
            recommendation = "COMMENT"
        else:
            recommendation = "APPROVE"
        
        # Identify strengths and weaknesses
        strengths = []
        weaknesses = []
        
        if overall_score > 80:
            strengths.append("High code quality overall")
        if security_findings_count == 0:
            strengths.append("No security vulnerabilities detected")
        if avg_complexity < 5:
            strengths.append("Low code complexity")
        
        if critical_issues > 0:
            weaknesses.append(f"{critical_issues} critical issues found")
        if security_findings_count > 0:
            weaknesses.append(f"{security_findings_count} security findings")
        if avg_complexity > 10:
            weaknesses.append("High code complexity")
        
        return ReviewSummary(
            total_files=total_files,
            total_lines_changed=total_lines_changed,
            overall_quality_score=overall_score,
            critical_issues=critical_issues,
            high_issues=high_issues,
            medium_issues=medium_issues,
            low_issues=low_issues,
            security_findings_count=security_findings_count,
            average_complexity=avg_complexity,
            recommendation=recommendation,
            strengths=strengths,
            weaknesses=weaknesses,
        )
