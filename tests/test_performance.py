"""
Performance tests
"""
import pytest
import time
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import patch


@pytest.mark.slow
class TestPerformance:
    """Performance and load testing"""
    
    def test_api_response_time(self, client, auth_headers):
        """Test API response time"""
        start_time = time.time()
        response = client.get("/api/v1/health", headers=auth_headers)
        end_time = time.time()
        
        response_time = (end_time - start_time) * 1000  # Convert to milliseconds
        assert response_time < 200  # Should respond in under 200ms
        assert response.status_code == 200
    
    @patch('app.services.code_analyzer.CodeAnalyzer.analyze_pull_request')
    def test_concurrent_requests(self, mock_analyze, client, auth_headers):
        """Test handling concurrent requests"""
        mock_analyze.return_value = {"status": "completed"}
        
        def make_request():
            return client.post(
                "/api/v1/review/analyze",
                headers=auth_headers,
                json={"repository": "test/repo", "pr_number": 1}
            )
        
        # Simulate 10 concurrent requests
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(10)]
            results = [f.result() for f in futures]
        
        # All requests should succeed
        assert all(r.status_code in [200, 201] for r in results)
    
    def test_database_query_performance(self, db_session):
        """Test database query performance"""
        from app.db.models import User
        
        # Create multiple users
        users = [
            User(
                email=f"perf{i}@example.com",
                github_username=f"perfuser{i}",
                role="user",
                is_active=True
            )
            for i in range(100)
        ]
        db_session.bulk_save_objects(users)
        db_session.commit()
        
        # Test query performance
        start_time = time.time()
        result = db_session.query(User).filter(User.is_active == True).limit(50).all()
        end_time = time.time()
        
        query_time = (end_time - start_time) * 1000
        assert query_time < 100  # Should complete in under 100ms
        assert len(result) == 50
