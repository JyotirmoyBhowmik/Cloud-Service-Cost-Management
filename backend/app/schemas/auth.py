"""
Authentication & User Schemas
Strict DTOs for login, registration, and token validation.
"""

from typing import Optional, Dict, Any
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime


class UserLogin(BaseModel):
    email: EmailStr = Field(..., description="User corporate email address")
    password: str = Field(..., min_length=6, description="Plaintext password")


class UserCreate(BaseModel):
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=100)
    password: str = Field(..., min_length=8)
    role: str = Field(default="READ_ONLY")
    tenant_id: Optional[str] = None


class UserResponse(BaseModel):
    id: str
    tenant_id: str
    email: str
    full_name: str
    role: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "Bearer"
    expires_in_minutes: int
    user: UserResponse
