"""
FILE: main.py
ROLE: The front door of the API. All endpoints live here.

WHAT THIS FILE DOES:
- Defines every URL the API responds to
- Validates incoming data using Pydantic models
- Calls auth.py to protect endpoints
- Calls database.py to read/write data
- Returns responses to the client

WHAT THIS FILE DOES NOT DO:
- Does not contain database connection logic (that's database.py)
- Does not contain token/password logic (that's auth.py)
- Does not talk to external services directly

IMPORTS FROM:
- database.py → Document, User, get_db
- auth.py → hash_password, verify_password, create_access_token,
             create_refresh_token, get_current_user

HOW TO READ THIS FILE:
1. Start at the Pydantic models — they show the shape of data in/out
2. Then read each endpoint — the function name tells you what it does
3. The Depends() calls tell you what each endpoint needs to run
"""

from fastapi import FastAPI, HTTPException, Depends, status, UploadFile, File
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.openapi.models import SecurityScheme
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional
from supabase import create_client, Client
from dotenv import load_dotenv
import uuid
import os
import io

import PyPDF2

from database import Document, User, get_db
from auth import (
    hash_password, verify_password,
    create_access_token, create_refresh_token,
    get_current_user
)

load_dotenv()

# ─────────────────────────────────────────
# APP SETUP
# ─────────────────────────────────────────

app = FastAPI(title="DocMind API", version="1.0.0")

# Supabase client for file storage
# We use this to upload files to Supabase Storage buckets
supabase: Client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    from fastapi.openapi.utils import get_openapi
    openapi_schema = get_openapi(
        title="DocMind API",
        version="1.0.0",
        routes=app.routes,
    )
    # Add Bearer auth scheme
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }
    # Apply to all endpoints
    for path in openapi_schema["paths"].values():
        for operation in path.values():
            operation["security"] = [{"BearerAuth": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi


# ─────────────────────────────────────────
# PYDANTIC MODELS
# ─────────────────────────────────────────

class UserRegister(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: str
    email: str
    created_at: datetime

    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class DocumentCreate(BaseModel):
    title: str
    content: str
    tags: list[str] = []

class DocumentUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    tags: Optional[list[str]] = None

class DocumentResponse(BaseModel):
    id: str
    user_id: str
    title: str
    content: str
    tags: list[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ─────────────────────────────────────────
# AUTH ENDPOINTS
# ─────────────────────────────────────────

@app.get("/")
async def root():
    return {"message": "DocMind API is running"}

@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    doc_count = db.query(Document).count()
    user_count = db.query(User).count()
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "version": "1.0.0",
        "document_count": doc_count,
        "user_count": user_count
    }

@app.post("/auth/register", response_model=UserResponse, status_code=201)
async def register(user_data: UserRegister, db: Session = Depends(get_db)):
    if len(user_data.password) > 72:
        raise HTTPException(status_code=400, detail="Password must be 72 characters or less")

    # Check if email already exists
    existing = db.query(User).filter(User.email == user_data.email).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    user = User(
        id=str(uuid.uuid4()),
        email=user_data.email,
        hashed_password=hash_password(user_data.password)
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@app.post("/auth/login", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    # Find user by email
    user = db.query(User).filter(User.email == form_data.username).first()

    # Verify user exists and password is correct
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    return TokenResponse(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id),
        token_type="bearer"
    )

@app.get("/auth/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    # get_current_user already did all the work
    # if we reach here, the token is valid and user exists
    return current_user


# ─────────────────────────────────────────
# DOCUMENT ENDPOINTS (now protected + user-scoped)
# ─────────────────────────────────────────

@app.post("/documents", response_model=DocumentResponse, status_code=201)
async def create_document(
    doc: DocumentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)  # 👈 protected
):
    db_doc = Document(
        id=str(uuid.uuid4()),
        user_id=current_user.id,   # document belongs to logged-in user
        title=doc.title,
        content=doc.content,
        tags=doc.tags
    )
    db.add(db_doc)
    db.commit()
    db.refresh(db_doc)
    return db_doc

@app.get("/documents", response_model=list[DocumentResponse])
async def list_documents(
    limit: int = 10,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Only returns THIS user's documents
    return db.query(Document).filter(
        Document.user_id == current_user.id
    ).offset(offset).limit(limit).all()

# ─────────────────────────────────────────
# SEARCH ENDPOINT
# Searches across title, content, and tags
# Uses PostgreSQL ILIKE = case-insensitive pattern matching
# Example: searching "python" finds "Python", "PYTHON", "python3"
# ─────────────────────────────────────────

@app.get("/documents/search", response_model=list[DocumentResponse])
async def search_documents(
    q: str,                          # the search query e.g. ?q=python
    limit: int = 10,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Search across the current user's documents.
    Searches title, content, and tags simultaneously.
    Returns documents ranked by most recently updated.
    """
    if not q or len(q.strip()) == 0:
        raise HTTPException(
            status_code=400,
            detail="Search query cannot be empty"
        )

    search_term = f"%{q.strip()}%"  # % is wildcard in SQL LIKE queries

    results = db.query(Document).filter(
        Document.user_id == current_user.id,  # only search THIS user's docs
        # Search across title OR content OR tags
        (
            Document.title.ilike(search_term) |
            Document.content.ilike(search_term) |
            Document.tags.any(q.strip().lower())  # search inside tags array
        )
    ).order_by(
        Document.updated_at.desc()   # most recently updated first
    ).offset(offset).limit(limit).all()

    return results

@app.get("/documents/{doc_id}", response_model=DocumentResponse)
async def get_document(
    doc_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    doc = db.query(Document).filter(
        Document.id == doc_id,
        Document.user_id == current_user.id  # can't access other users' docs
    ).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc

@app.patch("/documents/{doc_id}", response_model=DocumentResponse)
async def update_document(
    doc_id: str,
    updates: DocumentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    doc = db.query(Document).filter(
        Document.id == doc_id,
        Document.user_id == current_user.id
    ).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    if updates.title is not None:
        doc.title = updates.title
    if updates.content is not None:
        doc.content = updates.content
    if updates.tags is not None:
        doc.tags = updates.tags

    doc.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(doc)
    return doc

@app.delete("/documents/{doc_id}")
async def delete_document(
    doc_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    doc = db.query(Document).filter(
        Document.id == doc_id,
        Document.user_id == current_user.id
    ).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    db.delete(doc)
    db.commit()
    return {"message": "Document deleted successfully", "id": doc_id}

# ─────────────────────────────────────────
# FILE UPLOAD HELPERS
# ─────────────────────────────────────────

def extract_text_from_pdf(file_bytes: bytes) -> str:
    """
    Reads raw PDF bytes and extracts all text from every page.
    PyPDF2 reads the PDF structure and pulls out readable text.
    Some scanned PDFs return empty text — that's a known limitation.
    """
    pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
    text = ""
    for page in pdf_reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text.strip()


def upload_to_supabase(file_bytes: bytes, file_path: str, content_type: str) -> str:
    """
    Uploads a file to Supabase Storage bucket called 'documents'.
    Returns the file path so we can store it in the database.
    """
    supabase.storage.from_("documents").upload(
        path=file_path,
        file=file_bytes,
        file_options={"content-type": content_type}
    )
    return file_path


# ─────────────────────────────────────────
# FILE UPLOAD ENDPOINT
# ─────────────────────────────────────────

@app.post("/documents/upload", response_model=DocumentResponse, status_code=201)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Accepts a PDF or TXT file upload.
    Flow:
    1. Validate file type
    2. Read file bytes
    3. Extract text content
    4. Upload file to Supabase Storage
    5. Save metadata + content to PostgreSQL
    6. Return the created document
    """

    # Step 1 — Validate file type
    allowed_types = ["application/pdf", "text/plain"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Upload PDF or TXT files only."
        )

    # Step 2 — Read file bytes into memory
    file_bytes = await file.read()

    # Enforce file size limit (5MB)
    max_size = 5 * 1024 * 1024  # 5MB in bytes
    if len(file_bytes) > max_size:
        raise HTTPException(
            status_code=400,
            detail="File too large. Maximum size is 5MB."
        )

    # Step 3 — Extract text based on file type
    if file.content_type == "application/pdf":
        content = extract_text_from_pdf(file_bytes)
        file_type = "pdf"
        if not content:
            raise HTTPException(
                status_code=400,
                detail="Could not extract text from PDF. File may be scanned or image-based."
            )
    else:
        # TXT file — just decode the bytes to string
        content = file_bytes.decode("utf-8")
        file_type = "txt"

    # Step 4 — Upload to Supabase Storage
    # Path format: user_id/unique_id_filename
    # This keeps each user's files in their own folder
    file_extension = "pdf" if file_type == "pdf" else "txt"
    storage_path = f"{current_user.id}/{uuid.uuid4()}/{file.filename}"

    try:
        upload_to_supabase(file_bytes, storage_path, file.content_type)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"File storage failed: {str(e)}"
        )

    # Step 5 — Storage succeeded, now save to PostgreSQL
    try:
        db_doc = Document(
            id=str(uuid.uuid4()),
            user_id=current_user.id,
            title=file.filename,
            content=content,
            tags=[],
            file_path=storage_path,
            file_type=file_type
        )
        db.add(db_doc)
        db.commit()
        db.refresh(db_doc)
        return db_doc
    except Exception as e:
        print(f"DATABASE ERROR: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Database save failed: {str(e)}"
        )