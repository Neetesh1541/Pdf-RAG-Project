# ResearchMind AI – Intelligent Multi-Document Research Assistant

A production-style multi-document research assistant built with:

- **Frontend:** React, Tailwind CSS
- **Backend:** Django REST Framework
- **AI/RAG:** Gemini, LangChain, LangGraph, ChromaDB
- **Extraction:** PyMuPDF + Tesseract OCR
- **Database:** PostgreSQL or SQLite fallback

## What this project does

Users can:
- Upload multiple PDFs, reports, and research documents
- Extract text from digital and scanned PDFs
- Build embeddings and store chunk vectors in ChromaDB
- Ask questions across one or more documents
- Get answers with page-level source citations
- Compare documents
- Maintain conversation history and follow-up context
- Evaluate the RAG pipeline with retrieval and faithfulness metrics

## Architecture overview

```text
Upload PDF
  → Validate file
  → Extract text with PyMuPDF
  → OCR scanned pages with Tesseract
  → Clean text
  → Chunk text
  → Generate embeddings with Gemini
  → Store in ChromaDB
  → Retrieve relevant chunks for a question
  → Build contextual prompt with citations
  → Gemini generates grounded answer
```

### LangGraph workflow

The chat pipeline is orchestrated as a graph:

1. Load conversation history
2. Resolve follow-up references from prior messages
3. Retrieve relevant chunks from ChromaDB
4. Score context relevance
5. Generate answer or return a grounded fallback
6. Store assistant response back into conversation memory

## Project structure

```text
researchmind/
├── backend/
│   ├── manage.py
│   ├── config/
│   ├── documents/
│   ├── chat/
│   └── rag/
├── frontend/
│   ├── src/
│   ├── components/
│   ├── pages/
│   └── services/
├── data/
├── .env.example
├── README.md
└── requirements.txt
```

## Backend setup

```bash
cd researchmind/backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r ../requirements.txt
cp ../.env.example .env
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```

### Environment variables

Set these in `.env`:

- `GOOGLE_API_KEY` – Gemini API key
- `DATABASE_URL` – PostgreSQL or SQLite connection string
- `CHROMA_PERSIST_DIR` – Persistent vector store directory
- `MEDIA_ROOT` – Upload directory
- `MAX_UPLOAD_SIZE_MB` – Upload size limit
- `RAG_MIN_SCORE` – Minimum similarity score for grounded answers

## Frontend setup

```bash
cd researchmind/frontend
npm install
npm run dev
```

## Required system dependencies

For OCR support, install:

- **Tesseract OCR**
- **Poppler** is optional but helpful in some environments

> PyMuPDF is used for PDF parsing and page rendering. Tesseract handles scanned/image-based pages.

## API endpoints

- `POST /api/documents/upload/`
- `GET /api/documents/`
- `DELETE /api/documents/<id>/`
- `GET /api/documents/search/?q=...`
- `POST /api/chat/`
- `GET /api/conversations/`
- `GET /api/conversations/<id>/`
- `POST /api/evaluate/`
- `GET /api/dashboard/`

## RAG safeguards

- The complete document is **never** sent directly to the LLM
- Only retrieved chunks are passed as context
- Answers are gated by retrieval score thresholds
- If evidence is weak, the system returns:
  `I couldn't find sufficient evidence in the uploaded documents.`
- Responses include supporting citations such as:
  `Paper_A.pdf — Page 7`

## Notes

This repo is structured to be production-style and modular. It is intentionally split into:

- ingestion logic
- embeddings and vector storage
- retriever logic
- generation logic
- graph orchestration
- API layer
- frontend presentation layer

The code is ready to be extended with background jobs, auth, and deployment pipelines.
