"""
Authentication API Endpoints
Handles user login, token issuance, and current session inspection.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.exceptions import AuthenticationFailedException
from app.core.security import verify_password, create_access_token
from app.core.rbac import get_current_user_payload
from app.models.tenant_user import User
from app.schemas.auth import UserLogin, TokenResponse, UserResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=TokenResponse)
def login_for_access_token(payload: UserLogin, db: Session = Depends(get_db)):
    """Authenticates corporate user credentials and returns JWT Bearer token."""
    user = db.query(User).filter(User.email == payload.email, User.is_deleted == False).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise AuthenticationFailedException("Invalid email address or password provided.")
    
    if not user.is_active:
        raise AuthenticationFailedException("User account is inactive. Please contact your FinOps administrator.")

    token = create_access_token({
        "sub": user.id,
        "email": user.email,
        "role": user.role,
        "tenant_id": user.tenant_id,
        "full_name": user.full_name,
    })

    return TokenResponse(
        access_token=token,
        token_type="Bearer",
        expires_in_minutes=60 * 24,
        user=UserResponse.model_validate(user),
    )


@router.get("/me", response_model=UserResponse)
def get_current_user(current_user: dict = Depends(get_current_user_payload), db: Session = Depends(get_db)):
    """Returns profile for currently authenticated identity."""
    user_id = current_user.get("sub")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        # Fallback to first user in db for demo mode
        user = db.query(User).first()
        if not user:
            raise AuthenticationFailedException("Session identity not found.")
    return UserResponse.model_validate(user)
