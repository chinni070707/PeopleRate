"""
Enhanced PeopleRate Application with TrustPilot-inspired Design
Features comprehensive search, user management, and review system
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

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="PeopleRate API",
    description="A comprehensive people review platform inspired by TrustPilot",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Security
security = HTTPBearer()
JWT_SECRET = "your-enhanced-secret-key-here"
JWT_ALGORITHM = "HS256"

# In-memory database with enhanced sample data
DATABASE = {
    "users": {},
    "persons": {},
    "reviews": {}
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
    linkedin_url: Optional[str] = None
    bio: Optional[str] = None
    skills: Optional[List[str]] = []
    experience_years: Optional[int] = None
    education: Optional[str] = None
    certifications: Optional[List[str]] = []
    
    @field_validator('linkedin_url')
    @classmethod
    def validate_linkedin_url(cls, v):
        if v and not re.match(r'^https?://(www\.)?linkedin\.com/in/[\w\-]+/?$', v):
            raise ValueError('Invalid LinkedIn URL format')
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

# Enhanced sample data with more realistic profiles
def initialize_sample_data():
    """Initialize with comprehensive sample data"""
    
    # Sample users with usernames
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
        }
    ]
    
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
    """Home page with TrustPilot-inspired design"""
    return templates.TemplateResponse("trustpilot_index.html", {"request": request})

@app.get("/auth")
async def auth_page(request: Request):
    """Authentication page for login/register"""
    return templates.TemplateResponse("auth.html", {"request": request})

@app.post("/api/auth/register")
async def register_user(user: UserCreate):
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
        "reputation_score": 0
    }
    
    DATABASE["users"][user_id] = user_data
    
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
async def login_user(email: str = Form(...), password: str = Form(...)):
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

@app.get("/api/persons/search")
async def search_persons(
    q: str = Query("", description="Search query"),
    limit: int = Query(10, le=50, description="Maximum number of results")
):
    """Enhanced search for persons with pattern recognition"""
    try:
        persons = search_persons_enhanced(q, limit)
        return {
            "query": q,
            "count": len(persons),
            "persons": persons
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
    
    person["reviews"] = person_reviews
    return person

@app.post("/api/reviews")
async def create_review(review: ReviewBase, current_user: dict = Depends(get_current_user)):
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
        "reported_count": 0
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
        "reviewer_username": current_user["username"]
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

if __name__ == "__main__":
    # Initialize sample data
    initialize_sample_data()
    
    print("🚀 Enhanced PeopleRate API with TrustPilot Design starting...")
    print("📊 Sample data loaded:")
    print(f"   - {len(DATABASE['users'])} users")
    print(f"   - {len(DATABASE['persons'])} persons")  
    print(f"   - {len(DATABASE['reviews'])} reviews")
    print("🌐 Visit http://localhost:8000 to use the application")
    print("📚 API docs available at http://localhost:8000/docs")
    print("🎨 New TrustPilot-inspired design included!")
    
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)