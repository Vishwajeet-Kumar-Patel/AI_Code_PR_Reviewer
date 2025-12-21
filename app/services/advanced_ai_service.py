"""
Advanced AI features: Code fixes, auto-PR creation, learning from feedback
"""
from typing import List, Dict, Optional
from app.services.ai_service import AIService
from app.core.logging import logger
from app.db.database import get_db
from app.db.models import Review, ReviewFeedback
import difflib


class CodeFixGenerator:
    """Generate code fixes using AI"""
    
    def __init__(self, ai_service: AIService):
        self.ai_service = ai_service
    
    async def generate_fix(
        self,
        code: str,
        issue_description: str,
        language: str,
        context: Optional[str] = None
    ) -> Dict:
        """Generate code fix for an issue"""
        
        prompt = f"""You are an expert code reviewer. Generate a fix for the following issue:

Language: {language}
Issue: {issue_description}

Original Code:
```{language}
{code}
```

{f"Additional Context: {context}" if context else ""}

Provide:
1. Fixed code
2. Explanation of changes
3. Potential side effects
4. Testing recommendations

Return as JSON:
{{
    "fixed_code": "...",
    "explanation": "...",
    "changes_summary": "...",
    "side_effects": ["..."],
    "testing_recommendations": ["..."],
    "confidence": 0.9
}}
"""
        
        try:
            response = await self.ai_service.get_ai_response(prompt)
            
            # Parse response
            import json
            fix_data = json.loads(response)
            
            # Generate diff
            diff = self._generate_diff(code, fix_data["fixed_code"], language)
            fix_data["diff"] = diff
            
            return fix_data
        
        except Exception as e:
            logger.error(f"Error generating fix: {e}")
            return {
                "error": str(e),
                "fixed_code": None,
                "explanation": "Unable to generate fix"
            }
    
    def _generate_diff(self, original: str, fixed: str, language: str) -> str:
        """Generate unified diff"""
        original_lines = original.splitlines(keepends=True)
        fixed_lines = fixed.splitlines(keepends=True)
        
        diff = difflib.unified_diff(
            original_lines,
            fixed_lines,
            fromfile=f"original.{language}",
            tofile=f"fixed.{language}",
            lineterm=""
        )
        
        return "".join(diff)
    
    async def batch_generate_fixes(
        self,
        issues: List[Dict],
        language: str
    ) -> List[Dict]:
        """Generate fixes for multiple issues"""
        fixes = []
        
        for issue in issues:
            fix = await self.generate_fix(
                code=issue.get("code", ""),
                issue_description=issue.get("description", ""),
                language=language,
                context=issue.get("context")
            )
            
            fixes.append({
                "issue": issue,
                "fix": fix
            })
        
        return fixes


class AutoPRCreator:
    """Automatically create PRs with fixes"""
    
    def __init__(self, github_service, code_fix_generator: CodeFixGenerator):
        self.github_service = github_service
        self.code_fix_generator = code_fix_generator
    
    async def create_fix_pr(
        self,
        repo_full_name: str,
        base_branch: str,
        issues_with_files: List[Dict],
        github_token: str
    ) -> Dict:
        """
        Create a PR with automated fixes
        
        Args:
            repo_full_name: owner/repo
            base_branch: base branch name
            issues_with_files: [{"file_path": "...", "issue": {...}, "code": "..."}]
            github_token: GitHub access token
        
        Returns:
            PR details
        """
        try:
            # Generate fixes
            fixes = []
            for item in issues_with_files:
                fix = await self.code_fix_generator.generate_fix(
                    code=item["code"],
                    issue_description=item["issue"]["description"],
                    language=item.get("language", "python"),
                    context=item.get("context")
                )
                
                if fix.get("fixed_code"):
                    fixes.append({
                        "file_path": item["file_path"],
                        "original_code": item["code"],
                        "fixed_code": fix["fixed_code"],
                        "explanation": fix["explanation"],
                        "diff": fix["diff"]
                    })
            
            if not fixes:
                return {"error": "No valid fixes generated"}
            
            # Create branch
            branch_name = f"ai-code-review-fixes-{import_time()}"
            
            # Create commits
            pr_body = self._generate_pr_description(fixes)
            
            # Use GitHub API to create PR
            pr_data = await self.github_service.create_pull_request(
                repo_full_name=repo_full_name,
                title="🤖 AI Code Review: Automated Fixes",
                body=pr_body,
                head=branch_name,
                base=base_branch,
                files=fixes,
                token=github_token
            )
            
            return pr_data
        
        except Exception as e:
            logger.error(f"Error creating auto-fix PR: {e}")
            return {"error": str(e)}
    
    def _generate_pr_description(self, fixes: List[Dict]) -> str:
        """Generate PR description"""
        description = "# 🤖 Automated Code Fixes\n\n"
        description += "This PR contains automated fixes suggested by AI code review.\n\n"
        description += "## Changes\n\n"
        
        for idx, fix in enumerate(fixes, 1):
            description += f"### {idx}. {fix['file_path']}\n\n"
            description += f"{fix['explanation']}\n\n"
            description += "```diff\n"
            description += fix['diff'][:500]  # Limit diff size
            description += "\n```\n\n"
        
        description += "## ⚠️ Review Required\n\n"
        description += "Please carefully review all changes before merging.\n"
        description += "- Test the changes thoroughly\n"
        description += "- Verify no regressions\n"
        description += "- Check for edge cases\n"
        
        return description


class FeedbackLearningService:
    """Learn from user feedback to improve reviews"""
    
    def __init__(self, ai_service: AIService):
        self.ai_service = ai_service
    
    async def record_feedback(
        self,
        review_id: str,
        feedback_type: str,
        rating: int,
        comment: Optional[str],
        user_id: str,
        db
    ):
        """Record user feedback"""
        from datetime import datetime
        
        feedback = ReviewFeedback(
            review_id=review_id,
            user_id=user_id,
            feedback_type=feedback_type,
            rating=rating,
            comment=comment,
            created_at=datetime.utcnow()
        )
        
        db.add(feedback)
        db.commit()
        
        logger.info(f"Feedback recorded for review {review_id}: {rating}/5")
        
        return feedback
    
    async def analyze_feedback_patterns(self, db) -> Dict:
        """Analyze feedback to improve AI"""
        from sqlalchemy import func
        
        # Get feedback statistics
        stats = db.query(
            func.avg(ReviewFeedback.rating).label("avg_rating"),
            func.count(ReviewFeedback.id).label("total_feedback"),
            ReviewFeedback.feedback_type,
        ).group_by(ReviewFeedback.feedback_type).all()
        
        # Identify low-rated patterns
        low_rated = db.query(ReviewFeedback).filter(
            ReviewFeedback.rating < 3
        ).limit(100).all()
        
        patterns = {
            "statistics": [
                {
                    "type": stat.feedback_type,
                    "avg_rating": float(stat.avg_rating),
                    "count": stat.total_feedback
                }
                for stat in stats
            ],
            "improvement_areas": self._identify_improvement_areas(low_rated)
        }
        
        return patterns
    
    def _identify_improvement_areas(self, low_rated_feedback: List) -> List[str]:
        """Identify areas needing improvement"""
        areas = set()
        
        for feedback in low_rated_feedback:
            if feedback.comment:
                # Simple keyword extraction
                if "false positive" in feedback.comment.lower():
                    areas.add("reduce_false_positives")
                if "missed" in feedback.comment.lower():
                    areas.add("improve_detection")
                if "explanation" in feedback.comment.lower():
                    areas.add("better_explanations")
        
        return list(areas)


def import_time():
    """Get current timestamp for branch names"""
    from datetime import datetime
    return datetime.utcnow().strftime("%Y%m%d%H%M%S")
