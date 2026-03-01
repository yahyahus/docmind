# DocMind API

AI-powered document intelligence platform. Upload documents and chat with them using RAG (Retrieval Augmented Generation).

**Live API:** https://docmind-api-5jka.onrender.com/docs

## Tech Stack
- **Framework:** FastAPI (Python)
- **Database:** PostgreSQL (Supabase) with pgvector extension
- **Auth:** JWT tokens with bcrypt password hashing
- **AI:** OpenAI text-embedding-3-small + GPT-4o-mini
- **Storage:** Supabase Storage
- **Deployment:** Render

## Features
- JWT authentication (register, login, protected routes)
- PDF and TXT file upload with text extraction
- Vector embeddings for semantic document search
- RAG pipeline — retrieves relevant chunks, generates grounded AI responses
- Keyword search with PostgreSQL ILIKE
- Conversation and message history

## Architecture
```
User Question
      ↓
Embed question → 1536-dimension vector
      ↓
pgvector cosine similarity search → top 5 relevant chunks
      ↓
Context + history + question → GPT-4o-mini
      ↓
Grounded answer (no hallucination)
```

## API Endpoints
| Method | Path | Description |
|--------|------|-------------|
| POST | /auth/register | Create account |
| POST | /auth/login | Login, returns JWT |
| POST | /documents/upload | Upload PDF or TXT |
| POST | /documents/{id}/process | Chunk + embed document |
| POST | /conversations/{id}/chat | AI chat with RAG |
| GET | /documents/search | Keyword search |

## Local Setup
```bash
git clone https://github.com/yahyahus/docmind
cd docmind
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
# Create .env with DATABASE_URL, SUPABASE_URL, SUPABASE_KEY, OPENAI_API_KEY
uvicorn main:app --reload
```