from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, status
from app.database import get_db
from app.crud.follow import get_all, get_follow, create_follow, delete_follow
from app.schemas import Follows

router = APIRouter(prefix="/follows", tags=["follows"])

@router.get("/", response_model=list[Follows])
def getall(db: Session = Depends(get_db)):
    return get_all(db)

@router.get("/{follow_id}", response_model=Follows)
def getone(follow_id: int, db: Session = Depends(get_db)):
    data = get_follow(db, follow_id)
    if not data:
        raise HTTPException(status_code=404, detail="Follow relationship not found")
    return data

@router.post("/", response_model=Follows, status_code=status.HTTP_201_CREATED)
def addone(follow: Follows, db: Session = Depends(get_db)):
    return create_follow(
        db=db,
        follower_id=follow.follower_id,
        following_id=follow.following_id,
        id=follow.id
    )

@router.delete("/{follow_id}")
def removeone(follow_id: int, db: Session = Depends(get_db)):
    deleted = delete_follow(db, follow_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Follow relationship not found!")
    return {"detail": "Follow relationship deleted successfully"}

