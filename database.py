"""
FILE: database.py
ROLE: The data layer. Defines what data looks like and how to connect to it.

WHAT THIS FILE DOES:
- Creates the connection to Supabase PostgreSQL
- Defines database tables as Python classes (called models)
- Provides get_db() which gives each request its own DB session
- Auto-creates tables on startup if they don't exist

WHAT THIS FILE DOES NOT DO:
- Does not define API endpoints (that's main.py)
- Does not contain business logic
- Does not handle auth (that's auth.py)

KEY CONCEPTS:
- engine = the actual connection to PostgreSQL
- SessionLocal = a factory that creates DB sessions
- Base = parent class all table models inherit from
- get_db() = dependency that opens/closes a session per request

TABLE RELATIONSHIPS:
users (one) ──── documents (many)
One user can have many documents.
documents.user_id is a foreign key pointing to users.id
"""

from sqlalchemy import create_engine, Column, String, DateTime, ARRAY, Text, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from datetime import datetime
import uuid
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    connect_args={"sslmode": "require"}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# ─────────────────────────────────────────
# USER TABLE
# Stores registered users.
# Passwords are never stored plain — only bcrypt hash is saved.
# ─────────────────────────────────────────

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


# ─────────────────────────────────────────
# DOCUMENT TABLE
# Stores document metadata + extracted text content.
# The actual file lives in Supabase Storage.
# file_path = the path inside Supabase Storage bucket
# file_type = "pdf" or "txt"
# content = extracted text (what AI will read later)
# ─────────────────────────────────────────

class Document(Base):
    __tablename__ = "documents"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    tags = Column(ARRAY(String), default=[])
    file_path = Column(String, nullable=True)   # path in Supabase Storage
    file_type = Column(String, nullable=True)   # "pdf", "txt", or None if raw text
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)


# ─────────────────────────────────────────
# DATABASE SESSION DEPENDENCY
# FastAPI calls this to get a DB session for each request.
# try/finally ensures session always closes after request ends.
# ─────────────────────────────────────────

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Create all tables that don't exist yet
Base.metadata.create_all(bind=engine)