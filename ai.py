"""
FILE: ai.py
ROLE: The AI layer. All OpenAI API calls and RAG logic live here.

WHAT THIS FILE DOES:
- Splits documents into overlapping chunks (semantic-aware)
- Creates embeddings using OpenAI text-embedding-3-small (1536 dimensions)
- Performs semantic search to find relevant chunks
- Re-ranks retrieved chunks by relevance score before sending to GPT
- Sends context + question + history to GPT-4o-mini
- Returns AI response grounded in document content

KEY CONCEPTS:
- Embedding: text → vector of 1536 numbers capturing semantic meaning
- Cosine similarity: how similar two vectors are (1.0 = identical)
- RAG: Retrieval Augmented Generation
- Chunking: split docs into focused pieces for better embeddings
- Re-ranking: score retrieved chunks against query, drop low-relevance ones
"""

from openai import OpenAI
from sqlalchemy.orm import Session
from sqlalchemy import text
from database import DocumentChunk, Message
from dotenv import load_dotenv
import uuid
import re
import os
import math

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

EMBEDDING_MODEL = "text-embedding-3-small"   # 1536 dimensions
CHAT_MODEL = "gpt-4o-mini"                   # fast and cheap


# ─────────────────────────────────────────
# CHUNKING — SEMANTIC AWARE
#
# Old approach: split every 400 words, fixed overlap.
# Problem: cuts mid-sentence, mid-paragraph, loses context.
#
# New approach:
# 1. Split on paragraph boundaries first (double newline)
# 2. If a paragraph is too long, split on sentence boundaries
# 3. Group small paragraphs together up to chunk_size words
# 4. Overlap by carrying the last `overlap` words of previous chunk
#
# Result: chunks respect natural document structure.
# ─────────────────────────────────────────

def split_into_sentences(text: str) -> list[str]:
    """Split text into sentences using punctuation boundaries."""
    sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z])', text.strip())
    return [s.strip() for s in sentences if s.strip()]


def chunk_text(content: str, chunk_size: int = 400, overlap: int = 50) -> list[str]:
    """
    Semantic-aware chunking:
    1. Split on paragraphs first
    2. Split long paragraphs on sentences
    3. Group into chunks up to chunk_size words
    4. Add sentence-level overlap between chunks
    """
    # Step 1 — Split into paragraphs
    paragraphs = [p.strip() for p in re.split(r'\n\s*\n', content) if p.strip()]

    if not paragraphs:
        return [content]

    # Step 2 — Break long paragraphs into sentences
    units = []
    for para in paragraphs:
        word_count = len(para.split())
        if word_count > chunk_size:
            sentences = split_into_sentences(para)
            units.extend(sentences)
        else:
            units.append(para)

    # Step 3 — Group units into chunks up to chunk_size words
    chunks = []
    current_words = []
    current_count = 0

    for unit in units:
        unit_words = unit.split()
        unit_count = len(unit_words)

        if current_count + unit_count > chunk_size and current_words:
            chunks.append(" ".join(current_words))
            # Step 4 — Overlap: carry last `overlap` words into next chunk
            overlap_words = current_words[-overlap:] if len(current_words) > overlap else current_words
            current_words = overlap_words + unit_words
            current_count = len(current_words)
        else:
            current_words.extend(unit_words)
            current_count += unit_count

    if current_words:
        chunks.append(" ".join(current_words))

    return chunks if chunks else [content]


# ─────────────────────────────────────────
# EMBEDDING
# ─────────────────────────────────────────

def get_embedding(text: str) -> list[float]:
    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=text.replace("\n", " ")
    )
    return response.data[0].embedding


# ─────────────────────────────────────────
# COSINE SIMILARITY
# Used for re-ranking: measures how similar two vectors are.
# Returns a float between -1 and 1 (higher = more similar).
# ─────────────────────────────────────────

def cosine_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    dot = sum(a * b for a, b in zip(vec_a, vec_b))
    mag_a = math.sqrt(sum(a * a for a in vec_a))
    mag_b = math.sqrt(sum(b * b for b in vec_b))
    if mag_a == 0 or mag_b == 0:
        return 0.0
    return dot / (mag_a * mag_b)


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
# SEMANTIC SEARCH + RE-RANKING
#
# Step 1: fetch 2x candidates from pgvector
# Step 2: re-score each with cosine similarity
# Step 3: sort by score, filter below MIN_SCORE
# Step 4: return top `limit` chunks
#
# Why re-rank? pgvector's <=> is approximate and fast
# but not perfectly ordered. Re-ranking with exact
# cosine similarity improves result quality.
# ─────────────────────────────────────────

def find_relevant_chunks(
    question: str,
    user_id: str,
    document_id: str,
    db: Session,
    limit: int = 5
) -> list[str]:
    question_embedding = get_embedding(question)

    # Fetch more candidates than needed for re-ranking
    fetch_limit = limit * 2

    results = db.execute(text("""
        SELECT content, embedding
        FROM document_chunks
        WHERE user_id = :user_id
        AND document_id = :document_id
        ORDER BY embedding <=> CAST(:embedding AS vector)
        LIMIT :limit
    """), {
        "user_id": user_id,
        "document_id": document_id,
        "embedding": str(question_embedding),
        "limit": fetch_limit
    }).fetchall()

    if not results:
        return []

    # Re-rank by exact cosine similarity
    scored = []
    for row in results:
        content = row[0]
        chunk_embedding_str = row[1]
        try:
            chunk_embedding = [float(x) for x in chunk_embedding_str.strip("[]").split(",")]
            score = cosine_similarity(question_embedding, chunk_embedding)
        except Exception:
            score = 0.0
        scored.append((content, score))

    scored.sort(key=lambda x: x[1], reverse=True)

    # Filter out low relevance chunks
    MIN_SCORE = 0.3
    top_chunks = [content for content, score in scored[:limit] if score >= MIN_SCORE]

    # Fallback: if filtering removed everything, return top results unfiltered
    if not top_chunks:
        top_chunks = [content for content, _ in scored[:limit]]

    return top_chunks


# ─────────────────────────────────────────
# MULTI-DOC SEARCH
# ─────────────────────────────────────────

def find_relevant_chunks_multi(
    question: str,
    user_id: str,
    document_ids: list[str],
    db: Session,
    limit_per_doc: int = 3
) -> list[str]:
    """Find relevant chunks across multiple documents."""
    all_chunks = []
    for document_id in document_ids:
        chunks = find_relevant_chunks(
            question=question,
            user_id=user_id,
            document_id=document_id,
            db=db,
            limit=limit_per_doc
        )
        all_chunks.extend(chunks)
    return all_chunks


# ─────────────────────────────────────────
# CONVERSATION HISTORY HELPER
# ─────────────────────────────────────────

def get_conversation_history(conversation_id: str, db: Session) -> list:
    """Returns last 10 messages in chronological order."""
    return db.query(Message).filter(
        Message.conversation_id == conversation_id
    ).order_by(
        Message.created_at.asc()
    ).limit(10).all()


# ─────────────────────────────────────────
# BUILD MESSAGES HELPER
# Shared prompt structure for regular + streaming
# ─────────────────────────────────────────

def build_messages(context: str, history: list, question: str) -> list:
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
    for msg in history:
        messages.append({"role": msg.role, "content": msg.content})
    messages.append({"role": "user", "content": question})
    return messages


# ─────────────────────────────────────────
# GENERATE RAG RESPONSE (non-streaming)
# ─────────────────────────────────────────

def generate_rag_response(
    question: str,
    document_id: str,
    user_id: str,
    conversation_id: str,
    db: Session
) -> str:
    relevant_chunks = find_relevant_chunks(
        question=question,
        user_id=user_id,
        document_id=document_id,
        db=db
    )

    if not relevant_chunks:
        return "I couldn't find relevant information in this document to answer your question."

    context = "\n\n---\n\n".join(relevant_chunks)
    history = get_conversation_history(conversation_id, db)
    messages = build_messages(context, history, question)

    response = client.chat.completions.create(
        model=CHAT_MODEL,
        messages=messages,
        max_tokens=1000,
        temperature=0.3
    )

    return response.choices[0].message.content


# ─────────────────────────────────────────
# GENERATE SUMMARY
# ─────────────────────────────────────────

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