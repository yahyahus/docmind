# DocMind — Project Map

## What This Project Does
A full-stack AI platform where users upload documents (PDFs, text files)
and can chat with them, get summaries, and search through them using AI.

## How a Request Flows Through the App
Browser/Client → Uvicorn → FastAPI → Auth check → Your function → Database + Storage + AI → Response

## File Structure & Purpose

### Current Files
- `main.py` — All API endpoints (15+ endpoints)
- `database.py` — All 5 table definitions + DB connection
- `auth.py` — JWT tokens + bcrypt password hashing
- `ai.py` — RAG pipeline (chunking + embeddings + chat)
- `.env` — DATABASE_URL, SUPABASE_URL, SUPABASE_KEY, OPENAI_API_KEY
- `.gitignore` — Ignores venv/, .env, __pycache__/
- `render.yaml` — Render deployment config
- `Procfile` — Production server start command
- `requirements.txt` — All installed packages
- `PROJECT_MAP.md` — This file
- `DECISIONS.md` — Why each tool was chosen
- `PROGRESS.md` — Daily log + roadblocks + skills
- `CS_CONCEPTS.md` — Academic CS concepts applied
- `test_small.txt` — AI fundamentals test document (~250 words, 1 chunk)
- `test_medium.txt` — Software engineering test document (~600 words, 2 chunks)
- `test_large.txt` — Computer networks test document (~1000 words, 3 chunks)

### Files Coming Next (Week 4)
- `frontend/` — Next.js app directory

## The Stack
- FastAPI — Python web framework
- Uvicorn — ASGI server
- Pydantic — Request/response validation
- SQLAlchemy — ORM for PostgreSQL
- PostgreSQL (Supabase) — Cloud database
- pgvector — Vector similarity search extension
- Supabase Storage — File storage
- python-jose — JWT tokens
- passlib + bcrypt — Password hashing
- PyPDF2 — PDF text extraction
- OpenAI — Embeddings + chat completions
- Render — Backend hosting
- Next.js + Vercel — Frontend (Week 4)

## How the RAG Pipeline Works
```
User asks question
      ↓
Question embedded → 1536-dimension vector
      ↓
pgvector finds chunks with closest cosine distance
      ↓
Top 5 relevant chunks retrieved as context
      ↓
Context + conversation history + question → GPT-4o-mini
      ↓
AI answers grounded in document — no hallucination
      ↓
Response saved as "assistant" message
      ↓
Returned to user
```

## Keyword Search vs Semantic Search
- Keyword (ILIKE): matches exact words — "python" finds "python"
- Semantic (pgvector): matches meaning — "weaknesses" finds "limitations"

## Critical Route Order Rule
Specific routes before dynamic routes:
/documents/search   ← first
/documents/{doc_id} ← second
/documents/upload   ← also before /{doc_id}

## Database Schema (All 5 Tables)
```
users:
  id, email, hashed_password, is_active, created_at

documents:
  id, user_id(FK), title, content, tags,
  file_path, file_type, is_processed, created_at, updated_at

document_chunks:
  id, document_id(FK), user_id(FK), content,
  chunk_index, embedding(vector 1536), created_at

conversations:
  id, user_id(FK), document_id(FK nullable),
  title, created_at, updated_at

messages:
  id, conversation_id(FK), role, content, created_at
```

## API Endpoints (Current — 15 Total)
| Method | Path | What it does | Auth |
|--------|------|--------------|------|
| GET | / | Root check | No |
| GET | /health | Server status | No |
| POST | /auth/register | Create account | No |
| POST | /auth/login | Login → JWT | No |
| GET | /auth/me | Current user | Yes |
| POST | /documents | Create document | Yes |
| GET | /documents | List documents | Yes |
| GET | /documents/search | Keyword search | Yes |
| GET | /documents/{id} | Get document | Yes |
| PATCH | /documents/{id} | Update document | Yes |
| DELETE | /documents/{id} | Delete document | Yes |
| POST | /documents/upload | Upload PDF/TXT | Yes |
| POST | /documents/{id}/process | Chunk + embed | Yes |
| GET | /documents/{id}/chunks | View chunks | Yes |
| POST | /conversations | Create conversation | Yes |
| GET | /conversations | List conversations | Yes |
| GET | /conversations/{id} | Get conversation | Yes |
| DELETE | /conversations/{id} | Delete + messages | Yes |
| POST | /conversations/{id}/messages | Add message | Yes |
| GET | /conversations/{id}/messages | Get history | Yes |
| POST | /conversations/{id}/chat | AI chat (RAG) | Yes |

## Environments
| Environment | URL | Purpose |
|-------------|-----|---------|
| Local | http://localhost:8000 | Development |
| Production | https://YOUR-APP.onrender.com | Live API |

## Storage Bucket Structure
```
documents/
└── {user_id}/
    └── {uuid}/
        └── {filename}
```

## Where Do I Look When...
| Situation | File |
|-----------|------|
| Adding endpoint | main.py |
| Changing data structure | database.py |
| Auth bug | auth.py |
| AI not working | ai.py |
| Secrets | .env |
| Why a tool was chosen | DECISIONS.md |
| Daily progress | PROGRESS.md |
| CS concepts | CS_CONCEPTS.md |
| 401 error | auth.py → get_current_user() |
| 404 error | main.py → check route order |
| 422 error | Check JSON — strings need quotes |
| 500 error | Read terminal output first |
| AI hallucinating | ai.py → check system prompt rules |
| Wrong chunks retrieved | ai.py → find_relevant_chunks() |

## Current State
Week 1 — Backend complete (12 endpoints, auth, file upload, search, deploy)
Week 2 — Conversations + messages complete (6 more endpoints)
Week 3 — AI complete (RAG pipeline, embeddings, semantic search, GPT-4o-mini)
Week 4 — Next.js frontend starting next
