from sqlalchemy.orm import Session
from app.models import Follows
from typing import Optional

def get_all(db: Session):
    return db.query(Follows).all()

def get_follow(db: Session, id: int):
    return db.query(Follows).filter(Follows.id == id).first()

def create_follow(
    db: Session,
    follower_id: int,
    following_id: int,
    id: Optional[int] = None
):
    kwargs = {
        "follower_id": follower_id,
        "following_id": following_id
    }
    if id is not None:
        kwargs["id"] = id
        
    follow = Follows(**kwargs)
    db.add(follow)
    db.commit()
    db.refresh(follow)
    return follow

def delete_follow(db: Session, id: int):
    did = db.query(Follows).filter(Follows.id == id).first()
    if did:
        db.delete(did)
        db.commit()
    return did

