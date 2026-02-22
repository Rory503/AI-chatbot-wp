# Nonprofit AI Chatbot - RAG System

A production-ready, grounded AI chatbot for nonprofits using RAG (Retrieval-Augmented Generation). Powered by OpenAI, PostgreSQL + pgvector, and hosted on Vercel.

## 🎯 Features

- **Grounded Answers**: Only answers from your actual content—no hallucinations
- **Citations & Sources**: Every response includes source references
- **Confidence Gating**: Bot admits when it doesn't know rather than guessing
- **Site-Wide Widget**: Simple JavaScript embed for WordPress
- **Portable Architecture**: Easy to migrate providers (data is yours)
- **Cost-Effective**: Lean stack, minimal monthly operating costs

## 🏗️ Architecture

```
WordPress Site
     ↓
  Widget (JS)
     ↓
  FastAPI Backend (Vercel)
     ↓
  Vector DB (Supabase/pgvector)
     ↓
  OpenAI API (Embeddings + LLM)
```

### Components

- **Backend**: Python FastAPI
- **Vector DB**: PostgreSQL + pgvector (Supabase)
- **Hosting**: Vercel (serverless)
- **LLM**: OpenAI (embeddings + completions)
- **Widget**: Vanilla JavaScript

## 🚀 Getting Started

### 1. Prerequisites

- Python 3.9+
- PostgreSQL (Supabase account recommended)
- OpenAI API key
- Vercel account (free tier works)

### 2. Setup

Clone and install:
```bash
cd chatbot-backend
pip install -r requirements.txt
```

Configure environment:
```bash
cp .env.example .env
# Edit .env with your secrets:
# - OPENAI_API_KEY
# - SUPABASE_URL, SUPABASE_KEY, SUPABASE_DB_PASSWORD
# - WORDPRESS_SITE_URL and WORDPRESS_CRAWL_URLS
# - PDF_FOLDER (where your PDFs are)
```

Prepare content:
```bash
# Create pdfs folder
mkdir pdfs
# Add your PDF files here

# Update .env with WordPress URLs to crawl
# Example: WORDPRESS_CRAWL_URLS=https://yoursite.com/about,https://yoursite.com/services
```

Initialize database and ingest:
```bash
python scripts/setup.py
```

### 3. Local Testing

Start the API:
```bash
python -m src.api.main
```

Test the chat endpoint:
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "What services do you offer?"}'
```

Expected response:
```json
{
  "answer": "Based on our documentation...",
  "sources": [
    {
      "source": "https://yoursite.com/services",
      "similarity": 0.85,
      "excerpt": "..."
    }
  ],
  "confidence": 0.82,
  "query": "What services do you offer?"
}
```

## 📤 Deployment

### Deploy to Vercel

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel

# Set environment variables in Vercel dashboard
# - OPENAI_API_KEY
# - SUPABASE_URL, SUPABASE_KEY, SUPABASE_DB_PASSWORD
# - WORDPRESS_SITE_URL, WORDPRESS_CRAWL_URLS
# - PDF_FOLDER (if using Vercel storage or S3)
```

### Trigger Re-ingestion

```bash
# Call this endpoint after updating content
curl -X POST https://your-vercel-domain.com/ingest
```

## 🎧 WordPress Integration

### Option 1: Global Script (Easiest)

Add to your WordPress footer (Appearance → Theme File Editor → footer.php):

```html
<!-- Nonprofit AI Chatbot -->
<script>
  window.CHATBOT_API_URL = 'https://your-vercel-domain.vercel.app';
</script>
<script src="https://your-vercel-domain.vercel.app/widget.js"></script>
```

### Option 2: Custom Code Snippet Plugin

Use a plugin like "Code Snippets" or "Insert Headers and Footers" to inject:

```html
<script>
  window.CHATBOT_API_URL = 'https://your-vercel-domain.vercel.app';
</script>
<script src="https://your-vercel-domain.vercel.app/widget.js"></script>
```

### Option 3: Lightweight Plugin

Drop the widget files into a custom plugin (see `widget/` folder).

## ⚙️ Configuration

### Confidence Threshold
Lower = bot answers more often, higher = bot is pickier
```
CONFIDENCE_THRESHOLD=0.5  # Default: requires 50% similarity
```

### Chunking Strategy
Adjust based on content:
```
CHUNK_SIZE=500        # Words per chunk
CHUNK_OVERLAP=100     # Words to overlap between chunks
```

### LLM Model
Balance cost vs. quality:
```
LLM_MODEL=gpt-4o-mini      # Fast, cheap, good for facts
LLM_MODEL=gpt-4o           # Smarter, higher cost
```

## 💾 Data & Portability

Your data is **100% yours**:
- Content chunks stored in PostgreSQL (standard format)
- Embeddings compatible with any vector DB
- No vendor lock-in—migrate anytime

To export:
```sql
SELECT content, source, embedding FROM documents;
```

## 📊 Costs

### Initial Setup
- MVP: $2–3K (development)
- Polished: $5–8K

### Monthly Operating
- API (Vercel): ~$0–$20
- Database (Supabase): ~$25–$100
- OpenAI: ~$10–$50 (depends on usage)
- **Total: ~$50–$170/month**

## 🔒 Security

- API calls validated with CORS
- Vector searches are read-only by default
- Sensitive data (PDF content) stored securely in Supabase
- Environment variables never committed

## 🐛 Debugging

Check logs:
- **Local**: `python -m src.api.main` (prints to terminal)
- **Vercel**: Dashboard → Logs → Function Logs

Common issues:
- **"Connection refused"**: Check SUPABASE credentials
- **"No documents found"**: Run `python scripts/setup.py` again
- **"Embedding failed"**: Check OPENAI_API_KEY and rate limits
- **Widget not showing**: Check ALLOWED_ORIGINS in .env includes your domain

## 📝 API Reference

### POST /chat
Ask a question
```json
{
  "query": "What services do you provide?"
}
```

Response:
```json
{
  "answer": "Based on our website, we provide...",
  "sources": [...],
  "confidence": 0.85,
  "query": "..."
}
```

### POST /ingest
Re-ingest content (admin only)
```
curl -X POST https://your-domain.com/ingest
```

### GET /health
Health check
```
curl https://your-domain.com/health
```

## 🤝 Contributing

Contributions welcome! Areas for enhancement:
- Multi-language support
- Advanced analytics dashboard
- PDF image extraction (OCR)
- Feedback loop for model fine-tuning
- Rate limiting & auth

## 📄 License

MIT

## 📧 Support

For questions, reach out to [your contact info].

---

**Built with care for nonprofits. No hallucinations. No shortcuts.**
