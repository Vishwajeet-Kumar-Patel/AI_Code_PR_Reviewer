from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, List
from app.services.github_service import GitHubService
from app.models.pr_data import RepositoryInfo, PullRequestData
from app.core.logging import logger


router = APIRouter(prefix="/repository", tags=["Repository"])


def get_github_service() -> GitHubService:
    """Dependency to get GitHub service instance"""
    return GitHubService()


@router.get("/{owner}/{repo}", response_model=RepositoryInfo)
async def get_repository(
    owner: str,
    repo: str,
    github_service: GitHubService = Depends(get_github_service),
):
    """
    Get repository information
    
    Returns detailed information about a GitHub repository.
    """
    try:
        repo_name = f"{owner}/{repo}"
        logger.info(f"Fetching repository info for {repo_name}")
        
        repo_info = github_service.get_repository(repo_name)
        return repo_info
        
    except Exception as e:
        logger.error(f"Failed to get repository: {e}")
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{owner}/{repo}/pulls/{pr_number}", response_model=PullRequestData)
async def get_pull_request(
    owner: str,
    repo: str,
    pr_number: int,
    github_service: GitHubService = Depends(get_github_service),
):
    """
    Get pull request data
    
    Returns detailed information about a specific pull request.
    """
    try:
        repo_name = f"{owner}/{repo}"
        logger.info(f"Fetching PR #{pr_number} from {repo_name}")
        
        pr_data = github_service.get_pull_request(repo_name, pr_number)
        return pr_data
        
    except Exception as e:
        logger.error(f"Failed to get pull request: {e}")
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{owner}/{repo}/pulls")
async def list_pull_requests(
    owner: str,
    repo: str,
    state: str = "open",
    github_service: GitHubService = Depends(get_github_service),
) -> Dict[str, Any]:
    """
    List pull requests
    
    Returns a list of pull requests for a repository.
    """
    try:
        repo_name = f"{owner}/{repo}"
        logger.info(f"Listing PRs for {repo_name} with state={state}")
        
        # This would require additional implementation in GitHubService
        # For now, return a placeholder
        return {
            "repository": repo_name,
            "state": state,
            "message": "This endpoint needs additional implementation in GitHubService",
        }
        
    except Exception as e:
        logger.error(f"Failed to list pull requests: {e}")
        raise HTTPException(status_code=500, detail=str(e))
