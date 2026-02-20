# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What is SlideNode

A pipeline-first learning app that transforms PDFs into structured teaching slides (section → subsection → citation-backed bullets). Extracts text, images, and LaTeX formulas from academic PDFs. Two-phase rollout: local validation first, then GCP Cloud Run.

## Commands

All backend commands assume cwd is `backend/`. The venv is at `backend/.venv` (use the `python3.12` binary — the venv also contains a 3.14 symlink that lacks some compiled deps).

```bash
# Docker Compose (starts API, Worker, Redis, MinIO, Frontend)
make local-up          # build & start all services
make local-down        # stop
make local-logs        # tail logs

# Non-Docker local dev (preferred for iteration)
make dev-backend       # uvicorn on :8000 (auto-reload)
make dev-frontend      # Vite dev server on :5173
make dev-test          # cd backend && PYTHONPATH=. pytest tests/ -v

# Backend (from backend/)
cd backend && PYTHONPATH=. .venv/bin/python3.12 -m pytest tests/ -v       # all tests
cd backend && PYTHONPATH=. .venv/bin/python3.12 -m pytest tests/test_health.py  # single file

# Frontend (from frontend/)
npm run dev            # dev server :5173
npm run build          # tsc + vite build

# Celery worker (from backend/)
celery -A app.workers.celery_app worker --loglevel=info
```

For non-Docker dev, set `STORAGE_BACKEND=local` in `backend/.env` (MinIO won't be running). SQLite is the default DB (`sqlite:///./slidenode.db`); tables auto-create on app startup.

**Python version note:** pydantic-core requires Python ≤3.13 to build wheels. Use the `python3.12` binary in the venv.

## Architecture

**Stack:** FastAPI + SQLAlchemy (backend), Celery + Redis (queue), React + Vite + TypeScript (frontend), pluggable storage (local/S3/GCS), pluggable LLM (Anthropic-compatible/OpenAI-compatible/mock).

### Processing Pipeline (`backend/app/services/pipeline.py`)

```
ingest_pdf → parse_pdf (text + images) → language_detect → extract_images & detect_formulas
  → extract_facts (LLM) → fuzzy_dedupe → build_outline (LLM) → write_annotations (LLM)
  → align_citations → persist
```

- PDF text + image extraction via PyMuPDF (`services/pdf_parser.py`), text chunked by token count (default 1200 tokens)
- Image extraction per page via `page.get_images()` + `doc.extract_image(xref)`, returns `ParsedImage` dataclasses alongside `ParsedChunk`
- Formula detection via pix2tex (`services/formula.py`) — lazy-loaded `LatexOCR` singleton, heuristic pre-filter (size, aspect ratio, background brightness), returns LaTeX string or `None`
- Detected formulas are injected as `FactCandidate` entries (fact_id=`formula_{id}`) so the LLM includes them in the outline
- Language detection via `langdetect` on first 5 chunks, stored in `Document.language`
- LLM fact extraction (`services/llm.py`) — up to 8 structured facts per chunk, JSON-validated
- Fuzzy dedup via `thefuzz.fuzz.token_sort_ratio` (threshold from `dedupe_threshold` setting, default 0.86)
- LLM outline building — organizes facts into 3–8 sections with 1–5 subsections each
- LLM annotations — 1–3 sentence teaching notes per subsection (graceful fallback to empty on failure)
- Citation snippets found via keyword-overlap sliding window (`_find_best_snippet`)
- Formula bullets without text-based source get synthetic citations referencing the source page
- Jobs run via Celery; automatic fallback to inline execution if Redis/queue unavailable

### LLM Client (`backend/app/services/llm.py`)

Three LLM operations, each with a `mock` mode for testing without API keys:
- `extract_facts()` — fact extraction from text chunks
- `build_outline()` — organize facts into section/subsection structure
- `write_annotations()` — teaching annotations per subsection

Common low-level method `_call_llm_raw(system, user)` dispatches to OpenAI-compatible or Anthropic endpoint. JSON parsing handles markdown code fences and brace-balanced extraction.

Set `LLM_PROVIDER=mock` for offline development. Current production config uses OpenRouter (`LLM_BASE_URL=https://openrouter.ai/api/v1`).

### Data Model (`backend/app/models/entities.py`)

```
User → Document → Job (processing status)
              → DocumentImage (extracted images, formula LaTeX)
              → DeckSection → DeckSubsection → DeckBullet → BulletCitation → SourceSpan
                                                  ↘ image_id (FK) → DocumentImage
```

`SourceSpan` is linked to `Document` directly (no cascade from Document delete — must be deleted manually). `DocumentImage` cascades from `Document`. All other relationships cascade from `Document`.

`DeckBullet.image_id` is a nullable FK to `DocumentImage`, linking formula/figure bullets to their source image.

### Key Backend Paths

- `app/api/routes.py` — all REST endpoints (prefixed `/v1`)
- `app/core/config.py` — Pydantic BaseSettings, loads from `.env`
- `app/services/pipeline.py` — full pipeline orchestration
- `app/services/llm.py` — LLM client with extract/outline/annotate operations
- `app/services/pdf_parser.py` — PyMuPDF-based text + image extraction
- `app/services/formula.py` — pix2tex formula detection (lazy singleton)
- `app/services/pptx_export.py` — PPTX generation (16:9 slides, section dividers, auto-pagination at 6 bullets, image embedding)
- `app/services/storage.py` — storage abstraction (local/S3-MinIO/GCS)
- `app/services/auth.py` — Auth0 scaffold (`AUTH0_SKIP_VERIFY=true` skips JWT decoding, auto-creates dev users)
- `app/workers/tasks.py` — Celery task wrapping `PipelineService.run()`

### Frontend

- `src/App.tsx` — state management, job polling (5s interval), upload/export handlers
- `src/api/client.ts` — API client with auth header injection
- `src/components/DeckEditor.tsx` — three-level inline editing with save, Markdown export, PPTX export
- `src/types/index.ts` — TypeScript types mirroring backend schemas

## API Endpoints

```
POST   /v1/documents                            — upload PDF, create document & queue job
GET    /v1/jobs/{job_id}                        — poll job status/progress
GET    /v1/documents                            — list user's documents
GET    /v1/documents/{id}/slides                — fetch full deck structure
PATCH  /v1/documents/{id}/slides                — update deck content
GET    /v1/documents/{id}/export.md             — export as Markdown
GET    /v1/documents/{id}/export.pptx           — export as PowerPoint
GET    /v1/documents/{id}/images/{image_id}     — serve extracted image
DELETE /v1/documents/{document_id}              — delete document + images
GET    /healthz                                 — health check (no auth)
```

## Quality Gates

- Every bullet must have ≥1 citation (`citation_completeness = 1.0`)
- `coverage_ratio ≥ 0.85` (configurable via `quality_coverage_threshold`)
- Page limit ≤ 200
- Output: exactly 3 levels (section/subsection/bullet)
- Output language follows source document language

## Error Codes

DOC_TOO_LARGE, PARSE_FAILED, LLM_OUTPUT_INVALID, CITATION_INCOMPLETE, QUALITY_GATE_FAILED, GEN_TIMEOUT, STORAGE_ERROR, AUTH_REQUIRED

## Environment

- Backend env: `backend/.env` (copy from `backend/.env.example`)
- Frontend env: `frontend/.env` (copy from `frontend/.env.example`)
- `LLM_PROVIDER=mock` for tests/dev without an API key
- `AUTH0_SKIP_VERIFY=true` (default) for dev without Auth0
- `STORAGE_BACKEND=local` for dev without MinIO/S3

## Docker Services (`infra/docker-compose.yml`)

API (:8000), Worker (Celery), Redis (:6379), MinIO (:9000 API / :9001 console), Frontend (:5173)
