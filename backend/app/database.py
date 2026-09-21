import os
import logging
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

logger = logging.getLogger("convotech.database")

BACKEND_DIR = Path(__file__).resolve().parents[1]
env_path = BACKEND_DIR / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
else:
    load_dotenv()

DEFAULT_SQLITE_PATH = (BACKEND_DIR / "convotech.db").as_posix()
db_url = os.getenv("DATABASE_URL")
if not db_url:
    db_url = f"sqlite:///{DEFAULT_SQLITE_PATH}"

def build_engine(url: str):
    is_sqlite = url.startswith("sqlite")
    connect_args = {"check_same_thread": False} if is_sqlite else {}
    return create_engine(url, connect_args=connect_args)

try:
    engine = build_engine(db_url)
    with engine.connect() as conn:
        pass
except Exception as e:
    fallback_url = f"sqlite:///{DEFAULT_SQLITE_PATH}"
    logger.warning(
        f"Could not connect to configured database at '{db_url}': {e}. "
        f"Falling back to local SQLite database at '{fallback_url}'."
    )
    db_url = fallback_url
    engine = build_engine(fallback_url)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

# Backwards compatibility aliases
session = SessionLocal
base = Base


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()