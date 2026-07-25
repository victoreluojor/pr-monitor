# PR Media Monitoring Tool

A multi-client media monitoring and diagnostic dashboard, scoped to run entirely
on free-tier services. Pilot capacity: **5-8 clients, 2-3 keywords each**, refreshed
every 4-6 hours (see "Why these limits" below).

## What's included
- `backend/` — FastAPI app: multi-tenant auth, source connectors, sentiment scoring,
  alerting, dashboard API
- `frontend/` — Next.js dashboard: login, per-client sentiment/volume charts, live
  mention feed
- `.github/workflows/ingest.yml` — free scheduled job that replaces a paid cron host

---

## Part 1 — Get your free API keys

Do these first; the app runs with none of them (it just won't fetch anything), but
each one you skip means fewer sources monitored.

| Source | Where to get a key | Free limit |
|---|---|---|
| Google Custom Search | [programmablesearchengine.google.com](https://programmablesearchengine.google.com/) → create a search engine → "search the entire web" → get your **Engine ID (cx)**. Then [console.cloud.google.com](https://console.cloud.google.com) → enable "Custom Search API" → create an **API key** | 100 queries/day (shared across all clients) |
| YouTube Data API | Same Google Cloud project → enable "YouTube Data API v3" → reuse or create an API key | 10,000 units/day (~100 searches) |
| Reddit | [reddit.com/prefs/apps](https://www.reddit.com/prefs/apps) → "create app" → choose **script** → note the Client ID and Secret | ~100 requests/min |
| Guardian Open Platform | [open-platform.theguardian.com/access](https://open-platform.theguardian.com/access/) → register for a free developer key | 5,000 calls/day, commercial use OK |
| Currents API | [currentsapi.services](https://currentsapi.services/en) → sign up for a free key | 600 calls/day, commercial use OK |
| HuggingFace | [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens) → create a read token | Rate-limited, fine for this volume |
| Resend (alert emails) | [resend.com](https://resend.com) → sign up, no credit card | 3,000 emails/month |

**Skipped on purpose:** X/Twitter (no free API tier exists as of 2026) and
NewsAPI.org (its free tier legally forbids production/commercial use). If you
later get budget, these are the two to add first.

---

## Part 2 — Free hosting, step by step

### 2.1 Database — Supabase
1. Go to [supabase.com](https://supabase.com) → New project → free tier.
2. In **Project Settings → Database**, copy the connection string (URI format).
   It looks like `postgresql://postgres:[PASSWORD]@[HOST]:5432/postgres`.
3. Save it — this is your `DATABASE_URL`.

### 2.2 Backend — Render
1. Push this whole folder to a new GitHub repository.
2. Go to [render.com](https://render.com) → New → Web Service → connect your repo.
3. Set **Root Directory** to `backend`.
4. Render should detect the `Dockerfile` automatically. If asked, set:
   - Build command: (leave blank, Docker handles it)
   - Start command: (leave blank, Docker handles it)
5. Under **Environment**, add every variable from `backend/.env.example` with your
   real values (this is where `DATABASE_URL` and all API keys go).
6. Deploy. Render's free tier sleeps after 15 minutes of no traffic — the first
   request after a nap takes ~30-60 seconds to wake up. Fine for a pilot; if this
   becomes a problem later, it's the first thing worth paying to fix.
7. Once live, note your backend URL, e.g. `https://pr-monitor-api.onrender.com`.

### 2.3 Frontend — Vercel
1. Go to [vercel.com](https://vercel.com) → New Project → import the same repo.
2. Set **Root Directory** to `frontend`.
3. Add environment variable `NEXT_PUBLIC_API_URL` = your Render backend URL.
4. Deploy. Vercel gives you a URL like `https://pr-monitor.vercel.app` — this is
   what you send your team/clients to.

### 2.4 Scheduled ingestion — GitHub Actions (instead of a paid cron service)
1. In your GitHub repo, go to **Settings → Secrets and variables → Actions**.
2. Add each value from `backend/.env.example` as a repository secret (same names:
   `DATABASE_URL`, `GOOGLE_CSE_API_KEY`, etc).
3. That's it — `.github/workflows/ingest.yml` is already in the repo and will
   start running automatically every 20 minutes.
4. You can watch it run under the **Actions** tab, and trigger it manually anytime
   with the "Run workflow" button.

### 2.5 Create your first login
Render gives you a **Shell** tab on your web service. Open it and run:
```
python create_admin.py you@youragency.com yourpassword
```
Then log in at your Vercel URL with that email/password.

---

## Part 3 — Add your first client
Once logged in as agency admin, use the API directly (a client-management UI page
is the natural next addition — see "What to build next" below) or `curl`:

```bash
curl -X POST https://your-backend.onrender.com/clients/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "Acme Corp", "primary_website": "https://acme.com", "rss_feeds": "https://acme.com/blog/feed", "alert_email": "team@acme.com"}'
```

Then add keywords the same way against `/clients/{client_id}/keywords/`.

---

## Why these limits (read before adding your 9th client)

Google Custom Search's 100 queries/day is the tightest ceiling in this whole
stack — it's shared across every client. With 5-8 clients rotating through
`INGEST_BATCH_SIZE=2` clients per run, every 20 minutes, each client gets
refreshed roughly every 4-6 hours, which keeps you comfortably inside all the
free daily caps above. Push past ~10 clients and you'll start seeing gaps in
coverage — that's your signal to either upgrade Google CSE / Guardian, or split
ingestion across two Google Cloud projects (each gets its own 100/day quota).

## What to build next
- A simple client/keyword management page in the frontend (currently API-only)
- Weekly PDF/CSV export per client
- Slack webhook alerts as an alternative to email
