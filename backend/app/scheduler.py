"""
Rotation-based ingestion scheduler.

Design: instead of polling every client every few minutes (which would blow
through free-tier quotas instantly), this picks the N least-recently-polled
clients each run and checks ONLY those. With INGEST_BATCH_SIZE=2 and this
job running every ~20 minutes via cron/GitHub Actions, an 8-client agency
gets each client refreshed roughly every 4-5 hours - within the free daily
caps of Google CSE (100/day) and YouTube (100 searches/day).

Run manually with:  python -m app.scheduler
Or trigger it on a schedule from GitHub Actions (see .github/workflows/ingest.yml)
"""
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.config import settings
from app.database import SessionLocal
from app.models import Client, Keyword, Mention, SourceType
from app.sentiment import score_text
from app.connectors.rss_connector import fetch_rss_mentions
from app.connectors.reddit_connector import fetch_reddit_mentions
from app.connectors.youtube_connector import fetch_youtube_mentions
from app.connectors.google_cse_connector import fetch_google_mentions
from app.connectors.news_connectors import fetch_guardian_mentions, fetch_currents_mentions
from app.connectors.web_scraper_connector import fetch_page_mentions


def _pick_clients_to_poll(db: Session, batch_size: int):
    """Least-recently-polled clients first; never-polled clients come first of all."""
    return (
        db.query(Client)
        .order_by(Client.last_polled_at.asc().nulls_first())
        .limit(batch_size)
        .all()
    )


def _save_mention(db: Session, client_id: str, keyword_id, source_type: SourceType, raw) -> bool:
    """Returns True if a new row was inserted, False if it was a duplicate URL."""
    exists = (
        db.query(Mention)
        .filter(Mention.client_id == client_id, Mention.url == raw.url)
        .first()
    )
    if exists:
        return False

    label, score = score_text(f"{raw.title or ''} {raw.excerpt or ''}")

    mention = Mention(
        client_id=client_id,
        keyword_id=keyword_id,
        source_type=source_type,
        source_name=raw.source_name,
        title=raw.title,
        excerpt=raw.excerpt,
        url=raw.url,
        author=raw.author,
        published_at=raw.published_at,
        sentiment_label=label,
        sentiment_score=score,
    )
    db.add(mention)
    return True


def poll_client(db: Session, client: Client):
    keywords = db.query(Keyword).filter(Keyword.client_id == client.id).all()
    if not keywords:
        return
    terms = [k.term for k in keywords]
    primary_term = terms[0]  # used for quota-limited connectors (Google CSE / YouTube)
    new_count = 0

    # --- Unlimited free sources: check every keyword ---
    if client.rss_feeds:
        feed_urls = client.rss_feeds.splitlines()
        for raw in fetch_rss_mentions(feed_urls, terms):
            if _save_mention(db, client.id, None, SourceType.rss, raw):
                new_count += 1

    for raw in fetch_reddit_mentions(terms):
        if _save_mention(db, client.id, None, SourceType.reddit, raw):
            new_count += 1

    if client.primary_website:
        for raw in fetch_page_mentions(client.primary_website, terms):
            if _save_mention(db, client.id, None, SourceType.website_scrape, raw):
                new_count += 1

    # --- Quota-limited sources: only the primary keyword, to conserve daily caps ---
    for raw in fetch_youtube_mentions(primary_term):
        if _save_mention(db, client.id, None, SourceType.youtube, raw):
            new_count += 1

    for raw in fetch_google_mentions(primary_term):
        if _save_mention(db, client.id, None, SourceType.google_search, raw):
            new_count += 1

    for raw in fetch_guardian_mentions(primary_term):
        if _save_mention(db, client.id, None, SourceType.guardian_news, raw):
            new_count += 1

    for raw in fetch_currents_mentions(primary_term):
        if _save_mention(db, client.id, None, SourceType.currents_news, raw):
            new_count += 1

    client.last_polled_at = datetime.now(timezone.utc)
    db.commit()
    print(f"[ingest] {client.name}: {new_count} new mentions")


def run_ingestion_batch():
    db = SessionLocal()
    try:
        clients = _pick_clients_to_poll(db, settings.ingest_batch_size)
        for client in clients:
            poll_client(db, client)
    finally:
        db.close()


if __name__ == "__main__":
    run_ingestion_batch()
