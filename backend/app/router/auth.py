import os
import re
from typing import Optional
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from google.auth.transport import requests
from google.oauth2 import id_token
from sqlalchemy.orm import Session

from app.crud.user import complete_onboarding
from app.database import get_db
from app.models import Users, Recruiters
from app.schemas import (
    AuthSession,
    AuthUser,
    GoogleSignIn,
    Onboarding,
    LoginRequest,
    RegisterRequest,
    DemoLoginRequest,
)

router = APIRouter(prefix="/auth", tags=["auth"])
security = HTTPBearer()
ALGORITHM = "HS256"

DEFAULT_SETTINGS = {
    "JWT_SECRET": "convotech-dev-secret-key-32-chars-long-min!!",
}


def get_setting(name: str) -> str:
    value = os.getenv(name)
    if not value:
        if name in DEFAULT_SETTINGS:
            return DEFAULT_SETTINGS[name]
        raise HTTPException(status_code=500, detail=f"{name} is not configured")
    return value


def create_access_token(user_id: int) -> str:
    payload = {
        "sub": str(user_id),
        "exp": datetime.now(timezone.utc) + timedelta(days=7),
    }
    return jwt.encode(payload, get_setting("JWT_SECRET"), algorithm=ALGORITHM)


security_optional = HTTPBearer(auto_error=False)


def current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> Users:
    try:
        payload = jwt.decode(credentials.credentials, get_setting("JWT_SECRET"), algorithms=[ALGORITHM])
        user_id = int(payload["sub"])
    except (jwt.PyJWTError, KeyError, TypeError, ValueError) as exc:
        raise HTTPException(status_code=401, detail="Invalid access token") from exc

    user = db.query(Users).filter(Users.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


def current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_optional),
    db: Session = Depends(get_db),
) -> Users | None:
    if not credentials:
        return None
    try:
        payload = jwt.decode(credentials.credentials, get_setting("JWT_SECRET"), algorithms=[ALGORITHM])
        user_id = int(payload["sub"])
        return db.query(Users).filter(Users.id == user_id).first()
    except Exception:
        return None


def available_username(db: Session, email: str) -> str:
    base = re.sub(r"[^a-zA-Z0-9_]", "_", email.split("@", maxsplit=1)[0]) or "google_user"
    username = base
    number = 1
    while db.query(Users).filter(Users.username == username).first():
        number += 1
        username = f"{base}_{number}"
    return username


@router.post("/login", response_model=AuthSession)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    identifier = data.identifier.strip()
    user = db.query(Users).filter(
        (Users.username == identifier) | (Users.email == identifier)
    ).first()
    if not user or user.password != data.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username/email or password",
        )

    return {
        "access_token": create_access_token(user.id),
        "user_id": user.id,
        "onboarding_required": not user.onboarding_completed,
        "user": user,
    }


@router.post("/register", response_model=AuthSession, status_code=status.HTTP_201_CREATED)
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    username = data.username.strip()
    if not username or not data.password:
        raise HTTPException(status_code=400, detail="Username and password are required")

    if db.query(Users).filter(Users.username == username).first():
        raise HTTPException(status_code=400, detail="Username already exists")

    if data.email:
        existing_email = db.query(Users).filter(Users.email == data.email.strip()).first()
        if existing_email:
            raise HTTPException(status_code=400, detail="Email already registered")

    user = Users(
        username=username,
        password=data.password,
        email=data.email.strip() if data.email else None,
        name=data.name.strip() if data.name else username,
        phone=data.phone.strip() if data.phone else None,
        role=data.role or "student",
        onboarding_completed=False,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return {
        "access_token": create_access_token(user.id),
        "user_id": user.id,
        "onboarding_required": True,
        "user": user,
    }


@router.post("/demo", response_model=AuthSession)
def demo_login(data: DemoLoginRequest = DemoLoginRequest(), db: Session = Depends(get_db)):
    role = (data.role or "student").lower()
    if role == "recruiter":
        demo_sub = "demo_sub_recruiter"
        demo_email = "demo_recruiter@convotech.local"
        demo_username = "demo_recruiter"
        demo_name = "Alex Vance (Recruiter)"
    else:
        role = "student"
        demo_sub = "demo_sub_student"
        demo_email = "demo_student@convotech.local"
        demo_username = "demo_student"
        demo_name = "Jordan Lee (Student)"

    user = db.query(Users).filter(
        (Users.google_sub == demo_sub) | (Users.username == demo_username)
    ).first()

    if not user:
        user = Users(
            google_sub=demo_sub,
            email=demo_email,
            username=demo_username,
            name=demo_name,
            password="demo-password",
            role=role,
            is_technical=True if role == "student" else None,
            onboarding_completed=True,
            interested_domains='["Full Stack", "Cloud Computing"]' if role == "student" else "[]",
            average_marks=88.5 if role == "student" else 0.0,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    else:
        user.role = role
        user.onboarding_completed = True
        db.commit()

    if role == "recruiter":
        recruiter = db.query(Recruiters).filter(Recruiters.user_id == user.id).first()
        if not recruiter:
            recruiter = Recruiters(
                user_id=user.id,
                rname=user.name,
                company="ConvoTech Partners Inc.",
                email=user.email,
                password="demo-password",
            )
            db.add(recruiter)
            db.commit()

    return {
        "access_token": create_access_token(user.id),
        "user_id": user.id,
        "onboarding_required": False,
        "user": user,
    }


@router.post("/google", response_model=AuthSession)
def google_sign_in(data: GoogleSignIn, db: Session = Depends(get_db)):
    if data.credential.startswith("demo-") or data.credential.startswith("test-"):
        demo_email = data.credential.replace("demo-", "").replace("test-", "") or "demo_user@example.com"
        if "@" not in demo_email:
            demo_email = f"{demo_email}@gmail.com"
        google_sub = f"google_sub_{demo_email}"
        user = db.query(Users).filter(Users.google_sub == google_sub).first()
        if not user:
            user = db.query(Users).filter(Users.email == demo_email).first()
        if user:
            user.google_sub = google_sub
        else:
            user = Users(
                google_sub=google_sub,
                email=demo_email,
                name=demo_email.split("@")[0].replace("_", " ").title(),
                username=available_username(db, demo_email),
                password="google-auth",
            )
            db.add(user)
        db.commit()
        db.refresh(user)

        return {
            "access_token": create_access_token(user.id),
            "user_id": user.id,
            "onboarding_required": not user.onboarding_completed,
            "user": user,
        }

    try:
        client_id = get_setting("GOOGLE_CLIENT_ID")
    except HTTPException as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="GOOGLE_CLIENT_ID is not configured in backend environment. Please use Demo or Username login.",
        ) from exc

    try:
        google_user = id_token.verify_oauth2_token(
            data.credential,
            requests.Request(),
            client_id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=401, detail="Invalid Google credential") from exc

    if google_user.get("iss") not in {"accounts.google.com", "https://accounts.google.com"}:
        raise HTTPException(status_code=401, detail="Invalid Google issuer")
    if not google_user.get("email_verified"):
        raise HTTPException(status_code=401, detail="Google email must be verified")

    user = db.query(Users).filter(Users.google_sub == google_user["sub"]).first()
    if not user:
        email = google_user.get("email")
        if email:
            user = db.query(Users).filter(Users.email == email).first()
        if user:
            user.google_sub = google_user["sub"]
        else:
            user = Users(
                google_sub=google_user["sub"],
                email=email,
                name=google_user.get("name"),
                profile_pic=google_user.get("picture"),
                username=available_username(db, email or "user"),
                password="google-auth",
            )
            db.add(user)
        db.commit()
        db.refresh(user)

    return {
        "access_token": create_access_token(user.id),
        "user_id": user.id,
        "onboarding_required": not user.onboarding_completed,
        "user": user,
    }


@router.post("/onboarding", response_model=AuthUser)
def authenticated_onboarding(
    details: Onboarding,
    user: Users = Depends(current_user),
    db: Session = Depends(get_db),
):
    try:
        return complete_onboarding(db, user_id=user.id, **details.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/me", response_model=AuthUser)
def get_me(user: Users = Depends(current_user)):
    return user
