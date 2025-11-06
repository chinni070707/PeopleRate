from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional
from datetime import datetime
from bson import ObjectId
from .user import PyObjectId


class Review(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )
    
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    reviewer_id: PyObjectId = Field(..., description="User who wrote the review")
    person_id: PyObjectId = Field(..., description="Person being reviewed")
    
    # Review content
    rating: int = Field(..., ge=1, le=5, description="Star rating from 1 to 5")
    title: str = Field(..., min_length=5, max_length=100)
    content: str = Field(..., min_length=10, max_length=1000)
    
    # Review categories (optional)
    category: Optional[str] = Field(None, description="Professional, Personal, Service, etc.")
    
    # Verification and moderation
    is_verified: bool = False
    is_flagged: bool = False
    moderation_status: str = "pending"  # pending, approved, rejected
    
    # Engagement
    helpful_count: int = 0
    reported_count: int = 0
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    @field_validator('moderation_status')
    @classmethod
    def validate_moderation_status(cls, v):
        allowed_statuses = ['pending', 'approved', 'rejected']
        if v not in allowed_statuses:
            raise ValueError(f'Moderation status must be one of: {allowed_statuses}')
        return v


class ReviewCreate(BaseModel):
    person_id: str = Field(..., description="Person being reviewed")
    rating: int = Field(..., ge=1, le=5, description="Star rating from 1 to 5")
    title: str = Field(..., min_length=5, max_length=100)
    content: str = Field(..., min_length=10, max_length=1000)
    category: Optional[str] = Field(None, description="Professional, Personal, Service, etc.")


class ReviewUpdate(BaseModel):
    rating: Optional[int] = Field(None, ge=1, le=5)
    title: Optional[str] = Field(None, min_length=5, max_length=100)
    content: Optional[str] = Field(None, min_length=10, max_length=1000)
    category: Optional[str] = None


class ReviewResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    reviewer_id: str
    person_id: str
    rating: int
    title: str
    content: str
    category: Optional[str] = None
    is_verified: bool
    helpful_count: int
    created_at: datetime


class ReviewWithReviewer(ReviewResponse):
    reviewer_username: str
    reviewer_full_name: Optional[str] = None