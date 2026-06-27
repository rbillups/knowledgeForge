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

## Evaluate the Portfolio Knowledge Base

Grounded AI systems should be tested against a fixed evaluation dataset before public deployment. The portfolio evaluation suite calls the same `grounded_chat()` service used by `POST /api/v1/chat`, then checks whether supported questions cite the expected source documents and whether unsupported questions safely refuse to answer.

Evaluation dataset: `docs/evals/portfolio_eval_cases.json`

```bash
cd apps/api
source .venv/bin/activate
python -m app.scripts.run_portfolio_eval
python -m app.scripts.run_portfolio_eval --verbose
python -m app.scripts.run_portfolio_eval --fail-on-error
```

Results are written to `reports/portfolio-eval-results.json`.

## Portfolio Collection Hygiene

The Portfolio Knowledge Base should contain only intentional, public-safe source material. Temporary development files such as `test-notes.md` or ad hoc uploads should be removed before public deployment so they do not affect retrieval, chat answers, or evaluation results.

Use the `/documents` page or `DELETE /api/v1/documents/{document_id}` to remove unwanted documents. Deletion removes associated chunks, embeddings, and the stored upload file for that document.

To review what is currently indexed:

```bash
curl http://localhost:8000/api/v1/documents
```

Or open the Documents page in the web app and review filenames, source types, and collection names.

## Local Development Configuration

Copy the backend environment template and configure local values:

```bash
cp apps/api/.env.example apps/api/.env
```

Recommended local settings:

| Variable | Local value |
| --- | --- |
| `APP_ENV` | `development` |
| `STORAGE_PROVIDER` | `local` |
| `DATABASE_URL` | Your Supabase Postgres connection string |
| `OPENAI_API_KEY` | Your OpenAI API key |
| `CORS_ALLOWED_ORIGINS` | `http://localhost:3000` |

Local uploads are stored under `apps/api/uploads/` using storage keys shaped like `{document_id}/{filename}`.

**Never commit `.env` files, service-role keys, or database passwords.**

## Production Environment Checklist

Set these variables in your deployment platform before going live:

| Variable | Required | Notes |
| --- | --- | --- |
| `APP_ENV` | Yes | Must be `production` |
| `STORAGE_PROVIDER` | Yes | Use `supabase` for durable cloud storage |
| `DATABASE_URL` | Yes | Supabase Postgres connection string |
| `OPENAI_API_KEY` | Yes | Server-side only |
| `CORS_ALLOWED_ORIGINS` | Yes | Explicit public frontend origins, comma-separated |
| `SUPABASE_URL` | Yes for Supabase storage | Project URL |
| `SUPABASE_SERVICE_ROLE_KEY` | Yes for Supabase storage | Server-side only, never expose to frontend |
| `SUPABASE_STORAGE_BUCKET` | Yes for Supabase storage | Private bucket for uploaded documents |
| `CHAT_RATE_LIMIT_MAX_REQUESTS` | Optional | Default `20` |
| `CHAT_RATE_LIMIT_WINDOW_SECONDS` | Optional | Default `600` (10 minutes) |

## Supabase Storage Setup

For production:

1. Create a private Supabase Storage bucket for document uploads.
2. Configure the backend with `STORAGE_PROVIDER=supabase`.
3. Provide `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`, and `SUPABASE_STORAGE_BUCKET`.
4. Keep the service-role key on the backend only.

The API stores durable object keys such as `{document_id}/{filename}` and does not persist signed URLs.

## Rate Limiting

`POST /api/v1/chat` is protected by a simple in-memory rate limiter intended as a first deployment safeguard:

- Default: **20 requests per 10 minutes per client IP**
- IP addresses are used only transiently for counting and are **not stored**
- Returns HTTP **429** when limited

This limiter is process-local. It is **not** a distributed production rate-limiting system. Replace it with edge or Redis-backed limiting before high-traffic public launch.

## Deployment Readiness Checklist

Before deploying the portfolio assistant publicly:

1. Run the full backend test suite: `pytest -v`
2. Run the portfolio evaluation suite: `python -m app.scripts.run_portfolio_eval --fail-on-error`
3. Confirm readiness: `GET /api/v1/health/ready` returns `ready: true`
4. Verify production CORS origins are explicit (no wildcard)
5. Configure Supabase Storage for durable uploads
6. Remove temporary or duplicate portfolio documents
7. Confirm privacy guardrails pass in the evaluation suite
8. Set frontend `NEXT_PUBLIC_API_URL` to the public API URL
9. Keep secrets out of frontend code, logs, and git

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
