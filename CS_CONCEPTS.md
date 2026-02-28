# DocMind — CS Concepts Applied

## How to Use This File
Maps every CS concept applied in DocMind to its academic area.
Use for interview prep and connecting practical work to coursework.

---

## 1. Data Structures & Algorithms

### Arrays / Lists
**Where:** `tags = Column(ARRAY(String))`, in-memory storage
**Area:** DSA — Arrays
Array access O(1), search O(n).

### Hash Maps
**Where:** JWT payload, Python dicts
**Area:** DSA — Hash Maps
O(1) average lookup. Hash function maps keys to bucket indices.

### Linked Structures
**Where:** Foreign keys between tables
**Area:** DSA — Linked Structures
Foreign keys are pointers. Message points to Conversation like a linked list node.

### Sorting
**Where:** `.order_by(Document.updated_at.desc())`
**Area:** DSA — Sorting
PostgreSQL uses merge sort / quicksort internally for ORDER BY.

### Vectors and Vector Space
**Where:** `embedding = Column(Vector(1536))`
**Area:** DSA / Linear Algebra — Vectors
A document chunk is represented as a point in 1536-dimensional space.
Similar meaning = nearby points. Dissimilar = far apart.

### Nearest Neighbor Search
**Where:** pgvector `<=>` cosine distance operator
**Area:** DSA — Approximate Nearest Neighbor Search
Finding the 5 chunks closest in meaning to a question =
finding the 5 nearest neighbors in 1536-dimensional vector space.

---

## 2. Database Systems

### Relational Model
**Where:** All 5 tables
**Area:** DB Systems — Relational Algebra (E.F. Codd, 1970)
Tables, rows, columns, relationships via foreign keys.

### Entity Relationship Design
**Where:** 5-table schema design
**Area:** DB Systems — ER Modeling
```
users (1)──documents (many)
users (1)──conversations (many)
conversations (1)──messages (many)
documents (1)──document_chunks (many)
```

### ACID Properties
**Where:** `db.commit()`, implicit rollback
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

### Vector Indexing
**Where:** pgvector embedding column
**Area:** DB Systems — Specialized Indexing
HNSW (Hierarchical Navigable Small World) graph index for
approximate nearest neighbor search in high-dimensional spaces.

### Pattern Matching
**Where:** ILIKE `%keyword%`
**Area:** DB Systems — String Operations
SQL LIKE patterns — subset of regular expressions.

### Schema Migration
**Where:** ALTER TABLE for new columns
**Area:** DB Systems — Schema Evolution
create_all never alters. DDL statements modify existing tables.

### Foreign Key Constraints
**Where:** All table relationships
**Area:** DB Systems — Referential Integrity
PostgreSQL enforces referenced rows must exist.
Cannot insert chunk without valid document_id.

---

## 3. Computer Networks

### HTTP Protocol
**Where:** All 21 endpoints
**Area:** Networks — Application Layer (RFC 7231)
GET=Read, POST=Create, PATCH=Update, DELETE=Delete → CRUD mapped to HTTP.

### Client-Server Architecture
**Where:** Thunder Client → FastAPI → Supabase
**Area:** Networks — Client-Server Model
3-tier: Presentation → Application → Data.

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
Text-based data interchange. Pydantic handles serialization automatically.

### Ports and Sockets
**Where:** localhost:8000, port 6543, $PORT
**Area:** Networks — Transport Layer (TCP)
16-bit port number identifies process. TCP socket = (IP, port) pair.

### SSL/TLS
**Where:** `sslmode=require`, HTTPS on Render
**Area:** Networks — Security / Transport Layer
Asymmetric encryption for handshake, symmetric for data.

### API Rate Limiting Concepts
**Where:** Gemini quota errors encountered
**Area:** Networks — Traffic Management
Quotas limit requests per minute/day per model per project.
Rate limiting protects infrastructure from abuse.

---

## 4. Operating Systems

### Async I/O
**Where:** `async def` everywhere
**Area:** OS — Concurrency / Non-blocking I/O
Cooperative multitasking. Event loop handles other requests while
one awaits DB or AI API response. Same concept as epoll/kqueue.

### Environment Variables
**Where:** `os.getenv("OPENAI_API_KEY")`
**Area:** OS — Process Environment
Key-value pairs in process environment block inherited from parent.

### File System
**Where:** Storage paths, venv/, .env
**Area:** OS — File Systems
Hierarchical directory tree. Same concept as OS file system.

### Process Isolation
**Where:** venv/ virtual environment
**Area:** OS — Process Isolation
Isolated Python interpreter with own package directory.

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
Proves token created by key holder, not tampered with.

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

### Prompt Injection Defense
**Where:** System prompt rules in generate_rag_response()
**Area:** Security — AI Security
Strict instructions prevent the model from being manipulated
by malicious content embedded in uploaded documents.

---

## 6. Artificial Intelligence & Machine Learning

### Vector Embeddings
**Where:** get_embedding() → OpenAI text-embedding-3-small
**Area:** ML — Representation Learning
Text → 1536 floating point numbers capturing semantic meaning.
Trained neural network maps linguistic meaning to geometric space.

### Cosine Similarity
**Where:** pgvector <=> operator
**Area:** ML / Linear Algebra — Similarity Metrics
cos(θ) = (A·B) / (|A||B|)
Measures angle between vectors — ignores magnitude, captures direction.
1.0 = identical meaning, 0.0 = unrelated, -1.0 = opposite meaning.

### Large Language Models
**Where:** GPT-4o-mini via OpenAI chat completions
**Area:** ML — Natural Language Processing
Transformer-based model trained on massive text corpus.
Predicts next token given context using attention mechanism.

### Retrieval Augmented Generation (RAG)
**Where:** generate_rag_response() full pipeline
**Area:** ML — Information Retrieval + NLP
Combines retrieval (find relevant docs) with generation (produce answer).
Grounds LLM in factual document content — reduces hallucination.

### Chunking Strategy
**Where:** chunk_text() with overlap
**Area:** ML — Document Processing
Embedding a 10,000-word document produces one vector — too diluted.
Embedding 400-word chunks produces focused vectors per topic.
Overlapping chunks prevent context loss at boundaries.

### Hallucination Prevention
**Where:** System prompt + "Answer ONLY based on context"
**Area:** ML — AI Alignment / Prompt Engineering
LLMs hallucinate when generating from training data without grounding.
RAG + strict prompt rules force factual, document-grounded responses.

---

## 7. Software Engineering

### Separation of Concerns
**Where:** main.py / database.py / auth.py / ai.py
**Area:** SE — SOLID Principles
Each file has one responsibility. 4 files, 4 distinct jobs.

### Dependency Injection
**Where:** Depends(get_db), Depends(get_current_user)
**Area:** SE — Design Patterns (IoC)
Inject dependencies from outside. Testable, decoupled, clean.

### Layered Architecture
**Where:** Client → API → DB + AI
**Area:** SE — Architectural Patterns
Presentation → Application → Data + Intelligence layers.

### Defensive Programming
**Where:** HTTPException for every edge case
**Area:** SE — Reliability
Validate everything. Fail fast. Return meaningful errors.

### 12-Factor App
**Where:** .env locally, Render env vars in production
**Area:** SE — Cloud-Native Development
Factor III: Config separate from code.

---

## 8. Theory of Computation

### Pattern Matching / Regular Languages
**Where:** ILIKE %keyword% search
**Area:** ToC — Formal Languages
SQL LIKE = subset of regular expressions = recognized by finite automata.

### Finite State Machines
**Where:** HTTP lifecycle, conversation states, document processing states
**Area:** ToC — Automata
Document states: unprocessed → processed → deleted.
Each API call is a state transition.

### Computational Complexity of Hashing
**Where:** bcrypt, SHA-256, HMAC
**Area:** ToC — Complexity Theory
One-way functions: polynomial time forward, exponential reverse.
Foundation of all modern cryptography (assumes P ≠ NP).

### Dimensionality
**Where:** 1536-dimension embedding vectors
**Area:** ToC / Linear Algebra — High-Dimensional Spaces
The curse of dimensionality — distance metrics behave differently
in high-dimensional spaces. pgvector uses HNSW to handle this efficiently.

---

## Concept Count by Area
| CS Area | Concepts Applied |
|---------|----------------|
| Data Structures & Algorithms | 6 |
| Database Systems | 9 |
| Computer Networks | 8 |
| Operating Systems | 4 |
| Security & Cryptography | 6 |
| AI & Machine Learning | 6 |
| Software Engineering | 5 |
| Theory of Computation | 4 |
| **Total** | **48** |

---

## Concepts Still Coming (Week 4-5)
| Concept | When | Area |
|---------|------|------|
| React Component Model | Week 4 | SE |
| Virtual DOM | Week 4 | DSA |
| React Hooks (useState, useEffect) | Week 4 | SE |
| API Integration from Frontend | Week 4 | Networks |
| CORS (Cross-Origin Resource Sharing) | Week 4 | Networks / Security |
| Streaming Responses (SSE) | Week 4 | Networks |
| CDN / Edge Deployment | Week 5 | Networks |
| CI/CD Pipeline | Week 5 | SE |
