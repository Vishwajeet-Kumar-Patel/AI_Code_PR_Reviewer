"""
Database models for persistent storage
"""
from sqlalchemy import Column, String, Integer, Float, DateTime, Text, Boolean, JSON, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base


class User(Base):
    """User model"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    github_username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True, nullable=True)
    hashed_password = Column(String, nullable=True)  # For email/password auth
    avatar_url = Column(String, nullable=True)
    full_name = Column(String, nullable=True)
    
    # Role-based access control
    role = Column(String, default="user")  # user, admin, super_admin
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # OAuth data
    github_id = Column(String, unique=True, index=True, nullable=True)
    oauth_provider = Column(String, nullable=True)  # github, google, microsoft
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login_at = Column(DateTime, nullable=True)
    
    # Relationships
    reviews = relationship("Review", back_populates="user")
    api_keys = relationship("ApiKey", back_populates="user", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="user", cascade="all, delete-orphan")
    organizations = relationship("OrganizationMember", back_populates="user")


class Repository(Base):
    """Repository model"""
    __tablename__ = "repositories"
    
    id = Column(Integer, primary_key=True, index=True)
    owner = Column(String, index=True)
    name = Column(String, index=True)
    full_name = Column(String, unique=True, index=True)
    description = Column(Text, nullable=True)
    language = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    pull_requests = relationship("PullRequest", back_populates="repository")


class PullRequest(Base):
    """Pull Request model"""
    __tablename__ = "pull_requests"
    
    id = Column(Integer, primary_key=True, index=True)
    repository_id = Column(Integer, ForeignKey("repositories.id"))
    pr_number = Column(Integer, index=True)
    title = Column(String)
    description = Column(Text, nullable=True)
    author = Column(String)
    state = Column(String)  # open, closed, merged
    base_branch = Column(String)
    head_branch = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    repository = relationship("Repository", back_populates="pull_requests")
    reviews = relationship("Review", back_populates="pull_request")


class Review(Base):
    """Code Review model"""
    __tablename__ = "reviews"
    
    id = Column(Integer, primary_key=True, index=True)
    pull_request_id = Column(Integer, ForeignKey("pull_requests.id"))
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    status = Column(String, default="pending")  # pending, in_progress, completed, failed
    quality_score = Column(Float, nullable=True)
    security_score = Column(Float, nullable=True)
    complexity_score = Column(Float, nullable=True)
    
    # Analysis results (stored as JSON)
    file_analyses = Column(JSON, nullable=True)
    security_issues = Column(JSON, nullable=True)
    complexity_issues = Column(JSON, nullable=True)
    summary = Column(Text, nullable=True)
    recommendations = Column(JSON, nullable=True)
    
    # Metadata
    ai_provider = Column(String, nullable=True)
    analysis_duration = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    pull_request = relationship("PullRequest", back_populates="reviews")
    user = relationship("User", back_populates="reviews")


class Feedback(Base):
    """User feedback on reviews"""
    __tablename__ = "feedback"
    
    id = Column(Integer, primary_key=True, index=True)
    review_id = Column(Integer, ForeignKey("reviews.id"))
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    rating = Column(Integer)  # 1-5
    comment = Column(Text, nullable=True)
    helpful = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)


class ApiKey(Base):
    """API Key model for programmatic access"""
    __tablename__ = "api_keys"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)  # User-friendly name
    key = Column(String, unique=True, index=True, nullable=False)  # The actual JWT token
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)
    last_used_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="api_keys")


class AuditLog(Base):
    """Audit log for compliance and security"""
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    action = Column(String, nullable=False)  # create, read, update, delete
    resource_type = Column(String, nullable=False)  # user, review, repository, etc.
    resource_id = Column(String, nullable=True)
    
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    
    context_data = Column(JSON, nullable=True)  # Additional context (renamed from metadata)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    user = relationship("User", back_populates="audit_logs")


class Organization(Base):
    """Organization/Team model for multi-tenancy"""
    __tablename__ = "organizations"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    slug = Column(String, unique=True, index=True, nullable=False)
    
    description = Column(Text, nullable=True)
    avatar_url = Column(String, nullable=True)
    
    # Billing & quotas
    plan = Column(String, default="free")  # free, pro, enterprise
    max_repositories = Column(Integer, default=5)
    max_members = Column(Integer, default=5)
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    members = relationship("OrganizationMember", back_populates="organization")


class OrganizationMember(Base):
    """Organization membership with roles"""
    __tablename__ = "organization_members"
    
    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    role = Column(String, default="member")  # owner, admin, member
    invited_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    organization = relationship("Organization", back_populates="members")
    user = relationship("User", back_populates="organizations", foreign_keys=[user_id])


class ReviewFeedback(Base):
    """User feedback on code reviews for AI learning"""
    __tablename__ = "review_feedback"
    
    id = Column(Integer, primary_key=True, index=True)
    review_id = Column(Integer, ForeignKey("reviews.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    feedback_type = Column(String, nullable=False)  # helpful, not_helpful, false_positive
    rating = Column(Integer, nullable=False)  # 1-5 stars
    comment = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    review = relationship("Review", backref="feedback")
    user = relationship("User", backref="feedback_given")


