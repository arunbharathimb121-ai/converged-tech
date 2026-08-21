from sqlalchemy.orm import Session
from app.models import Likes
from typing import Optional

def get_all(db: Session):
    return db.query(Likes).all()

def get_like(db: Session, id: int):
    return db.query(Likes).filter(Likes.id == id).first()

def create_like(db: Session, user_id: int, post_id: int, id: Optional[int] = None):
    kwargs = {"user_id": user_id, "post_id": post_id}
    if id is not None:
        kwargs["id"] = id
    like = Likes(**kwargs)
    db.add(like)
    db.commit()
    db.refresh(like)
    return like

def delete_like(db: Session, id: int):
    did = db.query(Likes).filter(Likes.id == id).first()
    if did:
        db.delete(did)
        db.commit()
    return did

get_post = get_like
create_post = create_like
delete_post = delete_like

