# SlideNode Two-Phase Plan (Local First, Then GCP)

## Summary
Build and validate a complete local workflow first, then deploy to Google Cloud.

Primary sequence:
1. Local end-to-end validation (upload PDF -> async pipeline -> structured deck -> edit -> markdown export)
2. GCP deployment with Cloud Run-based services

Key priorities:
- High knowledge-point coverage
- Mandatory citation for every bullet
- Traceable evidence and stable pipeline behavior

## Scope
### In Scope (Current)
1. PDF upload and async processing (up to 200 pages)
2. Fixed 8-step pipeline
3. Three-level output hierarchy
4. Citation enforcement
5. Basic in-app editing
6. Markdown export and web reading
7. Auth scaffold and user-level document history

### Out of Scope (Current)
1. Video input/transcription
2. Native PPTX export
3. Collaboration features
4. Enterprise private deployment

## Finalized Decisions
1. Local goal this week: run full workflow successfully
2. Cloud target: Google Cloud Run (managed)
3. Async queue on cloud: keep Celery + Redis first
4. Database now: SQLite for local/dev validation
5. Cloud database note: SQLite on Cloud Run is demo-only; production should move to Cloud SQL Postgres

## Phase 1: Local Validation
### Objectives
1. Make full pipeline runnable locally
2. Confirm quality gates and error handling
3. Validate user flow from upload to export

### Success Criteria
1. At least 3 sample PDFs complete end-to-end
2. `citation_completeness = 1.0` for successful jobs
3. `coverage_ratio >= 0.85`
4. Markdown export contains structure and citations

### Local Runtime Components
1. Frontend: React + Vite
2. API: FastAPI
3. Worker: Celery
4. Queue/Broker: Redis
5. Object storage: MinIO (S3-compatible)
6. Database: SQLite (scaffold mode)

## Phase 2: GCP Deployment (Cloud Run)
### Target Topology
1. Frontend service on Cloud Run
2. API service on Cloud Run
3. Worker service on Cloud Run (same image, different command)
4. Redis on Memorystore
5. Object storage on GCS (or S3-compatible adapter against GCS)
6. Secrets in Secret Manager

### Deployment Order
1. Provision Memorystore Redis
2. Configure storage bucket and service account access
3. Deploy API container
4. Deploy Worker container
5. Deploy Frontend container
6. Run end-to-end verification tests on cloud

### Cloud Constraints
1. Cloud Run filesystem is ephemeral
2. SQLite file persistence is not reliable on Cloud Run
3. SQLite cloud usage is allowed only for short-lived demos
4. For stable cloud usage, plan migration to Cloud SQL Postgres

## Pipeline Definition (Fixed 8 Steps)
1. ingest_pdf
2. parse_pdf
3. extract_facts
4. merge_dedupe
5. build_outline
6. write_annotations
7. align_citations_validate
8. persist_export

## Public APIs (Stable)
1. `POST /v1/documents`
2. `GET /v1/jobs/{job_id}`
3. `GET /v1/documents`
4. `GET /v1/documents/{id}/slides`
5. `PATCH /v1/documents/{id}/slides`
6. `GET /v1/documents/{id}/export.md`

## Types/Interfaces (Stable)
1. `DeckOut`
2. `SectionOut`
3. `SubsectionOut`
4. `BulletOut` with `CitationOut[]`
5. `QualityReport`

## Data Model
1. users
2. documents
3. jobs
4. source_spans
5. deck_sections
6. deck_subsections
7. deck_bullets
8. bullet_citations
9. edits_log (next iteration)

## Quality Gates (Hard)
1. Every bullet must have at least one citation
2. Coverage ratio must be >= 0.85
3. Page limit <= 200
4. Output must remain exactly 3 levels
5. Output language defaults to source language

## Error Codes
1. DOC_TOO_LARGE
2. PARSE_FAILED
3. LLM_OUTPUT_INVALID
4. CITATION_INCOMPLETE
5. QUALITY_GATE_FAILED
6. GEN_TIMEOUT
7. STORAGE_ERROR
8. AUTH_REQUIRED

## Retry Policy
1. `extract_facts` and `build_outline`: up to 2 retries
2. On second retry, reduce chunk size
3. `LLM_OUTPUT_INVALID`: one format-repair retry
4. Never bypass quality gates after retries

## Test Plan
### Unit
1. Chunk and page mapping correctness
2. Citation attachment validation
3. Deck schema serialization/deserialization
4. Edit patch validation

### Integration
1. Upload -> queue -> process -> result flow
2. 200-page boundary behavior
3. Retry behavior and error code propagation
4. Markdown export with valid footnotes

### E2E
1. Upload and successful generation path
2. Edit and persistence after refresh
3. Citation reference correctness in UI/export

## Milestones
1. M1: Local baseline and environment stability
2. M2: Pipeline reliability and quality gate hardening
3. M3: Cloud Run deployment and connectivity
4. M4: Cloud validation and production migration prep (Cloud SQL)

## Assumptions and Defaults
1. Input remains PDF-only in current release
2. Model policy remains medium-cost, stable-quality
3. Citation completeness is mandatory
4. Celery + Redis remains the first cloud queue strategy
5. Video support later adds transcription before current pipeline
