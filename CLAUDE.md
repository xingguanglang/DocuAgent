# DocuAgent - AI-Powered Document Assistant

## Project Overview

DocuAgent is a full-stack intelligent document assistant combining RAG (Retrieval-Augmented Generation) with Agent tool-calling capabilities. Users upload documents, which are automatically chunked and embedded into a vector database. When users ask questions, the Agent autonomously decides whether to use RAG retrieval, execute code, query databases, or search the web, then generates answers with cited sources.

## Architecture

```
┌─────────────┐     ┌──────────────────────────────────────────────┐
│   React UI  │────▶│  FastAPI Backend                             │
│  (Vite+TS)  │ SSE │  ┌─────────┐  ┌──────────┐  ┌───────────┐  │
└─────────────┘◀────│  │ Auth    │  │ Chat API │  │ Doc API   │  │
                    │  │ (JWT)   │  │ (SSE)    │  │ (Upload)  │  │
                    │  └─────────┘  └────┬─────┘  └─────┬─────┘  │
                    │                    │               │         │
                    │              ┌─────▼─────┐  ┌─────▼─────┐  │
                    │              │  ReAct     │  │  RAG       │  │
                    │              │  Agent     │  │  Pipeline  │  │
                    │              │  Engine    │  │            │  │
                    │              └─────┬─────┘  └─────┬─────┘  │
                    │                    │               │         │
                    │  ┌─────────────────▼───────────────▼──────┐ │
                    │  │  Tools: RAG | Code | SQL | WebSearch   │ │
                    │  └────────────────────────────────────────┘ │
                    └──────────────┬──────────────┬───────────────┘
                                   │              │
                    ┌──────────────▼──┐  ┌───────▼────────┐
                    │  PostgreSQL     │  │  ChromaDB       │
                    │  (Users, Chat)  │  │  (Embeddings)   │
                    └─────────────────┘  └────────────────┘
```

## Tech Stack

| Layer          | Technology                              |
| -------------- | --------------------------------------- |
| Backend        | Python 3.11, FastAPI, Pydantic v2       |
| Agent/RAG      | LangChain / LangGraph                  |
| Vector DB      | ChromaDB                                |
| Relational DB  | PostgreSQL + SQLAlchemy                 |
| Frontend       | React 18, TypeScript, Tailwind CSS, Vite|
| LLM            | Claude API, OpenAI API (switchable)     |
| Deployment     | Docker Compose                          |
| Testing        | Pytest, React Testing Library           |
| CI/CD          | GitHub Actions                          |

## Code Standards

### Python (Backend)

- **Formatter/Linter**: Use `ruff` for formatting and linting. Configuration is in `pyproject.toml`.
- **Type Annotations**: Required on all function signatures. Use `from __future__ import annotations` in every module.
- **Docstrings**: Required for all public functions, classes, and modules. Use Google-style docstrings.
- **Pydantic**: Use Pydantic v2 for all request/response models. Never use `dict` for API boundaries.
- **Async**: All API endpoints and I/O-bound operations must be `async`.
- **Imports**: Use absolute imports from `app` package (e.g., `from app.config import settings`).

```python
# Good
async def retrieve_documents(query: str, top_k: int = 5) -> list[Document]:
    """Retrieve relevant documents for a query.

    Args:
        query: The search query string.
        top_k: Maximum number of documents to return.

    Returns:
        List of relevant documents ranked by relevance score.
    """
    ...

# Bad - missing types, no docstring, sync when it should be async
def retrieve_documents(query, top_k=5):
    ...
```

### TypeScript (Frontend)

- **Strict mode**: `strict: true` in `tsconfig.json`.
- **Components**: Functional components only, with explicit prop types via `interface`.
- **Styling**: Tailwind CSS utility classes. No inline styles. No CSS modules.
- **State**: React hooks + context. No Redux unless complexity demands it.

### API Design

- RESTful conventions: `GET /api/v1/documents`, `POST /api/v1/chat`.
- All endpoints return JSON with consistent envelope:
  ```json
  { "data": ..., "error": null }
  ```
- Error responses use HTTP status codes with structured error body:
  ```json
  { "data": null, "error": { "code": "NOT_FOUND", "message": "Document not found" } }
  ```
- Streaming responses (chat) use Server-Sent Events (SSE).

### Git Conventions

- **Commit messages**: Use [Conventional Commits](https://www.conventionalcommits.org/):
  - `feat:` new feature
  - `fix:` bug fix
  - `docs:` documentation
  - `refactor:` code change that neither fixes a bug nor adds a feature
  - `test:` adding or correcting tests
  - `chore:` maintenance tasks
- **Branch naming**: `feat/description`, `fix/description`, `refactor/description`.
- **PR policy**: All changes go through PR. Squash merge to `main`.

### Testing

- Every module must have corresponding unit tests.
- Tests live in `backend/tests/` mirroring the source structure.
- Use `pytest` with `pytest-asyncio` for async tests.
- Minimum test coverage target: 80%.
- Frontend tests use React Testing Library, not Enzyme.

## Development Commands

```bash
# Start all services
docker compose up --build

# Backend only (development)
cd backend && uvicorn app.main:app --reload --port 8000

# Frontend only (development)
cd frontend && npm run dev

# Run backend tests
cd backend && pytest -v

# Run linting
cd backend && ruff check . && ruff format --check .

# Run frontend tests
cd frontend && npm test
```

## Environment Variables

See `.env.example` for all required environment variables. Copy to `.env` before running:
```bash
cp .env.example .env
```
