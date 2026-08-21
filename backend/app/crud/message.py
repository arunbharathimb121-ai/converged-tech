from sqlalchemy.orm import Session
from app.models import Message
from datetime import datetime
from typing import Optional

def get_all(db: Session):
    return db.query(Message).all()

def get_message(db: Session, id: int):
    return db.query(Message).filter(Message.id == id).first()

def create_message(
    db: Session,
    sender_id: int,
    receiver_id: int,
    message: str,
    id: Optional[int] = None,
    created_at: Optional[datetime] = None
):
    kwargs = {
        "sender_id": sender_id,
        "receiver_id": receiver_id,
        "message": message
    }
    if id is not None:
        kwargs["id"] = id
    if created_at is not None:
        kwargs["created_at"] = created_at
        
    msg = Message(**kwargs)
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg

def delete_message(db: Session, id: int):
    did = db.query(Message).filter(Message.id == id).first()
    if did:
        db.delete(did)
        db.commit()
    return did

# Backward compatibility aliases
get_post = get_message
create_post = create_message
delete_post = delete_message

