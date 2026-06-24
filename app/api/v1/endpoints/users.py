"""/api/v1/users/* — role-protected user management."""
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.deps import AdminOnly, AnyUser, EditorPlus
from app.schemas.auth import UserPublic
from app.services import store

router = APIRouter()


@router.get(
    "/",
    response_model=list[UserPublic],
    summary="List all users — admin only",
)
async def list_users(_: Annotated[dict, AdminOnly]):
    return store.get_all_users()


@router.get(
    "/me",
    response_model=UserPublic,
    summary="Get own profile — any authenticated user",
)
async def get_me(current: Annotated[dict, AnyUser]):
    return current


@router.get(
    "/{user_id}",
    response_model=UserPublic,
    summary="Get user by ID — admin or editor",
)
async def get_user(user_id: int, _: Annotated[dict, EditorPlus]):
    user = store.get_user(user_id)
    if not user:
        raise HTTPException(404, f"User {user_id} not found")
    return user


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Deactivate user — admin only",
)
async def deactivate_user(user_id: int, current: Annotated[dict, AdminOnly]):
    if user_id == current["id"]:
        raise HTTPException(400, "You cannot deactivate your own account")
    if not store.deactivate_user(user_id):
        raise HTTPException(404, f"User {user_id} not found")
