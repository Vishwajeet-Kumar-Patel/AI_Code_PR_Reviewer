"""
AI-Powered Code Fix Service

This service provides:
- Automatic code fix suggestions
- One-click PR generation with fixes
- Refactoring recommendations
- Test case generation
- Documentation auto-generation
"""

import asyncio
import logging
import re
from typing import Dict, List, Optional, Tuple
from datetime import datetime

import openai
from github import Github, GithubException

from app.core.config import settings
from app.services.ai_service import ai_service
from app.services.github_service import github_service

logger = logging.getLogger(__name__)


class CodeFixService:
    """Service for generating and applying AI-powered code fixes"""
    
    def __init__(self):
        self.fix_templates = self._load_fix_templates()
    
    def _load_fix_templates(self) -> Dict:
        """Load code fix templates for common issues"""
        return {
            'security': {
                'hardcoded_secret': {
                    'pattern': r'(password|token|api_key|secret)\s*=\s*["\']([^"\']+)["\']',
                    'fix_template': 'Use environment variables: os.getenv("{var_name}")',
                    'severity': 'critical'
                },
                'sql_injection': {
                    'pattern': r'execute\((.*?)\+',
                    'fix_template': 'Use parameterized queries with placeholders',
                    'severity': 'critical'
                },
                'xss_vulnerability': {
                    'pattern': r'innerHTML\s*=',
                    'fix_template': 'Use textContent or sanitize with DOMPurify',
                    'severity': 'high'
                }
            },
            'performance': {
                'inefficient_loop': {
                    'pattern': r'for.*in.*:\s*if.*==',
                    'fix_template': 'Use list comprehension or filter()',
                    'severity': 'medium'
                },
                'repeated_computation': {
                    'pattern': r'(\w+\([^)]+\)).*\1',
                    'fix_template': 'Cache the result in a variable',
                    'severity': 'low'
                }
            },
            'code_quality': {
                'long_function': {
                    'threshold': 50,
                    'fix_template': 'Extract smaller helper functions',
                    'severity': 'medium'
                },
                'magic_numbers': {
                    'pattern': r'\b\d{2,}\b',
                    'fix_template': 'Define as named constants',
                    'severity': 'low'
                }
            }
        }
    
    async def analyze_and_generate_fixes(
        self,
        code: str,
        language: str,
        file_path: str,
        issues: List[Dict]
    ) -> List[Dict]:
        """
        Analyze code issues and generate fix suggestions
        
        Args:
            code: Source code
            language: Programming language
            file_path: File path
            issues: List of detected issues
            
        Returns:
            List of fix suggestions with diffs
        """
        logger.info(f"Generating fixes for {len(issues)} issues in {file_path}")
        
        fixes = []
        
        for issue in issues:
            try:
                fix = await self._generate_fix_for_issue(
                    code=code,
                    language=language,
                    file_path=file_path,
                    issue=issue
                )
                if fix:
                    fixes.append(fix)
            except Exception as e:
                logger.error(f"Failed to generate fix for issue: {e}")
        
        logger.info(f"Generated {len(fixes)} fixes")
        return fixes
    
    async def _generate_fix_for_issue(
        self,
        code: str,
        language: str,
        file_path: str,
        issue: Dict
    ) -> Optional[Dict]:
        """Generate a fix for a specific issue using AI"""
        
        issue_type = issue.get('type', 'general')
        issue_line = issue.get('line', 0)
        issue_description = issue.get('description', '')
        
        # Extract code context around the issue
        code_lines = code.split('\n')
        start_line = max(0, issue_line - 5)
        end_line = min(len(code_lines), issue_line + 5)
        context = '\n'.join(code_lines[start_line:end_line])
        
        # Prepare prompt for AI
        prompt = f"""You are an expert code reviewer. Fix the following {language} code issue:

**Issue**: {issue_description}
**Type**: {issue_type}
**Line**: {issue_line}

**Code Context**:
```{language}
{context}
```

Provide:
1. Fixed code (only the changed lines)
2. Explanation of the fix
3. Why this fix is better

Format your response as:
FIXED_CODE:
<fixed code here>

EXPLANATION:
<explanation here>

WHY_BETTER:
<rationale here>
"""
        
        try:
            # Call AI service
            response = await ai_service.get_completion(
                prompt=prompt,
                model=settings.OPENAI_MODEL,
                temperature=0.2,
                max_tokens=1000
            )
            
            # Parse response
            fixed_code = self._extract_section(response, 'FIXED_CODE')
            explanation = self._extract_section(response, 'EXPLANATION')
            why_better = self._extract_section(response, 'WHY_BETTER')
            
            if not fixed_code:
                return None
            
            # Generate diff
            diff = self._generate_diff(
                original=context,
                fixed=fixed_code,
                file_path=file_path,
                start_line=start_line
            )
            
            return {
                'issue': issue,
                'file_path': file_path,
                'line': issue_line,
                'original_code': context,
                'fixed_code': fixed_code,
                'diff': diff,
                'explanation': explanation,
                'why_better': why_better,
                'confidence': 0.85,
                'can_auto_apply': issue.get('severity') != 'critical'
            }
            
        except Exception as e:
            logger.error(f"AI fix generation failed: {e}")
            return None
    
    def _extract_section(self, text: str, section_name: str) -> str:
        """Extract a section from formatted AI response"""
        pattern = rf"{section_name}:\s*(.+?)(?=\n[A-Z_]+:|$)"
        match = re.search(pattern, text, re.DOTALL)
        if match:
            content = match.group(1).strip()
            # Remove code fences if present
            content = re.sub(r'^```\w*\n', '', content)
            content = re.sub(r'\n```$', '', content)
            return content
        return ""
    
    def _generate_diff(
        self,
        original: str,
        fixed: str,
        file_path: str,
        start_line: int
    ) -> str:
        """Generate unified diff format"""
        import difflib
        
        original_lines = original.split('\n')
        fixed_lines = fixed.split('\n')
        
        diff = difflib.unified_diff(
            original_lines,
            fixed_lines,
            fromfile=f'a/{file_path}',
            tofile=f'b/{file_path}',
            lineterm='',
            n=3
        )
        
        return '\n'.join(diff)
    
    async def create_fix_pr(
        self,
        owner: str,
        repo: str,
        base_branch: str,
        fixes: List[Dict],
        github_token: str
    ) -> Dict:
        """
        Create a pull request with all fixes applied
        
        Args:
            owner: Repository owner
            repo: Repository name
            base_branch: Base branch
            fixes: List of fixes to apply
            github_token: GitHub token
            
        Returns:
            PR details
        """
        logger.info(f"Creating fix PR for {owner}/{repo}")
        
        try:
            g = Github(github_token)
            repository = g.get_repo(f"{owner}/{repo}")
            
            # Create a new branch
            branch_name = f"ai-code-fixes-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}"
            base_ref = repository.get_git_ref(f"heads/{base_branch}")
            repository.create_git_ref(
                ref=f"refs/heads/{branch_name}",
                sha=base_ref.object.sha
            )
            
            # Apply fixes to files
            files_updated = []
            for fix in fixes:
                try:
                    file_path = fix['file_path']
                    fixed_code = fix['fixed_code']
                    
                    # Get current file content
                    file_content = repository.get_contents(file_path, ref=branch_name)
                    
                    # Update file with fix
                    repository.update_file(
                        path=file_path,
                        message=f"Fix: {fix['issue']['description'][:100]}",
                        content=fixed_code,
                        sha=file_content.sha,
                        branch=branch_name
                    )
                    
                    files_updated.append(file_path)
                    
                except Exception as e:
                    logger.error(f"Failed to update {file_path}: {e}")
            
            # Create pull request
            pr_title = f"🤖 AI-Powered Code Fixes ({len(files_updated)} files)"
            pr_body = self._generate_pr_body(fixes)
            
            pr = repository.create_pull(
                title=pr_title,
                body=pr_body,
                head=branch_name,
                base=base_branch
            )
            
            # Add labels
            pr.add_to_labels("automated", "code-quality", "ai-generated")
            
            logger.info(f"Created PR #{pr.number}: {pr.html_url}")
            
            return {
                'pr_number': pr.number,
                'pr_url': pr.html_url,
                'branch': branch_name,
                'files_updated': files_updated,
                'fixes_applied': len(fixes)
            }
            
        except GithubException as e:
            logger.error(f"GitHub API error: {e}")
            raise
    
    def _generate_pr_body(self, fixes: List[Dict]) -> str:
        """Generate PR description body"""
        body = """## 🤖 AI-Powered Code Fixes

This PR contains automated code fixes generated by our AI Code Review System.

### 📊 Summary
"""
        
        # Count fixes by type
        fix_types = {}
        for fix in fixes:
            fix_type = fix['issue'].get('type', 'general')
            fix_types[fix_type] = fix_types.get(fix_type, 0) + 1
        
        body += "\n"
        for fix_type, count in sorted(fix_types.items()):
            body += f"- **{fix_type.title()}**: {count} fixes\n"
        
        body += "\n### 🔧 Fixes Applied\n\n"
        
        for i, fix in enumerate(fixes, 1):
            body += f"""
#### {i}. {fix['file_path']} (Line {fix['line']})

**Issue**: {fix['issue']['description']}

**Fix**: {fix['explanation']}

**Why it's better**: {fix['why_better']}

<details>
<summary>View Diff</summary>

```diff
{fix['diff']}
```

</details>

---
"""
        
        body += """
### ✅ Review Checklist
- [ ] All fixes have been reviewed
- [ ] Tests pass locally
- [ ] No breaking changes introduced

### 🔍 How to Review
1. Check each fix individually
2. Run tests to ensure nothing breaks
3. Merge if all looks good!

*Generated by AI Code Review System v1.0*
"""
        
        return body
    
    async def generate_test_cases(
        self,
        code: str,
        language: str,
        function_name: str
    ) -> str:
        """
        Generate test cases for a function
        
        Args:
            code: Function code
            language: Programming language
            function_name: Name of the function
            
        Returns:
            Generated test code
        """
        logger.info(f"Generating test cases for {function_name}")
        
        prompt = f"""Generate comprehensive unit tests for the following {language} function:

```{language}
{code}
```

Requirements:
1. Test happy path scenarios
2. Test edge cases
3. Test error handling
4. Use appropriate testing framework ({self._get_test_framework(language)})
5. Include assertions and descriptive test names

Generate complete, runnable test code.
"""
        
        try:
            response = await ai_service.get_completion(
                prompt=prompt,
                model=settings.OPENAI_MODEL,
                temperature=0.3,
                max_tokens=2000
            )
            
            # Extract code from response
            test_code = self._extract_code_block(response, language)
            
            logger.info(f"Generated test cases for {function_name}")
            return test_code
            
        except Exception as e:
            logger.error(f"Test generation failed: {e}")
            return ""
    
    def _get_test_framework(self, language: str) -> str:
        """Get appropriate testing framework for language"""
        frameworks = {
            'python': 'pytest',
            'javascript': 'Jest',
            'typescript': 'Jest',
            'java': 'JUnit',
            'go': 'testing package',
            'rust': 'built-in test framework'
        }
        return frameworks.get(language.lower(), 'appropriate testing framework')
    
    def _extract_code_block(self, text: str, language: str) -> str:
        """Extract code block from markdown"""
        pattern = rf"```{language}\n(.+?)```"
        match = re.search(pattern, text, re.DOTALL)
        if match:
            return match.group(1).strip()
        return text
    
    async def generate_documentation(
        self,
        code: str,
        language: str,
        doc_style: str = "google"
    ) -> str:
        """
        Generate documentation for code
        
        Args:
            code: Source code
            language: Programming language
            doc_style: Documentation style (google, numpy, sphinx)
            
        Returns:
            Generated documentation
        """
        logger.info(f"Generating {doc_style} style documentation")
        
        prompt = f"""Generate comprehensive {doc_style} style documentation for this {language} code:

```{language}
{code}
```

Include:
1. Clear description of purpose
2. Parameter descriptions with types
3. Return value description
4. Usage examples
5. Notes about edge cases or important behavior

Format in {doc_style} docstring style.
"""
        
        try:
            response = await ai_service.get_completion(
                prompt=prompt,
                model=settings.OPENAI_MODEL,
                temperature=0.2,
                max_tokens=1500
            )
            
            logger.info("Documentation generated successfully")
            return response
            
        except Exception as e:
            logger.error(f"Documentation generation failed: {e}")
            return ""


# Singleton instance
code_fix_service = CodeFixService()
