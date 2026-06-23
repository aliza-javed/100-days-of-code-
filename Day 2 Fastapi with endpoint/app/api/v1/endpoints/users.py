from typing import List

from fastapi import APIRouter, HTTPException, Query, status

from app.schemas.user import UserCreate, UserResponse, UserUpdate, UserRole
from app.services import store

router = APIRouter()


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED,
             summary="Create a new user")
async def create_user(payload: UserCreate):
    """
    Creates a user with full Pydantic validation:
    - strong password rules
    - username format check
    - age ↔ date-of-birth cross-validation
    """
    # Check duplicate email (in-memory demo)
    existing = [u for u in store.get_all_users() if u["email"] == payload.email]
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Email '{payload.email}' is already registered",
        )
    data = payload.model_dump()
    user = store.create_user(data)
    return user


@router.get("/", response_model=List[UserResponse], summary="List all users")
async def list_users(
    role: UserRole | None = Query(default=None, description="Filter by role"),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    users = store.get_all_users()
    if role:
        users = [u for u in users if u.get("role") == role]
    return users[offset: offset + limit]


@router.get("/{user_id}", response_model=UserResponse, summary="Get user by ID")
async def get_user(user_id: int):
    user = store.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")
    return user


@router.patch("/{user_id}", response_model=UserResponse, summary="Partial update a user")
async def update_user(user_id: int, payload: UserUpdate):
    updated = store.update_user(user_id, payload.model_dump(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")
    return updated


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT,
               summary="Delete a user")
async def delete_user(user_id: int):
    if not store.delete_user(user_id):
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")
