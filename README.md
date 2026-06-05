# Defense Logistics Knowledge Intelligence Platform (DLKIP)

> An AI knowledge-retrieval platform that ingests operational documents, indexes them with vector embeddings, and answers questions with **source-grounded RAG**, plus a deterministic **exact-code lookup** that returns every record referencing a product code in under a second.

I built this for a naval logistics use case: teams were losing real time manually hunting through documents to confirm the right product code before a shipment. So the platform does two complementary things, semantic search when you're exploring, and exact, auditable code lookup when you need certainty. Ask it about a National Stock Number like `7810-00-995-2055` and it instantly tells you it maps to a **Football**, and shows every document that references it.

---

## Features

- **Document ingestion at scale** — ingests **10K+** operational documents (PDF/HTML), with **OCR text extraction**, chunking, and metadata enrichment.
- **Source-grounded RAG** — indexes content with vector embeddings (**Qdrant**) and answers questions with inline citations, so every answer is traceable back to its source.
- **Deterministic exact-code retrieval** — surfaces *every* record referencing a product code (e.g., `DDR333`, or NSN `7810-00-995-2055 → Football`) in **<1s**, eliminating manual lookup and cutting shipment errors.
- **Hybrid search** — fuses keyword and vector similarity, with a query router that picks exact lookup vs. semantic retrieval automatically.
- **Auth & RBAC** — JWT access/refresh tokens with role-based access control (Admin, Knowledge Manager, Logistics Officer, Viewer) enforced at the gateway.
- **Air-gapped or cloud** — runs with self-hosted local embeddings and no outbound calls when deployed in `airgapped` mode, important for defense contexts.
- **Single-service deploy** — the Express gateway serves the built React UI, so the whole app runs as one web service (no CORS in production).

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | React 18, Vite 5, TypeScript |
| Backend | Node.js, Express 4, TypeScript, JWT, bcryptjs, multer, axios |
| AI Layer | Python, FastAPI, Uvicorn, Pydantic, httpx |
| Vector DB | Qdrant |
| Database | MongoDB |
| File Storage | Cloudinary (cloud) / MinIO (air-gapped) |
| LLM | Hosted API (cloud) / vLLM or Ollama (air-gapped) |
| Deployment | Docker, Docker Compose |
| Testing | pytest (ai-service), node:test (backend) |

---

## Architecture

```
                          User (React SPA)
                                |
                                v
                    Node.js API Gateway (Express + TS)
                    - Auth / RBAC / request routing
                                |
            +-------------------+-------------------+
            |                   |                   |
            v                   v                   v
     Object Storage      MongoDB (metadata,    Python AI Service (FastAPI)
     (Cloudinary OR      users, chunks,        - Text extraction / OCR
      MinIO on-prem)     audit logs)           - Chunking / embeddings
                                               - RAG generation
                                               - Exact code index
                                                       |
                                          +------------+------------+
                                          v                         v
                                   Qdrant (vectors)         LLM (cloud OR
                                                            self-hosted vLLM)
```

The frontend builds into `backend/frontend/dist`, and the Express gateway serves that build, so the whole app runs as a single web service on port 4000. See [`prd.md`](./prd.md) for the full product requirements (v2.0).

---

## Installation

Prerequisites: **Node.js 18+**, **Python 3.11+**, and (optional) **Docker** for the full stack.

```bash
git clone https://github.com/theBrainly/navy-rag.git
cd navy-rag
```

### AI service

```bash
cd ai-service
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Backend gateway + UI

```bash
cd backend
npm install
npm run build:frontend     # builds the React app into frontend/dist
npm run dev                # http://localhost:4000  (serves UI + API)
```

The AI service runs standalone with in-memory fallbacks, so no Qdrant or LLM keys are required for local development.

---

## Environment Setup

Copy `.env.example` to `.env` and adjust. The key switch is `DEPLOYMENT_MODE=cloud|airgapped` (see PRD Section 11). In `airgapped` mode the platform uses local embeddings and a self-hosted LLM with no outbound calls.

```bash
cp .env.example .env
```

---

## Usage

1. Start the AI service and the backend gateway (see Installation).
2. Open http://localhost:4000 and sign in with a seed account (`admin@dlkip.mil` / `admin123`).
3. Seed sample defense-catalog documents (AI service must be running):

   ```bash
   cd ai-service && python -m app.seed
   ```

4. Try a **semantic** question (*"What is DDR333 used for?"*) for a synthesized, cited answer, or an **exact code** query (*"DDR333"*) to enumerate every record that references it.

---

## Project Structure

```
navy/
  prd.md                Product Requirements Document (v2.0)
  docker-compose.yml    Qdrant + MongoDB + AI service + web
  .env.example          Configuration template
  ai-service/           Python / FastAPI — RAG core
    app/
      services/         chunking, embeddings, vector store, code index, LLM
      pipeline.py       end-to-end processing + retrieval pipeline
      seed.py           sample document loader
    tests/              pytest suite
  backend/              Node / Express / TypeScript — API gateway
    src/
      auth.ts           JWT + RBAC
      routes/           auth, documents, search, ask, analytics
      aiClient.ts       AI-service client
    frontend/           React / Vite SPA (built and served by the backend)
      src/components/   Login, Search, Upload
```

---

## Development

```bash
# AI service tests
cd ai-service && python -m pytest

# Backend type-check / tests
cd backend && npm run typecheck && npm test
```

---

## Deployment

```bash
docker compose up --build
```

Brings up Qdrant, MongoDB, the AI service, and the web service (backend gateway that also serves the built React UI) on http://localhost:4000.

---

## API Documentation

Gateway endpoints (see PRD Section 7 for the full table):

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/login` | Authenticate, return tokens |
| POST | `/api/auth/refresh` | Refresh access token |
| POST | `/api/documents` | Upload a document |
| GET | `/api/documents` | List documents |
| POST | `/api/search/semantic` | Semantic RAG query |
| POST | `/api/search/code` | Exact code lookup (full enumeration) |
| POST | `/api/search/hybrid` | Hybrid search |
| POST | `/api/ask` | RAG answer with sources |
| GET | `/api/analytics` | Dashboard metrics |

---

## Future Enhancements

- **Phase 2:** Voice search, multilingual search, AI agents.
- **Phase 3:** Knowledge Graph RAG, fine-tuning dataset generation, quality analyzer.
- **Phase 4:** Automated dataset curation, synthetic data generation, benchmark leakage detection.

---

## Why it's interesting

Most RAG demos stop at "ask a question, get a fuzzy answer." Real logistics work needs **both** fuzzy and exact: semantic retrieval for open questions *and* deterministic, complete code lookup where a missed record means a wrong shipment. DLKIP combines the two behind one interface, with full provenance and an air-gapped mode for sensitive deployments.

---

## License

Released under the MIT License.
