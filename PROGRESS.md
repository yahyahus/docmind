# DocMind — Progress Tracker

## Timeline Overview
| Week | Focus | Status |
|------|-------|--------|
| Week 1 | Backend (API + DB + Auth + File Upload + Search + Deploy) | 🔄 In Progress |
| Week 2 | Schema hardening + Conversations + Auth polish | ⏳ Pending |
| Week 3 | AI Integration (RAG pipeline) | ⏳ Pending |
| Week 4 | Next.js Frontend | ⏳ Pending |
| Week 5 | Deployment + Polish | ⏳ Pending |
| Week 6 | Resume prep + Second project | ⏳ Pending |

---

## Daily Log

### Day 1
**Status:** ✅ Complete
**What was built:**
- Python environment setup on Windows
- FastAPI server running locally
- 7 CRUD endpoints for documents (in-memory storage)
- Swagger UI working at /docs
- PROJECT_MAP.md, DECISIONS.md, PROGRESS.md created
- File headers added to all code files

**Time spent:** ~3-4 hrs
**Roadblocks:** None

---

### Day 2
**Status:** ✅ Complete
**What was built:**
- PostgreSQL connected via Supabase
- SQLAlchemy ORM configured
- Documents table created automatically on startup
- Data persists across server restarts

**Time spent:** ~4-5 hrs
**Roadblocks:**
| # | Roadblock | Cause | Fix |
|---|-----------|-------|-----|
| 1 | Railway "Team not found" | Railway account bug | Switched to Supabase |
| 2 | DATABASE_URL showing None | Hidden characters in .env on Windows | Recreated .env via terminal echo |
| 3 | Connection timeout port 5432 | Windows firewall blocking direct PostgreSQL | Switched to Supabase pooler port 6543 |
| 4 | Password authentication failed | Wrong password in connection string | Reset Supabase DB password (no special chars) |

---

### Day 3
**Status:** ✅ Complete
**What was built:**
- JWT authentication system from scratch
- User registration + login endpoints
- Password hashing with bcrypt
- Protected routes (all document endpoints require auth)
- User-scoped documents (users only see their own data)
- File upload endpoint (PDF + TXT)
- Supabase Storage bucket connected
- Text extraction from PDFs with PyPDF2

**Time spent:** ~5-6 hrs
**Roadblocks:**
| # | Roadblock | Cause | Fix |
|---|-----------|-------|-----|
| 1 | bcrypt 500 error | passlib incompatible with new bcrypt | Pinned bcrypt==4.0.1 |
| 2 | Swagger auth broken | bearerAuth missing from OpenAPI spec | Added custom_openapi() |
| 3 | Windows multiline terminal failed | CMD doesn't support multiline -c | Used .py file instead |
| 4 | File upload 403 error | Supabase Storage RLS blocking uploads | Added permissive storage policy via SQL |
| 5 | Database save failed | documents table missing columns | Added columns via ALTER TABLE |
| 6 | Thunder Client file upload paywalled | Feature moved to paid tier | Switched to Swagger |

---

### Day 4
**Status:** ✅ Complete
**What was built:**
- Search endpoint across title, content, and tags
- Case-insensitive keyword search using PostgreSQL ILIKE
- Results filtered to current user only
- Results ordered by most recently updated
- Learned critical route ordering rule (specific before dynamic)

**Time spent:** ~1-2 hrs
**Roadblocks:**
| # | Roadblock | Cause | Fix |
|---|-----------|-------|-----|
| 1 | Search returning 404 | /search route placed after /{doc_id} | Moved /search above /{doc_id} in main.py |

**Key lesson learned:**
Specific routes (/documents/search) must always come before
dynamic routes (/documents/{doc_id}) in FastAPI. FastAPI matches
top to bottom — first match wins.

---

## Roadblocks Master Log
| Day | Roadblock | Time Lost | Fix |
|-----|-----------|-----------|-----|
| 2 | Railway team not found | 15 min | Switched to Supabase |
| 2 | .env hidden characters | 20 min | Recreated via terminal |
| 2 | Port 5432 blocked | 30 min | Used pooler port 6543 |
| 2 | Wrong DB password | 10 min | Reset without special chars |
| 3 | bcrypt incompatibility | 15 min | Pinned bcrypt==4.0.1 |
| 3 | Swagger auth broken | 25 min | Custom OpenAPI schema |
| 3 | Windows terminal multiline | 10 min | Used .py file instead |
| 3 | Storage 403 RLS error | 20 min | Added SQL storage policy |
| 3 | Missing DB columns | 30 min | ALTER TABLE in SQL Editor |
| 3 | Thunder Client paywall | 10 min | Switched to Swagger |
| 4 | Search returning 404 | 5 min | Fixed route order |

---

## Architecture Understanding Log
| Concept | Understood On |
|---------|--------------|
| Request lifecycle (browser → uvicorn → FastAPI → DB → response) | Day 1 |
| Pydantic validation and why it matters | Day 1 |
| Why async def is used everywhere | Day 1 |
| SQLAlchemy ORM vs raw SQL | Day 2 |
| Why .env exists and why it's gitignored | Day 2 |
| JWT token structure and lifecycle | Day 3 |
| Why bcrypt over MD5/SHA256 | Day 3 |
| Dependency injection with Depends() | Day 3 |
| Why two storage systems (DB + bucket) | Day 3 |
| Storage path structure and why user_id not username | Day 3 |
| SQLAlchemy create_all never alters existing tables | Day 3 |
| Separation of concerns across files | Day 3 |
| FastAPI route ordering (specific before dynamic) | Day 4 |
| PostgreSQL ILIKE for case-insensitive search | Day 4 |

---

## Skills Unlocked
- [x] FastAPI server setup
- [x] Pydantic models (request/response validation)
- [x] REST API design (CRUD endpoints)
- [x] PostgreSQL connection via SQLAlchemy ORM
- [x] Cloud database setup (Supabase)
- [x] Environment variables (.env pattern)
- [x] JWT authentication from scratch
- [x] Password hashing with bcrypt
- [x] Dependency injection pattern (Depends())
- [x] API testing with Thunder Client + Swagger
- [x] File upload handling (PDF + TXT)
- [x] Cloud file storage (Supabase Storage)
- [x] PDF text extraction (PyPDF2)
- [x] Database schema migrations (ALTER TABLE)
- [x] Keyword search with PostgreSQL ILIKE
- [x] FastAPI route ordering rules
- [ ] Semantic search with pgvector (Week 3)
- [ ] AI integration (RAG pipeline) (Week 3)
- [ ] Streaming AI responses (Week 3)
- [ ] Next.js frontend (Week 4)
- [ ] Production deployment (coming next)

---

## Resume Bullets Earned So Far
- "Built RESTful API with FastAPI and PostgreSQL with 12+ endpoints and JWT authentication"
- "Implemented secure user authentication with bcrypt password hashing and JWT token rotation"
- "Designed relational database schema with user-scoped data access using SQLAlchemy ORM"
- "Built file upload pipeline handling PDF and TXT files with text extraction and cloud storage"
- "Integrated Supabase Storage for file management with organized per-user folder structure"
- "Implemented full-text keyword search across documents using PostgreSQL ILIKE queries"

---

## What's Next (Day 5)
- [ ] Generate requirements.txt
- [ ] Deploy backend to Render (free tier)
- [ ] Get a live public URL
- [ ] Test everything on production

---

## Notes to Future Self
- Always recreate .env via terminal on Windows to avoid hidden characters
- Use port 6543 (pooler) not 5432 for Supabase on Windows
- Use Thunder Client for auth testing, Swagger for file upload testing
- bcrypt must stay at 4.0.1 — do not upgrade
- SQLAlchemy create_all NEVER alters existing tables — use ALTER TABLE in SQL Editor
- Always check terminal error first before reading Swagger error response
- Specific routes always before dynamic routes in FastAPI (/search before /{id})
