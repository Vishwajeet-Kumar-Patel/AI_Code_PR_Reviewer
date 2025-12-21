"""
Integration tests for the complete workflow
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock

from app.main import app
from tests.test_auth import client, db_session, auth_headers, test_user


@pytest.mark.integration
class TestCompleteWorkflow:
    """Test complete workflow from authentication to PR analysis"""
    
    def test_full_user_journey(self, client):
        """Test complete user journey"""
        # 1. Register
        register_response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "journey@example.com",
                "github_username": "journeyuser",
                "password": "Journey123",
                "full_name": "Journey User"
            }
        )
        assert register_response.status_code == 201
        
        # 2. Login
        login_response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "journey@example.com",
                "password": "Journey123"
            }
        )
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # 3. Get user info
        me_response = client.get("/api/v1/auth/me", headers=headers)
        assert me_response.status_code == 200
        
        # 4. Create API key
        api_key_response = client.post(
            "/api/v1/auth/api-keys",
            headers=headers,
            json={"name": "Test Key"}
        )
        assert api_key_response.status_code == 201
        
        # 5. Try to analyze PR (would need GitHub setup)
        # This would test the full review workflow
    
    @patch('app.services.github_service.GithubService.get_pull_request')
    @patch('app.services.ai_service.AIService.analyze_code')
    def test_pr_analysis_workflow(self, mock_ai, mock_github, client, auth_headers):
        """Test PR analysis workflow"""
        # Mock GitHub PR data
        mock_pr = Mock()
        mock_pr.title = "Test PR"
        mock_pr.number = 1
        mock_github.return_value = mock_pr
        
        # Mock AI analysis
        mock_ai.return_value = AsyncMock()
        
        # This test would verify the complete PR analysis flow
        # including GitHub integration, code analysis, and result storage


@pytest.mark.integration
@pytest.mark.slow
class TestDatabaseOperations:
    """Test database operations"""
    
    def test_user_crud_operations(self, db_session):
        """Test CRUD operations on User model"""
        from app.db.models import User
        from app.core.security import get_password_hash
        
        # Create
        user = User(
            email="crud@example.com",
            github_username="cruduser",
            hashed_password=get_password_hash("Password123"),
            role="user",
            is_active=True
        )
        db_session.add(user)
        db_session.commit()
        
        # Read
        fetched_user = db_session.query(User).filter(User.email == "crud@example.com").first()
        assert fetched_user is not None
        assert fetched_user.github_username == "cruduser"
        
        # Update
        fetched_user.full_name = "CRUD User"
        db_session.commit()
        
        updated_user = db_session.query(User).filter(User.email == "crud@example.com").first()
        assert updated_user.full_name == "CRUD User"
        
        # Delete
        db_session.delete(updated_user)
        db_session.commit()
        
        deleted_user = db_session.query(User).filter(User.email == "crud@example.com").first()
        assert deleted_user is None
