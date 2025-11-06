# Working PeopleRate application with simplified MongoDB setup
from fastapi import FastAPI, HTTPException, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
import asyncio
import json
from datetime import datetime

app = FastAPI(
    title="PeopleRate API - Full Version",
    description="A people review platform similar to TrustPilot but for individuals",
    version="1.0.0"
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates  
templates = Jinja2Templates(directory="templates")

# In-memory data store (will be replaced with MongoDB when available)
users_db = {}
persons_db = {}
reviews_db = {}
current_user_id = 1
current_person_id = 1
current_review_id = 1

# Pydantic models
class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    full_name: Optional[str] = None

class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    full_name: Optional[str] = None
    created_at: str

class PersonCreate(BaseModel):
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

class PersonResponse(BaseModel):
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
    total_reviews: int
    average_rating: float
    created_at: str

class ReviewCreate(BaseModel):
    person_id: str
    rating: int
    title: str
    content: str
    category: Optional[str] = None

class ReviewResponse(BaseModel):
    id: str
    reviewer_id: str
    person_id: str
    rating: int
    title: str
    content: str
    category: Optional[str] = None
    created_at: str
    reviewer_username: Optional[str] = None

# Add sample data
def initialize_sample_data():
    global current_user_id, current_person_id, current_review_id
    
    # Sample users
    sample_users = [
        {"username": "john_doe", "email": "john@example.com", "full_name": "John Doe"},
        {"username": "jane_smith", "email": "jane@example.com", "full_name": "Jane Smith"},
    ]
    
    for user_data in sample_users:
        user_id = str(current_user_id)
        users_db[user_id] = {
            "id": user_id,
            "username": user_data["username"],
            "email": user_data["email"],
            "full_name": user_data["full_name"],
            "created_at": datetime.now().isoformat()
        }
        current_user_id += 1
    
    # Sample persons
    sample_persons = [
        {
            "full_name": "John Smith",
            "company": "Microsoft",
            "job_title": "Software Engineer",
            "city": "Seattle",
            "email": "johnsmith@microsoft.com",
            "linkedin_url": "https://linkedin.com/in/johnsmith",
            "phone_number": "+1-555-123-4567"
        },
        {
            "full_name": "Jane Doe",
            "company": "Google",
            "job_title": "Product Manager", 
            "city": "Mountain View",
            "email": "jane.doe@google.com",
            "linkedin_url": "https://linkedin.com/in/janedoe",
            "phone_number": "+1-555-987-6543"
        },
        {
            "full_name": "Mike Johnson",
            "company": "Apple",
            "job_title": "Design Director",
            "city": "Cupertino",
            "email": "mike.johnson@apple.com"
        },
        {
            "full_name": "Sarah Wilson",
            "company": "Amazon",
            "job_title": "Data Scientist",
            "city": "Seattle",
            "phone_number": "+1-555-456-7890"
        }
    ]
    
    for person_data in sample_persons:
        person_id = str(current_person_id)
        persons_db[person_id] = {
            "id": person_id,
            "total_reviews": 0,
            "average_rating": 0.0,
            "created_at": datetime.now().isoformat(),
            **person_data
        }
        current_person_id += 1
    
    # Sample reviews
    sample_reviews = [
        {"person_id": "1", "reviewer_id": "2", "rating": 5, "title": "Excellent collaboration", "content": "John was very professional and delivered quality work on time.", "category": "Professional"},
        {"person_id": "1", "reviewer_id": "1", "rating": 4, "title": "Good experience", "content": "Worked well together on the project. Would recommend.", "category": "Professional"},
        {"person_id": "2", "reviewer_id": "1", "rating": 5, "title": "Outstanding manager", "content": "Jane is an exceptional product manager with great leadership skills.", "category": "Professional"},
    ]
    
    for review_data in sample_reviews:
        review_id = str(current_review_id)
        reviews_db[review_id] = {
            "id": review_id,
            "created_at": datetime.now().isoformat(),
            **review_data
        }
        current_review_id += 1
    
    # Update person review stats
    for person_id in persons_db:
        person_reviews = [r for r in reviews_db.values() if r["person_id"] == person_id]
        if person_reviews:
            persons_db[person_id]["total_reviews"] = len(person_reviews)
            persons_db[person_id]["average_rating"] = sum(r["rating"] for r in person_reviews) / len(person_reviews)

# Routes
@app.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "message": "PeopleRate API is running with in-memory database",
        "data_counts": {
            "users": len(users_db),
            "persons": len(persons_db),
            "reviews": len(reviews_db)
        }
    }

# User endpoints
@app.post("/api/auth/register", response_model=UserResponse)
async def register_user(user_data: UserCreate):
    global current_user_id
    
    # Check if user already exists
    for user in users_db.values():
        if user["email"] == user_data.email or user["username"] == user_data.username:
            raise HTTPException(status_code=400, detail="User with this email or username already exists")
    
    user_id = str(current_user_id)
    new_user = {
        "id": user_id,
        "username": user_data.username,
        "email": user_data.email,
        "full_name": user_data.full_name,
        "created_at": datetime.now().isoformat()
    }
    
    users_db[user_id] = new_user
    current_user_id += 1
    
    return UserResponse(**new_user)

@app.post("/api/auth/login")
async def login_user(username: str, password: str):
    # Find user
    user = None
    for u in users_db.values():
        if u["username"] == username or u["email"] == username:
            user = u
            break
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    return {
        "access_token": f"demo_token_{user['id']}",
        "token_type": "bearer",
        "user": UserResponse(**user)
    }

# Person endpoints
@app.post("/api/persons/", response_model=PersonResponse)
async def create_person(person_data: PersonCreate):
    global current_person_id
    
    person_id = str(current_person_id)
    new_person = {
        "id": person_id,
        "total_reviews": 0,
        "average_rating": 0.0,
        "created_at": datetime.now().isoformat(),
        **person_data.dict()
    }
    
    persons_db[person_id] = new_person
    current_person_id += 1
    
    return PersonResponse(**new_person)

@app.get("/api/persons/search", response_model=List[PersonResponse])
async def search_persons(q: str, limit: int = 10):
    """Search for persons by name, phone, email, company, city, or LinkedIn"""
    results = []
    query_lower = q.lower()
    
    for person in persons_db.values():
        # Check various fields for matches
        if (query_lower in person.get("full_name", "").lower() or
            query_lower in person.get("company", "").lower() or
            query_lower in person.get("city", "").lower() or
            query_lower in person.get("job_title", "").lower() or
            query_lower in person.get("email", "").lower() or
            query_lower in person.get("phone_number", "").lower() or
            query_lower in person.get("linkedin_url", "").lower()):
            
            results.append(PersonResponse(**person))
            
            if len(results) >= limit:
                break
    
    return results

@app.get("/api/persons/{person_id}", response_model=PersonResponse)
async def get_person(person_id: str):
    if person_id not in persons_db:
        raise HTTPException(status_code=404, detail="Person not found")
    
    return PersonResponse(**persons_db[person_id])

# Review endpoints  
@app.post("/api/reviews/", response_model=ReviewResponse)
async def create_review(review_data: ReviewCreate):
    global current_review_id
    
    # Validate person exists
    if review_data.person_id not in persons_db:
        raise HTTPException(status_code=404, detail="Person not found")
    
    review_id = str(current_review_id)
    new_review = {
        "id": review_id,
        "reviewer_id": "1",  # Demo user
        "created_at": datetime.now().isoformat(),
        **review_data.dict()
    }
    
    reviews_db[review_id] = new_review
    current_review_id += 1
    
    # Update person review stats
    person_reviews = [r for r in reviews_db.values() if r["person_id"] == review_data.person_id]
    persons_db[review_data.person_id]["total_reviews"] = len(person_reviews)
    persons_db[review_data.person_id]["average_rating"] = sum(r["rating"] for r in person_reviews) / len(person_reviews)
    
    # Add reviewer username
    new_review["reviewer_username"] = users_db.get(new_review["reviewer_id"], {}).get("username", "Anonymous")
    
    return ReviewResponse(**new_review)

@app.get("/api/reviews/person/{person_id}", response_model=List[ReviewResponse])
async def get_person_reviews(person_id: str, skip: int = 0, limit: int = 10):
    """Get all reviews for a specific person"""
    if person_id not in persons_db:
        raise HTTPException(status_code=404, detail="Person not found")
    
    person_reviews = []
    for review in reviews_db.values():
        if review["person_id"] == person_id:
            # Add reviewer username
            review_copy = review.copy()
            review_copy["reviewer_username"] = users_db.get(review["reviewer_id"], {}).get("username", "Anonymous")
            person_reviews.append(ReviewResponse(**review_copy))
    
    # Apply pagination
    return person_reviews[skip:skip + limit]

# Initialize data on startup
@app.on_event("startup")
async def startup_event():
    initialize_sample_data()
    print("🚀 PeopleRate API started successfully!")
    print("📊 Sample data loaded:")
    print(f"   - {len(users_db)} users")
    print(f"   - {len(persons_db)} persons") 
    print(f"   - {len(reviews_db)} reviews")
    print("🌐 Visit http://localhost:8000 to use the application")
    print("📚 API docs available at http://localhost:8000/docs")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)