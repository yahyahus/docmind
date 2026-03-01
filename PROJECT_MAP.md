# DocMind — Project Map

## What This Project Does
A full-stack AI platform where users upload documents (PDFs, text files)
and can chat with them using AI, search through them, and manage them.

## Live URLs
- **Frontend:** https://docmind-frontend-eight.vercel.app
- **Backend API:** https://docmind-api-5jka.onrender.com
- **API Docs:** https://docmind-api-5jka.onrender.com/docs

## Repositories
- **Backend:** https://github.com/yahyahus/docmind
- **Frontend:** https://github.com/yahyahus/docmind-frontend

## How a Request Flows Through the App
```
Browser (Vercel)
      ↓
Next.js page component
      ↓
lib/api.ts (axios + JWT header)
      ↓
FastAPI backend (Render)
      ↓
Auth check (auth.py)
      ↓
Business logic (main.py)
      ↓
Database + Storage + AI
      ↓
JSON response
      ↓
React state update → UI re-render
```

## Backend File Structure
```
docmind/
├── main.py         — All 21 API endpoints
├── database.py     — 5 table definitions + DB connection
├── auth.py         — JWT tokens + bcrypt hashing
├── ai.py           — RAG pipeline (chunk + embed + search + generate)
├── .env            — DATABASE_URL, SUPABASE_URL, SUPABASE_KEY, OPENAI_API_KEY
├── .gitignore
├── render.yaml     — Render deployment config
├── Procfile        — Production start command
├── requirements.txt
├── PROJECT_MAP.md
├── DECISIONS.md
├── PROGRESS.md
└── CS_CONCEPTS.md
```

## Frontend File Structure
```
docmind-frontend/
├── app/
│   ├── layout.tsx          — Root layout, DocMind title
│   ├── page.tsx            — Root redirect (token check)
│   ├── login/
│   │   └── page.tsx        — Login form
│   ├── register/
│   │   └── page.tsx        — Register form
│   ├── dashboard/
│   │   └── page.tsx        — Document management
│   └── chat/
│       └── [id]/
│           └── page.tsx    — AI chat interface
├── lib/
│   ├── api.ts              — Axios client + JWT interceptor
│   └── wakeup.ts           — Backend ping on app load
├── .env.local              — NEXT_PUBLIC_API_URL
└── package.json
```

## The Stack
### Backend
- FastAPI — Python web framework
- Uvicorn — ASGI server
- Pydantic — Request/response validation
- SQLAlchemy — ORM for PostgreSQL
- PostgreSQL (Supabase) — Cloud database
- pgvector — Vector similarity search
- Supabase Storage — File storage
- python-jose — JWT tokens
- passlib + bcrypt — Password hashing
- PyPDF2 — PDF text extraction
- OpenAI — Embeddings + chat completions
- Render — Backend hosting

### Frontend
- Next.js 14 (App Router) — React framework
- TypeScript — Type safety
- Tailwind CSS — Styling
- Axios — HTTP client
- js-cookie — Cookie management
- Vercel — Frontend hosting

## How the RAG Pipeline Works
```
User asks question
      ↓
Question embedded → 1536-dimension vector (OpenAI)
      ↓
pgvector <=> cosine distance search
      ↓
Top 5 most relevant chunks retrieved
      ↓
Context + conversation history + question → GPT-4o-mini
      ↓
AI answers grounded in document — no hallucination
      ↓
Response saved as "assistant" message
      ↓
Returned to frontend → displayed as chat bubble
```

## Database Schema (5 Tables)
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

## API Endpoints (21 Total)
| Method | Path | Description | Auth |
|--------|------|-------------|------|
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

## Frontend Pages
| Route | Description |
|-------|-------------|
| / | Redirects to dashboard or login |
| /login | Email + password login |
| /register | Account creation |
| /dashboard | Document list, upload, process, search, delete |
| /chat/[id] | AI chat interface with typing indicator |

## Where Do I Look When...
| Situation | File |
|-----------|------|
| Adding API endpoint | main.py |
| Changing DB table | database.py |
| Auth bug | auth.py |
| AI not working | ai.py |
| Frontend page bug | app/{page}/page.tsx |
| API call failing | lib/api.ts |
| Secrets | .env / .env.local |
| Why a tool was chosen | DECISIONS.md |
| Daily progress | PROGRESS.md |
| CS concepts | CS_CONCEPTS.md |
| 401 error | auth.py → get_current_user() |
| 404 error | main.py → check route order |
| 422 error | Check JSON — strings need quotes |
| 500 error | Read terminal output first |
| AI hallucinating | ai.py → check system prompt |
| Wrong chunks retrieved | ai.py → find_relevant_chunks() |
| Frontend not updating | Check Pydantic response model |
| Page reload on error | Check axios interceptor pathname |

## Storage Bucket Structure
```
documents/
└── {user_id}/
    └── {uuid}/
        └── {filename}
```

## Keyword Search vs Semantic Search
- **Keyword (ILIKE):** matches exact words — "python" finds "python"
- **Semantic (pgvector):** matches meaning — "weaknesses" finds "limitations"

## Critical Route Order Rule (FastAPI)
```
/documents/search   ← specific, must be FIRST
/documents/upload   ← specific, must be FIRST
/documents/{doc_id} ← dynamic, must be LAST
```

## Environment Variables
| Variable | Where | Purpose |
|----------|-------|---------|
| DATABASE_URL | Backend .env + Render | PostgreSQL connection |
| SUPABASE_URL | Backend .env + Render | Supabase project URL |
| SUPABASE_KEY | Backend .env + Render | Supabase anon key |
| OPENAI_API_KEY | Backend .env + Render | OpenAI API access |
| NEXT_PUBLIC_API_URL | Frontend .env.local + Vercel | Backend URL |
