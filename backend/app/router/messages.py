from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, status
from app.database import get_db
from app.crud.message import get_all, get_message, create_message, delete_message
from app.schemas import Message

router = APIRouter(prefix="/messages", tags=["messages"])
app = router

@router.get("/", response_model=list[Message])
def getall(db: Session = Depends(get_db)):
    return get_all(db)

@router.get("/{message_id}", response_model=Message)
def getone(message_id: int, db: Session = Depends(get_db)):
    data = get_message(db, message_id)
    if not data:
        raise HTTPException(status_code=404, detail="Message not found")
    return data

@router.post("/", response_model=Message, status_code=status.HTTP_201_CREATED)
def addone(msg: Message, db: Session = Depends(get_db)):
    return create_message(
        db=db,
        sender_id=msg.sender_id,
        receiver_id=msg.receiver_id,
        message=msg.message,
        id=msg.id,
        created_at=msg.created_at
    )

@router.delete("/{message_id}")
def removeone(message_id: int, db: Session = Depends(get_db)):
    deleted = delete_message(db, message_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Message not found!")
    return {"detail": "Message deleted successfully"}

