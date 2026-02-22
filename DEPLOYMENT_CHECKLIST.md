# Deployment Checklist

Use this to track your rollout from local testing → production.

## Phase 1: Foundation ✅ (Day 1)

- [ ] **Secrets gathered**
  - [ ] OpenAI API key created
  - [ ] Supabase project set up (PostgreSQL + pgvector)
  - [ ] Database password created
  - [ ] WordPress site URL identified

- [ ] **Local environment ready**
  - [ ] Python 3.9+ installed
  - [ ] Dependencies installed: `pip install -r requirements.txt`
  - [ ] `.env` file created and filled with secrets

- [ ] **Database initialized**
  - [ ] `python scripts/setup.py` runs without errors
  - [ ] Tables created in Supabase (check via SQL editor)

## Phase 2: Content & Ingestion ✅ (Days 2–3)

- [ ] **WordPress content identified**
  - [ ] Key page URLs listed (About, Services, FAQ, etc.)
  - [ ] Added to `WORDPRESS_CRAWL_URLS` in `.env`
  - [ ] Tested crawling: `python scripts/setup.py`

- [ ] **PDFs prepared**
  - [ ] 6–10 PDFs collected
  - [ ] Placed in `pdfs/` folder
  - [ ] Tested parsing: `python scripts/setup.py`

- [ ] **Content ingested locally**
  - [ ] Setup script completed without errors
  - [ ] Documents visible in Supabase (count rows: `SELECT COUNT(*) FROM documents;`)
  - [ ] Chunks created and embedded

## Phase 3: API Testing ✅ (Day 3)

- [ ] **Local API running**
  - [ ] `python -m src.api.main` starts successfully
  - [ ] `/health` endpoint responds
  - [ ] `/chat` endpoint responds with grounded answers

- [ ] **Sample queries tested**
  - [ ] Query 1: _____________________ → Answer ✓
  - [ ] Query 2: _____________________ → Answer ✓
  - [ ] Query 3: _____________________ → Answer ✓
  - [ ] Bot says "I don't know" when content doesn't support answer ✓

- [ ] **Confidence & sources**
  - [ ] Response includes source citations ✓
  - [ ] Confidence score shown (0–1) ✓

## Phase 4: Deployment ✅ (Days 4–5)

- [ ] **Code pushed to GitHub**
  - [ ] Repository created
  - [ ] All files committed (except `.env` and `pdfs/`)
  - [ ] `.gitignore` configured

- [ ] **Vercel deployment**
  - [ ] Vercel CLI installed: `npm i -g vercel`
  - [ ] Project deployed: `vercel`
  - [ ] Deployment successful (no build errors)
  - [ ] Live URL: `https://_____________________.vercel.app`

- [ ] **Environment variables set in Vercel**
  - [ ] OPENAI_API_KEY ✓
  - [ ] SUPABASE_URL ✓
  - [ ] SUPABASE_KEY ✓
  - [ ] SUPABASE_DB_PASSWORD ✓
  - [ ] WORDPRESS_SITE_URL ✓
  - [ ] WORDPRESS_CRAWL_URLS ✓
  - [ ] ALLOWED_ORIGINS (includes your WordPress domain) ✓

- [ ] **Live API tested**
  - [ ] `/health` endpoint: `https://_____.vercel.app/health` ✓
  - [ ] `/chat` endpoint: Sample query returns answer ✓

- [ ] **Re-ingest on live server**
  - [ ] Called `/ingest` endpoint to ingest content to production DB
  - [ ] No errors: `curl -X POST https://_____.vercel.app/ingest` ✓

## Phase 5: WordPress Integration ✅ (Days 5–6)

- [ ] **Widget deployment**
  - [ ] Widget code ready (see `widget/widget.js`)
  - [ ] API_URL set to your Vercel domain

- [ ] **WordPress integration method chosen**
  - [ ] Option A: Footer embed ← (Easiest)
  - [ ] Option B: Code snippet plugin
  - [ ] Option C: Custom plugin

- [ ] **Widget embedded**
  - [ ] Script added to WordPress footer (or via plugin)
  - [ ] ALLOWED_ORIGINS includes WordPress domain

- [ ] **Widget tested on live site**
  - [ ] Chat icon visible (bottom-right corner) ✓
  - [ ] Widget opens/closes ✓
  - [ ] Can type and send messages ✓
  - [ ] Bot responds with grounded answers ✓
  - [ ] Sources displayed ✓
  - [ ] Works on desktop & mobile ✓

## Phase 6: QA & Tuning ✅ (Days 6–7)

- [ ] **Content accuracy verified**
  - [ ] Tested 10+ realistic user questions
  - [ ] Answers match website content
  - [ ] Bot correctly says "I don't know" when appropriate

- [ ] **Bot behavior fine-tuned**
  - [ ] Confidence threshold adjusted if needed (`CONFIDENCE_THRESHOLD`)
  - [ ] Chunk size optimized for content (`CHUNK_SIZE`)
  - [ ] Max context chunks reviewed (`MAX_CONTEXT_CHUNKS`)

- [ ] **Edge cases handled**
  - [ ] Offensive/spam queries managed gracefully ✓
  - [ ] Very long queries handled ✓
  - [ ] Empty queries rejected ✓
  - [ ] Rapid-fire queries don't break API ✓

- [ ] **Performance checked**
  - [ ] Response time: < 5 seconds typically ✓
  - [ ] No timeouts on long queries ✓

- [ ] **Mobile tested**
  - [ ] Widget responsive on phones ✓
  - [ ] Typing works on mobile keyboard ✓
  - [ ] Messages display correctly ✓

## Phase 7: Monitoring & Handoff ✅ (Days 7–8)

- [ ] **Monitoring set up**
  - [ ] Vercel logs checked daily
  - [ ] Error tracking configured (optional: Sentry)
  - [ ] API health monitored

- [ ] **Documentation shared**
  - [ ] Client receives README.md
  - [ ] Client receives QUICKSTART.md
  - [ ] Client receives deployment checklist (this file)

- [ ] **Client training**
  - [ ] How to re-ingest content (`/ingest`)
  - [ ] How to monitor costs (OpenAI, Supabase, Vercel)
  - [ ] How to update WordPress URLs
  - [ ] What to do if widget stops working

- [ ] **Support plan documented**
  - [ ] Support contact info provided
  - [ ] Response time SLA agreed
  - [ ] Monthly maintenance plan agreed

## Phase 8: Post-Launch ✅ (Ongoing)

- [ ] **Weekly checks**
  - [ ] Bot is responding normally
  - [ ] No unusual error patterns
  - [ ] Content is accurate

- [ ] **Monthly reviews** (recommended)
  - [ ] Cost overspend? No
  - [ ] User feedback positive? Yes ✓
  - [ ] Any content updates needed? ___
  - [ ] Any model/threshold tuning? ___

- [ ] **Quarterly updates** (planned)
  - [ ] Content re-ingested (if pages updated)
  - [ ] Dependencies updated
  - [ ] Version bump released

---

## Cost Tracking

### Monthly Costs

| Service | Est. Cost | Actual | Notes |
|---------|-----------|--------|-------|
| Vercel (API hosting) | $0–$20 | $____ | Free tier sufficient for MVP |
| Supabase (DB + storage) | $25–$100 | $____ | Starts at free; scales with data |
| OpenAI (embeddings + LLM) | $10–$50 | $____ | ~$0.02 per 1K embeddings, ~$0.15 per 1K completions |
| **Total (est.)** | **$50–$170** | **$____** | More users = higher OpenAI cost |

### How to Monitor

1. **OpenAI**: dashboard.openai.com → Billing → Usage
2. **Supabase**: dashboard → Project → Billing
3. **Vercel**: vercel.com → Settings → Billing

---

## Rollback Plan

If something breaks in production:

1. **Immediate**: Disable widget in WordPress (remove script)
2. **Identify**: Check Vercel logs for errors
3. **Fix**:
   - Minor issue → Deploy fix via Git push
   - DB issue → Check Supabase dashboard
   - API down → Check OpenAI status page
4. **Test**: Verify in staging before re-deploying
5. **Resume**: Re-add widget script once confirmed working

---

**Status**: ☐ In Progress  ☐ Complete  
**Deployed Date**: _______________  
**Live URL**: _______________  
**Support Contact**: _______________  
