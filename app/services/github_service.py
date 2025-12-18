from github import Github, GithubException
from typing import List, Optional, Dict, Any
import base64
from app.core.config import settings
from app.core.logging import logger
from app.models.pr_data import (
    PullRequestData,
    PRFile,
    PRCommit,
    PRComment,
    RepositoryInfo,
    FileDiff,
    DiffHunk,
)


class GitHubService:
    """Service for interacting with GitHub API"""
    
    def __init__(self, token: Optional[str] = None):
        """Initialize GitHub service"""
        self.token = token or settings.GITHUB_TOKEN
        self.client = Github(self.token)
        logger.info("GitHub service initialized")
    
    def get_repository(self, repo_name: str) -> RepositoryInfo:
        """Get repository information"""
        try:
            repo = self.client.get_repo(repo_name)
            
            # Get languages
            languages = repo.get_languages()
            
            return RepositoryInfo(
                full_name=repo.full_name,
                name=repo.name,
                owner=repo.owner.login,
                description=repo.description,
                language=repo.language,
                languages=languages,
                default_branch=repo.default_branch,
                is_private=repo.private,
                url=repo.url,
                clone_url=repo.clone_url,
                created_at=repo.created_at,
                updated_at=repo.updated_at,
                stars=repo.stargazers_count,
                forks=repo.forks_count,
            )
        except GithubException as e:
            logger.error(f"Failed to get repository {repo_name}: {e}")
            raise
    
    def get_pull_request(self, repo_name: str, pr_number: int) -> PullRequestData:
        """Get pull request data"""
        try:
            repo = self.client.get_repo(repo_name)
            pr = repo.get_pull(pr_number)
            
            # Get files
            files = [
                PRFile(
                    filename=file.filename,
                    status=file.status,
                    additions=file.additions,
                    deletions=file.deletions,
                    changes=file.changes,
                    patch=file.patch,
                    previous_filename=file.previous_filename,
                    raw_url=file.raw_url,
                    blob_url=file.blob_url,
                )
                for file in pr.get_files()
            ]
            
            # Get commits
            commits = [
                PRCommit(
                    sha=commit.sha,
                    message=commit.commit.message,
                    author=commit.commit.author.name,
                    date=commit.commit.author.date,
                    url=commit.html_url,
                )
                for commit in pr.get_commits()
            ]
            
            # Get comments
            comments = []
            for comment in pr.get_issue_comments():
                comments.append(
                    PRComment(
                        id=comment.id,
                        user=comment.user.login,
                        body=comment.body,
                        created_at=comment.created_at,
                        updated_at=comment.updated_at,
                    )
                )
            
            # Get review comments
            for comment in pr.get_review_comments():
                comments.append(
                    PRComment(
                        id=comment.id,
                        user=comment.user.login,
                        body=comment.body,
                        created_at=comment.created_at,
                        updated_at=comment.updated_at,
                        path=comment.path,
                        line=comment.line,
                    )
                )
            
            return PullRequestData(
                number=pr.number,
                title=pr.title,
                description=pr.body,
                author=pr.user.login,
                state=pr.state,
                base_branch=pr.base.ref,
                head_branch=pr.head.ref,
                created_at=pr.created_at,
                updated_at=pr.updated_at,
                merged_at=pr.merged_at,
                files=files,
                commits=commits,
                comments=comments,
                additions=pr.additions,
                deletions=pr.deletions,
                changed_files=pr.changed_files,
                url=pr.url,
                html_url=pr.html_url,
                labels=[label.name for label in pr.labels],
                reviewers=[reviewer.login for reviewer in pr.requested_reviewers],
                assignees=[assignee.login for assignee in pr.assignees],
            )
        except GithubException as e:
            logger.error(f"Failed to get PR {pr_number} from {repo_name}: {e}")
            raise
    
    def get_file_content(self, repo_name: str, file_path: str, ref: str) -> Optional[str]:
        """Get file content from repository"""
        try:
            repo = self.client.get_repo(repo_name)
            content = repo.get_contents(file_path, ref=ref)
            
            if isinstance(content, list):
                logger.warning(f"Path {file_path} is a directory")
                return None
            
            # Decode content
            decoded_content = base64.b64decode(content.content).decode("utf-8")
            return decoded_content
        except GithubException as e:
            logger.error(f"Failed to get file content {file_path}: {e}")
            return None
    
    def parse_diff(self, patch: str) -> List[DiffHunk]:
        """Parse diff patch into hunks"""
        if not patch:
            return []
        
        hunks = []
        current_hunk = None
        
        for line in patch.split("\n"):
            if line.startswith("@@"):
                # Parse hunk header
                # Format: @@ -old_start,old_lines +new_start,new_lines @@
                parts = line.split("@@")
                if len(parts) >= 2:
                    ranges = parts[1].strip().split()
                    old_range = ranges[0][1:].split(",")
                    new_range = ranges[1][1:].split(",")
                    
                    if current_hunk:
                        hunks.append(current_hunk)
                    
                    current_hunk = DiffHunk(
                        old_start=int(old_range[0]),
                        old_lines=int(old_range[1]) if len(old_range) > 1 else 1,
                        new_start=int(new_range[0]),
                        new_lines=int(new_range[1]) if len(new_range) > 1 else 1,
                        header=line,
                        lines=[],
                    )
            elif current_hunk:
                current_hunk.lines.append(line)
        
        if current_hunk:
            hunks.append(current_hunk)
        
        return hunks
    
    def get_file_diffs(self, repo_name: str, pr_number: int) -> List[FileDiff]:
        """Get detailed file diffs for a PR"""
        try:
            pr_data = self.get_pull_request(repo_name, pr_number)
            
            file_diffs = []
            for file in pr_data.files:
                hunks = self.parse_diff(file.patch) if file.patch else []
                
                file_diff = FileDiff(
                    filename=file.filename,
                    old_filename=file.previous_filename,
                    status=file.status,
                    additions=file.additions,
                    deletions=file.deletions,
                    hunks=hunks,
                )
                file_diffs.append(file_diff)
            
            return file_diffs
        except Exception as e:
            logger.error(f"Failed to get file diffs: {e}")
            raise
    
    def post_review_comment(
        self,
        repo_name: str,
        pr_number: int,
        body: str,
        commit_id: Optional[str] = None,
        path: Optional[str] = None,
        line: Optional[int] = None,
    ) -> bool:
        """Post a review comment on a PR"""
        try:
            repo = self.client.get_repo(repo_name)
            pr = repo.get_pull(pr_number)
            
            if path and line and commit_id:
                # Post a review comment on specific line
                pr.create_review_comment(
                    body=body,
                    commit=repo.get_commit(commit_id),
                    path=path,
                    line=line,
                )
            else:
                # Post a general comment
                pr.create_issue_comment(body)
            
            logger.info(f"Posted review comment on PR {pr_number}")
            return True
        except GithubException as e:
            logger.error(f"Failed to post review comment: {e}")
            return False
    
    def create_review(
        self,
        repo_name: str,
        pr_number: int,
        body: str,
        event: str = "COMMENT",  # APPROVE, REQUEST_CHANGES, COMMENT
        comments: Optional[List[Dict[str, Any]]] = None,
    ) -> bool:
        """Create a review on a PR"""
        try:
            repo = self.client.get_repo(repo_name)
            pr = repo.get_pull(pr_number)
            
            review_comments = []
            if comments:
                for comment in comments:
                    review_comments.append({
                        "path": comment["path"],
                        "line": comment["line"],
                        "body": comment["body"],
                    })
            
            pr.create_review(
                body=body,
                event=event,
                comments=review_comments if review_comments else None,
            )
            
            logger.info(f"Created review on PR {pr_number}")
            return True
        except GithubException as e:
            logger.error(f"Failed to create review: {e}")
            return False
