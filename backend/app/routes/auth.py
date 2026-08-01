# app/routes/auth.py

from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime

from app.core.database import get_db  # ✅ NEW
from app.models.models import User
from app.services.auth_service import (
    hash_password,
    verify_password,
    create_access_token
)

router = APIRouter()


# ─────────────────────────────────────────────
# REQUEST MODELS
# ─────────────────────────────────────────────

class SignupRequest(BaseModel):
    name: str
    email: str
    password: str


class LoginRequest(BaseModel):
    email: str
    password: str


# ─────────────────────────────────────────────
# SIGNUP
# ─────────────────────────────────────────────

@router.post("/signup")
def signup(
    request: SignupRequest,
    db: Session = Depends(get_db)
):
    try:
        # CHECK EXISTING USER
        existing_user = (
            db.query(User)
            .filter(User.email == request.email)
            .first()
        )

        if existing_user:
            raise HTTPException(
                status_code=400,
                detail="Email already exists."
            )

        # CREATE USER - USE 'password' NOT 'hashed_password'
        user = User(
            name=request.name,
            email=request.email,
            password=hash_password(request.password),  # ← THIS IS THE FIX
            created_at=datetime.utcnow()
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        # TOKEN
        token = create_access_token({
            "user_id": user.id,
            "email": user.email
        })

        return {
            "success": True,
            "token": token,
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email
            }
        }

    except Exception as e:
        print("Signup Error:", e)
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# ─────────────────────────────────────────────
# LOGIN
# ─────────────────────────────────────────────

@router.post("/login")
def login(
    request: LoginRequest,
    db: Session = Depends(get_db)
):
    try:
        user = (
            db.query(User)
            .filter(User.email == request.email)
            .first()
        )

        if not user:
            raise HTTPException(
                status_code=400,
                detail="Invalid credentials."
            )

        # VERIFY PASSWORD - USE 'password' NOT 'hashed_password'
        valid = verify_password(
            request.password,
            user.password  # ← THIS IS THE FIX
        )

        if not valid:
            raise HTTPException(
                status_code=400,
                detail="Invalid credentials."
            )

        # TOKEN
        token = create_access_token({
            "user_id": user.id,
            "email": user.email
        })

        return {
            "success": True,
            "token": token,
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email
            }
        }

    except Exception as e:
        print("Login Error:", e)
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )