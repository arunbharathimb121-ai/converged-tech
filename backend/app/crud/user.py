from sqlalchemy.orm import Session
import json

from app.models import Recruiters, Users
from datetime import date, datetime
from typing import Optional

def get_all(db: Session, role: Optional[str] = "student"):
    query = db.query(Users)
    if role and role.lower() != "all":
        query = query.filter(Users.role == role)
    return query.all()

def get_user(db: Session, id: int):
    return db.query(Users).filter(Users.id == id).first()

def create_user(
    db: Session,
    username: str,
    password: str,
    phone: Optional[str],
    name: Optional[str] = None,
    dob: Optional[date] = None,
    career: Optional[str] = None,
    org: Optional[str] = None,
    bio: Optional[str] = None,
    profile_pic: Optional[str] = None,
    email: Optional[str] = None,
    role: Optional[str] = "student",
    id: Optional[int] = None
):
    kwargs = {
        "name": name,
        "dob": dob,
        "username": username,
        "password": password,
        "phone": phone,
        "career": career,
        "org": org,
        "bio": bio,
        "profile_pic": profile_pic,
        "email": email,
        "role": role or "student"
    }
    if id is not None:
        kwargs["id"] = id
        
    user = Users(**kwargs)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def delete_user(db: Session, id: int):
    did = db.query(Users).filter(Users.id == id).first()
    if did:
        db.delete(did)
        db.commit()
    return did


def complete_onboarding(
    db: Session,
    user_id: int,
    name: str,
    phone: str,
    role: str,
    is_technical: Optional[bool],
    interested_domains: list[str],
    company: Optional[str] = None,
    recruiter_name: Optional[str] = None,
):
    user = get_user(db, user_id)
    if not user:
        return None

    if role not in {"student", "recruiter"}:
        raise ValueError("Role must be student or recruiter.")
    if role == "student" and is_technical is None:
        raise ValueError("Students must choose technical or non-technical.")
    if role == "recruiter" and (not company or not recruiter_name):
        raise ValueError("Recruiters must provide company and recruiter name.")

    if phone:
        existing_phone = db.query(Users).filter(Users.phone == phone, Users.id != user_id).first()
        if existing_phone:
            raise ValueError(f"Phone number '{phone}' is already registered to another account. Please provide a unique phone number.")

    user.name = name
    user.phone = phone
    user.role = role
    user.is_technical = is_technical if role == "student" else None
    user.interested_domains = json.dumps(interested_domains)
    user.onboarding_completed = True

    if role == "recruiter":
        recruiter = db.query(Recruiters).filter(Recruiters.user_id == user_id).first()
        if not recruiter:
            recruiter = Recruiters(user_id=user_id, password=user.password)
            db.add(recruiter)
        recruiter.rname = recruiter_name
        recruiter.company = company
        recruiter.email = user.email

    db.commit()
    db.refresh(user)
    return user
