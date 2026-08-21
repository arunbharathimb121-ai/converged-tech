from sqlalchemy.orm import Session
from app.models import Users
from datetime import date, datetime
from typing import Optional

def get_all(db: Session):
    return db.query(Users).all()

def get_user(db: Session, id: int):
    return db.query(Users).filter(Users.id == id).first()

def create_user(
    db: Session,
    username: str,
    password: str,
    phone: str,
    name: Optional[str] = None,
    dob: Optional[date] = None,
    career: Optional[str] = None,
    org: Optional[str] = None,
    bio: Optional[str] = None,
    profile_pic: Optional[str] = None,
    email: Optional[str] = None,
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
        "email": email
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

