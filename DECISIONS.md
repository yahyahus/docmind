# DocMind — Architecture Decisions & Deep Understanding

## How to Use This File
Every time a new tool or pattern is introduced it gets documented here.
Read this when you want to understand WHY something was chosen.

---

## The Mental Model

Imagine you run a library with an AI research assistant:
- **Uvicorn** = the front door
- **FastAPI** = the librarian routing requests to the right desk
- **SQLAlchemy** = the catalog system
- **PostgreSQL** = the filing cabinets (structured data)
- **Supabase Storage** = the physical shelf (raw files)
- **pgvector** = the semantic index (groups books by meaning not title)
- **OpenAI Embeddings** = the tool that reads content and creates a meaning fingerprint
- **GPT-4o-mini** = the research assistant that reads relevant pages and answers questions
- **JWT tokens** = the library card proving who you are
- **Next.js** = the library's public-facing reception desk
- **Axios interceptors** = the staff member who automatically shows your library card on every visit
- **SSE (streaming)** = the assistant whispering each word as they think of it rather than waiting to finish the whole answer
- **Resend** = the postal service that delivers password reset letters
- **Google OAuth** = letting users show their Google ID card instead of creating a new library card
- **Share links** = a photocopy of a conversation anyone can read without a library card
- **pdf.js** = a dedicated PDF reader built into the library's reading desk
- **SlowAPI** = the door policy limiting how many requests one person can make per minute
- **GitHub Actions CI** = the quality checker that runs automatically before any change goes live

---

## Why Each Tool Was Chosen

### FastAPI over Flask/Django
Async, auto-docs, Pydantic built-in, type hints throughout.
Used by Uber, Netflix, Microsoft internally.
Auto-generates Swagger UI — testable without any frontend.

### Pydantic
Validates all incoming data automatically. One class definition
replaces hundreds of manual if/else checks. Also defines exactly
what fields the API returns — if a field isn't in the Pydantic model,
it won't appear in the response (learned the hard way with is_processed).

### SQLAlchemy over raw SQL
Type safety, SQL injection protection, database-agnostic.
Tables become Python classes — editor catches mistakes immediately.

### PostgreSQL over MongoDB
Relational data (users own documents own conversations own messages).
Has pgvector extension required for AI semantic search.
Strong consistency guarantees via ACID transactions.

### Supabase over Railway
Genuinely free tier, pgvector pre-installed,
visual table editor, includes file storage bucket.

### Two Storage Systems (PostgreSQL + Supabase Storage)
- Storage bucket = raw file bytes (optimized for binary data)
- PostgreSQL = metadata + extracted text (optimized for queries)
- file_path column bridges them
- Storing files in DB would make every query load massive binary blobs

### JWT over Sessions
Stateless — server remembers nothing between requests.
Token carries everything. Perfect for APIs + mobile apps.
Expires in 1 day — limits damage if stolen.
Stored in cookies (not localStorage) — safer, available server-side.

### Cookies over localStorage for JWT
localStorage is accessible via JavaScript — XSS attacks can steal it.
Cookies can be marked httpOnly — JavaScript can't read them.
For this project we use js-cookie (accessible) for simplicity,
but production apps should use httpOnly cookies set by the server.

### bcrypt over MD5/SHA256
Intentionally slow — attackers can't brute force billions of combinations.
Automatically salts — same password = different hash every time.
Cost factor increases over time as hardware gets faster.
Pinned to 4.0.1 — newer versions break passlib compatibility.

### OpenAI over Gemini
Gemini free tier unavailable in Pakistan (limit: 0 quota).
OpenAI works globally, $5 lasts entire project (~$0.03 actual spend).
text-embedding-3-small is cheaper than ada-002 with same quality.

### text-embedding-3-small over ada-002
Same 1536 dimensions. Cheaper per token. Newer model.
Both produce vectors that work identically with pgvector.

### GPT-4o-mini over GPT-4o
GPT-4o-mini is 15x cheaper with 85% of the capability.
For document Q&A with retrieved context, mini is more than sufficient.
GPT-4o is overkill when you're providing the answer in the context.

### Chunking with Overlap
Documents split into 400-word chunks with 50-word overlap.
Without overlap: a sentence split across chunk boundary loses context.
With overlap: the boundary content appears in both chunks — never lost.
Smaller chunks = more focused embeddings = better retrieval accuracy.

### Semantic Chunking over Fixed Word-Count Chunking (Week 6)
Fixed-size chunking cuts mid-sentence and mid-paragraph — the embedding
captures half an idea. Semantic chunking splits on paragraph boundaries
first, then sentence boundaries, grouping units up to 400 words.
This preserves topical coherence within each chunk.
Result: more accurate embeddings, better retrieval, fewer irrelevant answers.

### Two-Stage Retrieval with Re-ranking (Week 6)
pgvector's <=> operator uses approximate nearest neighbor search —
fast but not perfectly ordered. After fetching 2x candidates, exact
cosine similarity is re-computed in Python and results re-sorted.
Chunks below 0.3 threshold are filtered out.
Fallback: if all below threshold, return top results anyway so system never silently fails.
Cost: slightly more computation. Benefit: meaningfully better precision.

### RAG over Fine-tuning
Fine-tuning trains the model on your data permanently — expensive,
slow, and the model can't be updated without retraining.
RAG retrieves relevant context at query time — free to update,
always uses latest document content, no training required.
RAG is the industry standard for document Q&A applications.

### System Prompt Rules ("Answer ONLY based on context")
Without strict rules GPT will hallucinate answers from its training data.
The rule "if not in context, say I don't have enough information"
forces the model to stay grounded in the document.
Tested and confirmed — "price of mycelium leather products" returned correct refusal.

### SSE over WebSockets for Streaming (Week 5)
SSE is unidirectional server-to-client, which is exactly what token
streaming needs. WebSockets add bidirectional overhead and complexity.
SSE works over standard HTTP, is natively supported by ReadableStream,
and is simpler to implement in FastAPI via StreamingResponse.
Chosen because the client only sends one POST and then listens —
no need for a persistent two-way socket.

### jsPDF Direct Download over window.print() (Week 6)
window.print() opens the browser print dialog — not what users expect
from an "Export PDF" button. jsPDF generates the PDF file directly in
browser memory and triggers a real file download. No dialog, no paper
size confusion, no user friction.

### Per-Document Tag Normalization on Backend (Week 6)
Lowercase, strip whitespace, deduplicate — done in the PATCH endpoint,
not in the frontend form handler. Ensures consistency regardless of
how tags are submitted — from the frontend, from the API directly,
or from future integrations. Frontend can't be trusted to normalize.

### Always Return Success on Forgot-Password (Week 6)
The endpoint returns the same message whether the email exists or not.
This prevents user enumeration attacks — if we returned "Email not found",
an attacker could discover which emails have accounts.
Security best practice: never reveal account existence to unauthenticated callers.

### Single-Use Expiring Reset Tokens (Week 6)
Reset tokens use secrets.token_urlsafe(32) for 256-bit entropy.
Expire after 1 hour. Marked used=True after consumption.
Existing unused tokens for a user are invalidated when a new reset is requested.
This prevents token reuse, stale token attacks, and parallel reset races.

### Token-Based Public Share Links (Week 6)
GET /share/{token} requires no JWT — anyone with the token can view.
The token's randomness (urlsafe 24 bytes = 192 bits of entropy) is
the sole access control. ON DELETE CASCADE means revoking a conversation
also removes its share link automatically — no orphaned tokens.

### Google OAuth via Frontend Credential + Backend Verification (Week 6)
The frontend gets a Google-issued JWT using @react-oauth/google,
sends it to the backend, which verifies it with
google.oauth2.id_token.verify_oauth2_token().
Simpler than a full redirect flow — no OAuth state management,
no callback routes, no CSRF tokens needed.
Google handles the user-facing login UI entirely.

### Find-or-Create for Google OAuth Users (Week 6)
When a Google user signs in for the first time, an account is auto-created
with a random unusable hashed password. Email/password login is impossible
for these accounts by design — users who register via Google always sign
in via Google. This is the correct pattern: accounts are unified by email.

### Keeping document_id Alongside document_ids (Week 5)
When multi-doc chat was added, the original document_id column was kept
for backwards compatibility. New conversations populate both fields.
document_ids is the source of truth. document_id holds the first document
for legacy reads. Removing document_id would require a migration and
would break existing conversations.

### Per-Document Chunk Retrieval for Multi-Doc (Week 5)
Rather than pooling all chunks before retrieval, chunks are fetched
per document (3 per doc default), then combined into unified context.
This prevents one large document from dominating the context window
and ensures representation from each selected document.

### Next.js over React (plain)
App Router provides file-based routing — no react-router setup needed.
Server components possible for future optimization.
Vercel (same company) deploys it with zero configuration.
TypeScript support built in.

### Axios over fetch
Interceptors — automatically attach JWT to every request.
Automatic JSON parsing — no response.json() needed.
Better error objects — error.response.data instead of manual parsing.
One place to handle all 401 errors (token expired).

### Axios Interceptor for 401 with Pathname Check
Without pathname check: failed login (401) → interceptor → redirect to /login → page reloads → error disappears.
With pathname check: on /login page, 401 is expected (wrong password) → don't redirect → let the catch block handle it.
Critical lesson: interceptors are global — they catch ALL errors including expected ones.

### Optimistic UI Updates in Chat
Without optimistic updates: user sends message → waits 3-5 seconds → message appears.
With optimistic updates: user sends message → appears instantly → AI response arrives later.
Makes the app feel fast even when the AI is slow.
On error: remove the optimistic message and show error.

### Render over Heroku
Heroku removed free tier. Render has genuine free tier.
Render deploys directly from GitHub — push to deploy.
Environment variables managed in dashboard.
Cold start after 15 min inactivity on free tier — acceptable for portfolio.

### Vercel over Netlify for Next.js
Vercel built Next.js — perfect compatibility guaranteed.
Zero-config deployment for Next.js.
Auto-deploys on every GitHub push.
Free tier is genuinely generous.

### Wakeup Ping on Dashboard Load
Render free tier sleeps after 15 min inactivity.
First request after sleep takes 30-60 seconds.
Pinging /health on dashboard load gives backend a head start.
Silently fails if backend is already awake — no user impact.

### Pinned requirements.txt (Week 6)
All Python dependencies pinned to exact versions to prevent build failures
from upstream breaking changes.
Conflicts encountered and resolved:
- resend==0.28.0 doesn't exist → fixed to 2.23.0
- resend v2 changed "to" field from string to list → [user.email]
- google-auth 2.40.0 conflicts with cachetools==6.2.6 → downgraded cachetools to 5.5.2

### pgvector HAVING Threshold for Semantic Search (Week 7)
Similarity cutoff applied at the database query level using HAVING distance < 0.35
(equivalent to cosine similarity > 0.65). Doing this in SQL means irrelevant documents
never leave the database — faster and cleaner than filtering in Python after the fact.
Threshold of 0.35 chosen empirically: strict enough to remove noise,
loose enough to return results for imprecise queries.

### Document Versioning — Snapshot Pattern (Week 7)
Each version upload saves the current document state (content, file_path, file_type, summary)
into a document_versions table before overwriting. This is the snapshot pattern:
a point-in-time copy is stored, not a diff. Simpler to implement and restore than
delta-based versioning. Restore replaces the live document with the snapshot's values
and triggers re-processing (re-chunk + re-embed) so the AI always works from the active version.

### Auto-Title via GPT on First Message (Week 7)
Conversation titles default to the document name, which is not descriptive once
a conversation is underway. On the first user message, a GPT call generates a
short, meaningful title from the message content and document titles.
Triggered only once (when title is still the default) — never overwrites a user-renamed title.
Title update is async and non-blocking — the chat stream is unaffected.

### SlowAPI for Rate Limiting (Week 7)
SlowAPI is a thin wrapper around limits library that integrates natively with FastAPI.
Applied per-endpoint with decorator syntax: @limiter.limit("5/minute").
Chosen over a custom middleware because it's per-route granular — login and
forgot-password need tighter limits than chat stream.
Returns 429 Too Many Requests — standard HTTP status code for rate limit breach.

### Two Separate Repos + Two CI Pipelines (Week 7)
Monorepo was attempted but abandoned due to Windows git path complexity.
Each repo has its own .github/workflows/ci.yml.
Backend CI: Python 3.11, install requirements, import check, ruff lint.
Frontend CI: Node 20, npm ci, TypeScript type check, build.
This catches lint errors and type errors before they reach Render/Vercel.
Ruff chosen over flake8/pylint — significantly faster, modern Python linter.

### pdf.js over iframe/embed for PDF Rendering (Week 8)
iframe and <embed> tags render PDFs with the browser's native viewer —
no programmatic control over zoom, page, or scroll.
pdf.js renders each page to a <canvas> element — full control over zoom level,
page navigation, and fit-to-width behavior.
Enables future features like text selection and highlight-to-ask.
Worker loaded from unpkg (not cdnjs) to guarantee version match with npm package.

### ResizableSplit via Mousedown Drag (Week 8)
The split ratio is stored as a percentage in React state (default 50/50).
On drag start, a mousemove listener calculates the new ratio from cursor position.
Min 25% / max 75% clamps prevent either panel from collapsing.
On mobile (< 768px), panels stack vertically — no drag handle shown.
Pure CSS + event listeners, no external library needed.

### Serving Files via Backend Endpoint, Not Direct Supabase URL (Week 8)
Supabase Storage URLs can expire or require signed tokens.
Routing file serving through GET /documents/{doc_id}/file means:
- Auth check is enforced (only the document owner can fetch the file)
- The frontend never needs to know the storage bucket structure
- File serving logic is centralised and can be changed without frontend changes
Backend downloads bytes from Supabase Python client and streams them to the browser.

### Backend Conversation Search over Frontend Filter (Week 8)
Client-side filtering on conversations only has access to titles — messages
are not loaded on the dashboard. To search message content, a backend endpoint
is required. GET /conversations/search queries both conversation titles and
message content via SQL LIKE, using a subquery to find matching conversation IDs.
400ms debounce prevents a request on every keystroke.
Falls back to client-side title filter while the input is empty — no API call needed.

---

## Decision Log (Chronological)
| Day | Decision | Reason |
|-----|----------|--------|
| 2 | Supabase over Railway | Free + pgvector + storage |
| 2 | Port 6543 pooler | Port 5432 blocked on Windows |
| 3 | JWT over sessions | Stateless, API-friendly |
| 3 | bcrypt over SHA256 | Designed for passwords |
| 3 | SQLAlchemy over raw SQL | Type safety + injection protection |
| 3 | Thunder Client for auth | Better than Swagger for Bearer |
| 3 | bcrypt==4.0.1 pinned | Newer versions break passlib |
| 4 | Two storage systems | DB not designed for binary files |
| 4 | Specific routes before dynamic | FastAPI top-down matching |
| 5 | Cascading delete order | FK constraints require children first |
| 6 | OpenAI over Gemini | Region restrictions on Gemini |
| 6 | text-embedding-3-small | Cheaper + same quality as ada-002 |
| 6 | GPT-4o-mini | 15x cheaper, sufficient for RAG |
| 6 | 400-word chunks + 50 overlap | Balance between focus and context |
| 6 | RAG over fine-tuning | Cheaper, updatable, industry standard |
| 7 | Next.js over plain React | File routing, Vercel compatibility |
| 7 | Axios over fetch | Interceptors, auto JSON, better errors |
| 7 | Cookies over localStorage | Slightly safer, works cross-tab |
| 7 | Pathname check in interceptor | Login 401 must not redirect |
| 7 | Optimistic UI in chat | Perceived performance |
| 7 | Wakeup ping on dashboard | Render cold start mitigation |
| W5 | SSE over WebSockets | Unidirectional, simpler, sufficient |
| W5 | Streaming endpoint separate | Non-breaking — existing /chat preserved |
| W5 | document_ids + keep document_id | Backwards compatibility |
| W5 | Per-doc chunk retrieval | Prevent large doc dominating context |
| W5 | Auto-summary on process | No extra user action needed |
| W6 | Semantic chunking | Paragraph/sentence boundaries > word count |
| W6 | Re-ranking + 0.3 threshold | Exact cosine > ANN approximation |
| W6 | jsPDF over window.print() | Real download, no dialog |
| W6 | Tags normalized on backend | Frontend can't be trusted |
| W6 | limit=50 for document list | Was 10 — silently cut off documents |
| W6 | Always return success on forgot-pw | Prevent user enumeration |
| W6 | Single-use expiring tokens | Prevent reuse + stale token attacks |
| W6 | Token-based share links (public) | Entropy as access control |
| W6 | ON DELETE CASCADE on share_links | No orphaned tokens |
| W6 | Google OAuth credential flow | No redirect flow complexity |
| W6 | Find-or-create for Google users | Unified account by email |
| W6 | resend==2.23.0 | 0.28.0 doesn't exist |
| W6 | cachetools==5.5.2 | google-auth 2.40.0 conflict fix |
| W7 | pgvector HAVING threshold | SQL-level filter, faster than Python post-filter |
| W7 | Snapshot versioning | Simpler than delta — restore = copy snapshot back |
| W7 | Auto-title on first message | Default title not descriptive once chat starts |
| W7 | SlowAPI for rate limiting | Per-route granular, native FastAPI integration |
| W7 | Two repos + two CI pipelines | Monorepo blocked on Windows, CI per repo cleaner |
| W7 | Ruff over flake8/pylint | Faster, modern, same rules |
| W8 | pdf.js over iframe/embed | Programmatic control, enables future highlight feature |
| W8 | ResizableSplit via drag | No library needed, pure CSS + events |
| W8 | File serving via backend endpoint | Auth enforcement + abstraction over storage URL |
| W8 | Backend conversation search | Client-side has no access to message content |
| W8 | 400ms debounce on conv search | Prevents request per keystroke |

---

## What Would Change at Production Scale
| Current | Production alternative | Reason |
|---|---|---|
| Single main.py | FastAPI routers by domain | Maintainability |
| SlowAPI in-process | API gateway rate limiting | Distributed, survives restarts |
| allow_origins=["*"] | Explicit origin whitelist | Security |
| limit=50 on list endpoints | Cursor-based pagination | Scalability |
| Supabase free tier | Dedicated PostgreSQL | Connection limits |
| Render free tier | Paid instance | No cold starts |
| In-process streaming | Celery + Redis queue | Reliability at scale |
| js-cookie (accessible) | httpOnly server-set cookies | XSS protection |
| pdf.js canvas rendering | WebAssembly PDF renderer | Performance on large files |
| Snapshot versioning | Delta/diff versioning | Storage efficiency at scale |