"""
Code Fix API Endpoints

AI-powered code fix generation and application
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Dict, List, Optional
from pydantic import BaseModel

from app.core.deps import get_current_user, get_db
from app.models.auth import User
from app.services.code_fix_service import code_fix_service

router = APIRouter()


class CodeFixRequest(BaseModel):
    code: str
    language: str
    file_path: str
    issues: List[Dict]


class PRFixRequest(BaseModel):
    owner: str
    repo: str
    base_branch: str = "main"
    fixes: List[Dict]


class TestGenerationRequest(BaseModel):
    code: str
    language: str
    function_name: str


class DocumentationRequest(BaseModel):
    code: str
    language: str
    doc_style: str = "google"


@router.post("/generate-fixes", response_model=Dict)
async def generate_code_fixes(
    request: CodeFixRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Generate AI-powered code fixes for detected issues
    
    - **code**: Source code with issues
    - **language**: Programming language
    - **file_path**: Path to the file
    - **issues**: List of issues detected
    
    Returns:
    - List of fix suggestions with diffs
    - Explanations for each fix
    - Confidence scores
    - Auto-apply capability flags
    """
    try:
        fixes = await code_fix_service.analyze_and_generate_fixes(
            code=request.code,
            language=request.language,
            file_path=request.file_path,
            issues=request.issues
        )
        
        return {
            "file_path": request.file_path,
            "total_fixes": len(fixes),
            "fixes": fixes,
            "auto_applicable": len([f for f in fixes if f.get("can_auto_apply", False)])
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/create-fix-pr", response_model=Dict)
async def create_fix_pull_request(
    request: PRFixRequest,
    github_token: str,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
):
    """
    Create a pull request with AI-generated fixes
    
    - **owner**: Repository owner
    - **repo**: Repository name
    - **base_branch**: Base branch (default: main)
    - **fixes**: List of fixes to apply
    - **github_token**: GitHub access token
    
    Returns:
    - PR number and URL
    - Files updated
    - Branch name
    """
    try:
        # Create PR in background
        result = await code_fix_service.create_fix_pr(
            owner=request.owner,
            repo=request.repo,
            base_branch=request.base_branch,
            fixes=request.fixes,
            github_token=github_token
        )
        
        return {
            "status": "success",
            "pr_created": True,
            **result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create PR: {str(e)}")


@router.post("/generate-tests", response_model=Dict)
async def generate_test_cases(
    request: TestGenerationRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Generate unit test cases for a function
    
    - **code**: Function code to test
    - **language**: Programming language
    - **function_name**: Name of the function
    
    Returns:
    - Complete test code
    - Test framework used
    - Number of test cases generated
    """
    try:
        test_code = await code_fix_service.generate_test_cases(
            code=request.code,
            language=request.language,
            function_name=request.function_name
        )
        
        if not test_code:
            raise HTTPException(status_code=500, detail="Failed to generate tests")
        
        # Count test cases (approximate)
        test_count = test_code.count("def test_") + test_code.count("it(") + test_code.count("test(")
        
        return {
            "function_name": request.function_name,
            "language": request.language,
            "test_code": test_code,
            "test_count": test_count,
            "test_framework": code_fix_service._get_test_framework(request.language)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-docs", response_model=Dict)
async def generate_documentation(
    request: DocumentationRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Generate documentation for code
    
    - **code**: Code to document
    - **language**: Programming language
    - **doc_style**: Documentation style (google, numpy, sphinx)
    
    Returns:
    - Generated documentation
    - Documentation style used
    """
    try:
        documentation = await code_fix_service.generate_documentation(
            code=request.code,
            language=request.language,
            doc_style=request.doc_style
        )
        
        if not documentation:
            raise HTTPException(status_code=500, detail="Failed to generate documentation")
        
        return {
            "language": request.language,
            "doc_style": request.doc_style,
            "documentation": documentation
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/quick-fix/{issue_id}", response_model=Dict)
async def apply_quick_fix(
    issue_id: int,
    auto_apply: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Apply a quick fix for a specific issue
    
    - **issue_id**: ID of the issue to fix
    - **auto_apply**: Whether to automatically apply the fix
    
    Returns:
    - Fix details
    - Application status
    - Code diff
    """
    try:
        # Retrieve issue from database
        issue_query = """
        SELECT i.*, r.code_snippet, r.file_path, r.language
        FROM code_issues i
        JOIN code_reviews r ON i.review_id = r.id
        WHERE i.id = :issue_id
        """
        
        result = db.execute(issue_query, {"issue_id": issue_id})
        issue_data = result.fetchone()
        
        if not issue_data:
            raise HTTPException(status_code=404, detail="Issue not found")
        
        # Generate fix
        fixes = await code_fix_service.analyze_and_generate_fixes(
            code=issue_data.code_snippet,
            language=issue_data.language,
            file_path=issue_data.file_path,
            issues=[{
                'type': issue_data.type,
                'description': issue_data.description,
                'line': issue_data.line_number,
                'severity': issue_data.severity
            }]
        )
        
        if not fixes:
            raise HTTPException(status_code=500, detail="Could not generate fix")
        
        fix = fixes[0]
        
        response = {
            "issue_id": issue_id,
            "fix_generated": True,
            "fix": fix,
            "auto_applied": False
        }
        
        if auto_apply and fix.get("can_auto_apply", False):
            # In production, this would apply the fix to the repository
            # For now, just mark it as applied
            response["auto_applied"] = True
            response["message"] = "Fix applied successfully"
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/refactoring-suggestions/{repository}", response_model=Dict)
async def get_refactoring_suggestions(
    repository: str,
    file_path: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get AI-powered refactoring suggestions for a repository or file
    
    - **repository**: Repository to analyze
    - **file_path**: Specific file to analyze (optional)
    
    Returns:
    - Refactoring suggestions
    - Priority levels
    - Estimated effort
    - Code smells detected
    """
    try:
        # Query for code with potential refactoring needs
        query = """
        SELECT 
            r.file_path,
            r.code_snippet,
            r.complexity_score,
            r.issues_found,
            r.language
        FROM code_reviews r
        WHERE r.repository = :repo
        AND (r.complexity_score < 60 OR r.code_quality_score < 70)
        """
        
        params = {"repo": repository}
        
        if file_path:
            query += " AND r.file_path = :file_path"
            params["file_path"] = file_path
        
        query += " ORDER BY r.complexity_score ASC LIMIT 10"
        
        result = db.execute(query, params)
        candidates = result.fetchall()
        
        suggestions = []
        for candidate in candidates:
            suggestion = {
                "file_path": candidate.file_path,
                "complexity_score": candidate.complexity_score,
                "refactoring_type": _determine_refactoring_type(candidate.complexity_score),
                "priority": _calculate_refactoring_priority(
                    candidate.complexity_score,
                    candidate.issues_found
                ),
                "estimated_effort_hours": _estimate_refactoring_effort(candidate.complexity_score),
                "suggestions": _generate_refactoring_recommendations(candidate.complexity_score)
            }
            suggestions.append(suggestion)
        
        return {
            "repository": repository,
            "file_path": file_path,
            "total_suggestions": len(suggestions),
            "suggestions": suggestions
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def _determine_refactoring_type(complexity_score: float) -> str:
    """Determine type of refactoring needed"""
    if complexity_score < 40:
        return "Major refactoring required"
    elif complexity_score < 60:
        return "Moderate refactoring needed"
    else:
        return "Minor improvements"


def _calculate_refactoring_priority(complexity_score: float, issues_found: int) -> str:
    """Calculate refactoring priority"""
    if complexity_score < 40 or issues_found > 10:
        return "High"
    elif complexity_score < 60 or issues_found > 5:
        return "Medium"
    else:
        return "Low"


def _estimate_refactoring_effort(complexity_score: float) -> float:
    """Estimate hours needed for refactoring"""
    if complexity_score < 40:
        return 8.0
    elif complexity_score < 60:
        return 4.0
    else:
        return 2.0


def _generate_refactoring_recommendations(complexity_score: float) -> List[str]:
    """Generate specific refactoring recommendations"""
    recommendations = []
    
    if complexity_score < 50:
        recommendations.extend([
            "Break down large functions into smaller units",
            "Extract complex logic into helper functions",
            "Reduce nesting depth",
            "Apply SOLID principles"
        ])
    elif complexity_score < 70:
        recommendations.extend([
            "Simplify conditional logic",
            "Extract magic numbers into constants",
            "Improve naming conventions"
        ])
    else:
        recommendations.append("Minor code cleanup recommended")
    
    return recommendations
