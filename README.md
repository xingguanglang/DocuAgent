# DocuAgent

AI-powered document assistant combining RAG retrieval with Agent tool-calling. Upload documents, ask questions, and get answers with cited sources.

## Features

- **Document Upload** — PDF, Markdown, and plain text. Auto chunking + embedding.
- **RAG Retrieval** — Hybrid vector + BM25 search with cross-encoder reranking.
- **Agent Tools** — RAG search, code execution, SQL queries, web search.
- **Streaming Chat** — SSE-based real-time responses with agent reasoning trace.
- **Multi-LLM** — Switch between Claude and OpenAI APIs.

## Quick Start

```bash
# 1. Clone and configure
cp .env.example .env
# Edit .env with your API keys

# 2. Start all services
docker compose up --build

# 3. Open the app
# Frontend: http://localhost:5173
# Backend API: http://localhost:8000
# API docs: http://localhost:8000/docs
```

## Development

```bash
# Backend
cd backend
pip install -e ".[dev]"
uvicorn app.main:app --reload --port 8000

# Frontend
cd frontend
npm install
npm run dev

# Tests
cd backend && pytest -v
cd frontend && npm test
```

## Tech Stack

| Layer | Tech |
|-------|------|
| Backend | Python 3.11, FastAPI, LangChain/LangGraph |
| Vector DB | ChromaDB |
| Database | PostgreSQL |
| Frontend | React 18, TypeScript, Tailwind CSS, Vite |
| LLM | Claude API, OpenAI API |
| Deploy | Docker Compose |

## Project Structure

```
├── backend/
│   ├── app/
│   │   ├── main.py           # FastAPI entry point
│   │   ├── config.py          # Pydantic Settings
│   │   ├── api/routes/        # REST endpoints
│   │   ├── rag/               # RAG pipeline (loader, chunker, embedder, retriever, reranker)
│   │   ├── agent/             # ReAct agent engine + tools
│   │   ├── models/            # Pydantic schemas + SQLAlchemy models
│   │   └── services/          # LLM + vector store services
│   └── tests/
├── frontend/
│   └── src/
│       ├── components/        # React UI components
│       ├── hooks/             # useSSE streaming hook
│       ├── services/          # API client
│       └── types/             # TypeScript definitions
├── docker-compose.yml
├── CLAUDE.md
└── .env.example
```

## License

MIT
