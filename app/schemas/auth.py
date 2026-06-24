"""Pydantic models for all auth flows."""
import re
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class UserRole(str, Enum):
    admin  = "admin"
    editor = "editor"
    viewer = "viewer"


# ── Register ────────────────────────────────────────────────
class RegisterRequest(BaseModel):
    username:  str      = Field(..., min_length=3, max_length=30, examples=["aliza_dev"])
    email:     EmailStr = Field(..., examples=["aliza@example.com"])
    password:  str      = Field(..., min_length=8, examples=["Secure@123"])
    full_name: str      = Field(..., min_length=2, max_length=100, examples=["Aliza Javed"])
    role:      UserRole = Field(default=UserRole.viewer)

    @field_validator("username")
    @classmethod
    def username_valid(cls, v: str) -> str:
        if not re.match(r"^[a-zA-Z0-9_]+$", v):
            raise ValueError("Only letters, numbers, and underscores allowed")
        if v.startswith("_") or v.endswith("_"):
            raise ValueError("Cannot start or end with underscore")
        return v.lower()

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        checks = [
            (r"[A-Z]",       "at least one uppercase letter"),
            (r"[a-z]",       "at least one lowercase letter"),
            (r"\d",          "at least one digit"),
            (r"[@$!%*?&#]",  "at least one special character (@$!%*?&#)"),
        ]
        for pattern, msg in checks:
            if not re.search(pattern, v):
                raise ValueError(f"Password must contain {msg}")
        return v

    @field_validator("full_name")
    @classmethod
    def full_name_clean(cls, v: str) -> str:
        if any(c.isdigit() for c in v):
            raise ValueError("Full name cannot contain digits")
        return v.strip().title()


# ── Login ────────────────────────────────────────────────────
class LoginRequest(BaseModel):
    username: str = Field(..., examples=["aliza_dev"])
    password: str = Field(..., examples=["Secure@123"])


# ── Token responses ──────────────────────────────────────────
class TokenResponse(BaseModel):
    access_token:  str
    refresh_token: str
    token_type:    str = "bearer"
    expires_in:    int   # seconds


class AccessTokenResponse(BaseModel):
    access_token: str
    token_type:   str = "bearer"
    expires_in:   int


# ── Change password ──────────────────────────────────────────
class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password:     str = Field(..., min_length=8)

    @field_validator("new_password")
    @classmethod
    def new_password_strength(cls, v: str) -> str:
        checks = [
            (r"[A-Z]", "uppercase"),
            (r"[a-z]", "lowercase"),
            (r"\d",    "digit"),
            (r"[@$!%*?&#]", "special char"),
        ]
        for pat, label in checks:
            if not re.search(pat, v):
                raise ValueError(f"New password needs a {label}")
        return v


# ── User public response ─────────────────────────────────────
class UserPublic(BaseModel):
    id:        int
    username:  str
    email:     EmailStr
    full_name: str
    role:      UserRole

    model_config = ConfigDict(from_attributes=True)
