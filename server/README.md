# Manufacturing RAG

A retrieval-augmented generation (RAG) backend for manufacturing workers. Workers can ask questions in plain English and receive answers grounded in a set of authoritative documents covering standard operating procedures, workplace safety, equipment maintenance, quality control, and regulatory compliance.

---

## Documents

The knowledge base consists of five PDF documents stored in the `docs/` folder:

| Document | Topic |
|---|---|
| EPA SOP Guide | How to write, structure, review, and maintain Standard Operating Procedures |
| OSHA Safety and Health Program Management Guide | Hazard identification, incident reporting, PPE, emergency procedures |
| DOE Operations and Maintenance Best Practices Guide | Preventive maintenance strategies, equipment upkeep, reducing downtime |
| NIST Quality Manual | Quality control, measurement standards, calibration, quality assurance |
| OSHA Quick Reference for Manufacturing | Safety regulations, warning signs, PPE, confined spaces, compliance |

---

## Tech Stack

| Layer | Technology |
|---|---|
| LLM | Groq (configurable model via `MODEL_NAME` in `.env`) |
| Embeddings | `sentence-transformers/all-MiniLM-L6-v2` (local, no API key required) |
| Vector database | Pinecone |
| Auth and chat history | Supabase (PostgreSQL with Row Level Security) |
| API framework | FastAPI |
| Package manager | uv |

---

## Project Structure

```
manufacturing-rag/
├── core/
│   ├── ingestor.py        Load PDFs, chunk, embed, and store in Pinecone
│   ├── retriever.py       Embed a question and retrieve top-k chunks from Pinecone
│   └── generator.py       Build prompt with context and history, call Groq, return answer
├── api/
│   ├── main.py            FastAPI app entry point, router registration
│   ├── dependencies.py    JWT auth dependency (validates Supabase Bearer token)
│   ├── supabase_client.py Supabase client singleton
│   ├── auth/
│   │   ├── schemas.py     Pydantic models: SignUpRequest, SignInRequest, AuthResponse
│   │   ├── service.py     sign_up() and sign_in() logic
│   │   └── routes.py      POST /auth/signup, POST /auth/signin
│   └── chat/
│       ├── schemas.py     Pydantic models: ChatRequest, ChatResponse, SessionResponse
│       ├── service.py     Session creation, history loading, RAG pipeline, message saving
│       └── routes.py      POST /chat/session, POST /chat
├── cli.py                 Terminal chat client for testing the RAG pipeline
├── core/ingestor.py       Run once to ingest documents into Pinecone
├── docs/                  PDF knowledge base (gitignored)
├── .env                   Environment variables (gitignored)
├── .env.example           Environment variable template
└── pyproject.toml         Project dependencies
```

---

## Environment Variables

Copy `.env.example` to `.env` and fill in the values.

```env
GROQ_API_KEY=        # From console.groq.com
PINECONE_API_KEY=    # From app.pinecone.io
MODEL_NAME=          # Groq model name, e.g. llama-3.3-70b-versatile
SUPABASE_URL=        # Project URL from Supabase dashboard (Settings > Data API)
SUPABASE_KEY=        # Publishable key from Supabase dashboard (Settings > API Keys)
```

---

## Setup

**1. Install dependencies**

```bash
uv sync
```

**2. Ingest documents**

Place PDF files in the `docs/` folder, then run:

```bash
uv run python core/ingestor.py
```

This creates a Pinecone index named `manufacturing-rag` (dimension 384, cosine similarity) and upserts all chunks. Safe to re-run — it skips index creation if it already exists.

**3. Create Supabase tables**

Run the following SQL in the Supabase SQL Editor:

```sql
CREATE TABLE chat_sessions (
    id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id    UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE chat_messages (
    id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES chat_sessions(id) ON DELETE CASCADE,
    role       TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
    content    TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX ON chat_sessions(user_id);
CREATE INDEX ON chat_messages(session_id);

ALTER TABLE chat_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE chat_messages ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users see own sessions"
    ON chat_sessions FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Users see own messages"
    ON chat_messages FOR ALL USING (
        session_id IN (SELECT id FROM chat_sessions WHERE user_id = auth.uid())
    );
```

**4. Start the API server**

```bash
uv run uvicorn api.main:app --reload
```

API available at `http://localhost:8000`.
Interactive docs at `http://localhost:8000/docs`.

---

## API Reference

### Auth

#### POST /auth/signup

Create a new account. Role defaults to `"user"`.

```json
{
  "email": "worker@factory.com",
  "password": "securepassword",
  "role": "user"
}
```

Response:

```json
{
  "access_token": "<jwt>",
  "token_type": "bearer",
  "user_id": "<uuid>",
  "role": "user"
}
```

#### POST /auth/signin

Sign in with email and password.

```json
{
  "email": "worker@factory.com",
  "password": "securepassword"
}
```

Response: same shape as signup.

---

### Chat

All chat endpoints require the `Authorization: Bearer <access_token>` header.

#### POST /chat/session

Create a new conversation session. Call this once before sending messages.

Response:

```json
{
  "session_id": "<uuid>"
}
```

#### POST /chat

Send a question. The answer is grounded in the document knowledge base and the LLM receives the full conversation history for the session.

```json
{
  "question": "What PPE is required on the production floor?",
  "session_id": "<uuid>",
  "k": 3
}
```

- `k` (optional, default 3): number of document chunks to retrieve.

Response:

```json
{
  "answer": "Workers must wear hard hats, safety goggles, and steel-toed boots...\n\n[Source: osha_manufacturing.pdf, Page 12]",
  "sources": [
    { "file": "osha_manufacturing.pdf", "page": 12, "score": 0.91 }
  ]
}
```

---

## RAG Pipeline

```
User question
     |
     v
Retriever (core/retriever.py)
  - Embeds question with all-MiniLM-L6-v2
  - Queries Pinecone for top-k similar chunks
     |
     v
Generator (core/generator.py)
  - Loads prior session messages from Supabase as conversation history
  - Builds prompt: system prompt + history + RAG context + question
  - Calls Groq LLM
  - Returns cited answer
     |
     v
Service (api/chat/service.py)
  - Saves user message to Supabase before RAG call
  - Saves assistant reply to Supabase after RAG call
```

Each worker's chat history is scoped to their `user_id` via Row Level Security in Supabase. Workers cannot access each other's sessions or messages.

---

## Roles

Roles (`user` or `admin`) are stored in Supabase `user_metadata` at signup. The role is returned in the auth response and can be read from the JWT by the frontend to control UI access. Backend role enforcement (e.g., admin-only routes) can be added using the `get_current_user` dependency in `api/dependencies.py`.

---

## Testing the Pipeline (Terminal)

```bash
uv run python cli.py
```

This runs a terminal chat loop that calls the RAG pipeline directly without going through the HTTP layer. Useful for quickly verifying that ingestion and retrieval are working correctly.

---

## Switching Models

Change `MODEL_NAME` in `.env` to any model supported by Groq, for example:

- `llama-3.3-70b-versatile` (most capable)
- `llama-3.1-8b-instant` (fastest)
- `mixtral-8x7b-32768` (long context)

No code changes required.
