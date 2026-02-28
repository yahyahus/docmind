"""
FILE: database.py
ROLE: The data layer. Defines what data looks like and how to connect to it.

WHAT THIS FILE DOES:
- Creates the connection to Supabase PostgreSQL
- Defines all database tables as Python classes (models)
- Provides get_db() which gives each request its own DB session
- Auto-creates tables on startup if they don't exist

TABLE RELATIONSHIPS:
users (1) ──── documents (many)
users (1) ──── conversations (many)
conversations (1) ──── messages (many)
conversations (many) ──── documents (1) [optional]
documents (1) ──── document_chunks (many)

WHAT THIS FILE DOES NOT DO:
- Does not define API endpoints (that's main.py)
- Does not contain business logic
- Does not handle auth (that's auth.py)
"""

from sqlalchemy import create_engine, Column, String, DateTime, ARRAY, Text, Boolean, ForeignKey, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pgvector.sqlalchemy import Vector
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


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Document(Base):
    __tablename__ = "documents"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    tags = Column(ARRAY(String), default=[])
    file_path = Column(String, nullable=True)
    file_type = Column(String, nullable=True)
    is_processed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)


# ─────────────────────────────────────────
# DOCUMENT CHUNK TABLE
# Each document is split into small overlapping chunks.
# Each chunk gets an embedding — a vector of 768 numbers
# (Gemini embedding dimension is 768, OpenAI is 1536).
# The embedding captures the semantic meaning of the chunk.
# When a user asks a question, we embed the question too,
# then find chunks whose embeddings are most similar.
# ─────────────────────────────────────────

class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id = Column(String, ForeignKey("documents.id"), nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    chunk_index = Column(Integer, nullable=False)
    embedding = Column(Vector(1536))   # Gemini uses 768 dimensions
    created_at = Column(DateTime, default=datetime.utcnow)


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    document_id = Column(String, ForeignKey("documents.id"), nullable=True)
    title = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)


class Message(Base):
    __tablename__ = "messages"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    conversation_id = Column(String, ForeignKey("conversations.id"), nullable=False)
    role = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


Base.metadata.create_all(bind=engine)