from sqlalchemy.orm import Session
from app.models import Comments
from datetime import datetime
from typing import Optional

def get_all(db: Session):
    return db.query(Comments).all()

def get_comment(db: Session, id: int):
    return db.query(Comments).filter(Comments.id == id).first()

def create_comment(
    db: Session,
    user_id: int,
    post_id: int,
    comment: str,
    id: Optional[int] = None,
    created_at: Optional[datetime] = None
):
    kwargs = {
        "user_id": user_id,
        "post_id": post_id,
        "comment": comment
    }
    if id is not None:
        kwargs["id"] = id
    if created_at is not None:
        kwargs["created_at"] = created_at
        
    comm = Comments(**kwargs)
    db.add(comm)
    db.commit()
    db.refresh(comm)
    return comm

def delete_comment(db: Session, id: int):
    did = db.query(Comments).filter(Comments.id == id).first()
    if did:
        db.delete(did)
        db.commit()
    return did

