from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
from sqlmodel import Session, select
from backend.database import get_session
from backend.models.db_models import User
from backend.services.auth import verify_password, create_access_token, get_password_hash
from datetime import timedelta
from backend.config import config
from pydantic import BaseModel
from backend.limiter import limiter

router = APIRouter(prefix="/auth", tags=["auth"])

class Token(BaseModel):
    access_token: str
    token_type: str

class UserCreate(BaseModel):
    email: str
    password: str
    invite_code: str | None = None

@router.post("/token", response_model=Token)
@limiter.limit("5/minute")
async def login_for_access_token(
    request: Request,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Annotated[Session, Depends(get_session)]
):
    user = session.exec(select(User).where(User.email == form_data.username)).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/register", response_model=Token)
@limiter.limit("5/minute")
async def register_user(
    request: Request,
    user_in: UserCreate,
    session: Annotated[Session, Depends(get_session)]
):
    # Check Beta Invite Code
    if config.BETA_INVITE_CODE:
        if user_in.invite_code != config.BETA_INVITE_CODE:
            raise HTTPException(
                status_code=403,
                detail="Invalid invite code"
            )
    elif config.is_production:
        # Disallow open registration in production
        raise HTTPException(
            status_code=403,
            detail="Registration is disabled"
        )

    user = session.exec(select(User).where(User.email == user_in.email)).first()
    if user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    hashed_password = get_password_hash(user_in.password)
    new_user = User(email=user_in.email, hashed_password=hashed_password)
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    
    access_token_expires = timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": new_user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

class InviteCodeLogin(BaseModel):
    invite_code: str

@router.post("/login-with-code", response_model=Token)
@limiter.limit("5/minute")
async def login_with_code(
    request: Request,
    login_data: InviteCodeLogin,
    session: Annotated[Session, Depends(get_session)]
):
    """
    Login with just an invite code. Creates/uses a guest user.
    """
    if not config.BETA_INVITE_CODE or login_data.invite_code != config.BETA_INVITE_CODE:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid invite code"
        )
    
    # Use a consistent guest email
    guest_email = "guest@demo.com"
    user = session.exec(select(User).where(User.email == guest_email)).first()
    
    if not user:
        # Create guest user if not exists
        # Generate a random password that no one knows (we only auth via code)
        import secrets
        random_password = secrets.token_urlsafe(32)
        hashed_password = get_password_hash(random_password)
        user = User(email=guest_email, hashed_password=hashed_password)
        session.add(user)
        session.commit()
        session.refresh(user)
    
    access_token_expires = timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
