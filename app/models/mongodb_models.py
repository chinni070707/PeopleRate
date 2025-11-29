"""
MongoDB Models using Beanie ODM
Provides type-safe, Pydantic-based models for MongoDB collections
"""

from beanie import Document, Indexed
from pydantic import EmailStr, Field, field_validator
from typing import Optional, List
from datetime import datetime
import re


class User(Document):
    """User model for MongoDB with Beanie"""
    
    email: Indexed(EmailStr, unique=True)  # Indexed and unique
    username: Indexed(str, unique=True)  # Indexed and unique
    full_name: str
    password: str  # Hashed password
    is_active: bool = True
    email_verified: bool = False
    phone: Optional[str] = None
    phone_verified: bool = False
    
    # Profile
    profile_photo_url: Optional[str] = None
    bio: Optional[str] = None
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None
    
    # Stats
    review_count: int = 0
    reputation_score: int = 0
    
    # Subscription
    subscription_tier: str = "free"  # free, basic, professional, enterprise
    subscription_expires_at: Optional[datetime] = None
    
    @field_validator('username')
    @classmethod
    def validate_username(cls, v):
        if not re.match(r'^[a-zA-Z0-9_]{3,20}$', v):
            raise ValueError('Username must be 3-20 characters, letters, numbers, and underscores only')
        return v
    
    class Settings:
        name = "users"  # Collection name
        indexes = [
            "email",
            "username",
            "created_at",
        ]


class Person(Document):
    """Person profile model for MongoDB"""
    
    # Basic Info
    name: Indexed(str)  # Indexed for search
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    
    # Professional Info
    job_title: Optional[str] = None
    company: Indexed(str, sparse=True)  # Indexed for search
    industry: Optional[str] = None
    
    # Location
    city: Indexed(str, sparse=True)  # Indexed for search
    state: Optional[str] = None
    country: Optional[str] = None
    
    # Social Media
    linkedin_url: Optional[str] = None
    instagram_url: Optional[str] = None
    facebook_url: Optional[str] = None
    twitter_url: Optional[str] = None
    github_url: Optional[str] = None
    website_url: Optional[str] = None
    
    # Profile
    bio: Optional[str] = None
    profile_photo_url: Optional[str] = None
    skills: List[str] = []
    experience_years: Optional[int] = None
    education: Optional[str] = None
    certifications: List[str] = []
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Claiming
    is_claimed: bool = False
    claimed_by_user_id: Optional[str] = None
    claimed_at: Optional[datetime] = None
    
    # Review Stats
    review_count: int = 0
    average_rating: float = 0.0
    total_rating: int = 0
    
    # Verification
    is_verified: bool = False
    verification_badges: List[str] = []  # email, phone, linkedin, identity, company
    
    @field_validator('linkedin_url')
    @classmethod
    def validate_linkedin_url(cls, v):
        if v and v.strip() and not re.match(r'^https?://(www\.)?linkedin\.com/in/[\w\-]+/?$', v):
            raise ValueError('Invalid LinkedIn URL format')
        return v
    
    @field_validator('instagram_url')
    @classmethod
    def validate_instagram_url(cls, v):
        if v and v.strip() and not re.match(r'^https?://(www\.)?instagram\.com/[\w\.\-]+/?$', v):
            raise ValueError('Invalid Instagram URL format')
        return v
    
    @field_validator('facebook_url')
    @classmethod
    def validate_facebook_url(cls, v):
        if v and v.strip() and not re.match(r'^https?://(www\.)?facebook\.com/[\w\.\-]+/?$', v):
            raise ValueError('Invalid Facebook URL format')
        return v
    
    @field_validator('twitter_url')
    @classmethod
    def validate_twitter_url(cls, v):
        if v and v.strip() and not re.match(r'^https?://(www\.)?(twitter|x)\.com/[\w]+/?$', v):
            raise ValueError('Invalid Twitter/X URL format')
        return v
    
    @field_validator('github_url')
    @classmethod
    def validate_github_url(cls, v):
        if v and v.strip() and not re.match(r'^https?://(www\.)?github\.com/[\w\-]+/?$', v):
            raise ValueError('Invalid GitHub URL format')
        return v
    
    @field_validator('website_url')
    @classmethod
    def validate_website_url(cls, v):
        if v and v.strip() and not re.match(r'^https?://[\w\-\.]+\.[a-z]{2,}(/.*)?$', v):
            raise ValueError('Invalid website URL format')
        return v
    
    class Settings:
        name = "persons"
        indexes = [
            "name",
            "company",
            "city",
            "email",
            "created_at",
            [("name", 1), ("company", 1)],  # Compound index
        ]


class Review(Document):
    """Review model for MongoDB"""
    
    # References
    person_id: Indexed(str)  # Reference to Person
    reviewer_id: Indexed(str)  # Reference to User
    reviewer_username: str  # Public username (privacy protection)
    
    # Rating
    rating: int = Field(..., ge=1, le=5)
    title: Optional[str] = Field(None, max_length=100)
    comment: str = Field(..., min_length=10, max_length=1000)
    
    # Context
    relationship: Optional[str] = None  # colleague, client, manager, etc.
    
    # Dimensional Ratings
    work_quality: Optional[int] = Field(None, ge=1, le=5)
    communication: Optional[int] = Field(None, ge=1, le=5)
    reliability: Optional[int] = Field(None, ge=1, le=5)
    professionalism: Optional[int] = Field(None, ge=1, le=5)
    would_recommend: Optional[bool] = None
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Verification & Moderation
    is_verified: bool = False
    is_flagged: bool = False
    flag_count: int = 0
    moderation_status: str = "pending"  # pending, approved, rejected
    moderation_notes: Optional[str] = None
    moderated_by: Optional[str] = None
    moderated_at: Optional[datetime] = None
    
    # Community Feedback
    helpful_count: int = 0
    unhelpful_count: int = 0
    reported_count: int = 0
    
    class Settings:
        name = "reviews"
        indexes = [
            "person_id",
            "reviewer_id",
            "created_at",
            "moderation_status",
            [("person_id", 1), ("created_at", -1)],  # Compound index for person's reviews
        ]


class Notification(Document):
    """Notification model for MongoDB"""
    
    user_id: Indexed(str)  # User who receives notification
    notification_type: str  # new_review, review_response, profile_view, weekly_digest
    title: str
    message: str
    link: Optional[str] = None
    
    is_read: bool = False
    is_email_sent: bool = False
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    read_at: Optional[datetime] = None
    
    class Settings:
        name = "notifications"
        indexes = [
            "user_id",
            "is_read",
            "created_at",
        ]


class Subscription(Document):
    """Subscription model for MongoDB"""
    
    user_id: Indexed(str, unique=True)
    stripe_customer_id: Optional[str] = None
    stripe_subscription_id: Optional[str] = None
    
    tier: str = "free"  # free, basic, professional, enterprise
    status: str = "active"  # active, cancelled, expired, past_due
    
    # Pricing
    price_monthly: float = 0.0
    currency: str = "USD"
    
    # Dates
    started_at: datetime = Field(default_factory=datetime.utcnow)
    current_period_start: Optional[datetime] = None
    current_period_end: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None
    
    # Features
    features: List[str] = []
    
    class Settings:
        name = "subscriptions"
        indexes = [
            "user_id",
            "stripe_customer_id",
            "status",
        ]


class FlaggedContent(Document):
    """Model for tracking flagged content for moderation"""
    
    content_type: str  # review, person, user
    content_id: str
    reported_by_user_id: str
    
    reason: str  # spam, harassment, false_info, inappropriate, other
    description: Optional[str] = None
    
    status: str = "pending"  # pending, reviewing, resolved, dismissed
    resolution: Optional[str] = None
    resolved_by: Optional[str] = None
    resolved_at: Optional[datetime] = None
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "flagged_content"
        indexes = [
            "content_id",
            "status",
            "created_at",
        ]
