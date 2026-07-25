"""
Self-hosted scraper for a client's own website/web app when no RSS feed or
API exists. Free and unlimited, but bounded by your hosting's compute -
keep this to one page per client per run, not a deep crawl.

Requires: `playwright install chromium` on the host after pip install.
"""
from datetime import datetime, timezone
from typing import List

from playwright.sync_api import sync_playwright

from app.connectors.base import RawMention


def fetch_page_mentions(url: str, keyword_terms: List[str]) -> List[RawMention]:
    if not url:
        return []

    terms_lower = [t.lower() for t in keyword_terms]
    results: List[RawMention] = []

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, timeout=20000, wait_until="domcontentloaded")
            title = page.title()
            # Grab visible text only, capped, never the raw HTML/full article body
            body_text = page.inner_text("body")[:2000]
            browser.close()
    except Exception:
        return []

    combined = f"{title} {body_text}".lower()
    if any(term in combined for term in terms_lower):
        results.append(RawMention(
            source_name=url,
            title=title,
            excerpt=body_text[:300],
            url=url,
            author=None,
            published_at=datetime.now(timezone.utc),
        ))

    return results
