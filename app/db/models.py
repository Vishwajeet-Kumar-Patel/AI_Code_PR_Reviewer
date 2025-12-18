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
    avatar_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    reviews = relationship("Review", back_populates="user")


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
    
    id = Column(String, primary_key=True, index=True)
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
    review_id = Column(String, ForeignKey("reviews.id"))
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    rating = Column(Integer)  # 1-5
    comment = Column(Text, nullable=True)
    helpful = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
