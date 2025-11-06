from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.models.user import UserResponse
from app.routes.auth import get_current_user

router = APIRouter()

@router.get("/", response_model=List[UserResponse])
async def get_users(current_user: UserResponse = Depends(get_current_user)):
    """Get all users (for admin purposes)"""
    # This would typically be restricted to admin users
    return []