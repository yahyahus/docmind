# DocMind — AI Document Intelligence Platform

> Upload documents, ask questions, and get AI-powered answers grounded in your content.

![DocMind Dashboard](/Screenshots/Dashboard.png)

**Live Demo:** [docmind-frontend-eight.vercel.app](https://docmind-frontend-eight.vercel.app)  
**Backend API:** [docmind-api-5jka.onrender.com/docs](https://docmind-api-5jka.onrender.com/docs)

---

## What is DocMind?

DocMind is a full-stack RAG (Retrieval-Augmented Generation) application that lets users upload PDF and TXT documents and have AI-powered conversations with their content. Unlike general-purpose chatbots, DocMind grounds every answer in the actual document — no hallucinations, no guessing.

**Key differentiators:**
- Semantic chunking that respects paragraph and sentence boundaries
- Re-ranking pipeline that scores retrieved chunks by cosine similarity before sending to GPT
- Streaming responses with real-time word-by-word output
- Multi-document chat for cross-document analysis
- Shareable read-only conversation links

---

## Features

| Feature | Description |
|---|---|
| 📄 Document Upload | PDF and TXT, up to 5MB |
| ⚡ AI Processing | Semantic chunking + vector embeddings |
| 💬 Streaming Chat | Word-by-word responses via SSE |
| 🗂️ Multi-doc Chat | Ask questions across multiple documents |
| 🔍 Re-ranking | Cosine similarity re-ranking for better answers |
| 📊 Auto Summary | 3-sentence summary generated on processing |
| 🏷️ Document Tags | Tag and filter documents |
| ↓ Export Chat | Download as Markdown, TXT, or PDF |
| 🔗 Share Links | Public read-only conversation links |
| 🔐 Google OAuth | Sign in with Google |
| 🔑 Forgot Password | Email-based password reset via Resend |
| 👤 User Profile | Stats dashboard + password change |

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     CLIENT (Next.js)                     │
│  Dashboard │ Chat │ Profile │ Share │ Auth Pages         │
└─────────────────────┬───────────────────────────────────┘
                      │ HTTPS (REST + SSE)
┌─────────────────────▼───────────────────────────────────┐
│                  BACKEND (FastAPI)                        │
│                                                          │
│  Auth        Documents     Conversations    AI           │
│  ─────────   ──────────    ─────────────   ──────────    │
│  JWT         Upload        Create          Chunk         │
│  Google      Process       Messages        Embed         │
│  OAuth       Tags          Stream          Re-rank       │
│  Forgot PW   Export        Share           RAG           │
└──────┬──────────────┬──────────────────────┬────────────┘
       │              │                      │
┌──────▼──────┐ ┌─────▼──────┐ ┌────────────▼────────────┐
│  PostgreSQL  │ │  Supabase  │ │       OpenAI API         │
│  (Supabase)  │ │  Storage   │ │  text-embedding-3-small  │
│  pgvector    │ │  (files)   │ │  gpt-4o-mini             │
└─────────────┘ └────────────┘ └─────────────────────────┘
```

### RAG Pipeline

```
Document Upload
      │
      ▼
Text Extraction (PDF/TXT)
      │
      ▼
Semantic Chunking
  • Split on paragraph boundaries
  • Split long paragraphs on sentence boundaries
  • Group into ~400 word chunks with 50 word overlap
      │
      ▼
Embedding (text-embedding-3-small → 1536 dimensions)
      │
      ▼
Store in pgvector (Supabase PostgreSQL)


Query Time:
User Question → Embed → pgvector ANN search (2x candidates)
      │
      ▼
Re-rank by exact cosine similarity
      │
      ▼
Filter chunks below 0.3 relevance threshold
      │
      ▼
Build prompt: system + context + history + question
      │
      ▼
GPT-4o-mini (streaming) → SSE to client
```

---

## Tech Stack

### Backend
| Technology | Purpose |
|---|---|
| FastAPI | REST API framework |
| SQLAlchemy | ORM |
| PostgreSQL + pgvector | Database + vector similarity search |
| Supabase | Hosted PostgreSQL + file storage |
| OpenAI API | Embeddings (text-embedding-3-small) + Chat (GPT-4o-mini) |
| PyJWT + bcrypt | JWT auth + password hashing |
| Google Auth | OAuth 2.0 token verification |
| Resend | Transactional email (password reset) |
| PyPDF2 | PDF text extraction |
| Render | Backend deployment |

### Frontend
| Technology | Purpose |
|---|---|
| Next.js 14 | React framework with App Router |
| TypeScript | Type safety |
| js-cookie | JWT token storage |
| @react-oauth/google | Google Sign-In |
| jsPDF | Client-side PDF export |
| Vercel | Frontend deployment |

---

## Project Structure

```
docmind/                    # Backend
├── main.py                 # All API endpoints (21 routes)
├── database.py             # SQLAlchemy models + connection
├── auth.py                 # JWT + password utilities
├── ai.py                   # RAG pipeline (chunking, embedding, re-ranking)
└── requirements.txt

docmind-frontend/           # Frontend
├── app/
│   ├── dashboard/          # Document management
│   ├── chat/[id]/          # Streaming AI chat
│   ├── share/[token]/      # Public read-only view
│   ├── profile/            # User stats + password change
│   ├── login/              # Email + Google auth
│   ├── register/           # Email + Google auth
│   ├── forgot-password/    # Password reset request
│   └── reset-password/     # Password reset form
└── lib/
    ├── api.ts              # Axios instance with auth headers
    └── wakeup.ts           # Render cold start handler
```

---

## Database Schema

```sql
users
  id, email, hashed_password, created_at

documents
  id, user_id, title, content, file_path, file_type,
  tags[], is_processed, summary, created_at, updated_at

document_chunks
  id, document_id, user_id, content, chunk_index,
  embedding (vector 1536), created_at

conversations
  id, user_id, document_id, document_ids[], title,
  created_at, updated_at

messages
  id, conversation_id, role, content, created_at

password_reset_tokens
  id, user_id, token, expires_at, used, created_at

share_links
  id, conversation_id, token, created_at
```

---

## API Reference

### Auth
| Method | Endpoint | Description |
|---|---|---|
| POST | `/auth/register` | Register with email/password |
| POST | `/auth/login` | Login, returns JWT |
| GET | `/auth/me` | Get current user |
| POST | `/auth/google` | Google OAuth login/register |
| POST | `/auth/change-password` | Change password |
| POST | `/auth/forgot-password` | Send reset email |
| POST | `/auth/reset-password` | Reset with token |
| GET | `/auth/stats` | User statistics |

### Documents
| Method | Endpoint | Description |
|---|---|---|
| POST | `/documents/upload` | Upload PDF or TXT |
| GET | `/documents` | List all documents |
| GET | `/documents/{id}` | Get document |
| PATCH | `/documents/{id}` | Rename document |
| PATCH | `/documents/{id}/tags` | Update tags |
| DELETE | `/documents/{id}` | Delete document |
| POST | `/documents/{id}/process` | Chunk + embed document |

### Conversations & Chat
| Method | Endpoint | Description |
|---|---|---|
| POST | `/conversations` | Create conversation |
| GET | `/conversations` | List conversations |
| DELETE | `/conversations/{id}` | Delete conversation |
| GET | `/conversations/{id}/messages` | Get messages |
| POST | `/conversations/{id}/chat/stream` | Streaming AI chat (SSE) |
| GET | `/conversations/{id}/export` | Export as markdown |
| POST | `/conversations/{id}/share` | Create share link |
| DELETE | `/conversations/{id}/share` | Revoke share link |
| GET | `/share/{token}` | Public shared conversation |

---

## Local Setup

### Prerequisites
- Python 3.11+
- Node.js 18+
- A Supabase account (free)
- An OpenAI API key

### Backend

```bash
# Clone and install
git clone https://github.com/yourusername/docmind
cd docmind
pip install -r requirements.txt

# Environment variables
cp .env.example .env
# Fill in:
# DATABASE_URL=postgresql://...
# SUPABASE_URL=https://xxx.supabase.co
# SUPABASE_KEY=eyJ...
# OPENAI_API_KEY=sk-...
# JWT_SECRET=your-secret-key
# RESEND_API_KEY=re_...
# GOOGLE_CLIENT_ID=xxx.apps.googleusercontent.com
# GOOGLE_CLIENT_SECRET=GOCSPX-...
# FRONTEND_URL=http://localhost:3000

# Run database migrations (Supabase SQL Editor)
# See /sql/schema.sql for all CREATE TABLE statements

# Start server
uvicorn main:app --reload
# API running at http://localhost:8000
# Swagger docs at http://localhost:8000/docs
```

### Frontend

```bash
cd docmind-frontend
npm install

# Environment variables
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
echo "NEXT_PUBLIC_GOOGLE_CLIENT_ID=your_client_id" >> .env.local

# Start dev server
npm run dev
# App running at http://localhost:3000
```

### Supabase Setup

1. Create a new Supabase project
2. Go to SQL Editor and run:

```sql
-- Enable pgvector
CREATE EXTENSION IF NOT EXISTS vector;

-- Create tables (see full schema above)
CREATE TABLE users ( ... );
CREATE TABLE documents ( ... );
CREATE TABLE document_chunks (
  id TEXT PRIMARY KEY,
  document_id TEXT REFERENCES documents(id),
  user_id TEXT REFERENCES users(id),
  content TEXT,
  chunk_index INTEGER,
  embedding vector(1536),
  created_at TIMESTAMP DEFAULT NOW()
);
-- etc.
```

3. Create a storage bucket named `documents` (public: false)

---

## Deployment

### Backend → Render
1. Connect GitHub repo to Render
2. Build command: `pip install -r requirements.txt`
3. Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Add all environment variables in Render dashboard

### Frontend → Vercel
1. Connect GitHub repo to Vercel
2. Framework: Next.js (auto-detected)
3. Add environment variables:
   - `NEXT_PUBLIC_API_URL` = your Render URL
   - `NEXT_PUBLIC_GOOGLE_CLIENT_ID` = your Google client ID

---

## Key Engineering Decisions

**Why semantic chunking over fixed-size?**
Fixed-size chunking cuts mid-sentence and mid-paragraph, producing embeddings that capture half an idea. Semantic chunking keeps paragraphs together so the embedding captures complete concepts, improving retrieval quality.

**Why re-rank after pgvector search?**
pgvector's `<=>` operator uses approximate nearest neighbor search which is fast but not perfectly ordered. Re-scoring with exact cosine similarity on the top 2x candidates improves precision at minimal cost.

**Why Server-Sent Events for streaming?**
WebSockets add connection overhead and require stateful connections. SSE is unidirectional (server → client), simpler to implement, and perfectly suited for streaming text tokens.

**Why GPT-4o-mini over GPT-4o?**
For RAG applications the bottleneck is retrieval quality, not model size. GPT-4o-mini produces nearly identical answers at ~10x lower cost because the relevant context is already extracted and provided.

---

## Screenshots

**Dashboard**
![Dashboard](/Screenshots/Dashboard.png)

**AI Chat**
![Chat](/Screenshots/AI-Chat.png)

**Multi-doc Chat**
![Multi-doc](/Screenshots/MultiDocument-Chat.png)

**Profile**
![Profile](/Screenshots/Profile.png)

---

## License

MIT