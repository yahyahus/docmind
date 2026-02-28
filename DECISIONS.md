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
- **OpenAI Embeddings** = the tool that reads a book and creates a meaning fingerprint
- **GPT-4o-mini** = the research assistant that reads relevant pages and answers questions
- **JWT tokens** = the library card proving who you are

---

## Why Each Tool Was Chosen

### FastAPI over Flask/Django
Async, auto-docs, Pydantic built-in, type hints throughout.
Used by Uber, Netflix, Microsoft internally.

### Pydantic
Validates all incoming data automatically. One class definition
replaces hundreds of manual if/else checks.

### SQLAlchemy over raw SQL
Type safety, SQL injection protection, database-agnostic.
Tables become Python classes — editor catches mistakes immediately.

### PostgreSQL over MongoDB
Relational data (users own documents own conversations own messages).
Has pgvector extension required for AI semantic search.

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
Expires in 30 min — limits damage if stolen.

### bcrypt over MD5/SHA256
Intentionally slow — attackers can't brute force billions of combinations.
Automatically salts — same password = different hash every time.
Cost factor increases over time as hardware gets faster.

### Storage Path: {user_id}/{uuid}/{filename}
- user_id not username: immutable, private, never changes
- uuid folder: prevents duplicate filename conflicts
- original filename: human readable at the end

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

### Separate task_type for Doc vs Query Embeddings
Gemini: RETRIEVAL_DOCUMENT for chunks, RETRIEVAL_QUERY for questions.
OpenAI: same model for both (ada-002 / 3-small don't distinguish).
Different task types optimize the vector space for asymmetric search.

### pgvector <=> operator
Cosine distance — measures angle between vectors not magnitude.
Lower value = more similar meaning.
ORDER BY embedding <=> question_embedding LIMIT 5
= find 5 chunks whose meaning is closest to the question.

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
Tested and confirmed working — capital of France returned correct refusal.

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
