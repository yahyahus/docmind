# DocMind — CS Concepts Applied

## How to Use This File
Maps every CS concept applied in DocMind to its academic area.
Use for interview prep and connecting practical work to coursework.

---

## 1. Data Structures & Algorithms

### Arrays / Lists
**Where:** tags = Column(ARRAY(String)), document lists in frontend
**Area:** DSA — Arrays
Array access O(1), search O(n). Used for tags and rendering document cards.

### Hash Maps
**Where:** JWT payload, Python dicts, React state objects
**Area:** DSA — Hash Maps
O(1) average lookup. Hash function maps keys to bucket indices.

### Linked Structures
**Where:** Foreign keys between tables
**Area:** DSA — Linked Structures
Foreign keys are pointers. Message → Conversation → User like a linked chain.

### Sorting
**Where:** .order_by(Document.updated_at.desc())
**Area:** DSA — Sorting
PostgreSQL uses merge sort / quicksort internally for ORDER BY.

### Vectors and Vector Space
**Where:** embedding = Column(Vector(1536))
**Area:** DSA / Linear Algebra — Vectors
A document chunk is a point in 1536-dimensional space.
Similar meaning = nearby points. Dissimilar = far apart.

### Nearest Neighbor Search
**Where:** pgvector <=> cosine distance operator
**Area:** DSA — Approximate Nearest Neighbor Search
Finding 5 chunks closest to a question = finding 5 nearest neighbors
in 1536-dimensional vector space using HNSW graph index.

### Stack (Call Stack)
**Where:** async/await chain, React component tree
**Area:** DSA — Stack
Each async function call pushes a frame onto the call stack.
await suspends the frame until the promise resolves.

---

## 2. Database Systems

### Relational Model
**Where:** All 5 tables
**Area:** DB Systems — Relational Algebra (E.F. Codd, 1970)
Tables, rows, columns, relationships via foreign keys.

### Entity Relationship Design
**Where:** 5-table schema
**Area:** DB Systems — ER Modeling
```
users (1)──documents (many)
users (1)──conversations (many)
conversations (1)──messages (many)
documents (1)──document_chunks (many)
```

### ACID Properties
**Where:** db.commit(), implicit rollback
**Area:** DB Systems — Transaction Management
Atomicity, Consistency, Isolation, Durability on every commit.

### SQL Operations
**Where:** filter(), order_by(), limit(), offset()
**Area:** DB Systems — SQL / Relational Algebra
Maps to SELECT, WHERE, ORDER BY, LIMIT, OFFSET.

### Indexing (B-tree)
**Where:** Primary keys, unique email constraint
**Area:** DB Systems — Query Optimization
PostgreSQL auto-creates B-tree index. O(log n) vs O(n) full scan.

### Vector Indexing (HNSW)
**Where:** pgvector embedding column
**Area:** DB Systems — Specialized Indexing
Hierarchical Navigable Small World graph for approximate nearest
neighbor search in high-dimensional spaces.

### Pattern Matching
**Where:** ILIKE %keyword%
**Area:** DB Systems — String Operations
SQL LIKE patterns — subset of regular expressions.

### Schema Migration
**Where:** ALTER TABLE for new columns (is_processed, file_path etc.)
**Area:** DB Systems — Schema Evolution
create_all never alters existing tables. DDL statements required.

### Foreign Key Constraints
**Where:** All table relationships
**Area:** DB Systems — Referential Integrity
Cannot insert chunk without valid document_id.
Cannot insert message without valid conversation_id.

### Cascading Operations
**Where:** Delete conversation → delete all its messages
**Area:** DB Systems — Referential Actions
Must delete children before parent due to FK constraints.

---

## 3. Computer Networks

### HTTP Protocol
**Where:** All 21 endpoints
**Area:** Networks — Application Layer (RFC 7231)
GET=Read, POST=Create, PATCH=Update, DELETE=Delete.

### Client-Server Architecture
**Where:** Browser → Next.js → FastAPI → Supabase
**Area:** Networks — Client-Server Model
3-tier: Presentation (Vercel) → Application (Render) → Data (Supabase).

### REST Architecture
**Where:** All API design
**Area:** Networks / SE — REST (Fielding, 2000)
Stateless, resource-based URLs, uniform interface.

### HTTP Status Codes
**Where:** 200, 201, 400, 401, 404, 422, 500
**Area:** Networks — HTTP
2xx success, 4xx client error, 5xx server error.

### JSON Serialization
**Where:** All request/response bodies
**Area:** Networks — Data Representation
Text-based interchange. Pydantic serializes automatically.

### Ports and Sockets
**Where:** localhost:8000, localhost:3000, port 6543, $PORT
**Area:** Networks — Transport Layer (TCP)
16-bit port number identifies process on a machine.

### SSL/TLS
**Where:** sslmode=require, HTTPS on Render and Vercel
**Area:** Networks — Security / Transport Layer
Asymmetric encryption for handshake, symmetric for data transfer.

### CORS — Cross-Origin Resource Sharing
**Where:** CORSMiddleware in main.py
**Area:** Networks — Browser Security
Browsers block requests from different origins by default.
CORS headers tell the browser which origins are allowed.
Frontend (vercel.app) calling backend (onrender.com) = cross-origin.

### DNS Resolution
**Where:** docmind-api-5jka.onrender.com → IP address
**Area:** Networks — DNS
Hierarchical distributed system mapping names to IPs.

### CDN / Edge Deployment
**Where:** Vercel deploys Next.js to edge network
**Area:** Networks — Content Delivery
Static assets served from nearest edge node globally.

---

## 4. Operating Systems

### Async I/O
**Where:** async def everywhere in FastAPI
**Area:** OS — Concurrency / Non-blocking I/O
Event loop handles other requests while one awaits DB or AI response.
Same concept as epoll/kqueue in Linux kernel.

### Environment Variables
**Where:** os.getenv("OPENAI_API_KEY"), process.env.NEXT_PUBLIC_API_URL
**Area:** OS — Process Environment
Key-value pairs in process environment inherited from parent process.

### File System
**Where:** Storage paths, venv/, .env, .env.local
**Area:** OS — File Systems
Hierarchical directory tree. Path separators differ per OS.

### Process Isolation
**Where:** venv/ virtual environment
**Area:** OS — Process Isolation
Isolated Python interpreter with its own package directory.

### Cold Start / Process Lifecycle
**Where:** Render free tier sleeping after inactivity
**Area:** OS — Process Management
Process terminated after inactivity. New request triggers new process spawn.
Wakeup ping mitigates this by keeping process warm.

---

## 5. Security & Cryptography

### One-Way Hash Functions
**Where:** bcrypt passwords
**Area:** Security — Cryptographic Hash Functions
f(x) easy to compute, x impossible to recover from f(x).
Collision-resistant, avalanche effect.

### HMAC
**Where:** JWT signing with HS256
**Area:** Security — Message Authentication Codes
HMAC(key, message) = Hash(key + message).
Proves token was created by key holder, not tampered with.

### Authentication vs Authorization
**Where:** Login (authn) vs user_id filtering (authz)
**Area:** Security — Access Control (AAA)
AuthN = who are you. AuthZ = what can you do.

### Principle of Least Privilege
**Where:** user_id filter on every query
**Area:** Security — Access Control
Valid token doesn't grant access to other users' data.

### Salt in Hashing
**Where:** bcrypt auto-salt
**Area:** Security — Rainbow Table Defense
Random salt makes same password produce different hash each time.

### XSS and Cookie Security
**Where:** JWT stored in js-cookie vs localStorage
**Area:** Security — Web Security
localStorage accessible via JS = XSS risk.
httpOnly cookies inaccessible to JS = safer.
Current implementation uses accessible cookies for simplicity.

### Prompt Injection Defense
**Where:** System prompt rules in generate_rag_response()
**Area:** Security — AI Security
Strict instructions prevent model manipulation via uploaded documents.

---

## 6. Artificial Intelligence & Machine Learning

### Vector Embeddings
**Where:** get_embedding() → OpenAI text-embedding-3-small
**Area:** ML — Representation Learning
Text → 1536 floats capturing semantic meaning.
Trained neural network maps linguistic meaning to geometric space.

### Cosine Similarity
**Where:** pgvector <=> operator
**Area:** ML / Linear Algebra — Similarity Metrics
cos(θ) = (A·B) / (|A||B|)
Measures angle between vectors — ignores magnitude, captures direction.
1.0 = identical meaning, 0.0 = unrelated.

### Large Language Models
**Where:** GPT-4o-mini via OpenAI chat completions
**Area:** ML — Natural Language Processing
Transformer-based model. Predicts next token using attention mechanism.

### Retrieval Augmented Generation (RAG)
**Where:** generate_rag_response() full pipeline
**Area:** ML — Information Retrieval + NLP
Retrieve → Augment → Generate.
Grounds LLM in factual document content — reduces hallucination.

### Chunking Strategy
**Where:** chunk_text() with overlap
**Area:** ML — Document Processing
Embedding whole doc = diluted vector.
Embedding 400-word chunk = focused vector per topic.
Overlap prevents context loss at boundaries.

### Hallucination Prevention
**Where:** System prompt + "Answer ONLY based on context"
**Area:** ML — AI Alignment / Prompt Engineering
LLMs hallucinate when generating from training data without grounding.
RAG + strict prompt rules force document-grounded responses.
Tested: "What is capital of France" → correct refusal.

### Semantic Search vs Keyword Search
**Where:** pgvector vs ILIKE
**Area:** ML — Information Retrieval
Keyword: matches exact strings — fast, brittle.
Semantic: matches meaning — "weaknesses" finds "limitations".
DocMind implements both — user can choose approach.

---

## 7. Software Engineering

### Separation of Concerns
**Where:** main.py / database.py / auth.py / ai.py / lib/api.ts
**Area:** SE — SOLID Principles
Each file has one responsibility. 4 backend files, 4 distinct jobs.

### Dependency Injection
**Where:** Depends(get_db), Depends(get_current_user)
**Area:** SE — Design Patterns (IoC)
Inject dependencies from outside. Testable, decoupled, clean.

### Layered Architecture
**Where:** Client → API → DB + AI
**Area:** SE — Architectural Patterns
Presentation → Application → Data + Intelligence layers.

### Defensive Programming
**Where:** HTTPException for every edge case, try/catch in frontend
**Area:** SE — Reliability Engineering
Validate everything. Fail fast. Return meaningful errors.

### 12-Factor App
**Where:** .env locally, Render/Vercel env vars in production
**Area:** SE — Cloud-Native Development
Factor III: Config separate from code. Never hardcode secrets.

### Optimistic UI
**Where:** Chat message appears before AI responds
**Area:** SE — UX Engineering
Show expected result immediately. Revert on failure.
Improves perceived performance without changing actual speed.

### Interceptor Pattern
**Where:** Axios request/response interceptors
**Area:** SE — Design Patterns (Middleware / Chain of Responsibility)
Cross-cutting concerns (auth headers, error handling) in one place.
Every request goes through interceptor automatically.

### Component-Based Architecture
**Where:** Next.js pages as React components
**Area:** SE — Component Architecture
UI as composable, reusable, isolated units with local state.

---

## 8. Theory of Computation

### Pattern Matching
**Where:** ILIKE %keyword% search
**Area:** ToC — Formal Languages
SQL LIKE = subset of regular expressions = finite automata recognizable.

### Finite State Machines
**Where:** Document processing states, conversation lifecycle
**Area:** ToC — Automata
Document: unprocessed → processed → deleted.
HTTP lifecycle: request → processing → response.

### One-Way Functions
**Where:** bcrypt, SHA-256, HMAC
**Area:** ToC — Complexity Theory
Polynomial time forward, exponential reverse.
Foundation of modern cryptography (assumes P ≠ NP).

### Dimensionality
**Where:** 1536-dimension embedding vectors
**Area:** ToC / Linear Algebra — High-Dimensional Spaces
Curse of dimensionality — distance metrics behave differently.
HNSW approximates nearest neighbor efficiently in high dimensions.

---

## Concept Count by Area
| CS Area | Concepts Applied |
|---------|----------------|
| Data Structures & Algorithms | 7 |
| Database Systems | 10 |
| Computer Networks | 9 |
| Operating Systems | 5 |
| Security & Cryptography | 7 |
| AI & Machine Learning | 7 |
| Software Engineering | 8 |
| Theory of Computation | 4 |
| **Total** | **57** |

---

## Interview Prep — Key Concepts to Explain

### "How does RAG work?"
Embed question → cosine similarity search in pgvector → retrieve top 5 chunks →
inject as context into GPT-4o-mini prompt → model answers from context only.

### "Why cosine similarity and not Euclidean distance?"
Cosine measures angle between vectors (direction = meaning).
Euclidean measures absolute distance (affected by vector magnitude).
Two chunks about the same topic but different lengths produce similar
cosine similarity but very different Euclidean distance.

### "Why chunk documents instead of embedding the whole thing?"
One embedding for a 10,000-word document produces one diluted vector.
The AI can't retrieve the "API design section" specifically.
400-word chunks produce focused vectors per topic — much more precise retrieval.

### "Why store JWT in cookies instead of localStorage?"
localStorage is accessible via JavaScript — XSS attacks can steal it.
Cookies with httpOnly flag are invisible to JavaScript.
For this project we use accessible cookies for simplicity,
but production should use server-set httpOnly cookies.

### "What is CORS and why did you need it?"
Cross-Origin Resource Sharing. Browsers block JavaScript from calling
APIs on different domains by default (security policy).
Frontend on vercel.app calling backend on onrender.com = different origins.
CORSMiddleware adds response headers telling the browser it's allowed.
