# coderAI Development Guidelines

Auto-generated from all feature plans. Last updated: 2025-11-23

## Active Technologies
- Python 3.11+ + FastAPI 0.100+, SQLAlchemy 2.0, Pydantic V2, LangChain 0.3+ (multi-provider LLM), OpenAI Python SDK (002-backend-implementation)
- PostgreSQL 15+ (primary database), Redis 7+ (job queue — TBD) (002-backend-implementation)
- Document Ingestion: PyMuPDF (PDF), python-docx (DOCX), pandas + pyarrow (CSV/JSON/Parquet) (002-backend-implementation)
- Export: pandas + openpyxl (CSV + Excel) (002-backend-implementation)

- TypeScript 5.6+ with Next.js 15 (App Router), React 19 + Next.js 15, React 19, TypeScript 5.6, Tailwind CSS 4.0, shadcn/ui, Zustand (state management), TanStack Query (data fetching), TanStack Table (data grids) (001-complete-user-workflow)

## Project Structure

```text
src/
tests/
```

## Commands

npm test && npm run lint

## Code Style

TypeScript 5.6+ with Next.js 15 (App Router), React 19: Follow standard conventions

## Pipeline Architecture
- Backend implements a user-configurable corpus processing pipeline (see ai_agent_reference.md)
- Each project defines its own domain, extraction targets, and variables via the UI
- LLM assistant configs are auto-generated from variable definitions
- Pipeline stages: Ingestion → Extraction → Enrichment → Post-Processing → Storage → Export
- Deferred (v2): Duplicate detection, external API enrichment, advanced job queue

## Recent Changes
- 002-backend-implementation: Pipeline architecture alignment (LangChain, multi-format ingestion, auto-generated configs)
- 002-backend-implementation: Added Python 3.11+ + FastAPI 0.100+, SQLAlchemy 2.0, Pydantic V2, LangChain 0.3+, OpenAI Python SDK

- 001-complete-user-workflow: Added TypeScript 5.6+ with Next.js 15 (App Router), React 19 + Next.js 15, React 19, TypeScript 5.6, Tailwind CSS 4.0, shadcn/ui, Zustand (state management), TanStack Query (data fetching), TanStack Table (data grids)

<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
