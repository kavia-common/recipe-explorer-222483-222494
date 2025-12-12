from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .db import get_db
from .models import User as UserModel
from .schemas import UserCreate, User, Token
from .auth import hash_password, verify_password, create_token

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/signup", response_model=User, summary="Sign up", description="Create a new user account")
def signup(payload: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(UserModel).filter(UserModel.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    u = UserModel(email=payload.email, password_hash=hash_password(payload.password))
    db.add(u)
    db.commit()
    db.refresh(u)
    return u

@router.post("/login", response_model=Token, summary="Login", description="Login and receive an access token")
def login(payload: UserCreate, db: Session = Depends(get_db)):
    u = db.query(UserModel).filter(UserModel.email == payload.email).first()
    if not u or not verify_password(payload.password, u.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    token = create_token(u.id)
    return {"access_token": token, "token_type": "bearer"}
