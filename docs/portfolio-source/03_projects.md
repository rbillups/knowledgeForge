# Projects

**Category:** Personal and academic projects

Selected projects that demonstrate backend systems, AI-enabled product work, mobile development, and applied machine learning.

---

## KnowledgeForge

**Status:** Active personal project  
**Live demo:** Public portfolio assistant on [rkbillups.com](https://rkbillups.com)

### Overview

Citation-grounded AI knowledge assistant for answering questions from approved source documents with supporting excerpts.

### Problem addressed

Portfolio and document Q&A needs trustworthy answers tied to source material—not generic model responses without traceability.

### Technical approach

- Document ingestion and text extraction
- Chunking and embedding generation
- Semantic retrieval with vector search
- Grounded answer generation with source citations
- Privacy guardrails, evaluation coverage, and a restricted public API surface for portfolio use

### Key capabilities

- Upload and index Markdown and other supported documents
- Semantic search over embedded chunks
- Grounded chat responses with citation metadata
- Public portfolio assistant endpoint for [rkbillups.com](https://rkbillups.com)
- Rate limiting and public-mode API lockdown for production deployment

### Stack

Next.js, TypeScript, Python, FastAPI, Supabase PostgreSQL with pgvector, OpenAI embeddings, Railway, Vercel

### Notes

KnowledgeForge is an active personal project and portfolio demonstration—not an enterprise SaaS product or multi-tenant production platform.

---

## NextUp

**Status:** Personal project (in development)

### Overview

Mobile app for pickup basketball coordination—finding courts, organizing runs, and coordinating attendance.

### Problem addressed

Pickup games are hard to organize without a shared view of nearby courts, active runs, and who is coming.

### Technical approach

- Location-aware court discovery
- Run creation and RSVP coordination
- Mobile-first social coordination flows backed by a managed database

### Key capabilities

- Discover nearby basketball courts
- Create and join pickup runs
- RSVP and coordinate attendance with other players

### Stack

React Native, Expo, TypeScript, Supabase, PostgreSQL

---

## Face Mask Detection

**Status:** Academic / personal computer-vision project

### Overview

Computer-vision classifier project using Python and convolutional neural network (CNN) techniques.

### Problem addressed

Binary image classification to detect whether a face mask is present in an image.

### Technical approach

- Python-based machine learning pipeline
- CNN model training and inference for image classification
- Dataset preparation, model evaluation, and iterative refinement

### Key capabilities

- Image preprocessing and model inference workflow
- CNN-based classification for face mask detection
- Project originally developed in **2022** and modernized in **2026**

### Stack

Python, CNN / machine learning, computer vision

### Notes

No benchmark results or production deployment claims are documented in this portfolio material.
