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
"""

from fastapi import FastAPI, HTTPException, Depends, status, UploadFile, File
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional
from supabase import create_client, Client
from dotenv import load_dotenv
import uuid
import os
import io
import json
import PyPDF2

from ai import (
    process_document, generate_rag_response, generate_summary,
    client, find_relevant_chunks, find_relevant_chunks_multi,
    get_conversation_history, build_messages
)
from database import Document, User, Conversation, Message, DocumentChunk, get_db
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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }
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
    file_path: Optional[str] = None
    file_type: Optional[str] = None
    is_processed: bool = False
    summary: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ConversationCreate(BaseModel):
    title: str
    document_id: Optional[str] = None
    document_ids: Optional[list[str]] = []

class ConversationResponse(BaseModel):
    id: str
    user_id: str
    document_id: Optional[str] = None
    document_ids: list[str] = []
    title: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class MessageCreate(BaseModel):
    content: str

class MessageResponse(BaseModel):
    id: str
    conversation_id: str
    role: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True


# ─────────────────────────────────────────
# ROOT + HEALTH
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


# ─────────────────────────────────────────
# AUTH ENDPOINTS
# ─────────────────────────────────────────

@app.post("/auth/register", response_model=UserResponse, status_code=201)
async def register(user_data: UserRegister, db: Session = Depends(get_db)):
    if len(user_data.password) > 72:
        raise HTTPException(status_code=400, detail="Password must be 72 characters or less")

    existing = db.query(User).filter(User.email == user_data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

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
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    return TokenResponse(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id),
        token_type="bearer"
    )

@app.get("/auth/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user


# ─────────────────────────────────────────
# DOCUMENT ENDPOINTS
# ─────────────────────────────────────────

@app.post("/documents", response_model=DocumentResponse, status_code=201)
async def create_document(
    doc: DocumentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_doc = Document(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
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
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(Document).filter(
        Document.user_id == current_user.id
    ).offset(offset).limit(limit).all()

@app.get("/documents/search", response_model=list[DocumentResponse])
async def search_documents(
    q: str,
    limit: int = 10,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not q or len(q.strip()) == 0:
        raise HTTPException(status_code=400, detail="Search query cannot be empty")

    search_term = f"%{q.strip()}%"
    results = db.query(Document).filter(
        Document.user_id == current_user.id,
        (
            Document.title.ilike(search_term) |
            Document.content.ilike(search_term) |
            Document.tags.any(q.strip().lower())
        )
    ).order_by(
        Document.updated_at.desc()
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
        Document.user_id == current_user.id
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

    # Delete chunks first (FK constraint)
    db.query(DocumentChunk).filter(
        DocumentChunk.document_id == doc_id
    ).delete()

    # Delete linked conversations and their messages
    convs = db.query(Conversation).filter(
        Conversation.document_id == doc_id
    ).all()
    for conv in convs:
        db.query(Message).filter(
            Message.conversation_id == conv.id
        ).delete()
    db.query(Conversation).filter(
        Conversation.document_id == doc_id
    ).delete()

    db.delete(doc)
    db.commit()
    return {"message": "Document deleted successfully", "id": doc_id}


# ─────────────────────────────────────────
# FILE UPLOAD HELPERS
# ─────────────────────────────────────────

def extract_text_from_pdf(file_bytes: bytes) -> str:
    pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
    text = ""
    for page in pdf_reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text.strip()

def upload_to_supabase(file_bytes: bytes, file_path: str, content_type: str) -> str:
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
    allowed_types = ["application/pdf", "text/plain"]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="File type not allowed. Upload PDF or TXT files only.")

    file_bytes = await file.read()

    max_size = 5 * 1024 * 1024
    if len(file_bytes) > max_size:
        raise HTTPException(status_code=400, detail="File too large. Maximum size is 5MB.")

    if file.content_type == "application/pdf":
        content = extract_text_from_pdf(file_bytes)
        file_type = "pdf"
        if not content:
            raise HTTPException(status_code=400, detail="Could not extract text from PDF.")
    else:
        content = file_bytes.decode("utf-8")
        file_type = "txt"

    storage_path = f"{current_user.id}/{uuid.uuid4()}/{file.filename}"

    try:
        upload_to_supabase(file_bytes, storage_path, file.content_type)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File storage failed: {str(e)}")

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
        raise HTTPException(status_code=500, detail=f"Database save failed: {str(e)}")


# ─────────────────────────────────────────
# CONVERSATION ENDPOINTS
# ─────────────────────────────────────────

@app.post("/conversations", response_model=ConversationResponse, status_code=201)
async def create_conversation(
    conv: ConversationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Normalize — if document_id provided, include it in document_ids too
    doc_ids = list(conv.document_ids or [])
    if conv.document_id and conv.document_id not in doc_ids:
        doc_ids = [conv.document_id] + doc_ids

    # Verify all documents belong to this user and are processed
    for did in doc_ids:
        doc = db.query(Document).filter(
            Document.id == did,
            Document.user_id == current_user.id
        ).first()
        if not doc:
            raise HTTPException(status_code=404, detail=f"Document {did} not found")
        if not doc.is_processed:
            raise HTTPException(status_code=400, detail=f"Document '{doc.title}' is not processed yet")

    db_conv = Conversation(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        document_id=doc_ids[0] if doc_ids else None,
        document_ids=doc_ids,
        title=conv.title
    )
    db.add(db_conv)
    db.commit()
    db.refresh(db_conv)
    return db_conv

@app.get("/conversations", response_model=list[ConversationResponse])
async def list_conversations(
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(Conversation).filter(
        Conversation.user_id == current_user.id
    ).order_by(
        Conversation.updated_at.desc()
    ).offset(offset).limit(limit).all()

@app.get("/conversations/{conv_id}", response_model=ConversationResponse)
async def get_conversation(
    conv_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    conv = db.query(Conversation).filter(
        Conversation.id == conv_id,
        Conversation.user_id == current_user.id
    ).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conv

@app.delete("/conversations/{conv_id}")
async def delete_conversation(
    conv_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    conv = db.query(Conversation).filter(
        Conversation.id == conv_id,
        Conversation.user_id == current_user.id
    ).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    db.query(Message).filter(Message.conversation_id == conv_id).delete()
    db.delete(conv)
    db.commit()
    return {"message": "Conversation and all messages deleted", "id": conv_id}


# ─────────────────────────────────────────
# MESSAGE ENDPOINTS
# ─────────────────────────────────────────

@app.post("/conversations/{conv_id}/messages", response_model=MessageResponse, status_code=201)
async def add_message(
    conv_id: str,
    message: MessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    conv = db.query(Conversation).filter(
        Conversation.id == conv_id,
        Conversation.user_id == current_user.id
    ).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    db_message = Message(
        id=str(uuid.uuid4()),
        conversation_id=conv_id,
        role="user",
        content=message.content
    )
    db.add(db_message)
    conv.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_message)
    return db_message

@app.get("/conversations/{conv_id}/messages", response_model=list[MessageResponse])
async def get_messages(
    conv_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    conv = db.query(Conversation).filter(
        Conversation.id == conv_id,
        Conversation.user_id == current_user.id
    ).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    return db.query(Message).filter(
        Message.conversation_id == conv_id
    ).order_by(Message.created_at.asc()).all()


# ─────────────────────────────────────────
# AI ENDPOINTS
# ─────────────────────────────────────────

@app.post("/documents/{doc_id}/process")
async def process_document_endpoint(
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
    if not doc.content:
        raise HTTPException(status_code=400, detail="Document has no content to process")

    try:
        chunk_count = process_document(
            document_id=doc_id,
            user_id=current_user.id,
            content=doc.content,
            db=db
        )

        summary = generate_summary(doc.content)
        print(f"Generated summary: {summary[:100] if summary else 'NONE'}")

        doc.summary = summary
        doc.is_processed = True
        db.commit()

        return {
            "message": "Document processed successfully",
            "document_id": doc_id,
            "chunks_created": chunk_count,
            "summary": summary
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")


@app.post("/conversations/{conv_id}/chat", response_model=MessageResponse)
async def chat(
    conv_id: str,
    message: MessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    import uuid as uuid_lib

    conv = db.query(Conversation).filter(
        Conversation.id == conv_id,
        Conversation.user_id == current_user.id
    ).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    # Support both single and multi-doc conversations
    doc_ids = conv.document_ids if conv.document_ids else ([conv.document_id] if conv.document_id else [])
    if not doc_ids:
        raise HTTPException(status_code=400, detail="Conversation has no linked documents.")

    for did in doc_ids:
        d = db.query(Document).filter(Document.id == did).first()
        if not d or not d.is_processed:
            raise HTTPException(status_code=400, detail="Document not processed yet.")

    # Save user message
    user_message = Message(
        id=str(uuid_lib.uuid4()),
        conversation_id=conv_id,
        role="user",
        content=message.content
    )
    db.add(user_message)
    db.commit()

    # Generate AI response — single or multi doc
    try:
        if len(doc_ids) == 1:
            ai_response = generate_rag_response(
                question=message.content,
                document_id=doc_ids[0],
                user_id=current_user.id,
                conversation_id=conv_id,
                db=db
            )
        else:
            chunks = find_relevant_chunks_multi(
                question=message.content,
                user_id=current_user.id,
                document_ids=doc_ids,
                db=db
            )
            context = "\n\n---\n\n".join(chunks) if chunks else "No relevant context found."
            history = get_conversation_history(conv_id, db)
            messages_for_ai = build_messages(context, history, message.content)
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages_for_ai,
                max_tokens=1000,
                temperature=0.3
            )
            ai_response = response.choices[0].message.content

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI response failed: {str(e)}")

    # Save assistant message
    assistant_message = Message(
        id=str(uuid_lib.uuid4()),
        conversation_id=conv_id,
        role="assistant",
        content=ai_response
    )
    db.add(assistant_message)
    conv.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(assistant_message)
    return assistant_message


@app.post("/conversations/{conv_id}/chat/stream")
async def chat_stream(
    conv_id: str,
    message: MessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    import uuid as uuid_lib

    conv = db.query(Conversation).filter(
        Conversation.id == conv_id,
        Conversation.user_id == current_user.id
    ).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    # Support both single and multi-doc conversations
    doc_ids = conv.document_ids if conv.document_ids else ([conv.document_id] if conv.document_id else [])
    if not doc_ids:
        raise HTTPException(status_code=400, detail="Conversation has no linked documents.")

    for did in doc_ids:
        d = db.query(Document).filter(Document.id == did).first()
        if not d or not d.is_processed:
            raise HTTPException(status_code=400, detail="Document not processed yet.")

    # Save user message
    user_message = Message(
        id=str(uuid_lib.uuid4()),
        conversation_id=conv_id,
        role="user",
        content=message.content
    )
    db.add(user_message)
    db.commit()

    # Get relevant chunks — single or multi doc
    if len(doc_ids) == 1:
        chunks = find_relevant_chunks(
            question=message.content,
            document_id=doc_ids[0],
            user_id=current_user.id,
            db=db
        )
    else:
        chunks = find_relevant_chunks_multi(
            question=message.content,
            user_id=current_user.id,
            document_ids=doc_ids,
            db=db
        )

    context = "\n\n---\n\n".join(chunks) if chunks else "No relevant context found."
    history = get_conversation_history(conv_id, db)
    messages_for_ai = build_messages(context, history, message.content)
    assistant_id = str(uuid_lib.uuid4())

    async def generate():
        full_response = ""
        try:
            stream = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages_for_ai,
                max_tokens=1000,
                temperature=0.3,
                stream=True,
            )
            for chunk in stream:
                delta = chunk.choices[0].delta.content
                if delta:
                    full_response += delta
                    yield f"data: {json.dumps({'content': delta})}\n\n"

            # Save complete response after streaming finishes
            assistant_message = Message(
                id=assistant_id,
                conversation_id=conv_id,
                role="assistant",
                content=full_response
            )
            db.add(assistant_message)
            conv.updated_at = datetime.utcnow()
            db.commit()
            yield f"data: {json.dumps({'done': True, 'id': assistant_id})}\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"}
    )


@app.get("/documents/{doc_id}/chunks")
async def get_document_chunks(
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

    chunks = db.query(DocumentChunk).filter(
        DocumentChunk.document_id == doc_id
    ).order_by(DocumentChunk.chunk_index).all()

    return {
        "document_id": doc_id,
        "is_processed": doc.is_processed,
        "chunk_count": len(chunks),
        "chunks": [
            {
                "index": c.chunk_index,
                "preview": c.content[:200] + "..." if len(c.content) > 200 else c.content
            }
            for c in chunks
        ]
    }