from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from app.database import engine, base
from app.router import users, posts, likes, comments, follows, messages, recruiters
from pathlib import Path

app = FastAPI(
    title="ConvoTech Social API",
    description="Backend REST API for ConvoTech social media platform",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# convotech-main/
BASE_DIR = Path(__file__).resolve().parents[2]

app.include_router(users.router)
app.include_router(posts.router)
app.include_router(likes.router)
app.include_router(comments.router)
app.include_router(follows.router)
app.include_router(messages.router)
app.include_router(recruiters.router)


@app.get("/api-status")
def status():
    return {
        "message": "Welcome to ConvoTech API",
        "status": "online"
    }


@app.get("/")
def home():
    return FileResponse(BASE_DIR / "index.html")