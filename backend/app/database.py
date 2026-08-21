import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv()

db_url = os.getenv("DATABASE_URL")

if not db_url:
    raise ValueError("DATABASE_URL is not set. Add it to your .env file.")

engine = create_engine(db_url)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
session = SessionLocal

Base = declarative_base()
base = Base

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()