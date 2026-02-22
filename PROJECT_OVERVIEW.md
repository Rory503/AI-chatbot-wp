# Project Structure Overview

## Directory Tree

```
chatbot-backend/
├── src/                          # Main application code
│   ├── __init__.py
│   ├── db.py                     # Supabase (PostgreSQL + pgvector) connection
│   ├── api/
│   │   ├── __init__.py
│   │   └── main.py               # FastAPI application & routes
│   ├── ingestion/
│   │   ├── __init__.py
│   │   ├── content_ingester.py   # WordPress crawl + PDF parsing
│   │   └── embedding_manager.py  # OpenAI embeddings
│   └── rag/
│       ├── __init__.py
│       └── engine.py             # RAG retrieval & grounded answering
│
├── widget/
│   └── widget.js                 # WordPress chat widget (vanilla JS)
│
├── scripts/
│   ├── setup.py                  # Initialize DB & ingest content
│   └── test_chatbot.py           # System health checks
│
├── api/
│   └── handler.py                # Vercel serverless function
│
├── .env.example                  # Configuration template
├── .gitignore                    # Git ignore rules
├── requirements.txt              # Python dependencies
├── vercel.json                   # Vercel deployment config
├── README.md                     # Full documentation
├── QUICKSTART.md                 # 5-minute setup guide
└── DEPLOYMENT_CHECKLIST.md       # Phase-by-phase rollout tracker
```

## File Descriptions

### Core Application

| File | Purpose |
|------|---------|
| `src/db.py` | Database abstraction for Supabase (pgvector) operations |
| `src/api/main.py` | FastAPI server with `/chat`, `/ingest`, `/health` endpoints |
| `src/ingestion/content_ingester.py` | Crawls WordPress pages, parses PDFs, chunks content |
| `src/ingestion/embedding_manager.py` | Generates OpenAI embeddings for text chunks |
| `src/rag/engine.py` | Retrieves context & generates grounded answers with citations |

### Deployment & Testing

| File | Purpose |
|------|---------|
| `scripts/setup.py` | One-command ingestion: crawl, parse, embed, store |
| `scripts/test_chatbot.py` | Health checks for all systems (DB, API, OpenAI, etc.) |
| `widget/widget.js` | Standalone chat widget for WordPress |
| `api/handler.py` | Vercel serverless function entry point |
| `vercel.json` | Vercel build & deployment config |

### Documentation

| File | Purpose |
|------|---------|
| `README.md` | Complete guide (architecture, setup, deployment, costs) |
| `QUICKSTART.md` | 5-minute setup + troubleshooting |
| `DEPLOYMENT_CHECKLIST.md` | Phase-by-phase rollout tracking |
| `.env.example` | Configuration template for secrets |

---

## Key Features Implemented

### ✅ Ingestion
- WordPress page crawler (parses HTML, extracts text)
- PDF parser (PyPDF, handles multi-page)
- Smart chunking (configurable size + overlap)
- Batch embedding (OpenAI text-embedding-3-small)

### ✅ Vector Database
- Supabase PostgreSQL + pgvector
- Vector similarity search with cosine distance
- Full-text metadata (source, page number, title)
- Ready for Vercel & other hosts

### ✅ RAG Engine
- Retrieves top-K relevant chunks by embedding similarity
- Generates grounded answers from context only
- **Confidence gating**: Bot says "I don't know" if similarity < threshold
- **Citations**: Every answer includes source attribution
- Temperature controlled (0.3) for factual consistency

### ✅ API
- `/chat` - Main RAG endpoint (POST)
- `/ingest` - Re-ingest content (POST, admin)
- `/health` - Health check (GET)
- CORS middleware for WordPress integration
- Pydantic request/response validation

### ✅ WordPress Widget
- Vanilla JavaScript (no dependencies)
- Floating chat bubble (bottom-right, mobile-responsive)
- Message history (localStorage)
- Source citations displayed
- Open/close toggle
- Real-time streaming-ready (can be enhanced)

### ✅ Deployment
- Vercel-ready (serverless Python)
- Environment-based configuration
- Zero-code reingestion via API
- Cost-optimized (free/cheap tier options)

---

## Configuration Reference

All settings in `.env`:

```bash
# OpenAI API
OPENAI_API_KEY=sk-...
EMBEDDING_MODEL=text-embedding-3-small
LLM_MODEL=gpt-4o-mini

# Supabase Database
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=eyJhbGc...
SUPABASE_DB_PASSWORD=postgres_password

# WordPress
WORDPRESS_SITE_URL=https://example.com
WORDPRESS_CRAWL_URLS=https://example.com/about,https://example.com/services

# Content
PDF_FOLDER=./pdfs

# RAG Behavior
CONFIDENCE_THRESHOLD=0.5        # 0.0–1.0 (higher = pickier)
MAX_CONTEXT_CHUNKS=5            # How many chunks to include in LLM prompt
CHUNK_SIZE=500                  # Words per chunk
CHUNK_OVERLAP=100               # Overlap words

# API
API_PORT=8000
ALLOWED_ORIGINS=http://localhost:3000,https://example.com

```

---

## API Reference

### POST /chat
```json
{
  "query": "What services do you offer?"
}
```

Response:
```json
{
  "answer": "Based on our website, we offer...",
  "sources": [
    {
      "source": "https://example.com/services",
      "similarity": 0.87,
      "excerpt": "..."
    }
  ],
  "confidence": 0.85,
  "query": "What services do you offer?"
}
```

### POST /ingest
Triggers re-ingestion of all content. No request body needed.

### GET /health
Returns `{"status": "healthy", "service": "nonprofit-chatbot-api"}`

---

## Next Steps

1. **Add secrets** → Copy `.env.example` → `.env` → Fill in credentials
2. **Prepare content** → WordPress URLs + PDFs → `pdfs/` folder
3. **Test locally** → `python scripts/setup.py` + `python -m src.api.main`
4. **Deploy** → Push to GitHub → `vercel` → Set env vars
5. **Integrate** → Add widget script to WordPress footer

See `QUICKSTART.md` for detailed walkthrough.

---

## Support & Customization

### Common Customizations
- **Different embedding model**: Change `EMBEDDING_MODEL` (e.g., `text-embedding-3-large`)
- **Different LLM**: Change `LLM_MODEL` (e.g., `gpt-4o` for smarter answers, but higher cost)
- **More conservative answers**: Increase `CONFIDENCE_THRESHOLD` to 0.7+
- **Faster responses**: Reduce `MAX_CONTEXT_CHUNKS` to 2–3

### Known Limitations
- PDFs: No OCR for scanned images (can be added later)
- Real-time updates: Need to call `/ingest` to pick up new content
- Authentication: No API key auth yet (can be added)
- Rate limiting: Not implemented (recommended for production)

---

Generated: February 2026  
Architecture: RAG with Grounding  
Stack: Python + FastAPI + PostgreSQL + OpenAI + Vercel  
