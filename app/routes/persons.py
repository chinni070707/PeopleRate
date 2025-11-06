from fastapi import APIRouter, HTTPException, status, Query
from typing import List, Optional
from app.models.person import PersonCreate, PersonResponse, PersonUpdate, Person
from app.utils.database import get_person_collection
from bson import ObjectId
import re

router = APIRouter()

@router.post("/", response_model=PersonResponse, status_code=status.HTTP_201_CREATED)
async def create_person(person_data: PersonCreate):
    """Create a new person profile"""
    person_collection = await get_person_collection()
    
    person = Person(**person_data.dict())
    result = await person_collection.insert_one(person.dict(by_alias=True))
    created_person = await person_collection.find_one({"_id": result.inserted_id})
    
    return PersonResponse(
        id=str(created_person["_id"]),
        full_name=created_person["full_name"],
        nickname=created_person.get("nickname"),
        phone_number=created_person.get("phone_number"),
        email=created_person.get("email"),
        linkedin_url=created_person.get("linkedin_url"),
        company=created_person.get("company"),
        job_title=created_person.get("job_title"),
        city=created_person.get("city"),
        country=created_person.get("country"),
        bio=created_person.get("bio"),
        is_verified=created_person["is_verified"],
        total_reviews=created_person["total_reviews"],
        average_rating=created_person["average_rating"],
        created_at=created_person["created_at"]
    )


@router.get("/search", response_model=List[PersonResponse])
async def search_persons(
    q: str = Query(..., min_length=2, description="Search query"),
    limit: int = Query(10, ge=1, le=50)
):
    """Search for persons by name, phone, email, company, city, or LinkedIn"""
    person_collection = await get_person_collection()
    
    # Create search filters based on query
    search_filters = []
    
    # Check if query looks like a phone number
    if re.match(r'^[\+\-\d\s\(\)]+$', q):
        search_filters.append({"phone_number": {"$regex": q.replace(" ", "").replace("-", "").replace("(", "").replace(")", ""), "$options": "i"}})
    
    # Check if query looks like an email
    if "@" in q:
        search_filters.append({"email": {"$regex": q, "$options": "i"}})
    
    # Check if query looks like LinkedIn URL
    if "linkedin.com" in q.lower():
        search_filters.append({"linkedin_url": {"$regex": q, "$options": "i"}})
    
    # Add text-based searches
    search_filters.extend([
        {"full_name": {"$regex": q, "$options": "i"}},
        {"nickname": {"$regex": q, "$options": "i"}},
        {"company": {"$regex": q, "$options": "i"}},
        {"city": {"$regex": q, "$options": "i"}},
        {"job_title": {"$regex": q, "$options": "i"}}
    ])
    
    # Execute search with OR condition
    cursor = person_collection.find({"$or": search_filters}).limit(limit)
    persons = await cursor.to_list(length=limit)
    
    return [
        PersonResponse(
            id=str(person["_id"]),
            full_name=person["full_name"],
            nickname=person.get("nickname"),
            phone_number=person.get("phone_number"),
            email=person.get("email"),
            linkedin_url=person.get("linkedin_url"),
            company=person.get("company"),
            job_title=person.get("job_title"),
            city=person.get("city"),
            country=person.get("country"),
            bio=person.get("bio"),
            is_verified=person["is_verified"],
            total_reviews=person["total_reviews"],
            average_rating=person["average_rating"],
            created_at=person["created_at"]
        )
        for person in persons
    ]


@router.get("/{person_id}", response_model=PersonResponse)
async def get_person(person_id: str):
    """Get a specific person by ID"""
    person_collection = await get_person_collection()
    
    if not ObjectId.is_valid(person_id):
        raise HTTPException(status_code=400, detail="Invalid person ID")
    
    person = await person_collection.find_one({"_id": ObjectId(person_id)})
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    
    return PersonResponse(
        id=str(person["_id"]),
        full_name=person["full_name"],
        nickname=person.get("nickname"),
        phone_number=person.get("phone_number"),
        email=person.get("email"),
        linkedin_url=person.get("linkedin_url"),
        company=person.get("company"),
        job_title=person.get("job_title"),
        city=person.get("city"),
        country=person.get("country"),
        bio=person.get("bio"),
        is_verified=person["is_verified"],
        total_reviews=person["total_reviews"],
        average_rating=person["average_rating"],
        created_at=person["created_at"]
    )


@router.put("/{person_id}", response_model=PersonResponse)
async def update_person(person_id: str, person_update: PersonUpdate):
    """Update a person profile"""
    person_collection = await get_person_collection()
    
    if not ObjectId.is_valid(person_id):
        raise HTTPException(status_code=400, detail="Invalid person ID")
    
    # Get current person
    person = await person_collection.find_one({"_id": ObjectId(person_id)})
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    
    # Update only provided fields
    update_data = {k: v for k, v in person_update.dict().items() if v is not None}
    if update_data:
        update_data["updated_at"] = person_update.updated_at if hasattr(person_update, 'updated_at') else None
        await person_collection.update_one(
            {"_id": ObjectId(person_id)},
            {"$set": update_data}
        )
    
    # Return updated person
    updated_person = await person_collection.find_one({"_id": ObjectId(person_id)})
    return PersonResponse(
        id=str(updated_person["_id"]),
        full_name=updated_person["full_name"],
        nickname=updated_person.get("nickname"),
        phone_number=updated_person.get("phone_number"),
        email=updated_person.get("email"),
        linkedin_url=updated_person.get("linkedin_url"),
        company=updated_person.get("company"),
        job_title=updated_person.get("job_title"),
        city=updated_person.get("city"),
        country=updated_person.get("country"),
        bio=updated_person.get("bio"),
        is_verified=updated_person["is_verified"],
        total_reviews=updated_person["total_reviews"],
        average_rating=updated_person["average_rating"],
        created_at=updated_person["created_at"]
    )