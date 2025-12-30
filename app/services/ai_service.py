from typing import Optional, List, Dict, Any
import openai
import google.generativeai as genai
from app.core.config import settings
from app.core.logging import logger
from app.models.code_analysis import AIAnalysisRequest, AIAnalysisResponse
from app.services.rag_service import RAGService


class AIService:
    """Service for AI-powered code analysis using OpenAI or Gemini"""
    
    def __init__(self, rag_service: Optional[RAGService] = None):
        """Initialize AI service"""
        self.provider = settings.AI_PROVIDER
        self.rag_service = rag_service or RAGService()
        
        if self.provider == "openai":
            if not settings.is_openai_configured:
                raise ValueError("OpenAI API key not configured")
            openai.api_key = settings.OPENAI_API_KEY
            self.model = settings.OPENAI_MODEL
            logger.info("AI service initialized with OpenAI")
        elif self.provider == "gemini":
            if not settings.is_gemini_configured:
                raise ValueError("Gemini API key not configured")
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self.model = settings.GEMINI_MODEL
            self.gemini_model = genai.GenerativeModel(self.model)
            logger.info("AI service initialized with Gemini")
        else:
            raise ValueError(f"Unsupported AI provider: {self.provider}")
    
    async def analyze_code(self, request: AIAnalysisRequest) -> AIAnalysisResponse:
        """Analyze code using AI"""
        # Get RAG context if enabled
        rag_context = None
        if request.include_rag:
            rag_context = self.rag_service.search_by_language(
                query=f"{request.language} code analysis: {request.context or 'general'}",
                language=request.language,
                n_results=3
            )
        
        # Build prompt
        prompt = self._build_analysis_prompt(request, rag_context)
        
        # Call AI provider
        if self.provider == "openai":
            response = await self._analyze_with_openai(prompt)
        else:
            response = await self._analyze_with_gemini(prompt)
        
        return AIAnalysisResponse(
            insights=response["insights"],
            issues_found=response["issues_found"],
            suggestions=response["suggestions"],
            code_improvements=response.get("code_improvements"),
            confidence=response.get("confidence", 0.8),
            rag_context_used=request.include_rag and rag_context is not None,
        )
    
    def _build_analysis_prompt(
        self,
        request: AIAnalysisRequest,
        rag_context: Optional[Any] = None
    ) -> str:
        """Build analysis prompt"""
        prompt_parts = [
            f"Analyze the following {request.language} code for {', '.join([t.value for t in request.analysis_types])}:",
            "",
            "Code:",
            "```" + request.language,
            request.code,
            "```",
            "",
        ]
        
        if request.context:
            prompt_parts.extend([
                "Context:",
                request.context,
                "",
            ])
        
        if request.file_path:
            prompt_parts.extend([
                f"File: {request.file_path}",
                "",
            ])
        
        if rag_context and rag_context.best_practices:
            prompt_parts.extend([
                "Relevant best practices:",
                *[f"- {practice}" for practice in rag_context.best_practices[:3]],
                "",
            ])
        
        prompt_parts.extend([
            "Please provide:",
            "1. Detailed insights about the code quality, security, and complexity",
            "2. Specific issues found (with line numbers if applicable)",
            "3. Actionable suggestions for improvement",
            "4. Optional: Improved code examples",
            "",
            "Format your response as structured analysis.",
        ])
        
        return "\n".join(prompt_parts)
    
    async def _analyze_with_openai(self, prompt: str) -> Dict[str, Any]:
        """Analyze code using OpenAI"""
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert code reviewer specializing in code quality, security, and best practices. Provide detailed, actionable feedback."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=settings.OPENAI_TEMPERATURE,
                max_tokens=settings.OPENAI_MAX_TOKENS,
            )
            
            content = response.choices[0].message.content
            
            # Parse response
            return self._parse_ai_response(content)
        except Exception as e:
            logger.error(f"OpenAI analysis failed: {e}")
            raise
    
    async def _analyze_with_gemini(self, prompt: str) -> Dict[str, Any]:
        """Analyze code using Gemini"""
        try:
            response = self.gemini_model.generate_content(prompt)
            content = response.text
            
            # Parse response
            return self._parse_ai_response(content)
        except Exception as e:
            logger.error(f"Gemini analysis failed: {e}")
            raise
    
    def _parse_ai_response(self, content: str) -> Dict[str, Any]:
        """Parse AI response into structured format"""
        # Simple parsing - can be enhanced with more sophisticated parsing
        lines = content.split("\n")
        
        insights = []
        suggestions = []
        issues_found = 0
        code_improvements = None
        
        current_section = None
        code_block = []
        in_code_block = False
        
        for line in lines:
            line = line.strip()
            
            if "```" in line:
                if in_code_block:
                    code_improvements = "\n".join(code_block)
                    code_block = []
                in_code_block = not in_code_block
                continue
            
            if in_code_block:
                code_block.append(line)
                continue
            
            if not line:
                continue
            
            # Detect sections
            lower_line = line.lower()
            if "insight" in lower_line or "analysis" in lower_line:
                current_section = "insights"
            elif "suggestion" in lower_line or "recommendation" in lower_line:
                current_section = "suggestions"
            elif "issue" in lower_line or "problem" in lower_line:
                current_section = "issues"
                issues_found += 1
            
            # Add to appropriate section
            if line.startswith("-") or line.startswith("*") or line.startswith(tuple("0123456789")):
                cleaned = line.lstrip("-*0123456789. ")
                if current_section == "insights":
                    insights.append(cleaned)
                elif current_section == "suggestions":
                    suggestions.append(cleaned)
                elif current_section == "issues":
                    suggestions.append(f"Issue: {cleaned}")
        
        return {
            "insights": "\n".join(insights) if insights else content,
            "issues_found": issues_found,
            "suggestions": suggestions[:10],  # Limit to 10 suggestions
            "code_improvements": code_improvements,
            "confidence": 0.85,
        }
    
    async def generate_review_summary(
        self,
        file_analyses: List[Dict[str, Any]],
        pr_context: Dict[str, Any]
    ) -> str:
        """Generate comprehensive review summary"""
        prompt = self._build_summary_prompt(file_analyses, pr_context)
        
        if self.provider == "openai":
            try:
                response = openai.ChatCompletion.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are an expert code reviewer. Summarize the PR review findings concisely and professionally."
                        },
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=1500,
                )
                return response.choices[0].message.content
            except Exception as e:
                logger.error(f"Failed to generate summary with OpenAI: {e}")
                return "Failed to generate summary"
        else:
            try:
                response = self.gemini_model.generate_content(prompt)
                return response.text
            except Exception as e:
                logger.error(f"Failed to generate summary with Gemini: {e}")
                return "Failed to generate summary"
    
    def _build_summary_prompt(
        self,
        file_analyses: List[Dict[str, Any]],
        pr_context: Dict[str, Any]
    ) -> str:
        """Build prompt for review summary"""
        total_issues = sum(len(fa.get("issues", [])) for fa in file_analyses)
        total_files = len(file_analyses)
        
        prompt = f"""
Generate a comprehensive code review summary for this pull request:

**PR Information:**
- Title: {pr_context.get('title', 'N/A')}
- Author: {pr_context.get('author', 'N/A')}
- Files Changed: {total_files}
- Total Issues Found: {total_issues}

**Analysis Results:**
"""
        
        for fa in file_analyses[:10]:  # Limit to first 10 files
            file_path = fa.get("file_path", "unknown")
            quality_score = fa.get("quality_score", 0)
            issues_count = len(fa.get("issues", []))
            
            prompt += f"\n- {file_path}: Quality Score {quality_score:.1f}/100, {issues_count} issues"
        
        prompt += """

Please provide:
1. Executive Summary (2-3 sentences)
2. Key Strengths (2-3 points)
3. Main Concerns (2-3 points)
4. Critical Issues to Address
5. Overall Recommendation (Approve, Request Changes, or Comment)

Keep the summary professional, concise, and actionable.
"""
        
        return prompt
    
    async def get_completion(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> str:
        """
        Get a simple completion from the AI model
        
        Args:
            prompt: The prompt to send to the AI
            model: Model to use (optional, uses default if not specified)
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens to generate
            
        Returns:
            The AI's response text
        """
        try:
            if self.provider == "openai":
                response = await openai.ChatCompletion.acreate(
                    model=model or self.model,
                    messages=[
                        {"role": "system", "content": "You are a helpful code review assistant."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                return response.choices[0].message.content
            
            elif self.provider == "gemini":
                response = self.gemini_model.generate_content(
                    prompt,
                    generation_config={
                        "temperature": temperature,
                        "max_output_tokens": max_tokens
                    }
                )
                return response.text
            
            else:
                raise ValueError(f"Unknown AI provider: {self.provider}")
                
        except Exception as e:
            logger.error(f"Error getting AI completion: {e}")
            raise


# Singleton instance (with RAG disabled to avoid startup delays)
ai_service = AIService(rag_service=None)
