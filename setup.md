# FloorMan — Setup Guide

## Prerequisites

| Tool | Version | Purpose |
|------|---------|---------|
| Python | 3.12+ | Backend runtime |
| [uv](https://docs.astral.sh/uv/) | latest | Python package manager |
| Node.js | 20+ | Frontend build |
| Docker + Docker Compose | latest | Optional containerised run |

---

## 1. External Services

You need accounts and API keys for three services before running anything locally.

### Supabase (Auth + Chat History)

1. Create a free project at [supabase.com](https://supabase.com).
2. In the SQL editor, run the following to create the tables:

```sql
-- Chat sessions
create table chat_sessions (
  id         uuid primary key default gen_random_uuid(),
  user_id    uuid references auth.users not null,
  created_at timestamptz default now()
);

-- Chat messages
create table chat_messages (
  id         uuid primary key default gen_random_uuid(),
  session_id uuid references chat_sessions(id) on delete cascade not null,
  role       text check (role in ('user', 'assistant')) not null,
  content    text not null,
  created_at timestamptz default now()
);

-- Row Level Security
alter table chat_sessions  enable row level security;
alter table chat_messages  enable row level security;

create policy "Users own their sessions"
  on chat_sessions for all using (auth.uid() = user_id);

create policy "Users own their messages"
  on chat_messages for all
  using (session_id in (select id from chat_sessions where user_id = auth.uid()));
```

3. Note your **Project URL** and **anon/public key** (Settings → API).

### Pinecone (Vector Database)

1. Create a free account at [pinecone.io](https://pinecone.io).
2. Create an index with:
   - **Name**: `manufacturing-rag`
   - **Dimensions**: `384`
   - **Metric**: `cosine`
3. Note your **API key**.

### LLM Provider

FloorMan works with any LLM that exposes an OpenAI-compatible chat API. Recommended options:

| Provider | Example models |
|----------|---------------|
| [Groq](https://groq.com) | llama3-70b-8192, mixtral-8x7b, gemma2-9b |
| [OpenAI](https://platform.openai.com) | gpt-4o, gpt-4o-mini |
| [Together AI](https://together.ai) | many open-source models |
| [Ollama](https://ollama.com) (local) | llama3, mistral, phi3 |

Obtain an API key and pick a model name.

---

## 2. Environment Files

### Backend — `server/.env`

Copy the example and fill in your values:

```bash
cp server/.env.example server/.env
```

```env
GROQ_API_KEY="your_llm_provider_api_key"
PINECONE_API_KEY="your_pinecone_api_key"
MODEL_NAME="your_chosen_model_name"
SUPABASE_URL="https://your-project.supabase.co"
SUPABASE_KEY="your_supabase_anon_key"
```

> If you use a provider other than Groq, update the `ChatGroq` import in
> `server/core/generator.py` to the matching LangChain integration class.

### Frontend — `client/.env`

```bash
cp client/.env.example client/.env
```

```env
VITE_API_URL=http://localhost:8000
```

---

## 3. Ingest Documents

Add your PDF files to `server/docs/` then run the ingestion script once:

```bash
cd server
uv sync
uv run python -m core.ingestor
```

This embeds every chunk and stores them in Pinecone. Re-run whenever you add new documents.

---

## 4. Run Locally (Development)

### Backend

```bash
cd server
uv sync
uv run python -m uvicorn api.main:app --reload
# Listening on http://localhost:8000
```

### Frontend

```bash
cd client
npm install
npm run dev
# Listening on http://localhost:5173
```

Open [http://localhost:5173](http://localhost:5173), sign up, and start chatting.

---

## 5. Run with Docker Compose

```bash
# Build and start both services
docker compose up --build

# Run in the background
docker compose up --build -d
```

| Service | URL |
|---------|-----|
| Frontend | http://localhost |
| Backend API | http://localhost:8000 |

> **CORS note**: the FastAPI backend is configured to allow `http://localhost:5173`
> (Vite dev server). When running via Docker the frontend is served on port 80.
> Add `http://localhost` to the `allow_origins` list in `server/api/main.py`
> before building the Docker image.

To stop:

```bash
docker compose down
```

---

## 6. Project Structure

```
manufacturing-rag/
├── server/                  # FastAPI backend
│   ├── api/
│   │   ├── auth/            # Sign-up / sign-in routes
│   │   └── chat/            # Session + message routes
│   ├── core/
│   │   ├── ingestor.py      # PDF → Pinecone (run once)
│   │   ├── retriever.py     # Pinecone similarity search
│   │   └── generator.py     # LLM answer generation
│   ├── docs/                # Place your PDF documents here
│   ├── Dockerfile
│   └── pyproject.toml
├── client/                  # React + Vite frontend
│   ├── src/
│   │   ├── api/             # Axios API calls
│   │   ├── components/      # UI components
│   │   ├── pages/           # Auth + Chat pages
│   │   └── store/           # Zustand state (auth, chat)
│   ├── Dockerfile
│   └── vite.config.ts
└── docker-compose.yml
```
