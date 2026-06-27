# KnowledgeForge

A citation-grounded AI knowledge assistant platform built with Next.js, FastAPI, PostgreSQL, pgvector, Docker, and GitHub Actions.

## Goal

KnowledgeForge lets users upload documents, ask questions, and receive answers grounded in retrieved source content with visible citations.

The first deployment will support a public portfolio knowledge base containing professional background, projects, skills, and public documentation.

## Seed the Portfolio Knowledge Base

Public-safe portfolio Markdown files live in `docs/portfolio-source/`.

```bash
cd apps/api
source .venv/bin/activate
python -m app.scripts.import_portfolio --dry-run
python -m app.scripts.import_portfolio
```

See [docs/portfolio-source/README.md](docs/portfolio-source/README.md) for details.

## Planned Stack

- Frontend: Next.js, TypeScript, Tailwind CSS
- Backend: Python, FastAPI
- Database: PostgreSQL with pgvector
- AI: LLM and embedding APIs
- Local development: Docker Compose
- Testing: PyTest
- CI: GitHub Actions

## MVP Features

- Document upload and indexing
- Citation-grounded question answering
- Source excerpt review
- Feedback capture
- Dockerized local development
- Automated tests and CI checks
