# DocMind — Project Map

## What This Project Does
A full-stack AI platform where users upload documents (PDFs, text files)
and can chat with them, get summaries, and search through them using AI.

## How a Request Flows Through the App
Browser/Client → Uvicorn (server) → FastAPI (router) → Auth check → Your function → Database + Storage → Response

## File Structure & Purpose

### Current Files
- `main.py` — All API endpoints. Auth + document CRUD + file upload + search.
- `database.py` — Database connection + User and Document table definitions.
- `auth.py` — Password hashing (bcrypt), JWT creation, token decoding,
              get_current_user dependency that protects endpoints.
- `.env` — Supabase DB URL + Supabase API credentials + SECRET_KEY.
- `.gitignore` — Ignores venv/, .env, __pycache__/
- `venv/` — Isolated Python environment. Never touch manually.
- `PROJECT_MAP.md` — This file.
- `DECISIONS.md` — Why each tool and pattern was chosen.
- `PROGRESS.md` — Daily log, roadblocks, skills unlocked.
- `test_document.txt` — Test file for upload testing.

### Files Coming Next
- `requirements.txt` — List of all packages (needed for deployment)

## The Stack & Why
- FastAPI — Python web framework. Handles routing, validation, auto docs.
- Uvicorn — The actual server that listens for requests.
- Pydantic — Validates data shapes. Turns Python objects into JSON.
- SQLAlchemy — ORM. Talk to PostgreSQL using Python classes.
- PostgreSQL (Supabase) — Permanent cloud database. Free tier.
- Supabase Storage — File storage for uploaded PDFs and TXT files.
- python-jose — Creates and decodes JWT tokens.
- passlib + bcrypt — Hashes passwords securely. Never stores plain text.
- PyPDF2 — Extracts text from uploaded PDF files.
- Thunder Client — VS Code extension for testing API endpoints.
- OpenAI API — The AI brain (Week 3).
- Next.js — The frontend (Week 4).

## How File Upload Works (The Full Flow)
1. User sends PDF or TXT to POST /documents/upload
2. FastAPI reads raw file bytes into memory
3. Text extracted (PyPDF2 for PDFs, decode() for TXT)
4. File bytes uploaded to Supabase Storage bucket "documents"
   Path: {user_id}/{uuid}/{filename}
5. Document metadata + extracted text saved to PostgreSQL
6. Response returned with full document object

## How Search Works
1. User sends GET /documents/search?q=keyword
2. PostgreSQL ILIKE matches keyword against title, content, tags
3. ILIKE = case-insensitive (finds "Python", "PYTHON", "python")
4. Results filtered to current user's documents only
5. Ordered by most recently updated first

## Critical Route Order Rule
Specific routes MUST come before dynamic routes.
/documents/search   ← specific, must be first
/documents/{doc_id} ← dynamic, must be after
If reversed, FastAPI treats "search" as a document ID → 404 every time.

## API Endpoints (Current)
| Method | Path                  | What it does                   | Auth Required |
|--------|-----------------------|--------------------------------|---------------|
| GET    | /                     | Root check                     | No            |
| GET    | /health               | Server status + counts         | No            |
| POST   | /auth/register        | Create new user account        | No            |
| POST   | /auth/login           | Login, returns JWT tokens      | No            |
| GET    | /auth/me              | Get current logged-in user     | Yes           |
| POST   | /documents            | Create document (raw text)     | Yes           |
| GET    | /documents            | List your documents            | Yes           |
| GET    | /documents/search     | Search documents by keyword    | Yes           |
| GET    | /documents/{id}       | Get one document               | Yes           |
| PATCH  | /documents/{id}       | Update a document              | Yes           |
| DELETE | /documents/{id}       | Delete a document              | Yes           |
| POST   | /documents/upload     | Upload PDF or TXT file         | Yes           |

## Database (Supabase PostgreSQL)
- Host: Supabase pooler (port 6543)
- Tables: users, documents
- documents.user_id is a foreign key → users.id
- Every document is scoped to its owner

## Database Schema
users:
  id, email, hashed_password, is_active, created_at

documents:
  id, user_id (FK→users), title, content, tags,
  file_path, file_type, created_at, updated_at

## Storage Bucket Structure
documents/
└── {user_id}/
    └── {uuid}/
        └── {filename}

## Testing Tools
- Swagger UI: http://localhost:8000/docs (use for file upload + general testing)
- Thunder Client: VS Code extension (use for auth testing)

## Where Do I Look When...
| Situation | File to open |
|-----------|-------------|
| Adding a new API endpoint | main.py |
| Changing what data is stored | database.py |
| Fixing a login/token bug | auth.py |
| Changing database credentials | .env |
| Understanding why a tool was chosen | DECISIONS.md |
| Remembering the project structure | PROJECT_MAP.md |
| Tracking daily progress | PROGRESS.md |
| A request returns 401 | auth.py → get_current_user() |
| A request returns 404 | main.py → check route order first |
| A request returns 500 | Read terminal error output first |
| Adding a new database table | database.py → add a new class |
| Changing response shape | main.py → update Pydantic response model |
| Search returning 404 | main.py → check /search is above /{doc_id} |

## Current State
Week 1, Day 1 — Server running locally. 2 basic endpoints.
Week 1, Day 1 — 7 CRUD endpoints built. In-memory storage. All tested in Swagger.
Week 1, Day 2 — PostgreSQL connected via Supabase. Data persists. Documents table live.
Week 1, Day 3 — JWT auth complete. Register, login, protected routes all working.
Week 1, Day 3 — File upload complete. PDF + TXT → Storage + PostgreSQL working.
Week 1, Day 4 — Search endpoint complete. Keyword search across title, content, tags.

## Known Limitations Right Now
- Keyword search only — semantic/AI search comes in Week 3
- No AI integration yet
- No refresh token endpoint yet
- No frontend yet
- Not deployed yet (coming next)
