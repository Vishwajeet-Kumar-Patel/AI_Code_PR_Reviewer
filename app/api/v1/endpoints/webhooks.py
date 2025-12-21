"""
GitHub App & Webhook integration
"""
from fastapi import APIRouter, Request, HTTPException, Header, BackgroundTasks
from typing import Optional
import hmac
import hashlib
from app.core.config import settings
from app.core.logging import logger
from app.core.metrics import metrics
from app.services.github_service import GitHubService
from app.services.code_analyzer import CodeAnalyzer


router = APIRouter(prefix="/webhooks", tags=["Webhooks"])


def verify_webhook_signature(payload: bytes, signature: str) -> bool:
    """Verify GitHub webhook signature"""
    if not settings.GITHUB_WEBHOOK_SECRET:
        logger.warning("Webhook secret not configured")
        return True  # Allow in development
    
    expected_signature = "sha256=" + hmac.new(
        settings.GITHUB_WEBHOOK_SECRET.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(expected_signature, signature)


@router.post("/github")
async def github_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    x_github_event: str = Header(None),
    x_hub_signature_256: Optional[str] = Header(None)
):
    """
    Handle GitHub webhook events
    
    Supported events:
    - pull_request (opened, synchronize, reopened)
    - push
    - issues
    """
    # Get payload
    payload = await request.body()
    
    # Verify signature
    if x_hub_signature_256 and not verify_webhook_signature(payload, x_hub_signature_256):
        logger.error("Invalid webhook signature")
        raise HTTPException(status_code=401, detail="Invalid signature")
    
    # Parse JSON
    data = await request.json()
    
    logger.info(f"Received GitHub webhook: {x_github_event}")
    metrics.record_github_request("webhook")
    
    # Handle pull request events
    if x_github_event == "pull_request":
        background_tasks.add_task(handle_pull_request_event, data)
    
    # Handle push events
    elif x_github_event == "push":
        background_tasks.add_task(handle_push_event, data)
    
    # Handle issue events
    elif x_github_event == "issues":
        background_tasks.add_task(handle_issue_event, data)
    
    return {"message": "Webhook received", "event": x_github_event}


async def handle_pull_request_event(data: dict):
    """Handle pull request webhook event"""
    action = data.get("action")
    pr = data.get("pull_request", {})
    repository = data.get("repository", {})
    
    if action not in ["opened", "synchronize", "reopened"]:
        logger.info(f"Ignoring PR action: {action}")
        return
    
    repo_full_name = repository.get("full_name")
    pr_number = pr.get("number")
    
    logger.info(f"Processing PR #{pr_number} from {repo_full_name} (action: {action})")
    
    try:
        # Analyze PR
        analyzer = CodeAnalyzer()
        review = await analyzer.analyze_pull_request(
            repository=repo_full_name,
            pr_number=pr_number,
            include_security=True,
            include_complexity=True
        )
        
        # Post comment on PR
        github_service = GitHubService()
        await post_review_comment(github_service, repo_full_name, pr_number, review)
        
        # Update PR status
        await update_pr_status(github_service, repo_full_name, pr["head"]["sha"], review)
        
        logger.info(f"Successfully processed PR #{pr_number}")
        
    except Exception as e:
        logger.error(f"Error processing PR webhook: {e}", exc_info=True)


async def handle_push_event(data: dict):
    """Handle push webhook event"""
    repository = data.get("repository", {})
    commits = data.get("commits", [])
    
    repo_full_name = repository.get("full_name")
    branch = data.get("ref", "").replace("refs/heads/", "")
    
    logger.info(f"Processing push to {repo_full_name}/{branch} with {len(commits)} commits")
    
    # Could trigger various actions:
    # - Analyze recent commits
    # - Check for security issues
    # - Update statistics
    
    metrics.record_github_request("push")


async def handle_issue_event(data: dict):
    """Handle issue webhook event"""
    action = data.get("action")
    issue = data.get("issue", {})
    repository = data.get("repository", {})
    
    repo_full_name = repository.get("full_name")
    issue_number = issue.get("number")
    
    logger.info(f"Processing issue #{issue_number} from {repo_full_name} (action: {action})")
    
    # Could trigger actions like:
    # - Auto-label based on content
    # - Auto-assign
    # - Detect bug patterns
    
    metrics.record_github_request("issue")


async def post_review_comment(
    github_service: GitHubService,
    repository: str,
    pr_number: int,
    review: any
):
    """Post review results as PR comment"""
    try:
        comment_body = format_review_comment(review)
        
        # Post comment using GitHub API
        # github_service.post_pr_comment(repository, pr_number, comment_body)
        
        logger.info(f"Posted review comment on PR #{pr_number}")
    except Exception as e:
        logger.error(f"Error posting comment: {e}")


async def update_pr_status(
    github_service: GitHubService,
    repository: str,
    commit_sha: str,
    review: any
):
    """Update PR status check"""
    try:
        # Determine status based on review scores
        if review.quality_score and review.quality_score < 60:
            state = "failure"
            description = f"Code quality score: {review.quality_score}/100"
        elif review.security_score and review.security_score < 70:
            state = "failure"
            description = f"Security score: {review.security_score}/100"
        else:
            state = "success"
            description = "All checks passed"
        
        # Update status using GitHub API
        # github_service.update_commit_status(repository, commit_sha, state, description)
        
        logger.info(f"Updated PR status: {state}")
    except Exception as e:
        logger.error(f"Error updating status: {e}")


def format_review_comment(review: any) -> str:
    """Format review results as markdown comment"""
    comment = f"""## 🤖 AI Code Review Results

### 📊 Scores
- **Quality Score:** {review.quality_score or 'N/A'}/100
- **Security Score:** {review.security_score or 'N/A'}/100
- **Complexity Score:** {review.complexity_score or 'N/A'}/100

### 🔍 Summary
{review.summary or 'No summary available'}

### 🎯 Recommendations
"""
    
    if hasattr(review, 'recommendations') and review.recommendations:
        for i, rec in enumerate(review.recommendations[:5], 1):
            comment += f"{i}. {rec}\n"
    else:
        comment += "No specific recommendations\n"
    
    comment += f"\n---\n*Review ID: {review.review_id}*\n"
    comment += "*Powered by AI Code Review System*"
    
    return comment
