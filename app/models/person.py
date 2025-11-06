from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional, List
from datetime import datetime
from bson import ObjectId
from .user import PyObjectId


class Person(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )
    
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    full_name: str = Field(..., min_length=2, max_length=100)
    nickname: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[str] = None
    linkedin_url: Optional[str] = None
    company: Optional[str] = None
    job_title: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    bio: Optional[str] = None
    profile_picture_url: Optional[str] = None
    
    # Verification status
    is_verified: bool = False
    claimed_by_user_id: Optional[PyObjectId] = None
    
    # Statistics
    total_reviews: int = 0
    average_rating: float = 0.0
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    @field_validator('linkedin_url')
    @classmethod
    def validate_linkedin_url(cls, v):
        if v and not v.startswith('https://linkedin.com/in/'):
            raise ValueError('LinkedIn URL must start with https://linkedin.com/in/')
        return v

    @field_validator('phone_number')
    @classmethod
    def validate_phone_number(cls, v):
        if v and not v.replace('+', '').replace('-', '').replace(' ', '').isdigit():
            raise ValueError('Phone number must contain only digits, spaces, hyphens, and plus sign')
        return v


class PersonCreate(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=100)
    nickname: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[str] = None
    linkedin_url: Optional[str] = None
    company: Optional[str] = None
    job_title: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    bio: Optional[str] = None


class PersonUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    nickname: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[str] = None
    linkedin_url: Optional[str] = None
    company: Optional[str] = None
    job_title: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    bio: Optional[str] = None


class PersonResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    full_name: str
    nickname: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[str] = None
    linkedin_url: Optional[str] = None
    company: Optional[str] = None
    job_title: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    bio: Optional[str] = None
    is_verified: bool
    total_reviews: int
    average_rating: float
    created_at: datetime