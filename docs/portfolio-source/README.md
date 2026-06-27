# Portfolio Knowledge Pack

Public-safe Markdown sources for the KnowledgeForge **Portfolio Knowledge Base** collection (`slug: portfolio`).

## Source files

| File | Title |
|------|-------|
| `01_about.md` | About |
| `02_experience.md` | Professional Experience |
| `03_projects.md` | Projects |
| `04_skills.md` | Skills |
| `05_education.md` | Education |
| `06_career-focus.md` | Career Focus |
| `07_contact.md` | Contact |

These files intentionally exclude proprietary employer information, customer details, internal documents, and confidential technical material.

## Seed the Portfolio Knowledge Base

From the API directory, with your virtual environment activated and `apps/api/.env` configured:

### Dry run (no database writes)

```bash
cd apps/api
source .venv/bin/activate
python -m app.scripts.import_portfolio --dry-run
```

### Import / update documents

```bash
cd apps/api
source .venv/bin/activate
python -m app.scripts.import_portfolio
```

The import script:

- Discovers every `*.md` file in this directory
- Imports into the collection with slug `portfolio`
- Reuses the existing extract → chunk → embed pipeline
- Updates existing portfolio documents by filename instead of creating duplicates

## Custom source directory

```bash
python -m app.scripts.import_portfolio --source-dir /path/to/markdown/files
```

## Requirements

- Database schema applied (`apps/sql/001_initial_schema.sql`)
- `DATABASE_URL` set in `apps/api/.env`
- `OPENAI_API_KEY` set for embedding generation
- Portfolio collection seeded in the database

## Verify in chat

After import, open the frontend chat page, select **Portfolio Knowledge Base**, and ask questions such as:

- What is KnowledgeForge?
- What projects has Key'Shawn built?
- What is his educational background?
- What career areas is he focused on?
