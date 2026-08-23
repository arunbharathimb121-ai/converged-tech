import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app.router import (
    auth,
    comments,
    follows,
    likes,
    mcqs,
    messages,
    posts,
    recruiters,
    practices,
    streaks,
    users,
)

app = FastAPI(
    title="ConvoTech API",
    description="Backend REST API for ConvoTech platform",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parents[2]
UPLOAD_DIR = BASE_DIR / "backend" / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(posts.router)
app.include_router(likes.router)
app.include_router(comments.router)
app.include_router(follows.router)
app.include_router(messages.router)
app.include_router(recruiters.router)
app.include_router(mcqs.router)
app.include_router(practices.router)
app.include_router(streaks.router)


def get_env_value(key: str) -> str:
    env_file = BASE_DIR / "backend" / ".env"
    if not env_file.exists():
        env_file = BASE_DIR / ".env"
    if env_file.exists():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("#") or "=" not in stripped:
                continue
            env_key, env_value = stripped.split("=", 1)
            if env_key.strip() == key:
                return env_value.strip().strip('"').strip("'")
    return os.getenv(key, "")


@app.get("/api-status")
def status():
    return {"message": "Welcome to ConvoTech API", "status": "online"}


@app.get("/config")
def config():
    return JSONResponse(
        {
            "googleClientId": get_env_value("GOOGLE_CLIENT_ID"),
            "roles": ["student", "recruiter", "admin"],
        }
    )


@app.get("/")
def home():
    return FileResponse(BASE_DIR / "index.html")