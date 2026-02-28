# DocMind — Progress Tracker

## Timeline Overview
| Week | Focus | Status |
|------|-------|--------|
| Week 1 | Backend (API + DB + Auth + File Upload + Search + Deploy) | ✅ Complete |
| Week 2 | Conversations + Messages | ✅ Complete |
| Week 3 | AI Integration (Embeddings + RAG pipeline) | ✅ Complete |
| Week 4 | Next.js Frontend | 🔄 Starting Next |
| Week 5 | Polish + Deployment | ⏳ Pending |
| Week 6 | Resume prep + Interview prep | ⏳ Pending |

---

## Daily Log

### Day 1
**Status:** ✅ Complete
**What was built:**
- Python environment + FastAPI server
- 7 CRUD endpoints (in-memory storage)
- Swagger UI at /docs
- PROJECT_MAP.md, DECISIONS.md, PROGRESS.md, CS_CONCEPTS.md created

**Time spent:** ~3-4 hrs
**Roadblocks:** None

---

### Day 2
**Status:** ✅ Complete
**What was built:**
- PostgreSQL connected via Supabase
- SQLAlchemy ORM + documents table
- Data persists across restarts

**Time spent:** ~4-5 hrs
**Roadblocks:**
| # | Roadblock | Cause | Fix |
|---|-----------|-------|-----|
| 1 | Railway not free | Account bug | Switched to Supabase |
| 2 | DATABASE_URL None | Hidden chars in .env | Recreated via terminal |
| 3 | Port 5432 timeout | Windows firewall | Switched to pooler 6543 |
| 4 | Password auth failed | Special chars in password | Reset without special chars |

---

### Day 3
**Status:** ✅ Complete
**What was built:**
- JWT auth from scratch
- Register + login endpoints
- bcrypt password hashing
- Protected + user-scoped routes
- PDF + TXT file upload
- Supabase Storage connected
- PyPDF2 text extraction

**Time spent:** ~5-6 hrs
**Roadblocks:**
| # | Roadblock | Cause | Fix |
|---|-----------|-------|-----|
| 1 | bcrypt 500 error | passlib incompatibility | Pinned bcrypt==4.0.1 |
| 2 | Swagger auth broken | Missing bearerAuth scheme | Added custom_openapi() |
| 3 | Windows multiline terminal | CMD limitation | Used .py file instead |
| 4 | Storage 403 error | Supabase RLS | Added SQL storage policy |
| 5 | DB save failed | Missing table columns | ALTER TABLE |
| 6 | Thunder Client paywall | Paid feature | Switched to Swagger |

---

### Day 4
**Status:** ✅ Complete
**What was built:**
- Keyword search (ILIKE across title, content, tags)
- Deployed to Render — live public URL
- Production API tested and confirmed

**Time spent:** ~2-3 hrs
**Roadblocks:**
| # | Roadblock | Cause | Fix |
|---|-----------|-------|-----|
| 1 | Search returning 404 | Wrong route order | Moved /search above /{doc_id} |
| 2 | JSON decode error on prod | Missing quotes on strings | Added quotes to values |

---

### Day 5
**Status:** ✅ Complete
**What was built:**
- Conversations table + 4 endpoints
- Messages table + 2 endpoints
- Cascading delete (messages deleted with conversation)
- Full conversation flow tested end to end

**Time spent:** ~2-3 hrs
**Roadblocks:**
| # | Roadblock | Cause | Fix |
|---|-----------|-------|-----|
| 1 | Confused about conv_id in URL | Nested route not explained | Learned path parameter pattern |

---

### Day 6
**Status:** ✅ Complete
**What was built:**
- pgvector extension enabled on Supabase
- document_chunks table with 1536-dimension vector column
- ai.py — full RAG pipeline with OpenAI
- chunk_text() — overlapping word chunker
- get_embedding() — OpenAI text-embedding-3-small
- find_relevant_chunks() — pgvector cosine similarity search
- generate_rag_response() — context + history + GPT-4o-mini
- POST /documents/{id}/process endpoint
- POST /conversations/{id}/chat endpoint
- GET /documents/{id}/chunks endpoint
- is_processed column added to documents table
- Full AI pipeline tested with small + large documents
- Semantic search proved across 3 different document sections

**Time spent:** ~4-5 hrs
**Roadblocks:**
| # | Roadblock | Cause | Fix |
|---|-----------|-------|-----|
| 1 | google-generativeai deprecated | Package replaced | Switched to google-genai |
| 2 | Embedding model 404 | Model name changed | Found correct name via list_models() |
| 3 | Vector dimension mismatch 768 vs 3072 | Gemini uses 3072 not 768 | Updated Vector(3072) + ALTER TABLE |
| 4 | Gemini quota limit: 0 | Pakistan region restriction | Switched to OpenAI |
| 5 | OpenAI billing not prompted | UI changed | Found billing in settings manually |
| 6 | Vector dimension mismatch 3072 vs 1536 | OpenAI uses 1536 | Updated Vector(1536) + ALTER TABLE |

---

## Roadblocks Master Log
| Day | Roadblock | Time Lost | Fix |
|-----|-----------|-----------|-----|
| 2 | Railway not free | 15 min | Switched to Supabase |
| 2 | .env hidden characters | 20 min | Recreated via terminal |
| 2 | Port 5432 blocked | 30 min | Used pooler 6543 |
| 2 | Wrong DB password | 10 min | Reset without special chars |
| 3 | bcrypt incompatibility | 15 min | Pinned bcrypt==4.0.1 |
| 3 | Swagger auth broken | 25 min | Custom OpenAPI schema |
| 3 | Windows terminal multiline | 10 min | Used .py file instead |
| 3 | Storage 403 RLS | 20 min | Added SQL storage policy |
| 3 | Missing DB columns | 30 min | ALTER TABLE |
| 3 | Thunder Client paywall | 10 min | Switched to Swagger |
| 4 | Search 404 wrong route order | 5 min | Fixed route order |
| 4 | JSON decode error | 5 min | Added quotes to strings |
| 5 | Nested route path param | 10 min | Learned pattern |
| 6 | Deprecated Gemini package | 15 min | Switched to google-genai |
| 6 | Wrong embedding model name | 10 min | Used list_models() to find correct name |
| 6 | Vector dimension 768 vs 3072 | 15 min | Updated code + ALTER TABLE |
| 6 | Gemini region restriction | 30 min | Switched to OpenAI |
| 6 | OpenAI billing UI changed | 10 min | Found in settings |
| 6 | Vector dimension 3072 vs 1536 | 10 min | Updated code + ALTER TABLE |

---

## Architecture Understanding Log
| Concept | Understood On |
|---------|--------------|
| Request lifecycle | Day 1 |
| Pydantic validation | Day 1 |
| Why async def | Day 1 |
| SQLAlchemy ORM vs raw SQL | Day 2 |
| Why .env exists | Day 2 |
| JWT structure and lifecycle | Day 3 |
| Why bcrypt over MD5/SHA256 | Day 3 |
| Dependency injection Depends() | Day 3 |
| Why two storage systems | Day 3 |
| Storage path structure | Day 3 |
| SQLAlchemy create_all limitation | Day 3 |
| Separation of concerns | Day 3 |
| FastAPI route ordering | Day 4 |
| PostgreSQL ILIKE search | Day 4 |
| JSON string quoting rules | Day 4 |
| Local vs production environments | Day 4 |
| Nested routes + path parameters | Day 5 |
| Cascading delete + foreign key constraints | Day 5 |
| What embeddings are (text → vector) | Day 6 |
| Cosine similarity for semantic search | Day 6 |
| Why chunking improves RAG quality | Day 6 |
| Overlapping chunks prevent context loss | Day 6 |
| RAG pipeline end to end | Day 6 |
| Difference between keyword and semantic search | Day 6 |
| Why AI doesn't hallucinate with RAG | Day 6 |
| pgvector <=> cosine distance operator | Day 6 |
| task_type difference for doc vs query embeddings | Day 6 |

---

## Skills Unlocked
- [x] FastAPI server setup
- [x] Pydantic models
- [x] REST API design (CRUD)
- [x] PostgreSQL + SQLAlchemy ORM
- [x] Cloud database (Supabase)
- [x] Environment variables (.env)
- [x] JWT authentication from scratch
- [x] bcrypt password hashing
- [x] Dependency injection (Depends())
- [x] API testing (Thunder Client + Swagger)
- [x] File upload (PDF + TXT)
- [x] Cloud file storage (Supabase Storage)
- [x] PDF text extraction (PyPDF2)
- [x] Database migrations (ALTER TABLE)
- [x] Keyword search (PostgreSQL ILIKE)
- [x] FastAPI route ordering rules
- [x] Production deployment (Render)
- [x] Environment variable management in production
- [x] Relational data modeling (4 tables)
- [x] Foreign key relationships + cascading delete
- [x] Text chunking with overlap
- [x] Vector embeddings (OpenAI text-embedding-3-small)
- [x] pgvector cosine similarity search
- [x] RAG pipeline end to end
- [x] GPT-4o-mini chat completions
- [x] Semantic vs keyword search
- [ ] Next.js frontend
- [ ] React components + hooks
- [ ] Vercel deployment
- [ ] Streaming AI responses

---

## Resume Bullets Earned So Far
- "Built and deployed RESTful API with FastAPI and PostgreSQL with 15+ endpoints"
- "Implemented JWT authentication with bcrypt password hashing from scratch"
- "Designed relational database schema with 4 tables and user-scoped access"
- "Built file upload pipeline for PDF/TXT with text extraction and Supabase cloud storage"
- "Implemented full-text keyword search using PostgreSQL ILIKE queries"
- "Deployed production backend to Render with environment-based configuration"
- "Built RAG pipeline using OpenAI embeddings, pgvector cosine similarity search, and GPT-4o-mini"
- "Implemented semantic document search with 1536-dimension vector embeddings stored in PostgreSQL"

---

## What's Next (Week 4)
- [ ] Next.js frontend setup
- [ ] Document upload UI
- [ ] Conversation and chat UI
- [ ] Connect frontend to live API
- [ ] Deploy frontend to Vercel

## Notes to Future Self
- Always recreate .env via terminal on Windows (hidden characters)
- Use port 6543 (pooler) not 5432 for Supabase on Windows
- bcrypt must stay at 4.0.1 — do not upgrade
- SQLAlchemy create_all NEVER alters existing tables — use ALTER TABLE
- Specific routes always before dynamic routes in FastAPI
- Every string in JSON body needs quotes
- Check terminal errors before reading Swagger error responses
- Gemini free tier has region restrictions — OpenAI works everywhere
- Always check vector dimensions match between code and DB column
- Use list_models() to find actual available models for any AI provider
