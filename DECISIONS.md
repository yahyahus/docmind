# DocMind — Architecture Decisions & Deep Understanding

## How to Use This File
Every time a new tool, library, or pattern is introduced, it gets documented here.
Read this when you want to understand WHY something was chosen, not just what it does.

---

## The Mental Model: What Actually Happens When a Request Comes In

Imagine you run a restaurant:
- **Uvicorn** = the front door. Accepts customers (requests) coming in.
- **FastAPI** = the manager. Looks at what the customer wants, sends them to the right table.
- **Your endpoint function** = the waiter. Takes the order, does the work.
- **SQLAlchemy** = the kitchen order system. Translates notes into something the kitchen understands.
- **PostgreSQL** = the kitchen. Actually stores and retrieves the food (data).
- **Pydantic** = the quality checker. Makes sure every dish looks right before it goes out.
- **JWT tokens** = the wristband at an event. You get it once at the door (login),
  and flash it every time you want access to something inside.
- **Supabase Storage** = the warehouse out back. Stores the actual heavy items (files).
  The kitchen (PostgreSQL) just keeps a note of where each item is stored.

---

## Why Each Tool Was Chosen

### FastAPI (not Flask, not Django)
**What it is:** A Python web framework that handles HTTP requests.
**Why not Flask:** Simpler but gives you nothing out of the box.
  You'd manually add validation, docs, async support.
**Why not Django:** Full framework with too much built in — opinionated,
  slower for API-only backends.
**Why FastAPI:**
- Automatic API docs (Swagger) generated from your code
- Built-in data validation via Pydantic
- Async by default — handles many requests simultaneously
- Type hints drive everything — less bugs, better editor support
**Real world:** Used by Uber, Netflix, Microsoft internally.

---

### Pydantic (not manual validation)
**What it is:** Validates data using Python type hints.
**Why we need it:** When a user sends JSON, you can't trust it.
  They might send wrong types or skip required fields.
  Pydantic catches this automatically before your code runs.
**How it works in our code:**
```python
class DocumentCreate(BaseModel):
    title: str        # must be string, required
    content: str      # must be string, required
    tags: list[str] = []  # optional, defaults to []
```
If someone sends {"title": 123} — Pydantic rejects it automatically.

---

### SQLAlchemy (not raw SQL)
**What it is:** ORM (Object Relational Mapper).
  Lets you talk to PostgreSQL using Python classes instead of SQL strings.
**Why not raw SQL:** Easy typos, SQL injection risk, no type hints.
**Why SQLAlchemy:**
- Tables are Python classes — editor catches mistakes
- Handles SQL injection protection automatically
- Works with any database — just change the URL
**Translation example:**
db.query(Document).filter(Document.id == doc_id).first()
→ SELECT * FROM documents WHERE id = 'xxx' LIMIT 1

---

### PostgreSQL (not MySQL, not MongoDB)
**Why not MongoDB:** Our data has clear relationships (users own documents)
  so relational fits better. PostgreSQL also has pgvector for AI in Week 3.
**Why not MySQL:** PostgreSQL has better array support, JSON columns,
  and pgvector extension needed for AI features.
**Why Supabase:** Free hosted PostgreSQL, visual table editor,
  pgvector already installed, includes file storage.

---

### Two Storage Systems: PostgreSQL + Supabase Storage Bucket
**This is the most important architecture decision to understand.**

**Why not store files in PostgreSQL:**
  Databases are optimized for structured data (rows, columns, relationships).
  Storing raw file bytes in a database column makes it extremely slow —
  every query that touches that table has to load massive binary data.
  It also makes backups huge and expensive.

**Why not store metadata in the bucket:**
  Buckets store files, not structured queryable data. You can't do
  "give me all documents owned by user X uploaded in the last 7 days"
  against a storage bucket. That's a database query.

**The correct pattern (used by every major app):**
- Raw file → Storage bucket (fast, cheap, designed for binary data)
- Metadata → Database (queryable, relational, fast for structured queries)
- file_path column = the bridge between the two systems

---

### JWT Tokens (not sessions, not API keys)
**Why not sessions:** Sessions store user data on the server — server must
  remember every logged-in user. JWT is stateless — token carries everything.
  Perfect for APIs used by mobile apps, frontends, other services.
**Why not API keys:** API keys don't expire. JWT tokens expire (30 min)
  which limits damage if a token is stolen.
**The three parts of a JWT (split by dots):**
- Header: algorithm used to sign it
- Payload: your data (user_id, expiry time)
- Signature: proves token wasn't tampered with

---

### bcrypt (not MD5, not SHA256)
**Why not plain text:** If DB is leaked, every password is exposed.
**Why not MD5/SHA256:** These are fast — attackers try billions of
  combinations per second. Fast is BAD for passwords.
**Why bcrypt:** Intentionally slow. Has a cost factor you increase
  over time. Adds random salt so same password = different hashes.
  You can NEVER reverse a bcrypt hash. That's the point.

---

### Storage Path Structure: {user_id}/{uuid}/{filename}
**Why user_id not username/email:**
- Users can change username/email — ID never changes
- Email in path = privacy leak
- ID is immutable — path is permanent

**Why uuid folder:**
- Same user uploading report.pdf twice won't overwrite the first
- Each upload is isolated in its own folder

**Why keep original filename:**
- Human readable at the end for quick identification
- Stored in DB title column anyway

---

### python-dotenv + .env file (not hardcoding secrets)
**Why:** If you write DATABASE_URL directly in code and push to GitHub,
  your password is public forever. Even if deleted, Git history keeps it.
**Rule:** Anything sensitive or environment-specific goes in .env. Never in code.

---

## The Dependency Injection Pattern (Depends())

Used on every endpoint:
```python
async def create_document(
    doc: DocumentCreate,                          # from request body
    db: Session = Depends(get_db),               # database session
    current_user: User = Depends(get_current_user)  # logged-in user
):
```
FastAPI runs get_db() and get_current_user() BEFORE your function.
If either fails → automatically returns error. Your function never runs.
Think of it as: "I need these things to exist before I can do my job."

---

## The Layered Architecture

```
main.py      → WHAT the API does (routes, request/response shapes)
database.py  → WHAT the data looks like (tables, columns, DB connection)
auth.py      → HOW security works (hashing, tokens, verification)
.env         → WHERE secrets live (never in code)
```

Each file has ONE job. When something breaks:
- Auth bug → auth.py
- Database error → database.py
- Wrong API response → main.py

This is called Separation of Concerns — one of the most important
principles in software engineering.

---

## Decision Log (Chronological)

| Decision | Why |
|----------|-----|
| FastAPI over Flask/Django | Async, auto-docs, Pydantic built-in |
| Supabase over Railway | Genuinely free, pgvector built-in for Week 3 AI |
| JWT over sessions | Stateless, perfect for APIs, works with any frontend |
| bcrypt over SHA256 | Designed for passwords, intentionally slow, salted |
| SQLAlchemy over raw SQL | Type safety, injection protection, cleaner code |
| Pooler connection port 6543 | Direct port 5432 blocked by ISP/firewall on Windows |
| Thunder Client over Swagger | Better auth header support (free tier can't upload files) |
| bcrypt==4.0.1 pinned | Newer versions incompatible with passlib on Windows |
| Supabase Storage for files | Databases not designed for binary file storage |
| user_id in storage path | Immutable, private, never changes unlike username/email |
| uuid folder in storage path | Prevents duplicate filename conflicts per user |
| Columns added via SQL not code | SQLAlchemy create_all only creates new tables, never alters existing ones |
