from sqlalchemy.orm import Session
from app.models import Posts
from datetime import datetime
from typing import Optional

def get_all(db: Session):
    return db.query(Posts).all()

def get_post(db: Session, id: int):
    return db.query(Posts).filter(Posts.id == id).first()

def create_post(
    db: Session,
    image: str,
    caption: str,
    user_id: int,
    username: Optional[str] = None,
    id: Optional[int] = None,
    date: Optional[datetime] = None
):
    kwargs = {
        "username": username,
        "image": image,
        "caption": caption,
        "user_id": user_id,
    }
    if id is not None:
        kwargs["id"] = id
    if date is not None:
        kwargs["date"] = date
        
    post = Posts(**kwargs)
    db.add(post)
    db.commit()
    db.refresh(post)
    return post

def delete_post(db: Session, id: int):
    did = db.query(Posts).filter(Posts.id == id).first()
    if did:
        db.delete(did)
        db.commit()
    return did

