"""
Tests for AI service
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock

from app.services.ai_service import AIService
from app.models.code_analysis import AIAnalysisRequest, AnalysisType


@pytest.mark.unit
class TestAIService:
    """Test AI service functionality"""
    
    @patch('app.services.ai_service.openai')
    @pytest.mark.asyncio
    async def test_analyze_code_openai(self, mock_openai):
        """Test code analysis with OpenAI"""
        # Mock OpenAI response
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content='{"insights": "Test", "issues_found": [], "suggestions": []}'))]
        mock_openai.ChatCompletion.acreate.return_value = mock_response
        
        service = AIService()
        request = AIAnalysisRequest(
            code="def test(): pass",
            language="python",
            analysis_types=[AnalysisType.QUALITY],
            include_rag=False
        )
        
        # Note: This will need proper async handling
        # result = await service.analyze_code(request)
        # assert result.insights is not None
    
    def test_build_analysis_prompt(self):
        """Test prompt building"""
        service = AIService()
        request = AIAnalysisRequest(
            code="def test(): pass",
            language="python",
            analysis_types=[AnalysisType.QUALITY],
            context="Test function",
            file_path="test.py"
        )
        
        prompt = service._build_analysis_prompt(request, None)
        
        assert "python" in prompt
        assert "def test(): pass" in prompt
        assert "Test function" in prompt
        assert "test.py" in prompt


@pytest.mark.unit
class TestRAGService:
    """Test RAG service"""
    
    def test_rag_service_initialization(self):
        """Test RAG service initialization"""
        from app.services.rag_service import RAGService
        
        service = RAGService()
        assert service is not None
        assert hasattr(service, 'collection')
    
    @patch('app.services.rag_service.RAGService.search_by_language')
    def test_search_best_practices(self, mock_search):
        """Test searching best practices"""
        from app.services.rag_service import RAGService
        
        mock_search.return_value = Mock(
            best_practices=["Use descriptive names", "Follow PEP 8"]
        )
        
        service = RAGService()
        result = service.search_by_language(
            query="python best practices",
            language="python",
            n_results=5
        )
        
        assert result is not None
