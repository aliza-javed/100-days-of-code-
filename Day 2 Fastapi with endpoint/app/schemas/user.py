import re
from datetime import date, datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator


class UserRole(str, Enum):
    admin  = "admin"
    editor = "editor"
    viewer = "viewer"


class Address(BaseModel):
    street: str  = Field(..., min_length=3, max_length=200, examples=["123 Main St"])
    city:   str  = Field(..., min_length=2, max_length=100, examples=["Islamabad"])
    country: str = Field(..., min_length=2, max_length=100, examples=["Pakistan"])
    zip_code: str = Field(..., pattern=r"^\d{4,10}$", examples=["44000"])


class UserCreate(BaseModel):
    username:   str      = Field(..., min_length=3, max_length=30, examples=["aliza_dev"])
    email:      EmailStr = Field(..., examples=["aliza@example.com"])
    password:   str      = Field(..., min_length=8, examples=["Secure@123"])
    full_name:  str      = Field(..., min_length=2, max_length=100, examples=["Aliza Javed"])
    age:        int      = Field(..., ge=13, le=120, examples=[22])
    role:       UserRole = Field(default=UserRole.viewer)
    address:    Optional[Address] = None
    date_of_birth: Optional[date] = None
    bio:        Optional[str] = Field(default=None, max_length=500)

    @field_validator("username")
    @classmethod
    def username_alphanumeric(cls, v: str) -> str:
        if not re.match(r"^[a-zA-Z0-9_]+$", v):
            raise ValueError("Username can only contain letters, numbers, and underscores")
        if v.startswith("_") or v.endswith("_"):
            raise ValueError("Username cannot start or end with an underscore")
        return v.lower()

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one digit")
        if not re.search(r"[@$!%*?&#]", v):
            raise ValueError("Password must contain at least one special character (@$!%*?&#)")
        return v

    @field_validator("full_name")
    @classmethod
    def full_name_no_digits(cls, v: str) -> str:
        if any(char.isdigit() for char in v):
            raise ValueError("Full name cannot contain digits")
        return v.strip().title()

    @field_validator("date_of_birth")
    @classmethod
    def dob_in_past(cls, v: Optional[date]) -> Optional[date]:
        if v and v >= date.today():
            raise ValueError("Date of birth must be in the past")
        return v

    @model_validator(mode="after")
    def age_matches_dob(self) -> "UserCreate":
        if self.date_of_birth:
            today = date.today()
            real_age = today.year - self.date_of_birth.year - (
                (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
            )
            if abs(real_age - self.age) > 1:
                raise ValueError("Age does not match the date of birth")
        return self


class UserUpdate(BaseModel):
    full_name:  Optional[str]      = Field(default=None, min_length=2, max_length=100)
    bio:        Optional[str]      = Field(default=None, max_length=500)
    role:       Optional[UserRole] = None
    address:    Optional[Address]  = None

    @field_validator("full_name")
    @classmethod
    def full_name_no_digits(cls, v: Optional[str]) -> Optional[str]:
        if v and any(char.isdigit() for char in v):
            raise ValueError("Full name cannot contain digits")
        return v.strip().title() if v else v


class UserResponse(BaseModel):
    id:         int
    username:   str
    email:      EmailStr
    full_name:  str
    age:        int
    role:       UserRole
    address:    Optional[Address]
    created_at: datetime

    model_config = {"from_attributes": True}
