from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, status
from app.database import get_db
from app.crud.comment import get_all, get_comment, create_comment, delete_comment
from app.schemas import Comments

router = APIRouter(prefix="/comments", tags=["comments"])

@router.get("/", response_model=list[Comments])
def getall(db: Session = Depends(get_db)):
    return get_all(db)

@router.get("/{comment_id}", response_model=Comments)
def getone(comment_id: int, db: Session = Depends(get_db)):
    data = get_comment(db, comment_id)
    if not data:
        raise HTTPException(status_code=404, detail="Comment not found")
    return data

@router.post("/", response_model=Comments, status_code=status.HTTP_201_CREATED)
def addone(comment: Comments, db: Session = Depends(get_db)):
    return create_comment(
        db=db,
        user_id=comment.user_id,
        post_id=comment.post_id,
        comment=comment.comment,
        id=comment.id,
        created_at=comment.created_at
    )

@router.delete("/{comment_id}")
def removeone(comment_id: int, db: Session = Depends(get_db)):
    deleted = delete_comment(db, comment_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Comment not found!")
    return {"detail": "Comment deleted successfully"}

