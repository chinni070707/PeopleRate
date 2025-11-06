from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import List
from app.models.review import ReviewCreate, ReviewResponse, ReviewWithReviewer, Review
from app.models.user import UserResponse
from app.routes.auth import get_current_user
from app.utils.database import get_review_collection, get_person_collection, get_user_collection
from bson import ObjectId

router = APIRouter()

@router.post("/", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
async def create_review(
    review_data: ReviewCreate,
    current_user: UserResponse = Depends(get_current_user)
):
    """Create a new review"""
    review_collection = await get_review_collection()
    person_collection = await get_person_collection()
    
    # Validate person exists
    if not ObjectId.is_valid(review_data.person_id):
        raise HTTPException(status_code=400, detail="Invalid person ID")
    
    person = await person_collection.find_one({"_id": ObjectId(review_data.person_id)})
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    
    # Check if user already reviewed this person
    existing_review = await review_collection.find_one({
        "reviewer_id": ObjectId(current_user.id),
        "person_id": ObjectId(review_data.person_id)
    })
    
    if existing_review:
        raise HTTPException(
            status_code=400, 
            detail="You have already reviewed this person"
        )
    
    # Create review
    review = Review(
        reviewer_id=ObjectId(current_user.id),
        person_id=ObjectId(review_data.person_id),
        rating=review_data.rating,
        title=review_data.title,
        content=review_data.content,
        category=review_data.category
    )
    
    result = await review_collection.insert_one(review.dict(by_alias=True))
    created_review = await review_collection.find_one({"_id": result.inserted_id})
    
    # Update person's review statistics
    await update_person_review_stats(review_data.person_id)
    
    return ReviewResponse(
        id=str(created_review["_id"]),
        reviewer_id=str(created_review["reviewer_id"]),
        person_id=str(created_review["person_id"]),
        rating=created_review["rating"],
        title=created_review["title"],
        content=created_review["content"],
        category=created_review.get("category"),
        is_verified=created_review["is_verified"],
        helpful_count=created_review["helpful_count"],
        created_at=created_review["created_at"]
    )


@router.get("/person/{person_id}", response_model=List[ReviewWithReviewer])
async def get_person_reviews(
    person_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=50)
):
    """Get all reviews for a specific person"""
    review_collection = await get_review_collection()
    user_collection = await get_user_collection()
    
    if not ObjectId.is_valid(person_id):
        raise HTTPException(status_code=400, detail="Invalid person ID")
    
    # Get reviews with pagination
    cursor = review_collection.find(
        {"person_id": ObjectId(person_id), "moderation_status": "approved"}
    ).sort("created_at", -1).skip(skip).limit(limit)
    
    reviews = await cursor.to_list(length=limit)
    
    # Fetch reviewer information for each review
    review_responses = []
    for review in reviews:
        reviewer = await user_collection.find_one({"_id": review["reviewer_id"]})
        
        review_responses.append(ReviewWithReviewer(
            id=str(review["_id"]),
            reviewer_id=str(review["reviewer_id"]),
            person_id=str(review["person_id"]),
            rating=review["rating"],
            title=review["title"],
            content=review["content"],
            category=review.get("category"),
            is_verified=review["is_verified"],
            helpful_count=review["helpful_count"],
            created_at=review["created_at"],
            reviewer_username=reviewer["username"] if reviewer else "Unknown",
            reviewer_full_name=reviewer.get("full_name") if reviewer else None
        ))
    
    return review_responses


@router.get("/my-reviews", response_model=List[ReviewResponse])
async def get_my_reviews(
    current_user: UserResponse = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=50)
):
    """Get current user's reviews"""
    review_collection = await get_review_collection()
    
    cursor = review_collection.find(
        {"reviewer_id": ObjectId(current_user.id)}
    ).sort("created_at", -1).skip(skip).limit(limit)
    
    reviews = await cursor.to_list(length=limit)
    
    return [
        ReviewResponse(
            id=str(review["_id"]),
            reviewer_id=str(review["reviewer_id"]),
            person_id=str(review["person_id"]),
            rating=review["rating"],
            title=review["title"],
            content=review["content"],
            category=review.get("category"),
            is_verified=review["is_verified"],
            helpful_count=review["helpful_count"],
            created_at=review["created_at"]
        )
        for review in reviews
    ]


async def update_person_review_stats(person_id: str):
    """Update person's review statistics"""
    review_collection = await get_review_collection()
    person_collection = await get_person_collection()
    
    # Calculate statistics
    pipeline = [
        {"$match": {"person_id": ObjectId(person_id), "moderation_status": "approved"}},
        {"$group": {
            "_id": None,
            "total_reviews": {"$sum": 1},
            "average_rating": {"$avg": "$rating"}
        }}
    ]
    
    result = await review_collection.aggregate(pipeline).to_list(length=1)
    
    if result:
        stats = result[0]
        await person_collection.update_one(
            {"_id": ObjectId(person_id)},
            {"$set": {
                "total_reviews": stats["total_reviews"],
                "average_rating": round(stats["average_rating"], 2)
            }}
        )
    else:
        # No reviews yet
        await person_collection.update_one(
            {"_id": ObjectId(person_id)},
            {"$set": {
                "total_reviews": 0,
                "average_rating": 0.0
            }}
        )