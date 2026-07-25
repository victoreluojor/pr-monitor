"""
RSS feed connector.
No rate limit, no API key. Client blogs/newsrooms and any site that publishes
a feed can be polled as often as you like without hitting a quota.
"""
from datetime import datetime, timezone
from typing import List

import feedparser

from app.connectors.base import RawMention


def fetch_rss_mentions(feed_urls: List[str], keyword_terms: List[str]) -> List[RawMention]:
    results: List[RawMention] = []
    terms_lower = [t.lower() for t in keyword_terms]

    for feed_url in feed_urls:
        feed_url = feed_url.strip()
        if not feed_url:
            continue
        try:
            parsed = feedparser.parse(feed_url)
        except Exception:
            continue

        for entry in parsed.entries[:50]:
            title = getattr(entry, "title", "") or ""
            summary = getattr(entry, "summary", "") or ""
            combined = f"{title} {summary}".lower()

            # Only keep entries that actually mention one of the tracked keywords
            if not any(term in combined for term in terms_lower):
                continue

            published = None
            if getattr(entry, "published_parsed", None):
                published = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)

            results.append(RawMention(
                source_name=parsed.feed.get("title", feed_url),
                title=title,
                excerpt=summary[:300],
                url=entry.get("link", feed_url),
                author=getattr(entry, "author", None),
                published_at=published,
            ))

    return results
