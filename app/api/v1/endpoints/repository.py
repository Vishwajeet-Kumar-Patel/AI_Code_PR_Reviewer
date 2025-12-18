from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Dict, Any, List, Optional
from app.services.github_service import GitHubService
from app.models.pr_data import RepositoryInfo, PullRequestData
from app.core.logging import logger


router = APIRouter(prefix="/repository", tags=["Repository"])
pull_requests_router = APIRouter(prefix="/pull-requests", tags=["Pull Requests"])


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


# General pull requests endpoint for dashboard
@pull_requests_router.get("/")
async def list_all_pull_requests(
    repository: Optional[str] = Query(None, description="Filter by repository (owner/repo)"),
    status: Optional[str] = Query("open", description="Filter by status: open, closed, merged, all"),
    author: Optional[str] = Query(None, description="Filter by author"),
    sort: Optional[str] = Query("newest", description="Sort by: newest, oldest, updated"),
    search: Optional[str] = Query(None, description="Search in title and description"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    github_service: GitHubService = Depends(get_github_service),
) -> Dict[str, Any]:
    """
    List all pull requests across repositories
    
    Returns a paginated list of pull requests with filtering and sorting.
    """
    try:
        logger.info(f"Listing all PRs with filters: status={status}, repository={repository}")
        
        # Fetch real data from GitHub
        prs = github_service.search_pull_requests(
            repo_name=repository,
            state=status if status else "open",
            author=author,
            max_results=per_page * 2  # Fetch more to allow for filtering
        )
        
        # Apply search filter if provided
        if search:
            search_lower = search.lower()
            prs = [
                pr for pr in prs 
                if search_lower in pr["title"].lower() or 
                   (pr["description"] and search_lower in pr["description"].lower())
            ]
        
        # Sort results
        if sort == "oldest":
            prs.sort(key=lambda x: x["created_at"])
        elif sort == "updated":
            prs.sort(key=lambda x: x["updated_at"], reverse=True)
        else:  # newest
            prs.sort(key=lambda x: x["created_at"], reverse=True)
        
        # Paginate
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        paginated_prs = prs[start_idx:end_idx]
        
        return {
            "items": paginated_prs,
            "total": len(prs),
            "page": page,
            "per_page": per_page,
            "pages": (len(prs) + per_page - 1) // per_page if prs else 1
        }
        
    except Exception as e:
        logger.error(f"Failed to list all pull requests: {e}")
        # Return empty data instead of failing
        return {
            "items": [],
            "total": 0,
            "page": page,
            "per_page": per_page,
            "pages": 1
        }


# List user repositories
@pull_requests_router.get("/repositories/list")
async def list_repositories(
    max_repos: int = Query(30, ge=1, le=100, description="Maximum number of repositories to return"),
    github_service: GitHubService = Depends(get_github_service),
) -> Dict[str, Any]:
    """
    List repositories for the authenticated user
    
    Returns a list of repositories accessible by the authenticated user.
    """
    try:
        logger.info(f"Listing repositories (max: {max_repos})")
        
        repos = github_service.list_user_repositories(max_repos=max_repos)
        
        return {
            "repositories": repos,
            "total": len(repos)
        }
        
    except Exception as e:
        logger.error(f"Failed to list repositories: {e}")
        return {
            "repositories": [],
            "total": 0
        }

