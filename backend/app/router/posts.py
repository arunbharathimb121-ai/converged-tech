import os
import shutil
import uuid
from typing import Optional
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form
from app.database import get_db
from app.crud.post import get_all, get_post, create_post, delete_post
from app.schemas import Posts

router = APIRouter(prefix="/posts", tags=["posts"])

UPLOAD_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "uploads"))
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.get("/", response_model=list[Posts])
def getall(db: Session = Depends(get_db)):
    return get_all(db)

@router.post("/upload-image/")
def upload_image(file: UploadFile = File(...)):
    ext = os.path.splitext(file.filename)[1] if file.filename else ".jpg"
    filename = f"{uuid.uuid4().hex}{ext}"
    file_path = os.path.join(UPLOAD_DIR, filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {"image_url": f"/uploads/{filename}", "filename": filename}

@router.post("/with-image", response_model=Posts, status_code=status.HTTP_201_CREATED)
def create_post_with_image(
    user_id: int = Form(...),
    caption: str = Form(...),
    username: Optional[str] = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    ext = os.path.splitext(file.filename)[1] if file.filename else ".jpg"
    filename = f"{uuid.uuid4().hex}{ext}"
    file_path = os.path.join(UPLOAD_DIR, filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    image_url = f"/uploads/{filename}"

    return create_post(
        db=db,
        image=image_url,
        caption=caption,
        user_id=user_id,
        username=username
    )

@router.get("/{post_id}", response_model=Posts)
def getone(post_id: int, db: Session = Depends(get_db)):
    data = get_post(db, post_id)
    if not data:
        raise HTTPException(status_code=404, detail="Post not found")
    return data

@router.post("/", response_model=Posts, status_code=status.HTTP_201_CREATED)
def addone(post: Posts, db: Session = Depends(get_db)):
    return create_post(
        db=db,
        image=post.image,
        caption=post.caption,
        user_id=post.user_id,
        username=post.username,
        id=post.id,
        date=post.date
    )

@router.delete("/{post_id}")
def removeone(post_id: int, db: Session = Depends(get_db)):
    deleted = delete_post(db, post_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Post not found!")
    return {"detail": "Post deleted successfully"}


