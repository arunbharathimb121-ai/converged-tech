from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, status
from app.database import get_db
from app.crud.like import get_all, get_like, create_like, delete_like
from app.schemas import Likes

from app.router.auth import current_user_optional
from app.models import Users, Likes as LikesModel

router = APIRouter(prefix="/likes", tags=["likes"])

@router.get("/", response_model=list[Likes])
def getall(db: Session = Depends(get_db)):
    return get_all(db)

@router.get("/{like_id}", response_model=Likes)
def getone(like_id: int, db: Session = Depends(get_db)):
    data = get_like(db, like_id)
    if not data:
        raise HTTPException(status_code=404, detail="Like not found")
    return data

@router.post("/", response_model=Likes, status_code=status.HTTP_201_CREATED)
def addone(
    like: Likes,
    user: Users | None = Depends(current_user_optional),
    db: Session = Depends(get_db)
):
    target_user_id = user.id if user else like.user_id
    existing = db.query(LikesModel).filter(
        LikesModel.user_id == target_user_id,
        LikesModel.post_id == like.post_id
    ).first()
    if existing:
        delete_like(db, existing.id)
        raise HTTPException(status_code=status.HTTP_200_OK, detail="Unliked post")

    return create_like(
        db=db,
        user_id=target_user_id,
        post_id=like.post_id,
        id=like.id
    )

@router.delete("/{like_id}")
def removeone(like_id: int, db: Session = Depends(get_db)):
    deleted = delete_like(db, like_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Like not found!")
    return {"detail": "Like deleted successfully"}
