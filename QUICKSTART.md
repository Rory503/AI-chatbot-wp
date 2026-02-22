# Quick Start Guide

## 5-Minute Setup

### 1. Clone & Install (2 min)
```bash
cd chatbot-backend
pip install -r requirements.txt
```

### 2. Configure Secrets (1 min)
```bash
cp .env.example .env
# Edit .env and add:
# - OPENAI_API_KEY (from platform.openai.com)
# - SUPABASE_URL, SUPABASE_KEY, SUPABASE_DB_PASSWORD (from supabase.com/dashboard)
# - WORDPRESS_SITE_URL=https://yoursite.com
# - WORDPRESS_CRAWL_URLS=https://yoursite.com/page1,https://yoursite.com/page2
```

### 3. Prepare Content (1 min)
```bash
mkdir pdfs
# Add your 6–10 PDFs to pdfs/
```

### 4. Ingest & Test (1 min)
```bash
python scripts/setup.py
python -m src.api.main
# Open another terminal:
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "hello"}'
```

Done! ✅

---

## Step-by-Step Walkthrough

### Get Your Secrets

**OpenAI API Key:**
1. Go to https://platform.openai.com/api-keys
2. Create a new secret key
3. Copy it → paste into `.env` as `OPENAI_API_KEY`

**Supabase (PostgreSQL + pgvector):**
1. Sign up at https://supabase.com
2. Create a new project
3. Go to Settings → Database
4. Copy: `Project URL` → `SUPABASE_URL`
5. Go to Settings → API Keys → Copy `anon public key` → `SUPABASE_KEY`
6. Set `SUPABASE_DB_PASSWORD` to your Postgres password (from project creation)

**WordPress Content:**
- Identify 3–5 key pages on your site (About, Services, FAQ, etc.)
- Get their URLs
- Add them to `.env`: `WORDPRESS_CRAWL_URLS=https://yoursite.com/about,https://yoursite.com/services`

### Test Locally

1. **Start the server:**
   ```bash
   python -m src.api.main
   ```
   You should see:
   ```
   ✓ Connected to Supabase
   ✓ pgvector tables initialized
   ```

2. **Ingest content:**
   ```bash
   python scripts/setup.py
   ```
   You should see:
   ```
   ✓ Crawled: https://yoursite.com/about
   ✓ Parsed: document.pdf (10 pages)
   ✓ Created 47 chunks from 3 documents
   ✓ Embedded 47 chunks
   ```

3. **Ask the bot:**
   ```bash
   curl -X POST http://localhost:8000/chat \
     -H "Content-Type: application/json" \
     -d '{"query": "What is your mission?"}'
   ```

   Expected response:
   ```json
   {
     "answer": "According to your About page, your mission is to...",
     "sources": [
       {
         "source": "https://yoursite.com/about",
         "similarity": 0.92,
         "excerpt": "..."
       }
     ],
     "confidence": 0.88,
     "query": "What is your mission?"
   }
   ```

---

## Deploy to Vercel

### 1. Push to GitHub

```bash
git init
git add .
git commit -m "Initial commit: nonprofit chatbot"
git remote add origin https://github.com/YOUR_USERNAME/REPO.git
git push -u origin main
```

### 2. Deploy

```bash
npm i -g vercel
vercel
```
Follow the prompts. It will detect your Python project.

### 3. Add Environment Variables

In Vercel dashboard → Your Project → Settings → Environment Variables:
- `OPENAI_API_KEY`
- `SUPABASE_URL`
- `SUPABASE_KEY`
- `SUPABASE_DB_PASSWORD`
- `WORDPRESS_SITE_URL`
- `WORDPRESS_CRAWL_URLS`
- `ALLOWED_ORIGINS` (add your WordPress domain)

### 4. Ingest Content

```bash
curl -X POST https://your-project.vercel.app/ingest
```

---

## Add Widget to WordPress

### Simple Embed (Recommended)

1. Go to WordPress admin → Appearance → Theme File Editor
2. Find `footer.php`
3. Add this before `</body>`:

```html
<!-- Nonprofit AI Chatbot Widget -->
<script>
  window.CHATBOT_API_URL = 'https://your-project.vercel.app';
</script>
<script src="https://your-project.vercel.app/widget/widget.js"></script>
```

4. Save & visit your site
5. You should see the 💬 chat icon in the bottom-right corner

### Using a Code Plugin

If you can't edit theme files:
1. Install "Insert Headers and Footers" plugin
2. Go to Settings → Insert Headers and Footers
3. Paste the script above into "Footer Code"
4. Save

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "Connection refused" | Check SUPABASE_URL and credentials in .env |
| "No documents found" | Run `python scripts/setup.py` again; check PDF folder and WORDPRESS_CRAWL_URLS |
| "Embedding failed" | Check OPENAI_API_KEY; verify you have enough API credits |
| Widget not showing | Clear browser cache; check console for CORS errors; verify ALLOWED_ORIGINS |
| Slow responses | Normal first time (embeddings can take 30–60 sec); check OpenAI rate limits |

---

## Next Steps

- [ ] Configure WordPress crawl URLs
- [ ] Add 6–10 PDFs to `pdfs/` folder
- [ ] Test locally with `setup.py` and `main.py`
- [ ] Deploy to Vercel
- [ ] Set environment variables in Vercel
- [ ] Ingest content on live server
- [ ] Embed widget in WordPress footer
- [ ] Test with real user queries
- [ ] Monitor API usage and costs

---

Questions? Check the [main README.md](README.md) or open an issue.
