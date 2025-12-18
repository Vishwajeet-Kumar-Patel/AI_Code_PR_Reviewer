from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class PRFile(BaseModel):
    """Model for a file in a pull request"""
    filename: str
    status: str  # added, modified, removed, renamed
    additions: int
    deletions: int
    changes: int
    patch: Optional[str] = None
    previous_filename: Optional[str] = None
    raw_url: Optional[str] = None
    blob_url: Optional[str] = None


class PRCommit(BaseModel):
    """Model for a commit in a pull request"""
    sha: str
    message: str
    author: str
    date: datetime
    url: str


class PRComment(BaseModel):
    """Model for a comment on a pull request"""
    id: int
    user: str
    body: str
    created_at: datetime
    updated_at: datetime
    path: Optional[str] = None
    line: Optional[int] = None


class PullRequestData(BaseModel):
    """Complete pull request data"""
    number: int
    title: str
    description: Optional[str] = None
    author: str
    state: str  # open, closed, merged
    base_branch: str
    head_branch: str
    created_at: datetime
    updated_at: datetime
    merged_at: Optional[datetime] = None
    files: List[PRFile] = []
    commits: List[PRCommit] = []
    comments: List[PRComment] = []
    additions: int
    deletions: int
    changed_files: int
    url: str
    html_url: str
    labels: List[str] = []
    reviewers: List[str] = []
    assignees: List[str] = []


class RepositoryInfo(BaseModel):
    """Repository information"""
    full_name: str
    name: str
    owner: str
    description: Optional[str] = None
    language: Optional[str] = None
    languages: Dict[str, int] = {}
    default_branch: str = "main"
    is_private: bool = False
    url: str
    clone_url: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    stars: int = 0
    forks: int = 0


class DiffHunk(BaseModel):
    """Model for a diff hunk"""
    old_start: int
    old_lines: int
    new_start: int
    new_lines: int
    header: str
    lines: List[str] = []


class FileDiff(BaseModel):
    """Detailed file diff information"""
    filename: str
    old_filename: Optional[str] = None
    status: str
    additions: int
    deletions: int
    hunks: List[DiffHunk] = []
    language: Optional[str] = None
    content_before: Optional[str] = None
    content_after: Optional[str] = None
