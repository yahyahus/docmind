"""
FILE: ai.py
ROLE: The AI layer. All OpenAI API calls and RAG logic live here.

WHAT THIS FILE DOES:
- Splits documents into overlapping chunks
- Creates embeddings using OpenAI text-embedding-ada-002 (1536 dimensions)
- Performs semantic search to find relevant chunks
- Sends context + question + history to GPT-4o-mini
- Returns AI response grounded in document content

KEY CONCEPTS:
- Embedding: text → vector of 1536 numbers capturing semantic meaning
- Cosine similarity: how similar two vectors are (1.0 = identical)
- RAG: Retrieval Augmented Generation
- Chunking: split docs into focused pieces for better embeddings
"""

from openai import OpenAI
from sqlalchemy.orm import Session
from sqlalchemy import text
from database import DocumentChunk, Message
from dotenv import load_dotenv
import uuid
import os

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

EMBEDDING_MODEL = "text-embedding-3-small"   # 1536 dimensions
CHAT_MODEL = "gpt-4o-mini"                   # fast and cheap


# ─────────────────────────────────────────
# CHUNKING
# ─────────────────────────────────────────

def chunk_text(text: str, chunk_size: int = 400, overlap: int = 50) -> list[str]:
    words = text.split()

    if len(words) <= chunk_size:
        return [text]

    chunks = []
    start = 0
    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunk = " ".join(words[start:end])
        chunks.append(chunk)
        start += chunk_size - overlap
        if start >= len(words):
            break

    return chunks


# ─────────────────────────────────────────
# EMBEDDING
# OpenAI ada-002 produces 1536-dimensional vectors.
# Same model used for both documents and queries.
# ─────────────────────────────────────────

def get_embedding(text: str) -> list[float]:
    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=text.replace("\n", " ")
    )
    return response.data[0].embedding


# ─────────────────────────────────────────
# PROCESS DOCUMENT
# ─────────────────────────────────────────

def process_document(
    document_id: str,
    user_id: str,
    content: str,
    db: Session
) -> int:
    # Clean up existing chunks
    db.query(DocumentChunk).filter(
        DocumentChunk.document_id == document_id
    ).delete()
    db.commit()

    chunks = chunk_text(content)

    for i, chunk_content in enumerate(chunks):
        embedding = get_embedding(chunk_content)

        chunk = DocumentChunk(
            id=str(uuid.uuid4()),
            document_id=document_id,
            user_id=user_id,
            content=chunk_content,
            chunk_index=i,
            embedding=embedding
        )
        db.add(chunk)

    db.commit()
    return len(chunks)


# ─────────────────────────────────────────
# SEMANTIC SEARCH
# ─────────────────────────────────────────

def find_relevant_chunks(
    question: str,
    user_id: str,
    document_id: str,
    db: Session,
    limit: int = 5
) -> list[str]:
    question_embedding = get_embedding(question)

    results = db.execute(text("""
        SELECT content
        FROM document_chunks
        WHERE user_id = :user_id
        AND document_id = :document_id
        ORDER BY embedding <=> CAST(:embedding AS vector)
        LIMIT :limit
    """), {
        "user_id": user_id,
        "document_id": document_id,
        "embedding": str(question_embedding),
        "limit": limit
    }).fetchall()

    return [row[0] for row in results]


# ─────────────────────────────────────────
# GENERATE RAG RESPONSE
# ─────────────────────────────────────────

def generate_rag_response(
    question: str,
    document_id: str,
    user_id: str,
    conversation_id: str,
    db: Session
) -> str:
    # Step 1 — Retrieve relevant chunks
    relevant_chunks = find_relevant_chunks(
        question=question,
        user_id=user_id,
        document_id=document_id,
        db=db
    )

    if not relevant_chunks:
        return "I couldn't find relevant information in this document to answer your question."

    context = "\n\n---\n\n".join(relevant_chunks)

    # Step 2 — Get conversation history
    history = db.query(Message).filter(
        Message.conversation_id == conversation_id
    ).order_by(
        Message.created_at.asc()
    ).limit(10).all()

    # Step 3 — Build messages array for OpenAI
    messages = [
        {
            "role": "system",
            "content": f"""You are a helpful document assistant for DocMind.
Answer questions about the document provided.

RULES:
- Answer ONLY based on the context below
- If the answer is not in the context, say:
  "I don't have enough information in this document to answer that"
- Be concise and clear
- Quote relevant parts when helpful

DOCUMENT CONTEXT:
{context}"""
        }
    ]

    # Add conversation history
    for msg in history:
        messages.append({
            "role": msg.role,
            "content": msg.content
        })

    # Add current question
    messages.append({
        "role": "user",
        "content": question
    })

    # Step 4 — Call OpenAI
    response = client.chat.completions.create(
        model=CHAT_MODEL,
        messages=messages,
        max_tokens=1000,
        temperature=0.3
    )

    return response.choices[0].message.content

def generate_summary(content: str) -> str:
    """
    Generates a concise 3-sentence summary of the document.
    Called automatically after processing.
    """
    prompt = f"""Summarize the following document in exactly 3 sentences.
Be specific about the main topics covered. Be concise.

Document:
{content[:3000]}

Summary:"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=200,
        temperature=0.3
    )
    return response.choices[0].message.content.strip()