"""
PeopleRate - Professional People Review Platform
Features comprehensive search, user management, anonymous reviews, and privacy-first design
Empowering authentic peer reviews while protecting user identity
"""

from fastapi import FastAPI, HTTPException, Depends, Query, Request, Form
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field, EmailStr, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import jwt
import bcrypt
import re
import uvicorn
from bson import ObjectId
import logging
from nlp_processor import nlp_processor
import os
from dotenv import load_dotenv
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from better_profanity import profanity

# Load environment variables
load_dotenv()

# Initialize profanity filter
profanity.load_censor_words()

# Import moderation system
from moderation import contains_profanity, filter_profanity, analyze_content, should_auto_flag

# Import email service
from email_service import send_verification_email, verify_token, send_password_reset_email

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

# Try to import MongoDB models and utilities
USE_MONGODB = False
try:
    from app.utils.database import connect_to_mongo, close_mongo_connection, init_sample_data, get_database_stats
    from app.models.mongodb_models import User as UserModel, Person as PersonModel, Review as ReviewModel
    USE_MONGODB = bool(os.getenv("MONGODB_URL") and "<username>" not in os.getenv("MONGODB_URL", ""))
    if USE_MONGODB:
        logger.info("✅ MongoDB integration enabled - data will persist")
    else:
        logger.warning("⚠️ MongoDB not configured - using in-memory mode (data will reset on restart)")
        logger.warning("💡 To enable MongoDB: Configure MONGODB_URL in .env file")
except ImportError:
    logger.warning("⚠️ MongoDB models not found - using in-memory mode")
    USE_MONGODB = False

app = FastAPI(
    title="PeopleRate API",
    description="Professional people review platform with privacy-first anonymous reviews and comprehensive search",
    version="2.2.0"
)

# Add rate limiter to app
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Custom error handlers
@app.exception_handler(404)
async def not_found_handler(request: Request, exc: HTTPException):
    """Custom 404 error page"""
    return templates.TemplateResponse("404.html", {"request": request}, status_code=404)

@app.exception_handler(500)
async def internal_error_handler(request: Request, exc: Exception):
    """Custom 500 error page"""
    logger.error(f"Internal server error: {exc}")
    return templates.TemplateResponse("500.html", {"request": request}, status_code=500)

# Startup event - required for proper async lifecycle
@app.on_event("startup")
async def startup_event():
    """Async startup handler"""
    logger.info("✅ Server startup complete - ready to handle requests")

@app.on_event("shutdown")
async def shutdown_event():
    """Async shutdown handler"""
    logger.info("👋 Server shutting down")

# CORS middleware - restrict in production
allowed_origins = os.getenv("CORS_ORIGINS", "*").split(",") if os.getenv("ENVIRONMENT") == "production" else ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security headers middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response

# Static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Security
security = HTTPBearer()
JWT_SECRET = os.getenv("SECRET_KEY", "your-enhanced-secret-key-here")
JWT_ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# In-memory database with enhanced sample data
DATABASE = {
    "users": {},
    "persons": {},
    "reviews": {},
    "scams": {},
    "scam_votes": {}
}

# Enhanced Pydantic Models
class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, schema, handler):
        schema.update(type="string")
        return schema

class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    username: str = Field(..., min_length=3, max_length=20, description="Public username for reviews")
    is_active: bool = True
    
    @field_validator('username')
    @classmethod
    def validate_username(cls, v):
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError('Username can only contain letters, numbers, and underscores')
        return v
    
    class Config:
        json_encoders = {ObjectId: str}

class UserCreate(UserBase):
    password: str
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters long')
        return v

class User(UserBase):
    id: str = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    review_count: int = 0
    reputation_score: int = 0  # Based on helpful reviews, verified status, etc.
    
    class Config:
        populate_by_name = True

class PersonBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    job_title: Optional[str] = None
    company: Optional[str] = None
    industry: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    # Bengaluru-specific fields
    area: Optional[str] = None
    category: Optional[str] = None
    whatsapp_number: Optional[str] = None
    google_maps_url: Optional[str] = None
    services_offered: Optional[List[str]] = []
    languages: Optional[List[str]] = []
    payment_modes: Optional[List[str]] = []
    established_year: Optional[int] = None
    # Social media
    linkedin_url: Optional[str] = None
    instagram_url: Optional[str] = None
    facebook_url: Optional[str] = None
    twitter_url: Optional[str] = None
    github_url: Optional[str] = None
    website_url: Optional[str] = None
    bio: Optional[str] = None
    skills: Optional[List[str]] = []
    experience_years: Optional[int] = None
    education: Optional[str] = None
    certifications: Optional[List[str]] = []
    
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
    
    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v):
        if v and not re.match(r'^\+?[\d\s\-\(\)]{10,}$', v):
            raise ValueError('Invalid phone number format')
        return v

class Person(PersonBase):
    id: str = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    review_count: int = 0
    average_rating: float = 0.0
    total_rating: int = 0
    
    class Config:
        populate_by_name = True

class ReviewBase(BaseModel):
    person_id: str
    rating: int = Field(..., ge=1, le=5)
    comment: str = Field(..., min_length=10, max_length=1000)
    title: Optional[str] = Field(None, max_length=100, description="Review title/headline")
    relationship: Optional[str] = None  # colleague, client, manager, etc.
    work_quality: Optional[int] = Field(None, ge=1, le=5)
    communication: Optional[int] = Field(None, ge=1, le=5)
    reliability: Optional[int] = Field(None, ge=1, le=5)
    professionalism: Optional[int] = Field(None, ge=1, le=5)
    would_recommend: Optional[bool] = None

class Review(ReviewBase):
    id: str = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    reviewer_id: str
    reviewer_username: str  # Public username, not real name
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_verified: bool = False
    helpful_count: int = 0
    reported_count: int = 0  # For moderation
    
    class Config:
        populate_by_name = True

# Scam Alert Models
class ScamBase(BaseModel):
    title: str = Field(..., min_length=10, max_length=200)
    description: str = Field(..., min_length=50, max_length=1000)
    how_it_works: str = Field(..., min_length=50, max_length=1000)
    prevention_tips: List[str]
    severity: str = Field(..., pattern="^(Critical|High|Medium)$")
    location: str = Field(default="Bengaluru, India")
    reported_cases: int = Field(default=0, ge=0)

class Scam(ScamBase):
    id: str = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    upvotes: int = 0
    downvotes: int = 0
    reported_date: datetime = Field(default_factory=datetime.utcnow)
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True

class ScamVote(BaseModel):
    scam_id: str
    user_id: str
    vote_type: str  # 'upvote' or 'downvote'
    voted_at: datetime = Field(default_factory=datetime.utcnow)

# Enhanced sample data with more realistic profiles
def initialize_sample_data():
    """Initialize sample data; prefers Bengaluru-local dataset when available."""
    seed_payload = None
    try:
        from scripts.bangalore_seed_data import get_bangalore_seed_data
        seed_payload = get_bangalore_seed_data()
    except ImportError:
        logger.info("Bengaluru seed data not found, falling back to legacy global dataset")

    if seed_payload:
        DATABASE["users"].clear()
        DATABASE["persons"].clear()
        DATABASE["reviews"].clear()

        for user in seed_payload.get("users", []):
            DATABASE["users"][user["id"]] = user

        reviews = seed_payload.get("reviews", [])
        for review in reviews:
            DATABASE["reviews"][review["id"]] = review

        for person in seed_payload.get("persons", []):
            person_id = person["id"]
            attached_reviews = [r for r in reviews if r["person_id"] == person_id]
            if attached_reviews:
                total_rating = sum(r.get("rating", 0) for r in attached_reviews)
                person["review_count"] = len(attached_reviews)
                person["total_rating"] = total_rating
                person["average_rating"] = round(total_rating / len(attached_reviews), 1)
            else:
                person.setdefault("review_count", 0)
                person.setdefault("total_rating", 0)
                person.setdefault("average_rating", 0.0)

            DATABASE["persons"][person_id] = person

        # Initialize scam alerts for Bengaluru seed too
        initialize_scam_alerts()
        
        logger.info(
            "Seeded Bengaluru dataset: %s users, %s vendors, %s reviews",
            len(DATABASE["users"]),
            len(DATABASE["persons"]),
            len(DATABASE["reviews"]),
        )
        return

    from scripts.generate_50_users import generate_all_users, generate_all_persons
    
    # Add base 3 users
    users_data = [
        {
            "id": "user1",
            "email": "john.reviewer@email.com",
            "full_name": "John Reviewer",
            "username": "TechReviewer2024",
            "password": bcrypt.hashpw("password123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
            "is_active": True,
            "created_at": datetime.utcnow(),
            "review_count": 3,
            "reputation_score": 85
        },
        {
            "id": "user2", 
            "email": "sarah.manager@email.com",
            "full_name": "Sarah Manager",
            "username": "ProjectManager_Pro",
            "password": bcrypt.hashpw("password123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
            "is_active": True,
            "created_at": datetime.utcnow(),
            "review_count": 4,
            "reputation_score": 92
        },
        {
            "id": "user3",
            "email": "mike.colleague@email.com", 
            "full_name": "Mike Colleague",
            "username": "DataScience_Mike",
            "password": bcrypt.hashpw("password123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
            "is_active": True,
            "created_at": datetime.utcnow(),
            "review_count": 2,
            "reputation_score": 78
        }
    ]
    
    # Add generated diverse users
    generated_users = generate_all_users()
    users_data.extend(generated_users)
    
    for user in users_data:
        DATABASE["users"][user["id"]] = user
    
    # Sample persons with detailed profiles
    persons_data = [
        {
            "id": "person1",
            "name": "Alice Johnson",
            "email": "alice.johnson@microsoft.com",
            "phone": "+1-555-0123",
            "job_title": "Senior Software Engineer",
            "company": "Microsoft",
            "industry": "Technology",
            "city": "Seattle",
            "state": "WA",
            "country": "USA",
            "linkedin_url": "https://linkedin.com/in/alice-johnson",
            "bio": "Experienced software engineer specializing in cloud computing and AI. Lead developer on Azure ML platform with 8+ years in tech industry.",
            "skills": ["Python", "Azure", "Machine Learning", "JavaScript", "React"],
            "experience_years": 8,
            "education": "MS Computer Science, University of Washington",
            "certifications": ["Azure Solutions Architect", "AWS Certified Developer"],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "review_count": 5,
            "average_rating": 4.6,
            "total_rating": 23
        },
        {
            "id": "person2",
            "name": "Robert Chen",
            "email": "r.chen@google.com",
            "phone": "+1-555-0234", 
            "job_title": "Product Manager",
            "company": "Google",
            "industry": "Technology",
            "city": "Mountain View",
            "state": "CA",
            "country": "USA",
            "linkedin_url": "https://linkedin.com/in/robert-chen",
            "bio": "Strategic product manager with expertise in mobile applications and user experience. Led product launches reaching 100M+ users.",
            "skills": ["Product Strategy", "Data Analysis", "User Research", "Agile", "SQL"],
            "experience_years": 6,
            "education": "MBA Stanford, BS Engineering UC Berkeley",
            "certifications": ["Certified Scrum Product Owner", "Google Analytics"],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "review_count": 3,
            "average_rating": 4.3,
            "total_rating": 13
        },
        {
            "id": "person3",
            "name": "Emily Rodriguez",
            "email": "emily.rodriguez@apple.com",
            "phone": "+1-555-0345",
            "job_title": "UX Design Director",
            "company": "Apple",
            "industry": "Technology",
            "city": "Cupertino",
            "state": "CA", 
            "country": "USA",
            "linkedin_url": "https://linkedin.com/in/emily-rodriguez",
            "bio": "Award-winning UX designer with 10+ years creating intuitive user experiences. Led design teams for major product launches at Apple.",
            "skills": ["UX Design", "Figma", "Design Systems", "User Research", "Prototyping"],
            "experience_years": 10,
            "education": "MFA Design, Art Center College of Design",
            "certifications": ["Google UX Design Certificate", "Adobe Certified Expert"],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "review_count": 7,
            "average_rating": 4.8,
            "total_rating": 34
        },
        {
            "id": "person4", 
            "name": "David Kim",
            "email": "david.kim@amazon.com",
            "phone": "+1-555-0456",
            "job_title": "Senior Data Scientist",
            "company": "Amazon",
            "industry": "Technology",
            "city": "Seattle",
            "state": "WA",
            "country": "USA",
            "linkedin_url": "https://linkedin.com/in/david-kim",
            "bio": "Data scientist specializing in machine learning and analytics. Built recommendation systems serving millions of customers daily.",
            "skills": ["Python", "Machine Learning", "SQL", "TensorFlow", "Statistics"],
            "experience_years": 7,
            "education": "PhD Statistics, MIT",
            "certifications": ["AWS Machine Learning", "TensorFlow Developer"],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "review_count": 4,
            "average_rating": 4.5,
            "total_rating": 18
        },
        {
            "id": "person5",
            "name": "Sarah Thompson",
            "email": "sarah.thompson@consulting.com",
            "phone": "+1-555-0567",
            "job_title": "Management Consultant",
            "company": "McKinsey & Company",
            "industry": "Consulting",
            "city": "New York",
            "state": "NY",
            "country": "USA",
            "linkedin_url": "https://linkedin.com/in/sarah-thompson",
            "bio": "Management consultant helping Fortune 500 companies with digital transformation and operational excellence initiatives.",
            "skills": ["Strategy", "Digital Transformation", "Process Improvement", "Leadership", "Analytics"],
            "experience_years": 5,
            "education": "MBA Harvard Business School",
            "certifications": ["PMP", "Six Sigma Black Belt"],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "review_count": 6,
            "average_rating": 4.7,
            "total_rating": 28
        },
        {
            "id": "person6",
            "name": "Dr. Michael Brown",
            "email": "m.brown@hospital.com",
            "phone": "+1-555-0678",
            "job_title": "Cardiologist",
            "company": "Johns Hopkins Hospital",
            "industry": "Healthcare",
            "city": "Baltimore",
            "state": "MD",
            "country": "USA",
            "linkedin_url": "https://linkedin.com/in/dr-michael-brown",
            "bio": "Board-certified cardiologist with 15+ years experience. Specialist in interventional cardiology and heart failure treatment.",
            "skills": ["Cardiology", "Patient Care", "Medical Research", "Teaching", "Leadership"],
            "experience_years": 15,
            "education": "MD Johns Hopkins, Residency Mayo Clinic",
            "certifications": ["Board Certified Cardiology", "Advanced Cardiac Life Support"],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "review_count": 8,
            "average_rating": 4.9,
            "total_rating": 39
        },
        {
            "id": "person7",
            "name": "Sasikala",
            "email": "sasikala.chennai@email.com",
            "phone": "+91-9952282170",
            "job_title": "Software Developer",
            "company": "Tech Solutions",
            "industry": "Technology",
            "city": "Chennai",
            "state": "Tamil Nadu",
            "country": "India",
            "linkedin_url": "https://linkedin.com/in/sasikala-chennai",
            "instagram_url": "https://instagram.com/sasikala.dev",
            "twitter_url": "https://twitter.com/sasikala_tech",
            "github_url": "https://github.com/sasikala-chennai",
            "bio": "Experienced software developer with expertise in full-stack development and cloud technologies.",
            "skills": ["Python", "JavaScript", "React", "Node.js", "AWS"],
            "experience_years": 5,
            "education": "BTech Computer Science",
            "certifications": ["AWS Certified Developer"],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "review_count": 0,
            "average_rating": 0.0,
            "total_rating": 0
        },
        {
            "id": "person8",
            "name": "Sahasra",
            "email": "sahasra@email.com",
            "phone": "+1-555-0789",
            "job_title": "Data Analyst",
            "company": "Analytics Corp",
            "industry": "Technology",
            "city": "Bangalore",
            "state": "Karnataka",
            "country": "India",
            "linkedin_url": "https://linkedin.com/in/sahasra",
            "bio": "Data analyst specializing in business intelligence and data visualization.",
            "skills": ["SQL", "Python", "Tableau", "Power BI", "Data Analysis"],
            "experience_years": 3,
            "education": "MS Data Science",
            "certifications": ["Tableau Desktop Specialist"],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "review_count": 0,
            "average_rating": 0.0,
            "total_rating": 0
        },
        {
            "id": "person9",
            "name": "Haasini",
            "email": "haasini@email.com",
            "phone": "+1-555-0890",
            "job_title": "Product Designer",
            "company": "Design Studio",
            "industry": "Technology",
            "city": "Hyderabad",
            "state": "Telangana",
            "country": "India",
            "linkedin_url": "https://linkedin.com/in/haasini",
            "bio": "Creative product designer with a passion for user-centered design and innovative solutions.",
            "skills": ["UI/UX Design", "Figma", "Adobe XD", "Prototyping", "User Research"],
            "experience_years": 4,
            "education": "BFA Design",
            "certifications": ["Google UX Design Certificate"],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "review_count": 0,
            "average_rating": 0.0,
            "total_rating": 0
        },
        {
            "id": "person10",
            "name": "Sasikala",
            "email": "sasikala.sanjose@email.com",
            "phone": "+1-408-555-0999",
            "job_title": "Senior Engineer",
            "company": "Silicon Valley Tech",
            "industry": "Technology",
            "city": "San Jose",
            "state": "CA",
            "country": "USA",
            "linkedin_url": "https://linkedin.com/in/sasikala-sanjose",
            "facebook_url": "https://facebook.com/sasikala.engineer",
            "github_url": "https://github.com/sasikala-sj",
            "website_url": "https://sasikala.dev",
            "bio": "Senior engineer with extensive experience in distributed systems and microservices architecture.",
            "skills": ["Java", "Kubernetes", "Docker", "Microservices", "System Design"],
            "experience_years": 8,
            "education": "MS Computer Science, San Jose State University",
            "certifications": ["Kubernetes Certified", "Java Certified Professional"],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "review_count": 0,
            "average_rating": 0.0,
            "total_rating": 0
        }
    ]
    
    # Add generated diverse persons
    generated_persons = generate_all_persons()
    persons_data.extend(generated_persons)
    
    # Sample reviews with usernames only (privacy protected)
    reviews_data = [
        {
            "id": "review1",
            "person_id": "person1",
            "reviewer_id": "user1", 
            "reviewer_username": "TechReviewer2024",
            "rating": 5,
            "title": "Outstanding technical expertise and mentorship",
            "comment": "Alice is an exceptional software engineer. I worked with her on the Azure ML platform project and was consistently impressed by her technical expertise and problem-solving abilities. She has a knack for breaking down complex problems into manageable solutions and always delivers high-quality code. Her knowledge of machine learning and cloud architecture is outstanding. Highly recommend working with Alice on any technical project.",
            "relationship": "colleague",
            "work_quality": 5,
            "communication": 5,
            "reliability": 5,
            "professionalism": 5,
            "would_recommend": True,
            "created_at": datetime.utcnow() - timedelta(days=5),
            "updated_at": datetime.utcnow() - timedelta(days=5),
            "is_verified": True,
            "helpful_count": 12,
            "reported_count": 0
        },
        {
            "id": "review2",
            "person_id": "person1",
            "reviewer_id": "user2",
            "reviewer_username": "ProjectManager_Pro",
            "rating": 4,
            "title": "Great developer, excellent team player",
            "comment": "Had the pleasure of managing Alice for 2 years. She's incredibly talented and always goes above and beyond. Her ability to mentor junior developers is remarkable, and she consistently contributes innovative ideas to our team. The only minor area for improvement would be her presentation skills, but her technical abilities more than make up for it.",
            "relationship": "manager",
            "work_quality": 5,
            "communication": 4,
            "reliability": 5,
            "professionalism": 5,
            "would_recommend": True,
            "created_at": datetime.utcnow() - timedelta(days=15),
            "updated_at": datetime.utcnow() - timedelta(days=15),
            "is_verified": True,
            "helpful_count": 8,
            "reported_count": 0
        },
        {
            "id": "review3",
            "person_id": "person2",
            "reviewer_id": "user1",
            "reviewer_username": "TechReviewer2024",
            "rating": 4,
            "title": "Solid product management skills",
            "comment": "Robert is a solid product manager with great analytical skills. He led our mobile app redesign project and delivered excellent results. His data-driven approach to decision making is impressive, and he's great at stakeholder management. Communication is clear and he keeps everyone aligned on priorities.",
            "relationship": "team member",
            "work_quality": 4,
            "communication": 5,
            "reliability": 4,
            "professionalism": 4,
            "would_recommend": True,
            "created_at": datetime.utcnow() - timedelta(days=10),
            "updated_at": datetime.utcnow() - timedelta(days=10),
            "is_verified": True,
            "helpful_count": 6,
            "reported_count": 0
        },
        {
            "id": "review4", 
            "person_id": "person3",
            "reviewer_id": "user2",
            "reviewer_username": "ProjectManager_Pro",
            "rating": 5,
            "title": "World-class UX design expertise",
            "comment": "Emily is hands-down one of the best UX designers I've ever worked with. Her designs are not only beautiful but incredibly functional. She has an amazing ability to understand user needs and translate them into intuitive interfaces. Led our design system overhaul which improved consistency across all products. A true design leader!",
            "relationship": "client",
            "work_quality": 5,
            "communication": 5,
            "reliability": 5,
            "professionalism": 5,
            "would_recommend": True,
            "created_at": datetime.utcnow() - timedelta(days=20),
            "updated_at": datetime.utcnow() - timedelta(days=20),
            "is_verified": True,
            "helpful_count": 15,
            "reported_count": 0
        },
        {
            "id": "review5",
            "person_id": "person4",
            "reviewer_id": "user3",
            "reviewer_username": "DataScience_Mike",
            "rating": 4,
            "title": "Brilliant data scientist and team player",
            "comment": "David is a brilliant data scientist with deep knowledge of machine learning algorithms. Worked with him on recommendation system improvements and saw significant performance gains. He's methodical in his approach and great at explaining complex concepts to non-technical stakeholders. Reliable team player who always meets deadlines.",
            "relationship": "colleague",
            "work_quality": 5,
            "communication": 4,
            "reliability": 5,
            "professionalism": 4,
            "would_recommend": True,
            "created_at": datetime.utcnow() - timedelta(days=8),
            "updated_at": datetime.utcnow() - timedelta(days=8),
            "is_verified": True,
            "helpful_count": 9,
            "reported_count": 0
        },
        {
            "id": "review6",
            "person_id": "person5",
            "reviewer_id": "user1",
            "reviewer_username": "TechReviewer2024",
            "rating": 5,
            "title": "Exceptional consulting results",
            "comment": "Sarah delivered outstanding results as our management consultant. Her strategic thinking and execution capabilities are top-notch. She quickly understood our business challenges and provided actionable solutions that drove real value. Professional, responsive, and a pleasure to work with. Would definitely hire her again for future projects.",
            "relationship": "client",
            "work_quality": 5,
            "communication": 5,
            "reliability": 5,
            "professionalism": 5,
            "would_recommend": True,
            "created_at": datetime.utcnow() - timedelta(days=12),
            "updated_at": datetime.utcnow() - timedelta(days=12),
            "is_verified": True,
            "helpful_count": 11,
            "reported_count": 0
        },
        {
            "id": "review7",
            "person_id": "person6", 
            "reviewer_id": "user2",
            "reviewer_username": "ProjectManager_Pro",
            "rating": 5,
            "title": "Life-saving medical expertise",
            "comment": "Dr. Brown is an exceptional cardiologist who saved my father's life. His expertise, compassion, and dedication to patient care are remarkable. He took time to explain the treatment options clearly and made us feel confident in the care plan. The surgery was successful, and the follow-up care has been excellent. Highly recommend Dr. Brown to anyone needing cardiac care.",
            "relationship": "patient family",
            "work_quality": 5,
            "communication": 5,
            "reliability": 5,
            "professionalism": 5,
            "would_recommend": True,
            "created_at": datetime.utcnow() - timedelta(days=25),
            "updated_at": datetime.utcnow() - timedelta(days=25),
            "is_verified": True,
            "helpful_count": 18,
            "reported_count": 0
        }
    ]
    
    # Initialize database
    for user in users_data:
        DATABASE["users"][user["id"]] = user
        
    for person in persons_data:
        DATABASE["persons"][person["id"]] = person
        
    for review in reviews_data:
        DATABASE["reviews"][review["id"]] = review
    
    # Initialize scam alerts
    initialize_scam_alerts()

def initialize_scam_alerts():
    """Initialize common scam alerts for Bengaluru/India"""
    scams_data = [
        {
            "id": "scam_001",
            "title": "📞 OTP Call Merging Scam - Bank Account Takeover",
            "description": "Fraudsters call pretending to be bank officials or delivery agents, asking you to press numbers (like *1 or 0) during the call. This triggers call forwarding/merging, giving them access to your OTP messages and potentially your bank account.",
            "how_it_works": "The scammer calls posing as a bank representative, courier service, or customer care. They ask you to press certain digits (*1, 0, etc.) claiming it's for verification or to cancel a fake transaction. When you press these numbers, it activates call forwarding on your phone, redirecting all your calls and SMS (including OTPs) to their number. They then use these OTPs to access your bank accounts, credit cards, or other sensitive accounts.",
            "prevention_tips": [
                "NEVER press any numbers (*1, 0, #) when receiving unexpected calls from 'banks' or 'couriers'",
                "Banks and delivery services will NEVER ask you to press digits during a call",
                "If asked to press buttons, hang up immediately and call the official customer care number",
                "Check your phone's call forwarding settings regularly (dial *#21# to check)",
                "Enable two-factor authentication beyond just SMS OTPs (use authenticator apps)",
                "If you've pressed any numbers during a suspicious call, immediately dial ##002# to deactivate all call forwarding"
            ],
            "severity": "Critical",
            "location": "Bengaluru & All India",
            "reported_cases": 2847,
            "upvotes": 1543,
            "downvotes": 12,
            "reported_date": datetime.utcnow() - timedelta(days=5),
            "last_updated": datetime.utcnow() - timedelta(days=1)
        },
        {
            "id": "scam_002",
            "title": "🏍️ Two-Wheeler Accident Extortion Scam",
            "description": "Bikers intentionally hit your vehicle at low speed, then demand immediate cash payment (₹5,000-₹20,000) claiming damage and threatening to involve police. They create a scene and pressure you to pay on the spot.",
            "how_it_works": "A bike rider (often working in a group) deliberately hits your car or two-wheeler at a traffic signal or quiet road. They immediately start shouting about damage to their bike, threatening to call police, or claim injury. They demand instant cash settlement, usually ₹10,000-₹20,000. If you refuse, their accomplices arrive to intimidate you. They target lone drivers, especially women and elderly, counting on your fear of police hassle.",
            "prevention_tips": [
                "Stay calm and insist on filing a police complaint - genuine accident victims won't refuse",
                "Take photos/videos of the scene, damage, and people involved immediately",
                "Call 100 (police) or 112 (emergency) immediately if threatened",
                "Don't agree to cash settlement on the spot - always involve police for insurance claims",
                "Install a dashcam in your vehicle to record such incidents",
                "Note the bike number plate - if they resist, it's likely a scam",
                "If in a crowded area, ask bystanders to stay as witnesses"
            ],
            "severity": "High",
            "location": "Bengaluru (ORR, Marathahalli, Whitefield, HSR Layout)",
            "reported_cases": 523,
            "upvotes": 892,
            "downvotes": 34,
            "reported_date": datetime.utcnow() - timedelta(days=12),
            "last_updated": datetime.utcnow() - timedelta(days=3)
        },
        {
            "id": "scam_003",
            "title": "📦 Fake Courier OTP Scam",
            "description": "Scammers pose as courier delivery agents (Swiggy, Zomato, Amazon, Flipkart) and ask for OTPs claiming it's needed to deliver your package or verify your identity. They use the OTP to access your account or make fraudulent transactions.",
            "how_it_works": "You receive a call from someone claiming to be from a delivery service. They say they're at your door or need to verify delivery. They ask you to share the OTP that was just sent to your phone 'for verification'. Once shared, they use this OTP to access your payment apps (PhonePe, Paytm, GPay), e-commerce accounts, or bank accounts to make unauthorized purchases or transfers.",
            "prevention_tips": [
                "Delivery agents NEVER need OTPs - OTPs are only for YOU to verify transactions",
                "Never share OTPs with anyone, even if they claim to be from courier services",
                "Genuine delivery persons only need your signature or a package code, not OTP",
                "If someone asks for OTP, hang up and contact the official customer care",
                "Enable app-level locks (PIN/fingerprint) on payment apps for extra security"
            ],
            "severity": "Critical",
            "location": "All India (High in Bengaluru, Delhi, Mumbai)",
            "reported_cases": 1654,
            "upvotes": 1205,
            "downvotes": 18,
            "reported_date": datetime.utcnow() - timedelta(days=8),
            "last_updated": datetime.utcnow() - timedelta(days=2)
        },
        {
            "id": "scam_004",
            "title": "⚡ Electricity Bill Refund Scam",
            "description": "Fraudsters call claiming to be from BESCOM (Bangalore Electricity Supply Company) offering refunds for overpaid electricity bills. They ask you to click a link or share bank details to process the 'refund'.",
            "how_it_works": "The scammer calls saying you're eligible for a refund due to billing errors or government schemes. They send a link via SMS or WhatsApp asking you to enter bank details, card numbers, CVV, or OTP to 'verify' your account for refund. The link is actually a phishing site that steals your banking credentials. Some variants involve screen-sharing apps that give them remote access to your phone.",
            "prevention_tips": [
                "BESCOM never calls customers for refunds - refunds are processed automatically to your bank",
                "Never click on links sent via SMS or WhatsApp claiming to be from utility companies",
                "BESCOM will never ask for bank details, OTPs, or card information over phone",
                "Check your official BESCOM account online or visit the nearest BESCOM office for refund queries",
                "Never download screen-sharing apps (AnyDesk, TeamViewer) at the request of unknown callers"
            ],
            "severity": "High",
            "location": "Bengaluru",
            "reported_cases": 389,
            "upvotes": 645,
            "downvotes": 28,
            "reported_date": datetime.utcnow() - timedelta(days=15),
            "last_updated": datetime.utcnow() - timedelta(days=5)
        },
        {
            "id": "scam_005",
            "title": "🏦 Bank Account Freeze Scam",
            "description": "You receive a call claiming your bank account/PAN/Aadhaar is being blocked due to suspicious activity or KYC issues. They ask you to share OTP or install remote access apps to 'fix' the problem urgently.",
            "how_it_works": "Scammers impersonate bank officials, RBI, or government agencies. They create panic by claiming your account will be frozen in hours unless you complete KYC update or verify your identity. They pressure you to share OTPs, banking credentials, or install remote access software (AnyDesk, TeamViewer). Once they have access, they drain your account, make online purchases, or steal sensitive data.",
            "prevention_tips": [
                "Banks NEVER call asking for OTPs, card details, CVV, or PIN",
                "RBI/government agencies don't call individuals about account freezing",
                "Never install screen-sharing apps at the request of unknown callers",
                "If you receive such a call, hang up and call your bank's official customer care number",
                "Banks send official letters/emails for KYC updates, not urgent phone calls",
                "Visit your bank branch in person if you have doubts about your account status"
            ],
            "severity": "Critical",
            "location": "All India",
            "reported_cases": 3156,
            "upvotes": 1876,
            "downvotes": 24,
            "reported_date": datetime.utcnow() - timedelta(days=3),
            "last_updated": datetime.utcnow()
        },
        {
            "id": "scam_006",
            "title": "💼 Fake Job Offer Scam",
            "description": "Scammers post fake job offers on WhatsApp, Telegram, or job portals offering work-from-home opportunities with high pay. They ask for registration fees, security deposits, or personal documents and disappear after receiving money.",
            "how_it_works": "You receive messages about lucrative work-from-home jobs (data entry, product reviews, survey completion) with promises of ₹20,000-₹50,000/month for minimal work. They ask for a registration fee (₹500-₹5,000), 'refundable' security deposit, or copies of Aadhaar/PAN. Once paid, they either vanish or keep asking for more fees citing various reasons (training, software, verification).",
            "prevention_tips": [
                "Legitimate companies never ask for money upfront for job offers",
                "Research the company thoroughly - check reviews, official website, and registration",
                "Be wary of jobs promising unusually high pay for simple tasks",
                "Never share Aadhaar/PAN copies unless verified through official channels",
                "If asked to pay for 'training' or 'registration', it's likely a scam",
                "Use verified job portals (Naukri, LinkedIn) and ignore WhatsApp/Telegram job offers"
            ],
            "severity": "Medium",
            "location": "All India (targeting youth in Bengaluru, Hyderabad, Delhi)",
            "reported_cases": 1247,
            "upvotes": 723,
            "downvotes": 56,
            "reported_date": datetime.utcnow() - timedelta(days=20),
            "last_updated": datetime.utcnow() - timedelta(days=7)
        }
    ]
    
    for scam in scams_data:
        DATABASE["scams"][scam["id"]] = scam

# INITIALIZE DATABASE IMMEDIATELY ON MODULE LOAD
logger.info("🚀 PeopleRate starting up...")
logger.info("🔧 Initializing in-memory database...")
initialize_sample_data()
logger.info(f"✅ Database ready: {len(DATABASE['users'])} users, {len(DATABASE['persons'])} persons, {len(DATABASE['reviews'])} reviews, {len(DATABASE['scams'])} scam alerts")
logger.info("🌐 Server is ready to accept connections on http://localhost:8080")

# Helper functions
def create_jwt_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=30)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)

def verify_jwt_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.PyJWTError:
        return None

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    payload = verify_jwt_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    
    user_id = payload.get("sub")
    user = DATABASE["users"].get(user_id)
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    
    return user

# Content Moderation Functions
def check_profanity(text: str) -> dict:
    """Check if text contains profanity and return analysis"""
    has_profanity = profanity.contains_profanity(text)
    censored_text = profanity.censor(text) if has_profanity else text
    
    return {
        "has_profanity": has_profanity,
        "original_text": text,
        "censored_text": censored_text,
        "severity": "high" if has_profanity else "none"
    }

def filter_profanity(text: str) -> str:
    """Remove profanity from text and return cleaned version"""
    return profanity.censor(text)

def should_auto_flag(text: str) -> bool:
    """Determine if content should be auto-flagged for moderation"""
    # Check for profanity
    if profanity.contains_profanity(text):
        return True
    
    # Check for excessive caps (shouting)
    if len(text) > 20 and sum(1 for c in text if c.isupper()) / len(text) > 0.7:
        return True
    
    # Check for suspicious patterns
    spam_patterns = [
        r'(click here|buy now|limited offer)',
        r'(\d{10,})',  # Long numbers (potential spam)
        r'(http://|https://|www\.)',  # URLs
    ]
    
    for pattern in spam_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    
    return False

def analyze_content(text: str) -> dict:
    """Comprehensive content analysis for moderation"""
    profanity_check = check_profanity(text)
    auto_flag = should_auto_flag(text)
    
    return {
        "has_profanity": profanity_check["has_profanity"],
        "censored_text": profanity_check["censored_text"],
        "should_flag": auto_flag,
        "severity": profanity_check["severity"],
        "original_length": len(text),
        "cleaned_length": len(profanity_check["censored_text"])
    }

MIN_SEARCH_CONFIDENCE = 55

def search_persons_enhanced(query: str, limit: int = 10) -> List[Dict]:
    """Enhanced search with pattern recognition and scoring"""
    if not query:
        # Return all persons if no query
        persons = list(DATABASE["persons"].values())
        return persons[:limit]
    
    query_lower = query.lower()
    results = []
    
    # Pattern detection
    email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
    phone_pattern = re.compile(r'[\+]?[\d\s\-\(\)]{10,}')
    linkedin_pattern = re.compile(r'linkedin\.com/in/[\w\-]+')
    
    is_email_search = bool(email_pattern.search(query))
    is_phone_search = bool(phone_pattern.search(query))
    is_linkedin_search = bool(linkedin_pattern.search(query))
    
    for person in DATABASE["persons"].values():
        score = 0
        match_found = False
        
        # Exact match scoring
        if is_email_search and person.get("email"):
            if query_lower in person["email"].lower():
                score += 100
                match_found = True
        elif is_phone_search and person.get("phone"):
            if query in person["phone"]:
                score += 100
                match_found = True
        elif is_linkedin_search and person.get("linkedin_url"):
            if query_lower in person["linkedin_url"].lower():
                score += 100
                match_found = True
        else:
            # Text-based search
            searchable_fields = [
                ("name", 50),
                ("job_title", 30),
                ("company", 30),
                ("industry", 20),
                ("city", 20),
                ("bio", 15),
                ("skills", 10)
            ]
            
            for field, weight in searchable_fields:
                value = person.get(field)
                if value:
                    if isinstance(value, list):
                        value = " ".join(value)
                    if query_lower in str(value).lower():
                        score += weight
                        match_found = True
        
        # Boost score based on rating and review count
        if match_found:
            rating_boost = person.get("average_rating", 0) * 5
            review_boost = min(person.get("review_count", 0) * 2, 20)
            score += rating_boost + review_boost
            
            results.append((person, score))
    
    # Sort by score and return
    results.sort(key=lambda x: x[1], reverse=True)
    return [person for person, score in results[:limit]]

# API Routes
@app.get("/")
async def home(request: Request):
    logger.info(f"📥 Homepage request from {request.client.host}")
    """Home page with professional design"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/auth")
async def auth_page(request: Request):
    """Authentication page for login/register"""
    return templates.TemplateResponse("auth.html", {"request": request})

@app.get("/profile")
async def profile_page(request: Request):
    """User profile page"""
    return templates.TemplateResponse("profile.html", {"request": request})

@app.get("/my-reviews")
async def my_reviews_page(request: Request):
    """My reviews page"""
    return templates.TemplateResponse("my-reviews.html", {"request": request})

@app.get("/person/{person_id}")
async def person_detail_page(request: Request, person_id: str):
    """Person detail page"""
    return templates.TemplateResponse("person-detail.html", {"request": request})

@app.get("/legal/terms")
async def terms_page(request: Request):
    """Terms of Service page"""
    return templates.TemplateResponse("terms.html", {"request": request})

@app.get("/legal/privacy")
async def privacy_page(request: Request):
    """Privacy Policy page"""
    return templates.TemplateResponse("privacy.html", {"request": request})

@app.get("/moderation")
async def moderation_page(request: Request):
    """Moderation Guidelines page"""
    return templates.TemplateResponse("moderation.html", {"request": request})

@app.get("/scam-alert")
async def scam_alert_page(request: Request):
    """Scam Alert page"""
    return templates.TemplateResponse("scam-alert.html", {"request": request})

@app.post("/api/auth/register")
@limiter.limit("5/hour")  # Prevent spam registration
async def register_user(request: Request, user: UserCreate):
    """Register a new user with username for anonymous reviews"""
    # Check if email exists
    for existing_user in DATABASE["users"].values():
        if existing_user["email"] == user.email:
            raise HTTPException(status_code=400, detail="Email already registered")
    
    # Check if username exists
    for existing_user in DATABASE["users"].values():
        if existing_user["username"] == user.username:
            raise HTTPException(status_code=400, detail="Username already taken")
    
    # Hash password
    hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt())
    
    # Create user
    user_id = str(ObjectId())
    user_data = {
        "id": user_id,
        "email": user.email,
        "full_name": user.full_name,
        "username": user.username,
        "password": hashed_password.decode('utf-8'),
        "is_active": user.is_active,
        "created_at": datetime.utcnow(),
        "review_count": 0,
        "reputation_score": 0,
        "email_verified": False
    }
    
    DATABASE["users"][user_id] = user_data
    
    # Send verification email (MVP: file-based)
    try:
        base_url = str(request.base_url).rstrip('/')
        send_verification_email(user.email, user_id, user.username, base_url)
        logger.info(f"📧 Verification email sent for user: {user.username}")
    except Exception as e:
        logger.error(f"Failed to send verification email: {e}")
    
    # Create JWT token
    token = create_jwt_token({"sub": user_id, "email": user.email, "username": user.username})
    
    return {
        "message": "User registered successfully",
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user_id,
            "email": user.email,
            "username": user.username,
            "full_name": user.full_name
        }
    }

@app.post("/api/auth/login")
@limiter.limit("10/minute")  # Prevent brute force attacks
async def login_user(request: Request, email: str = Form(...), password: str = Form(...)):
    """Login user"""
    # Find user
    user = None
    for u in DATABASE["users"].values():
        if u["email"] == email:
            user = u
            break
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Verify password
    if not bcrypt.checkpw(password.encode('utf-8'), user["password"].encode('utf-8')):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Create JWT token
    token = create_jwt_token({"sub": user["id"], "email": user["email"], "username": user["username"]})
    
    return {
        "message": "Login successful",
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user["id"],
            "email": user["email"],
            "username": user["username"],
            "full_name": user["full_name"],
            "review_count": user.get("review_count", 0),
            "reputation_score": user.get("reputation_score", 0)
        }
    }

@app.get("/auth/me")
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current authenticated user information"""
    return {
        "id": current_user["id"],
        "email": current_user["email"],
        "username": current_user["username"],
        "full_name": current_user["full_name"],
        "review_count": current_user.get("review_count", 0),
        "reputation_score": current_user.get("reputation_score", 0)
    }

@app.get("/api/persons/search")
async def search_persons(
    q: str = Query("", description="Natural language search query"),
    limit: int = Query(10, le=50, description="Maximum number of results")
):
    """Natural language search for persons - understands queries like 'sasikala who is into consulting business in Hyderabad'"""
    try:
        # Parse natural language query
        parsed_query = nlp_processor.parse_search_query(q)
        logger.info(f"Parsed query: {parsed_query}")
        
        # Get all persons and score them
        results = []
        for person in DATABASE["persons"].values():
            score = nlp_processor.generate_search_score(person, parsed_query)
            # Only include results with meaningful matches (score >= 30)
            # This filters out weak/random matches
            if score >= 30:
                results.append((person, score))
                logger.info(f"Match found: {person.get('name')} with score {score}")
        
        # Sort by score
        results.sort(key=lambda x: x[1], reverse=True)
        top_score = results[0][1] if results else 0
        confidence_cutoff = max(MIN_SEARCH_CONFIDENCE, top_score - 15)
        suggest_add_person = True
        persons: List[Dict[str, Any]] = []

        if results and top_score >= MIN_SEARCH_CONFIDENCE:
            persons = [person for person, score in results if score >= confidence_cutoff][:limit]
            suggest_add_person = len(persons) == 0
        else:
            logger.info(
                "Low confidence search - suppressing matches (query='%s', top_score=%s)",
                q,
                top_score
            )
            suggest_add_person = True
            persons = []
        
        return {
            "query": q,
            "parsed": parsed_query,
            "count": len(persons),
            "persons": persons,
            "top_score": top_score,
            "confidence_cutoff": confidence_cutoff,
            "suggest_add_person": suggest_add_person
        }
    except Exception as e:
        logger.error(f"Search error: {str(e)}")
        raise HTTPException(status_code=500, detail="Search failed")

@app.post("/api/persons")
async def create_person(person: PersonBase, current_user: dict = Depends(get_current_user)):
    """Create a new person profile"""
    person_id = str(ObjectId())
    person_data = person.dict()
    person_data.update({
        "id": person_id,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "review_count": 0,
        "average_rating": 0.0,
        "total_rating": 0
    })
    
    DATABASE["persons"][person_id] = person_data
    return {"message": "Person created successfully", "person_id": person_id}

@app.post("/api/persons/nlp")
async def create_person_from_text(
    description: str = Form(..., description="Natural language description of the person"),
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new person from natural language description
    
    Example: "John Smith is a senior software engineer at Google in Mountain View 
              with 10 years experience in Python and machine learning. 
              Email: john@gmail.com, Phone: +1-555-0123"
    """
    try:
        # Parse natural language description
        parsed_data = nlp_processor.extract_person_fields(description)
        logger.info(f"Parsed person data: {parsed_data}")
        
        # Validate we have at least a name
        if not parsed_data.get("name"):
            raise HTTPException(
                status_code=400, 
                detail="Could not extract a name from the description. Please include a person's name."
            )
        
        # Create person
        person_id = str(ObjectId())
        person_data = {
            "id": person_id,
            "name": parsed_data["name"],
            "email": parsed_data.get("email"),
            "phone": parsed_data.get("phone"),
            "job_title": parsed_data.get("job_title"),
            "company": parsed_data.get("company"),
            "industry": parsed_data.get("industry"),
            "city": parsed_data.get("city"),
            "state": parsed_data.get("state"),
            "country": parsed_data.get("country"),
            "linkedin_url": parsed_data.get("linkedin_url"),
            "bio": parsed_data.get("bio") or description,  # Use description as bio
            "skills": parsed_data.get("skills", []),
            "experience_years": parsed_data.get("experience_years"),
            "education": None,
            "certifications": [],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "review_count": 0,
            "average_rating": 0.0,
            "total_rating": 0
        }
        
        DATABASE["persons"][person_id] = person_data
        
        return {
            "message": "Person created successfully from natural language description",
            "person_id": person_id,
            "parsed_data": parsed_data,
            "person": person_data
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating person from NLP: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create person: {str(e)}")

@app.get("/api/persons/{person_id}")
async def get_person(person_id: str):
    """Get person details"""
    person = DATABASE["persons"].get(person_id)
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    
    # Get reviews for this person
    person_reviews = [
        review for review in DATABASE["reviews"].values()
        if review["person_id"] == person_id
    ]
    
    return {
        "person": person,
        "reviews": person_reviews
    }

@app.post("/api/reviews")
@limiter.limit("5/hour")  # Prevent review spam
async def create_review(request: Request, review: ReviewBase, current_user: dict = Depends(get_current_user)):
    """Create a new review (requires authentication, shows only username)"""
    # Check if person exists
    person = DATABASE["persons"].get(review.person_id)
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    
    # Check if user already reviewed this person
    existing_review = None
    for r in DATABASE["reviews"].values():
        if r["reviewer_id"] == current_user["id"] and r["person_id"] == review.person_id:
            existing_review = r
            break
    
    if existing_review:
        raise HTTPException(status_code=400, detail="You have already reviewed this person")
    
    # Content moderation check
    content_analysis = analyze_content(review.comment)
    auto_flagged = should_auto_flag(review.comment)
    
    if content_analysis["has_profanity"]:
        # Filter profanity automatically
        review.comment = filter_profanity(review.comment)
        logger.warning(f"Profanity filtered in review by {current_user['username']}")
    
    # Create review with username only (privacy protection)
    review_id = str(ObjectId())
    review_data = review.dict()
    review_data.update({
        "id": review_id,
        "reviewer_id": current_user["id"],
        "reviewer_username": current_user["username"],  # Only username, not real name
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "is_verified": False,
        "helpful_count": 0,
        "reported_count": 1 if auto_flagged else 0  # Auto-flag if score is high
    })
    
    DATABASE["reviews"][review_id] = review_data
    
    # Update person's rating
    person_reviews = [r for r in DATABASE["reviews"].values() if r["person_id"] == review.person_id]
    total_rating = sum(r["rating"] for r in person_reviews)
    review_count = len(person_reviews)
    average_rating = total_rating / review_count if review_count > 0 else 0
    
    DATABASE["persons"][review.person_id].update({
        "review_count": review_count,
        "average_rating": round(average_rating, 1),
        "total_rating": total_rating,
        "updated_at": datetime.utcnow()
    })
    
    # Update user's review count
    DATABASE["users"][current_user["id"]]["review_count"] = DATABASE["users"][current_user["id"]].get("review_count", 0) + 1
    
    return {
        "message": "Review created successfully", 
        "review_id": review_id,
        "reviewer_username": current_user["username"],
        "moderation_note": "Content was automatically filtered" if content_analysis["has_profanity"] else None
    }

@app.get("/api/reviews/")
async def get_reviews(
    limit: int = Query(10, le=50),
    person_id: Optional[str] = None
):
    """Get reviews with optional filtering"""
    reviews = list(DATABASE["reviews"].values())
    
    if person_id:
        reviews = [r for r in reviews if r["person_id"] == person_id]
    
    # Sort by creation date (newest first)
    reviews.sort(key=lambda x: x["created_at"], reverse=True)
    
    # Add person names to reviews (but keep reviewer usernames anonymous)
    for review in reviews:
        person = DATABASE["persons"].get(review["person_id"])
        if person:
            review["person_name"] = person["name"]
        # Note: reviewer_username is already in the review, real name is protected
    
    return {
        "count": len(reviews),
        "reviews": reviews[:limit]
    }

@app.post("/api/flag-review")
@limiter.limit("10/hour")  # Prevent flag spam
async def flag_review(
    request: Request,
    review_id: str,
    reason: str,
    description: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Flag a review for moderation (requires authentication)"""
    # Check if review exists
    review = DATABASE["reviews"].get(review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    
    # Check valid reason
    valid_reasons = ["spam", "harassment", "false_info", "inappropriate", "other"]
    if reason not in valid_reasons:
        raise HTTPException(status_code=400, detail=f"Invalid reason. Must be one of: {', '.join(valid_reasons)}")
    
    # Create flag record
    flag_id = str(ObjectId())
    flag_data = {
        "id": flag_id,
        "review_id": review_id,
        "flagger_id": current_user["id"],
        "flagger_username": current_user["username"],
        "reason": reason,
        "description": description or "",
        "created_at": datetime.utcnow(),
        "status": "pending",  # pending, reviewed, resolved, dismissed
        "reviewed_by": None,
        "reviewed_at": None
    }
    
    # Initialize flagged_reviews collection if not exists
    if "flagged_reviews" not in DATABASE:
        DATABASE["flagged_reviews"] = {}
    
    DATABASE["flagged_reviews"][flag_id] = flag_data
    
    # Increment reported_count on the review
    review["reported_count"] = review.get("reported_count", 0) + 1
    
    # Auto-hide review if reported 3+ times
    if review["reported_count"] >= 3:
        review["is_hidden"] = True
        logger.warning(f"Review {review_id} auto-hidden after {review['reported_count']} reports")
    
    return {
        "message": "Review flagged successfully",
        "flag_id": flag_id,
        "review_reported_count": review["reported_count"],
        "auto_hidden": review.get("is_hidden", False)
    }


@app.get("/api/stats")
async def get_stats():
    """Get platform statistics"""
    total_users = len(DATABASE["users"])
    total_persons = len(DATABASE["persons"])
    total_reviews = len(DATABASE["reviews"])
    
    # Calculate average rating across all persons
    persons_with_ratings = [p for p in DATABASE["persons"].values() if p.get("review_count", 0) > 0]
    avg_platform_rating = sum(p.get("average_rating", 0) for p in persons_with_ratings) / len(persons_with_ratings) if persons_with_ratings else 0
    
    return {
        "total_users": total_users,
        "total_persons": total_persons,
        "total_reviews": total_reviews,
        "average_rating": round(avg_platform_rating, 1),
        "verified_reviews": sum(1 for r in DATABASE["reviews"].values() if r.get("is_verified", False))
    }

# ==================== ADMIN & MODERATION ====================

# In-memory flagged content storage (move to database for production)
FLAGGED_CONTENT = {}

# Profile claim requests storage (move to database for production)
PROFILE_CLAIMS = {}

@app.get("/admin")
async def admin_page(request: Request, current_user: dict = Depends(get_current_user)):
    """Admin dashboard for content moderation"""
    # Check if user is admin (simple check - enhance for production)
    if current_user.get("username") not in ["TechReviewer2024", "ProjectManager_Pro"]:  # Demo admin users
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Get statistics
    stats = {
        "users": len(DATABASE["users"]),
        "persons": len(DATABASE["persons"]),
        "reviews": len(DATABASE["reviews"])
    }
    
    # Get flagged reviews
    flagged_reviews = []
    for flag_id, flag in FLAGGED_CONTENT.items():
        if flag.get("status") == "pending":
            review = DATABASE["reviews"].get(flag["review_id"])
            if review:
                person = DATABASE["persons"].get(review["person_id"])
                flagged_reviews.append({
                    "flag_id": flag_id,
                    "review_id": flag["review_id"],
                    "reason": flag["reason"],
                    "description": flag.get("description"),
                    "reporter_username": flag["reporter_username"],
                    "reviewer_username": review["reviewer_username"],
                    "person_name": person["name"] if person else "Unknown",
                    "rating": review["rating"],
                    "title": review.get("title"),
                    "comment": review["comment"],
                    "created_at": flag["created_at"]
                })
    
    # Get recent reviews
    recent_reviews = sorted(
        DATABASE["reviews"].values(),
        key=lambda x: x["created_at"],
        reverse=True
    )[:20]
    
    for review in recent_reviews:
        person = DATABASE["persons"].get(review["person_id"])
        review["person_name"] = person["name"] if person else "Unknown"
    
    # Get top users
    top_users = sorted(
        DATABASE["users"].values(),
        key=lambda x: x.get("review_count", 0),
        reverse=True
    )[:10]
    
    return templates.TemplateResponse("admin.html", {
        "request": request,
        "stats": stats,
        "flagged_count": len(flagged_reviews),
        "flagged_reviews": flagged_reviews,
        "recent_reviews": recent_reviews,
        "top_users": top_users
    })

@app.post("/api/admin/moderate-review/{review_id}")
async def moderate_review(
    review_id: str,
    action: str = Form(...),
    current_user: dict = Depends(get_current_user)
):
    """Admin endpoint to approve or reject a review"""
    # Check admin permission
    if current_user.get("username") not in ["TechReviewer2024", "ProjectManager_Pro"]:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    review = DATABASE["reviews"].get(review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    
    if action == "approve":
        review["reported_count"] = 0
        review["is_verified"] = True
        message = "Review approved"
    elif action == "reject":
        # Remove the review
        del DATABASE["reviews"][review_id]
        # Update person stats
        person = DATABASE["persons"].get(review["person_id"])
        if person:
            person["review_count"] = max(0, person.get("review_count", 1) - 1)
            if person["review_count"] > 0:
                remaining_reviews = [r for r in DATABASE["reviews"].values() if r["person_id"] == review["person_id"]]
                total = sum(r["rating"] for r in remaining_reviews)
                person["average_rating"] = total / len(remaining_reviews) if remaining_reviews else 0
            else:
                person["average_rating"] = 0
        message = "Review removed"
    else:
        raise HTTPException(status_code=400, detail="Invalid action")
    
    # Remove flags for this review
    for flag_id in list(FLAGGED_CONTENT.keys()):
        if FLAGGED_CONTENT[flag_id]["review_id"] == review_id:
            FLAGGED_CONTENT[flag_id]["status"] = "resolved"
    
    logger.info(f"Admin {current_user['username']} {action}ed review {review_id}")
    
    return {"message": message}

@app.post("/api/admin/moderate-flag/{flag_id}")
async def moderate_flag(
    flag_id: str,
    action: str = Form(...),
    current_user: dict = Depends(get_current_user)
):
    """Admin endpoint to dismiss a flag"""
    # Check admin permission
    if current_user.get("username") not in ["TechReviewer2024", "ProjectManager_Pro"]:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    flag = FLAGGED_CONTENT.get(flag_id)
    if not flag:
        raise HTTPException(status_code=404, detail="Flag not found")
    
    if action == "dismiss":
        flag["status"] = "dismissed"
        # Reset report count on review
        review = DATABASE["reviews"].get(flag["review_id"])
        if review:
            review["reported_count"] = max(0, review.get("reported_count", 1) - 1)
        message = "Flag dismissed"
    else:
        raise HTTPException(status_code=400, detail="Invalid action")
    
    logger.info(f"Admin {current_user['username']} dismissed flag {flag_id}")
    
    return {"message": message}

# ==================== EMAIL VERIFICATION ====================

@app.get("/verify-email")
async def verify_email_page(request: Request, token: str):
    """Verify user's email address"""
    # Verify token
    token_data = verify_token(token)
    
    if not token_data:
        return templates.TemplateResponse("error.html", {
            "request": request,
            "title": "Invalid Verification Link",
            "message": "This verification link is invalid or has expired. Please request a new one."
        }, status_code=400)
    
    # Update user's email_verified status
    user_id = token_data["user_id"]
    user = DATABASE["users"].get(user_id)
    
    if user:
        user["email_verified"] = True
        user["verified_at"] = datetime.utcnow()
        logger.info(f"✅ Email verified for user: {user['username']}")
        
        return templates.TemplateResponse("verification_success.html", {
            "request": request,
            "username": user["username"]
        })
    else:
        raise HTTPException(status_code=404, detail="User not found")

@app.post("/api/resend-verification")
async def resend_verification(request: Request, current_user: dict = Depends(get_current_user)):
    """Resend verification email"""
    user = DATABASE["users"].get(current_user["id"])
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.get("email_verified"):
        raise HTTPException(status_code=400, detail="Email already verified")
    
    # Send new verification email
    try:
        base_url = str(request.base_url).rstrip('/')
        send_verification_email(user["email"], user["id"], user["username"], base_url)
        logger.info(f"📧 Verification email resent for user: {user['username']}")
        return {"message": "Verification email sent. Please check your inbox."}
    except Exception as e:
        logger.error(f"Failed to resend verification email: {e}")
        raise HTTPException(status_code=500, detail="Failed to send verification email")

# ==================== PROFILE CLAIMING ====================

@app.post("/api/claim-profile")
@limiter.limit("3/hour")
async def claim_profile(
    request: Request,
    person_id: str = Form(...),
    reason: str = Form(...),
    evidence: Optional[str] = Form(None),
    current_user: dict = Depends(get_current_user)
):
    """Submit a profile claim request"""
    # Check if person exists
    person = DATABASE["persons"].get(person_id)
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    
    # Check if already claimed
    if person.get("is_claimed"):
        raise HTTPException(status_code=400, detail="This profile has already been claimed")
    
    # Check if user already has pending claim
    for claim in PROFILE_CLAIMS.values():
        if claim["person_id"] == person_id and claim["claimer_id"] == current_user["id"] and claim["status"] == "pending":
            raise HTTPException(status_code=400, detail="You already have a pending claim for this profile")
    
    # Create claim request
    claim_id = str(ObjectId())
    PROFILE_CLAIMS[claim_id] = {
        "id": claim_id,
        "person_id": person_id,
        "person_name": person["name"],
        "claimer_id": current_user["id"],
        "claimer_username": current_user["username"],
        "claimer_email": current_user["email"],
        "reason": reason,
        "evidence": evidence,
        "status": "pending",  # pending, approved, rejected
        "created_at": datetime.utcnow(),
        "reviewed_at": None,
        "reviewed_by": None
    }
    
    logger.info(f"📋 Profile claim submitted: {person['name']} by {current_user['username']}")
    
    return {
        "message": "Profile claim submitted successfully. Our team will review it within 24-48 hours.",
        "claim_id": claim_id
    }

@app.post("/api/admin/review-claim/{claim_id}")
async def review_claim(
    claim_id: str,
    action: str = Form(...),  # approve or reject
    notes: Optional[str] = Form(None),
    current_user: dict = Depends(get_current_user)
):
    """Admin endpoint to approve or reject profile claims"""
    # Check admin permission
    if current_user.get("username") not in ["TechReviewer2024", "ProjectManager_Pro"]:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    claim = PROFILE_CLAIMS.get(claim_id)
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    
    if claim["status"] != "pending":
        raise HTTPException(status_code=400, detail="Claim already reviewed")
    
    if action == "approve":
        # Mark profile as claimed
        person = DATABASE["persons"].get(claim["person_id"])
        if person:
            person["is_claimed"] = True
            person["claimed_by"] = claim["claimer_id"]
            person["claimed_at"] = datetime.utcnow()
        
        claim["status"] = "approved"
        message = f"Profile claim approved for {claim['person_name']}"
        
    elif action == "reject":
        claim["status"] = "rejected"
        message = f"Profile claim rejected for {claim['person_name']}"
    else:
        raise HTTPException(status_code=400, detail="Invalid action. Use 'approve' or 'reject'")
    
    claim["reviewed_at"] = datetime.utcnow()
    claim["reviewed_by"] = current_user["username"]
    claim["admin_notes"] = notes
    
    logger.info(f"Admin {current_user['username']} {action}d claim {claim_id}")
    
    return {"message": message}

# Scam Alert API Endpoints
@app.get("/api/scams")
async def get_scams(current_user: dict = Depends(lambda: None)):
    """Get all scam alerts sorted by net votes (upvotes - downvotes)"""
    scams = list(DATABASE["scams"].values())
    
    # Calculate net votes and sort
    for scam in scams:
        scam["net_votes"] = scam["upvotes"] - scam["downvotes"]
        
        # If user is logged in, include their vote
        if current_user:
            user_vote = None
            for vote in DATABASE["scam_votes"].values():
                if vote["scam_id"] == scam["id"] and vote["user_id"] == current_user.get("id"):
                    user_vote = vote["vote_type"]
                    break
            scam["user_vote"] = user_vote
        else:
            scam["user_vote"] = None
    
    # Sort by net votes descending (most upvoted first)
    scams.sort(key=lambda x: x["net_votes"], reverse=True)
    
    return {"scams": scams, "count": len(scams)}

@app.post("/api/scams/{scam_id}/vote")
async def vote_on_scam(
    scam_id: str,
    vote_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Vote on a scam alert (upvote or downvote) - requires authentication"""
    scam = DATABASE["scams"].get(scam_id)
    if not scam:
        raise HTTPException(status_code=404, detail="Scam alert not found")
    
    vote_type = vote_data.get("vote_type")
    if vote_type not in ["upvote", "downvote"]:
        raise HTTPException(status_code=400, detail="Invalid vote type. Use 'upvote' or 'downvote'")
    
    user_id = current_user["id"]
    
    # Check if user already voted
    existing_vote = None
    vote_key = None
    for key, vote in DATABASE["scam_votes"].items():
        if vote["scam_id"] == scam_id and vote["user_id"] == user_id:
            existing_vote = vote
            vote_key = key
            break
    
    if existing_vote:
        old_vote_type = existing_vote["vote_type"]
        
        # If same vote type, remove vote (toggle off)
        if old_vote_type == vote_type:
            del DATABASE["scam_votes"][vote_key]
            if vote_type == "upvote":
                scam["upvotes"] = max(0, scam["upvotes"] - 1)
            else:
                scam["downvotes"] = max(0, scam["downvotes"] - 1)
            return {"message": "Vote removed", "scam": scam}
        else:
            # Change vote type
            existing_vote["vote_type"] = vote_type
            existing_vote["voted_at"] = datetime.utcnow()
            
            # Update counts
            if vote_type == "upvote":
                scam["upvotes"] += 1
                scam["downvotes"] = max(0, scam["downvotes"] - 1)
            else:
                scam["downvotes"] += 1
                scam["upvotes"] = max(0, scam["upvotes"] - 1)
            
            return {"message": "Vote changed", "scam": scam}
    else:
        # New vote
        vote_id = str(ObjectId())
        new_vote = {
            "id": vote_id,
            "scam_id": scam_id,
            "user_id": user_id,
            "vote_type": vote_type,
            "voted_at": datetime.utcnow()
        }
        DATABASE["scam_votes"][vote_id] = new_vote
        
        # Update scam counts
        if vote_type == "upvote":
            scam["upvotes"] += 1
        else:
            scam["downvotes"] += 1
        
        scam["last_updated"] = datetime.utcnow()
        
        return {"message": "Vote registered", "scam": scam}