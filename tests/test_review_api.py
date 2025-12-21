"""
Tests for review endpoints
"""
import pytest
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient

from app.main import app
from tests.test_auth import client, db_session, auth_headers, test_user


@pytest.mark.api
class TestReviewEndpoints:
    """Test review API endpoints"""
    
    @patch('app.services.code_analyzer.CodeAnalyzer.analyze_pull_request')
    def test_analyze_pr(self, mock_analyze, client, auth_headers):
        """Test PR analysis endpoint"""
        # Mock the analyzer response
        mock_review = Mock()
        mock_review.review_id = "test-review-123"
        mock_review.status = "completed"
        mock_review.quality_score = 85.0
        mock_analyze.return_value = mock_review
        
        response = client.post(
            "/api/v1/review/analyze",
            headers=auth_headers,
            json={
                "repository": "owner/repo",
                "pr_number": 1,
                "include_security_scan": True,
                "include_complexity_analysis": True
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "review_id" in data
        mock_analyze.assert_called_once()
    
    def test_analyze_pr_unauthorized(self, client):
        """Test PR analysis without authentication"""
        response = client.post(
            "/api/v1/review/analyze",
            json={
                "repository": "owner/repo",
                "pr_number": 1
            }
        )
        assert response.status_code == 403
    
    @patch('app.services.code_analyzer.CodeAnalyzer.analyze_pull_request')
    def test_analyze_pr_invalid_repo(self, mock_analyze, client, auth_headers):
        """Test PR analysis with invalid repository"""
        mock_analyze.side_effect = ValueError("Repository not found")
        
        response = client.post(
            "/api/v1/review/analyze",
            headers=auth_headers,
            json={
                "repository": "invalid/repo",
                "pr_number": 999
            }
        )
        
        assert response.status_code == 500


@pytest.mark.unit
class TestReviewModels:
    """Test review data models"""
    
    def test_review_response_model(self):
        """Test ReviewResponse model validation"""
        from app.models.review import ReviewResponse, ReviewStatus
        
        review = ReviewResponse(
            review_id="test-123",
            status=ReviewStatus.COMPLETED,
            repository="owner/repo",
            pr_number=1,
            quality_score=85.0,
            security_score=90.0,
            complexity_score=75.0
        )
        
        assert review.review_id == "test-123"
        assert review.status == ReviewStatus.COMPLETED
        assert review.quality_score == 85.0
