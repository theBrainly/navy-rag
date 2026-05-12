# Product Requirements Document (PRD)

# Defense Logistics Knowledge Intelligence Platform (DLKIP)

## Version

2.0

## Product Type

Enterprise AI Knowledge Retrieval & Document Intelligence Platform

---

# 1. Executive Summary

Defense Logistics Knowledge Intelligence Platform (DLKIP) is an AI-powered enterprise
knowledge system designed to help logistics personnel quickly retrieve product codes,
shipping classifications, inventory information, operational procedures, and procurement
details from large collections of documents.

The platform ingests PDFs, catalogs, manuals, spreadsheets, and operational documents,
converts them into searchable knowledge using vector embeddings, and provides accurate
source-grounded answers using Retrieval-Augmented Generation (RAG).

The platform serves two distinct retrieval needs:

1. **Conversational Q&A (RAG):** "What is DDR333 used for?" returns a synthesized,
   source-grounded answer.
2. **Exact Code Lookup (Structured Retrieval):** "DDR333" returns every record and
   document that references that code, with no information dropped.

The goal is to reduce the time required to find information from hours to seconds.

---

# 2. Problem Statement

Organizations maintain thousands of documents containing:

* Product codes
* Inventory catalogs
* Procurement manuals
* Shipping classifications
* Technical documentation
* Operational procedures

Personnel often spend significant time searching through documents to locate the correct
product or shipment information.

Problems include:

* Slow document search
* Duplicate documents
* Knowledge silos
* Human errors
* Poor discoverability
* Manual lookup processes
* **Exact code matches lost inside semantic ranking** (a product code may exist in 30
  documents, but a pure RAG system returns only the top few)

---

# 3. Objectives

### Business Objectives

* Reduce search time by 90%
* Improve operational efficiency
* Centralize organizational knowledge
* Eliminate duplicate documentation
* Improve retrieval accuracy

### Technical Objectives

* Semantic document retrieval
* **Deterministic exact-code lookup with full enumeration**
* Enterprise document management
* Source-grounded AI responses
* Metadata extraction
* Duplicate detection
* Dataset quality analysis

---

# 4. User Roles

| Role | Responsibilities |
|------|------------------|
| **Admin** | Upload documents, manage users, configure AI settings, view analytics |
| **Knowledge Manager** | Organize documents, validate metadata, monitor document quality |
| **Logistics Officer** | Search product codes, verify shipment classifications, access procedures |
| **Viewer** | Search knowledge base, view AI responses |

Role-Based Access Control (RBAC) is enforced at the API gateway. Each role maps to a
permission set; permissions are checked per route.

---

# 5. System Architecture

```
                          User (React SPA)
                                |
                                v
                    Node.js API Gateway (Express + TS)
                    - Auth / RBAC / Rate limiting
                    - Request routing
                                |
            +-------------------+-------------------+
            |                   |                   |
            v                   v                   v
     Object Storage      MongoDB (metadata,    Python AI Service (FastAPI)
     (Cloudinary OR      users, chunks,        - Text extraction / OCR
      MinIO on-prem)     audit logs)           - Chunking
                                               - Embeddings
                                               - RAG generation
                                               - Exact code index
                                                       |
                                          +------------+------------+
                                          v                         v
                                   Qdrant (vectors)         LLM (cloud OR
                                                            self-hosted vLLM)
```

The deployment topology is selectable at install time: **Cloud mode** (Cloudinary + hosted
LLM) or **Air-gapped mode** (MinIO + self-hosted vLLM/Ollama). See Section 11.

---

# 6. Functional Requirements

## Module A: Authentication & Authorization

* Login / Logout
* JWT access tokens + refresh tokens
* Role-Based Access Control (Admin, Knowledge Manager, Logistics Officer, Viewer)
* Password hashing (bcrypt/argon2)
* Account lockout after repeated failures

---

## Module B: Document Management

Supported formats: PDF, DOCX, TXT, XLSX, CSV, PNG, JPG.

Upload flow:

```
User Upload -> Object Storage -> MongoDB metadata record -> Processing Queue
```

MongoDB stores metadata, processing status, and ownership. Object storage holds the
original binary.

---

## Module C: Storage Integration

Abstracted behind a `StorageProvider` interface with two implementations:

* **CloudinaryProvider** (cloud mode)
* **MinioProvider** (air-gapped mode)

Buckets/folders: `documents/`, `catalogs/`, `manuals/`, `inventory/`.
Features: upload, preview URL, download URL, versioning, change logs.

---

## Module D: Document Processing Pipeline

* Text extraction: PDF, DOCX, spreadsheets
* OCR for scanned documents (Tesseract)
* Table and product-code extraction
* Cleaning: strip headers/footers/noise, normalize dates and codes
* Idempotent and resumable; processing status tracked per document

---

## Module E: Metadata Extraction

Automatically identify and store:

* Product Code (e.g., `DDR333`)
* Product Name / Category (e.g., Football Equipment)
* Department, Country, Shipment Type, Effective Date

Extraction uses regex/dictionary rules for known code formats plus LLM-assisted extraction
for unstructured text. Every extracted code is written to the **Code Index** (Module H2).

---

## Module F: Chunking Engine

```
Document -> Page -> Paragraph -> Chunk
```

Stores: chunk text, chunk ID, page number, document reference, and any product codes found
in the chunk. Configurable chunk size and overlap.

---

## Module G: Embedding Engine

* Models: BGE-Large, E5-Large, or Sentence Transformers (configurable)
* Embeddings stored in Qdrant with chunk metadata as payload
* Batch embedding with retry/backoff

---

## Module H: Retrieval

### H1: Vector / Semantic Search

```
Query -> Embedding -> Qdrant ANN search -> Ranked chunks
```

### H2: Exact Code Lookup (NEW)

A deterministic inverted index (MongoDB collection `code_index`) maps each normalized
product code to **every** chunk and document that references it.

```
Query "DDR333" -> normalize -> code_index lookup -> ALL matching records (no truncation)
```

Returns complete enumeration, grouped by document, with page numbers and metadata.

### H3: Hybrid Search

Combines BM25/keyword + vector similarity with score fusion (Reciprocal Rank Fusion).
The query router decides:

* If the query matches a known code pattern -> run H2 (exact) + H3 (context).
* Otherwise -> run H3 (hybrid) -> RAG.

---

## Module I: AI Knowledge Assistant (RAG)

```
User question -> Query router -> Retrieve (H1/H2/H3) -> Build context
              -> LLM generate -> Answer + Sources + Confidence
```

Example response:

> **DDR333** is categorized as Football Equipment.
> Sources: Catalog 2025, Page 14 — Confidence: 96%

---

## Module J: Source Attribution

Every answer includes source document, page number, confidence score, and upload date.
**No answer is returned without sources.** If retrieval confidence is below threshold, the
system responds "Not found in the knowledge base" rather than hallucinating.

---

## Module K: Duplicate Detection

* Exact: SHA-256 content hash comparison on upload
* Semantic: Sentence-Transformer similarity via Qdrant to flag near-duplicate manuals,
  procedures, and catalogs

---

## Module L: Knowledge Analytics

Dashboard metrics: total documents, total chunks, search volume, top queries, retrieval
accuracy, duplicate rate, processing success rate.

---

## Module M: Dataset Quality Engine

Scores documents 0–100 on completeness, readability, metadata coverage, and duplicate risk.

---

## Module N: Audit Logs

Immutable log of uploads, searches, downloads, user actions, and document updates.
Each entry: actor, action, target, timestamp, IP. Required for defense compliance.

---

# 7. API Specification (Gateway)

| Method | Endpoint | Role | Description |
|--------|----------|------|-------------|
| POST | `/api/auth/login` | public | Authenticate, return tokens |
| POST | `/api/auth/refresh` | public | Refresh access token |
| POST | `/api/documents` | Admin/KM | Upload a document |
| GET | `/api/documents` | all | List documents |
| GET | `/api/documents/:id` | all | Document detail + status |
| POST | `/api/search/semantic` | all | Semantic RAG query |
| POST | `/api/search/code` | all | Exact code lookup (full enumeration) |
| POST | `/api/search/hybrid` | all | Hybrid search |
| POST | `/api/ask` | all | RAG answer with sources |
| GET | `/api/analytics` | Admin/KM | Dashboard metrics |
| GET | `/api/audit` | Admin | Audit log |

### AI Service (internal, called by gateway)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/process` | Extract, chunk, embed, index a document |
| POST | `/embed` | Embed text |
| POST | `/search` | Vector/hybrid search |
| POST | `/code-lookup` | Exact code enumeration |
| POST | `/ask` | RAG generation with sources |

---

# 8. Database Design (MongoDB)

**users**: name, email, role, passwordHash, createdAt
**documents**: title, storageUrl, publicId, fileType, sha256, uploadedBy, status, version
**chunks**: documentId, chunkText, pageNumber, embeddingId, codes[]
**code_index**: code (indexed), documentId, chunkId, pageNumber, context
**search_logs**: query, type, resultsCount, userId, timestamp
**audit_logs**: actor, action, target, ip, timestamp

---

# 9. Non-Functional Requirements

* **Availability:** 99.9% uptime
* **Scalability:** 1M documents, 100M chunks
* **Performance:** search response < 2 seconds
* **Security:** JWT, HTTPS/TLS, encrypted storage at rest, RBAC, audit logging

---

# 10. Technology Stack

| Layer | Technology |
|-------|------------|
| Frontend | React, Tailwind CSS, TanStack Query |
| Backend | Node.js, Express, TypeScript |
| AI Layer | Python, FastAPI, LangChain |
| Vector DB | Qdrant |
| Database | MongoDB |
| File Storage | Cloudinary (cloud) / MinIO (air-gapped) |
| LLM | Hosted API (cloud) / vLLM or Ollama (air-gapped) |
| Deployment | Docker, Docker Compose, AWS EC2 (cloud) / on-prem (air-gapped) |
| Monitoring | Grafana, Prometheus |

---

# 11. Deployment & Security Modes (NEW)

Defense data often cannot leave controlled networks. The platform supports two modes via
configuration (`DEPLOYMENT_MODE=cloud|airgapped`):

### Cloud Mode
* Cloudinary storage, hosted LLM API, AWS EC2.
* Fast to stand up; suitable for unclassified / FOUO data.

### Air-Gapped Mode
* MinIO object storage, self-hosted LLM (vLLM/Ollama), local embeddings, on-prem Qdrant
  and MongoDB. No outbound internet calls.
* Suitable for classified networks.

Security baseline (both modes): TLS in transit, encryption at rest, RBAC, full audit
trail, no answer without sources, configurable data-retention policy.

> Note: Handling of classified material requires organizational ATO (Authority to Operate)
> and accreditation beyond the scope of this software.

---

# 12. Future Roadmap

* **Phase 2:** Voice search, multilingual search, AI agents
* **Phase 3:** Knowledge Graph RAG, fine-tuning dataset generation, quality analyzer
* **Phase 4:** Automated dataset curation, synthetic data generation, benchmark leakage detection

---

# 13. Success Metrics

* 90% reduction in search time
* 95% retrieval accuracy
* < 2 second response time
* 100% recall on exact-code lookup (no matching record missed)
* 80% reduction in duplicate information lookup
* 99.9% uptime
com