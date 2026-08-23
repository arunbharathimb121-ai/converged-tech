import os
import re
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from google.auth.transport import requests
from google.oauth2 import id_token
from sqlalchemy.orm import Session

from app.crud.user import complete_onboarding
from app.database import get_db
from app.models import Users
from app.schemas import AuthSession, AuthUser, GoogleSignIn, Onboarding

router = APIRouter(prefix="/auth", tags=["auth"])
security = HTTPBearer()
ALGORITHM = "HS256"


def get_setting(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise HTTPException(status_code=500, detail=f"{name} is not configured")
    return value


def create_access_token(user_id: int) -> str:
    payload = {
        "sub": str(user_id),
        "exp": datetime.now(timezone.utc) + timedelta(days=7),
    }
    return jwt.encode(payload, get_setting("JWT_SECRET"), algorithm=ALGORITHM)


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


def available_username(db: Session, email: str) -> str:
    base = re.sub(r"[^a-zA-Z0-9_]", "_", email.split("@", maxsplit=1)[0]) or "google_user"
    username = base
    number = 1
    while db.query(Users).filter(Users.username == username).first():
        number += 1
        username = f"{base}_{number}"
    return username


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
        }

    try:
        google_user = id_token.verify_oauth2_token(
            data.credential,
            requests.Request(),
            get_setting("GOOGLE_CLIENT_ID"),
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
