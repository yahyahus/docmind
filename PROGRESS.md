# DocMind — Progress Tracker

## Timeline Overview
| Week | Focus | Status |
|------|-------|--------|
| Week 1 | Backend (API + DB + Auth + File Upload + Search + Deploy) | ✅ Complete |
| Week 2 | Conversations + Messages | ✅ Complete |
| Week 3 | AI Integration (Embeddings + RAG pipeline) | ✅ Complete |
| Week 4 | Next.js Frontend + Vercel Deploy | ✅ Complete |
| Week 5 | Streaming + Multi-doc + UI Revamp + Auto-summary | ✅ Complete |
| Week 6 | Performance + Export + Tags + Auth Suite + README | ✅ Complete |

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

### Day 7
**Status:** ✅ Complete
**What was built:**
- Next.js app with TypeScript + Tailwind
- lib/api.ts — axios client with JWT interceptor + cold start awareness
- lib/wakeup.ts — backend ping on app load
- app/layout.tsx — root layout with DocMind title
- app/page.tsx — root redirect based on token
- app/login/page.tsx — login form with error handling
- app/register/page.tsx — register form with validation
- app/dashboard/page.tsx — document list, upload, process, search, delete, chat
- app/chat/[id]/page.tsx — full chat UI with typing indicator
- No duplicate conversations — reuses existing conversation per document
- Deployed to Vercel — live at docmind-frontend-eight.vercel.app
- CORS middleware added to backend
- is_processed added to DocumentResponse Pydantic model
- Cold start handling — wakeup ping + retry button + helpful error messages

**Time spent:** ~5-6 hrs
**Roadblocks:**
| # | Roadblock | Cause | Fix |
|---|-----------|-------|-----|
| 1 | Render build failed | Gemini packages conflicting | Manually removed from requirements.txt |
| 2 | Render deploy failed | OPENAI_API_KEY not set on Render | Added to Render environment variables |
| 3 | Login page refreshing on error | 401 interceptor doing hard redirect on login page | Added pathname check to interceptor |
| 4 | All files merged into one | Copy-paste mistake | Separated into correct files |
| 5 | Process for AI not updating UI | is_processed missing from DocumentResponse | Added field to Pydantic model |
| 6 | Chat not finding SOLID principles | Only mentioned once in document | Expected RAG behavior, not a bug |
| 7 | tsx vs js confusion | TypeScript selected by default | Used .tsx throughout |

---

### Week 5 — UI Revamp + Streaming + Multi-doc + Auto-summary
**Status:** ✅ Complete

**What was built:**

**UI Revamp — "Intelligence Interface" dark aesthetic**
- CSS variables: --bg-base, --bg-surface, --bg-elevated, --accent, --accent-bright, --text-primary, --text-secondary, --text-muted, --border, --danger, --success
- Typography: DM Mono (monospace labels), DM Sans (body)
- Indigo gradient buttons (#6366F1 → #818CF8)
- Grain texture overlay on base background
- Consistent sidebar + content layout across all pages

**Auto-Summary on Process**
- generate_summary() in ai.py — 3-sentence summary via GPT
- Called automatically when POST /documents/{id}/process runs
- summary column added to documents table (Supabase SQL + SQLAlchemy model)
- Took debug session: summary column was missing from SQLAlchemy model — db.commit() ran but assignment was silently ignored

**Streaming AI Responses**
- POST /conversations/{id}/chat/stream endpoint with StreamingResponse
- SSE format: data: {"content": "token"}\n\n per chunk, data: {"done": true, "id": "..."} on completion
- Frontend: Fetch API with ReadableStream reader — words appear one by one
- Full response saved to DB after stream ends
- TypeScript fix: window.document.cookie instead of document.cookie (possibly null error)
- chunks returned as list[str] not objects — removed .content access in streaming endpoint

**Multi-document Chat**
- document_ids TEXT[] column added to conversations table via Supabase SQL
- document_ids added to SQLAlchemy Conversation model and Pydantic schemas
- find_relevant_chunks_multi() in ai.py — fetches 3 chunks per doc, combines context
- Both /chat and /chat/stream updated to support single or multi-doc via doc_ids list
- Dashboard: ⊕ Multi-doc chat toggle, checkbox per document card
- Chat with N docs → button appears when ≥2 processed docs selected
- Chat header shows document count and names for multi-doc conversations

**Roadblocks:**
| # | Roadblock | Cause | Fix |
|---|-----------|-------|-----|
| 1 | Summary columns null | summary missing from SQLAlchemy model | Added Column(Text, nullable=True) |
| 2 | Document list capped at 10 | Default limit=10 in GET /documents | Raised to limit=50 |
| 3 | TypeScript build error on document.cookie | Possibly null | Used window.document.cookie |
| 4 | Streaming 500 error | chunks is list[str] not objects | Removed .content — join(chunks) directly |

---

### Week 6 — Performance + Export + Tags + Auth Suite + README
**Status:** ✅ Complete

**Day 1-2: Performance Upgrades (ai.py)**

Semantic chunking:
- split_into_sentences() — regex sentence boundary detection
- chunk_text() rewritten: paragraph split → sentence grouping → 400-word target
- 50-word overlap preserved across boundaries

Re-ranking:
- cosine_similarity(vec_a, vec_b) — exact dot product / magnitude calculation
- find_relevant_chunks() now fetches limit*2 candidates from pgvector
- Re-scores each with exact cosine similarity, sorts descending
- Filters below MIN_SCORE=0.3 threshold
- Fallback to unfiltered if all below threshold

Tested on mycelium document:
- Specific stat retrieval ✓
- Multi-paragraph synthesis ✓
- Hallucination test: abstained correctly on out-of-context question ✓

**Day 3: Export Chat + Document Tags**

Export:
- GET /conversations/{id}/export returns {title, markdown, message_count}
- Frontend: dropdown with MD / TXT / PDF options
- MD → Blob download, TXT → strip markdown + Blob, PDF → jsPDF direct download

Tags:
- PATCH /documents/{id}/tags normalizes (lowercase, strip, deduplicate) and saves
- Dashboard: tag pills per card, click tag → filter documents, ✕ to remove individual tag
- + tag pill → inline comma-separated input
- Active filter shows all matching docs with ✕ Clear button

**Day 4: Forgot Password**

Database: password_reset_tokens table — id, user_id, token, expires_at, used, created_at

Backend:
- POST /auth/forgot-password — always returns success, creates token, sends via Resend
- POST /auth/reset-password — validates token, updates password, marks used=True

Frontend:
- app/forgot-password/page.tsx — email input + success state with 📬
- app/reset-password/page.tsx — reads ?token= from URL, redirects to /login after 2.5s
- Login page: "Forgot password?" link added
- Wrapped in Suspense for useSearchParams

**Roadblocks:**
| # | Roadblock | Cause | Fix |
|---|-----------|-------|-----|
| 1 | resend install fails | 0.28.0 doesn't exist | Pinned resend==2.23.0 |
| 2 | Email not sending | resend v2 changed "to" to list | Changed to [user.email] |

**Day 5: Shareable Chat Links**

Database: share_links table — id, conversation_id (ON DELETE CASCADE), token, created_at

Backend:
- POST /conversations/{id}/share — creates or returns existing token
- DELETE /conversations/{id}/share — revokes link
- GET /share/{token} — public, no auth, returns conversation + messages

Frontend:
- ↗ Share button in chat header
- Share modal: URL display, Copy (2s "Copied!" feedback), Revoke link, Done
- app/share/[token]/page.tsx — public read-only view, "Read-only" badge, 404 state, footer

**Day 6: Google OAuth**

Setup: Google Cloud Console project, OAuth consent (External), authorized origins + redirect URIs for localhost and Vercel.

Backend:
- POST /auth/google — verifies Google JWT credential, find-or-create user by email
- Returns same TokenResponse as regular login

Frontend:
- npm install @react-oauth/google
- layout.tsx wrapped with GoogleOAuthProvider
- Login + Register: Google Sign-In button with theme="filled_black"
- handleGoogleSuccess → POST /auth/google → set cookie → /dashboard

**Roadblocks:**
| # | Roadblock | Cause | Fix |
|---|-----------|-------|-----|
| 1 | google-auth install conflict | cachetools==6.2.6 incompatible | Downgraded cachetools to 5.5.2 |
| 2 | google-auth 2.40.0 broken | Too new | Pinned google-auth==2.38.0 |

**Week 6 Final: README + Resume**
- README.md with ASCII architecture diagram, RAG pipeline diagram, full API reference, local setup guide, deployment guide, tech stack tables, engineering decisions, screenshot placeholders (4 to replace)
- resume-bullets.txt organized by role: Full Stack, Backend-focused, ML/AI Engineer
- Interview talking points for architecture, RAG, hardest problem, SSE vs WebSockets, auth

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
| 6 | Wrong embedding model name | 10 min | Used list_models() |
| 6 | Vector dimension 768 vs 3072 | 15 min | Updated code + ALTER TABLE |
| 6 | Gemini region restriction | 30 min | Switched to OpenAI |
| 6 | OpenAI billing UI changed | 10 min | Found in settings |
| 6 | Vector dimension 3072 vs 1536 | 10 min | Updated code + ALTER TABLE |
| 7 | Gemini packages in requirements | 20 min | Manually removed lines |
| 7 | OPENAI_API_KEY not on Render | 10 min | Added env var on Render |
| 7 | 401 interceptor causing reload | 30 min | Added pathname check |
| 7 | Files merged into one | 20 min | Separated correctly |
| 7 | is_processed missing from response | 15 min | Added to Pydantic model |
| W5 | summary column null | Missing from SQLAlchemy model | Added Column(Text, nullable=True) |
| W5 | Document list capped at 10 | Default limit=10 | Raised to 50 |
| W5 | TypeScript document.cookie null | SSR null check | Used window.document.cookie |
| W5 | Streaming 500 on chunks | list[str] not objects | Removed .content access |
| W6 | resend install fails | Version 0.28.0 doesn't exist | resend==2.23.0 |
| W6 | Email "to" field error | resend v2 needs list | [user.email] |
| W6 | google-auth conflict | cachetools version clash | cachetools==5.5.2 |
| W6 | google-auth too new | 2.40.0 broken | google-auth==2.38.0 |

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
- [x] Relational data modeling (7 tables)
- [x] Foreign key relationships + cascading delete
- [x] Text chunking with overlap
- [x] Vector embeddings (OpenAI text-embedding-3-small)
- [x] pgvector cosine similarity search
- [x] RAG pipeline end to end
- [x] GPT-4o-mini chat completions
- [x] Semantic vs keyword search
- [x] Next.js App Router
- [x] React hooks (useState, useEffect, useRef, useCallback)
- [x] TypeScript interfaces
- [x] Axios interceptors
- [x] JWT storage in cookies
- [x] File upload from browser
- [x] Optimistic UI updates
- [x] Vercel deployment
- [x] CORS configuration
- [x] Dynamic routes ([id] pattern)
- [x] Streaming AI responses (SSE + ReadableStream)
- [x] Multi-document conversations
- [x] User profile + stats
- [x] Auto-document summaries
- [x] Document tags + filtering
- [x] Chat export (MD / TXT / PDF via jsPDF)
- [x] Shareable read-only chat links
- [x] Forgot password + email reset (Resend)
- [x] Google OAuth (credential flow)
- [x] Semantic chunking (paragraph/sentence boundaries)
- [x] Re-ranking with cosine threshold
- [x] Dependency conflict resolution

---

## Resume Bullets Earned
- "Built and deployed RESTful API with FastAPI and PostgreSQL with 21+ endpoints"
- "Implemented JWT authentication with bcrypt password hashing from scratch"
- "Designed relational database schema with 7 tables and user-scoped access using SQLAlchemy ORM"
- "Built file upload pipeline for PDF/TXT with text extraction and Supabase cloud storage"
- "Implemented full-text keyword search using PostgreSQL ILIKE queries"
- "Deployed production backend to Render and frontend to Vercel with environment-based configuration"
- "Built RAG pipeline using OpenAI embeddings, pgvector cosine similarity search, and GPT-4o-mini"
- "Implemented semantic document search with 1536-dimension vector embeddings in PostgreSQL"
- "Added streaming AI responses via Server-Sent Events with FastAPI StreamingResponse"
- "Built multi-document chat supporting simultaneous query across N user-selected documents"
- "Implemented semantic chunking and re-ranking pipeline improving retrieval precision over ANN baseline"
- "Built complete auth suite: JWT, Google OAuth, forgot/reset password via Resend email"
- "Added document tags, chat export (MD/TXT/PDF), and shareable read-only conversation links"
- "Built full-stack AI document chat application with Next.js frontend and FastAPI backend"
- "Implemented JWT authentication flow with cookie storage and automatic token refresh"

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
| Next.js App Router vs Pages Router | Day 7 |
| React component lifecycle with hooks | Day 7 |
| Why axios interceptors over manual headers | Day 7 |
| Optimistic UI updates | Day 7 |
| CORS — why browsers block cross-origin | Day 7 |
| Dynamic routes in Next.js | Day 7 |
| Cookie vs localStorage for JWT | Day 7 |
| Render free tier cold starts | Day 7 |
| SSE vs WebSockets — when to use each | Week 5 |
| ReadableStream API in browser | Week 5 |
| Why SQLAlchemy silently ignores unknown columns | Week 5 |
| How multi-doc context windows work | Week 5 |
| Why ANN search needs re-ranking | Week 6 |
| Cosine similarity vs Euclidean distance | Week 6 |
| User enumeration attacks | Week 6 |
| Token entropy and why it replaces auth | Week 6 |
| OAuth credential flow vs redirect flow | Week 6 |
| Dependency version conflicts | Week 6 |

---

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
- Pydantic response models must include ALL fields you want returned
- 401 interceptor must not redirect on the login page itself
- Render deploys from GitHub — always push before expecting changes
- Vercel auto-redeploys on every push to main branch
- SQLAlchemy silently ignores assignment to columns not in the model — if a field isn't persisting, check the model first
- resend v2 requires "to" as a list: [user.email] not user.email
- google-auth and cachetools have a version conflict — keep cachetools==5.5.2
- Streaming chunks are list[str] — never try .content on them