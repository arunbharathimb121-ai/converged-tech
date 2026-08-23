from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import APIRouter, Depends, HTTPException, status
from app.database import get_db
from app.crud.user import complete_onboarding, get_all, get_user, create_user, delete_user
from app.schemas import Onboarding, Users
from typing import Optional

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/", response_model=list[Users])
def getall(db: Session = Depends(get_db)):
    return get_all(db)

@router.get("/{user_id}", response_model=Users)
def getone(user_id: int, db: Session = Depends(get_db)):
    data = get_user(db, user_id)
    if not data:
        raise HTTPException(status_code=404, detail="User not found")
    return data

@router.post("/", response_model=Users, status_code=status.HTTP_201_CREATED)
def addone(user: Users, db: Session = Depends(get_db)):
    try:
        return create_user(
            db=db,
            username=user.username,
            password=user.password,
            phone=user.phone,
            name=user.name,
            dob=user.dob,
            career=user.career,
            org=user.org,
            bio=user.bio,
            profile_pic=user.profile_pic,
            email=user.email,
            id=user.id
        )
    except IntegrityError as e:
        db.rollback()
        err_msg = str(e.orig)
        if "users_pkey" in err_msg or "Key (id)=" in err_msg:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User ID sequence conflict. Reset PostgreSQL sequence using: SELECT setval(pg_get_serial_sequence('users', 'id'), COALESCE(max(id), 1)) FROM users;"
            )
        elif "username" in err_msg:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists")
        elif "phone" in err_msg:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Phone number already exists")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Database constraint error: {err_msg}")

@router.delete("/{user_id}")
def removeone(user_id: int, db: Session = Depends(get_db)):
    deleted = delete_user(db, user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="User not found!")
    return {"detail": "User deleted successfully"}


@router.post("/{user_id}/onboarding", response_model=Users)
def onboarding(user_id: int, details: Onboarding, db: Session = Depends(get_db)):
    try:
        user = complete_onboarding(db, user_id=user_id, **details.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
