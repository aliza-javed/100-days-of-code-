"""/auth/* endpoints."""
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError

from app.core.config import settings
from app.core.deps import get_current_user
from app.core.security import verify_password
from app.core.tokens import (
    create_access_token, create_refresh_token,
    decode_refresh_token, revoke_access_token, revoke_refresh_token,
)
from app.schemas.auth import (
    AccessTokenResponse, ChangePasswordRequest, LoginRequest,
    RegisterRequest, TokenResponse, UserPublic,
)
from app.services import store

router = APIRouter()
bearer = HTTPBearer(auto_error=False)

_EXPIRE_SECS = settings.ACCESS_TOKEN_EXPIRE_MIN * 60


# ── Register ────────────────────────────────────────────────
@router.post(
    "/register",
    response_model=UserPublic,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new account",
)
async def register(payload: RegisterRequest):
    if store.get_user_by_username(payload.username):
        raise HTTPException(409, f"Username '{payload.username}' is already taken")
    if store.get_user_by_email(payload.email):
        raise HTTPException(409, f"Email '{payload.email}' is already registered")

    user = store.create_user(
        username=payload.username,
        email=str(payload.email),
        password=payload.password,
        full_name=payload.full_name,
        role=payload.role.value,
    )
    return user


# ── Login ────────────────────────────────────────────────────
@router.post("/login", response_model=TokenResponse, summary="Login — get JWT tokens")
async def login(payload: LoginRequest):
    user = store.authenticate_user(payload.username, payload.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.get("is_active"):
        raise HTTPException(status_code=403, detail="Account is deactivated")

    return TokenResponse(
        access_token=create_access_token(user["id"], user["role"]),
        refresh_token=create_refresh_token(user["id"]),
        expires_in=_EXPIRE_SECS,
    )


# ── Refresh ──────────────────────────────────────────────────
@router.post(
    "/refresh",
    response_model=AccessTokenResponse,
    summary="Exchange refresh token for a new access token",
)
async def refresh(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)],
):
    if not credentials:
        raise HTTPException(401, "Refresh token required")

    try:
        payload = decode_refresh_token(credentials.credentials)
    except JWTError as e:
        raise HTTPException(401, str(e))

    user = store.get_user(int(payload["sub"]))
    if not user:
        raise HTTPException(401, "User no longer exists")

    # Rotate: revoke old refresh token
    revoke_refresh_token(credentials.credentials)

    return AccessTokenResponse(
        access_token=create_access_token(user["id"], user["role"]),
        expires_in=_EXPIRE_SECS,
    )


# ── Logout ───────────────────────────────────────────────────
@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Revoke the current access token (logout)",
)
async def logout(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)],
):
    if credentials:
        revoke_access_token(credentials.credentials)


# ── Me ───────────────────────────────────────────────────────
@router.get("/me", response_model=UserPublic, summary="Get current user profile")
async def me(current: Annotated[dict, Depends(get_current_user)]):
    return current


# ── Change password ───────────────────────────────────────────
@router.post(
    "/change-password",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Change own password",
)
async def change_password(
    payload: ChangePasswordRequest,
    current: Annotated[dict, Depends(get_current_user)],
):
    full = store.get_user_by_username(current["username"])
    if not verify_password(payload.current_password, full["hashed_pw"]):
        raise HTTPException(400, "Current password is incorrect")
    if payload.current_password == payload.new_password:
        raise HTTPException(400, "New password must differ from current password")
    store.update_password(current["id"], payload.new_password)
