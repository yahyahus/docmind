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

## How Streaming Flows (Week 5)
```
User sends message
      ↓
POST /conversations/{id}/chat/stream
      ↓
Backend saves user message to DB
      ↓
Fetches relevant chunks (pgvector)
      ↓
Opens OpenAI stream
      ↓
Yields SSE chunks: data: {"content": "word "}\n\n
      ↓
Browser ReadableStream reader receives tokens
      ↓
React state updates on each token → live text appears
      ↓
On done event: full response saved to DB
```

## Backend File Structure
```
docmind/
├── main.py         — All API endpoints (21+)
├── database.py     — 7 table definitions + DB connection
├── auth.py         — JWT tokens + bcrypt hashing
├── ai.py           — RAG pipeline (chunk + embed + search + re-rank + generate)
├── .env            — DATABASE_URL, SUPABASE_URL, SUPABASE_KEY, OPENAI_API_KEY,
│                     RESEND_API_KEY, GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, FRONTEND_URL
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
│   ├── layout.tsx              — Root layout, GoogleOAuthProvider wrapper
│   ├── page.tsx                — Root redirect (token check)
│   ├── globals.css             — CSS variables, DM Mono/Sans fonts, base styles
│   ├── login/
│   │   └── page.tsx            — Email login + Google OAuth button
│   ├── register/
│   │   └── page.tsx            — Register form + Google OAuth button
│   ├── forgot-password/
│   │   └── page.tsx            — Email input → send reset link
│   ├── reset-password/
│   │   └── page.tsx            — New password form (reads ?token= from URL)
│   ├── dashboard/
│   │   └── page.tsx            — Doc list, upload, tags, multi-doc select, export
│   ├── chat/
│   │   └── [id]/
│   │       └── page.tsx        — Streaming chat, share modal, export dropdown
│   ├── profile/
│   │   └── page.tsx            — User stats + change password
│   └── share/
│       └── [token]/
│           └── page.tsx        — Public read-only conversation view
├── lib/
│   ├── api.ts                  — Axios client + JWT interceptor
│   └── wakeup.ts               — Backend ping on app load
├── .env.local                  — NEXT_PUBLIC_API_URL, NEXT_PUBLIC_GOOGLE_CLIENT_ID
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
- Resend — Transactional email (password reset)
- google-auth — Google OAuth token verification
- Render — Backend hosting

### Frontend
- Next.js 14 (App Router) — React framework
- TypeScript — Type safety
- Tailwind CSS — Styling
- Axios — HTTP client
- js-cookie — Cookie management
- @react-oauth/google — Google Sign-In button
- jsPDF — Client-side PDF generation (chat export)
- Vercel — Frontend hosting

## How the RAG Pipeline Works
```
User asks question
      ↓
Question embedded → 1536-dimension vector (OpenAI)
      ↓
pgvector <=> cosine distance ANN search (fetches 2x candidates)
      ↓
Re-rank: exact cosine similarity computed in Python
      ↓
Filter: drop chunks below 0.3 threshold (fallback: keep top if all below)
      ↓
Top chunks passed as context to GPT-4o-mini
      ↓
AI answers grounded in document — no hallucination
      ↓
Response streamed token by token to browser (SSE)
      ↓
Full response saved to DB after stream ends
```

## Database Schema (7 Tables)
```
users:
  id, email, hashed_password, is_active, created_at

documents:
  id, user_id(FK), title, content, tags[],
  file_path, file_type, is_processed, summary, created_at, updated_at

document_chunks:
  id, document_id(FK), user_id(FK), content,
  chunk_index, embedding(vector 1536), created_at

conversations:
  id, user_id(FK), document_id(FK nullable),
  document_ids(TEXT[]), title, created_at, updated_at

messages:
  id, conversation_id(FK), role, content, created_at

password_reset_tokens:
  id, user_id(FK), token(UNIQUE), expires_at, used, created_at

share_links:
  id, conversation_id(FK ON DELETE CASCADE), token(UNIQUE), created_at
```

## API Endpoints (Full Reference)
| Method | Path | Description | Auth |
|--------|------|-------------|------|
| GET | / | Root check | No |
| GET | /health | Server status + counts | No |
| POST | /auth/register | Create account | No |
| POST | /auth/login | Login → JWT tokens | No |
| GET | /auth/me | Current user | Yes |
| POST | /auth/change-password | Change password | Yes |
| POST | /auth/forgot-password | Send reset email | No |
| POST | /auth/reset-password | Reset with token | No |
| GET | /auth/stats | Doc/conv/chunk counts | Yes |
| POST | /auth/google | Google OAuth sign-in | No |
| POST | /documents | Create document | Yes |
| GET | /documents | List documents (limit=50) | Yes |
| GET | /documents/search | Keyword search | Yes |
| GET | /documents/{id} | Get document | Yes |
| PATCH | /documents/{id} | Rename / update | Yes |
| PATCH | /documents/{id}/tags | Update tags (normalized) | Yes |
| DELETE | /documents/{id} | Delete + cascade | Yes |
| POST | /documents/upload | Upload PDF/TXT | Yes |
| POST | /documents/{id}/process | Chunk + embed + summarize | Yes |
| GET | /documents/{id}/chunks | Debug: view chunks | Yes |
| POST | /conversations | Create (single or multi-doc) | Yes |
| GET | /conversations | List conversations | Yes |
| GET | /conversations/{id} | Get conversation | Yes |
| DELETE | /conversations/{id} | Delete + messages | Yes |
| POST | /conversations/{id}/messages | Add message (no AI) | Yes |
| GET | /conversations/{id}/messages | Get history | Yes |
| POST | /conversations/{id}/chat | AI chat (non-streaming) | Yes |
| POST | /conversations/{id}/chat/stream | AI chat (SSE streaming) | Yes |
| GET | /conversations/{id}/export | Export as markdown | Yes |
| POST | /conversations/{id}/share | Create/get share link | Yes |
| DELETE | /conversations/{id}/share | Revoke share link | Yes |
| GET | /share/{token} | Public read-only view | No |

## Frontend Pages
| Route | Description |
|-------|-------------|
| / | Redirects to dashboard or login |
| /login | Email + password login + Google OAuth |
| /register | Account creation + Google OAuth |
| /forgot-password | Send reset email |
| /reset-password | New password form (reads ?token=) |
| /dashboard | Document list, upload, process, tags, multi-doc select |
| /chat/[id] | Streaming AI chat, export dropdown, share modal |
| /profile | User stats + change password |
| /share/[token] | Public read-only conversation (no auth) |

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
| Email not sending | Check RESEND_API_KEY + "to" as list |
| Google login failing | Check GOOGLE_CLIENT_ID on Render + Vercel |
| Summary not saving | Check SQLAlchemy model has summary column |
| Streaming broken | Chunks are list[str] — no .content access |

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
/documents/search       ← specific, must be FIRST
/documents/upload       ← specific, must be FIRST
/documents/{doc_id}     ← dynamic, must be LAST
```

## Environment Variables
| Variable | Where | Purpose |
|----------|-------|---------|
| DATABASE_URL | Backend .env + Render | PostgreSQL connection |
| SUPABASE_URL | Backend .env + Render | Supabase project URL |
| SUPABASE_KEY | Backend .env + Render | Supabase anon key |
| OPENAI_API_KEY | Backend .env + Render | OpenAI API access |
| RESEND_API_KEY | Backend .env + Render | Transactional email |
| GOOGLE_CLIENT_ID | Backend .env + Render | Google OAuth verify |
| GOOGLE_CLIENT_SECRET | Backend .env + Render | Google OAuth verify |
| FRONTEND_URL | Backend .env + Render | Reset email link base URL |
| NEXT_PUBLIC_API_URL | Frontend .env.local + Vercel | Backend URL |
| NEXT_PUBLIC_GOOGLE_CLIENT_ID | Frontend .env.local + Vercel | Google Sign-In button |

## Key Dependency Versions (Pinned)
```
bcrypt==4.0.1               — passlib compatibility
resend==2.23.0              — 0.28.0 doesn't exist; v2 requires "to" as list
google-auth==2.38.0         — 2.40.0 has issues
google-auth-oauthlib==1.2.1
cachetools==5.5.2           — google-auth conflicts with 6.x
pgvector==0.4.2
```