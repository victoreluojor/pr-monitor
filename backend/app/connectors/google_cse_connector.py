"""
Google Custom Search JSON API connector.
Free quota: 100 queries/day TOTAL across the whole project - this is the
tightest constraint in the whole stack. The scheduler must ration this
carefully across all clients (see scheduler.py INGEST_BATCH_SIZE).
"""
from datetime import datetime, timezone
from typing import List

import httpx

from app.config import settings
from app.connectors.base import RawMention

SEARCH_URL = "https://www.googleapis.com/customsearch/v1"


def fetch_google_mentions(keyword_term: str, num_results: int = 10) -> List[RawMention]:
    if not settings.google_cse_api_key or not settings.google_cse_engine_id:
        return []

    try:
        response = httpx.get(SEARCH_URL, params={
            "key": settings.google_cse_api_key,
            "cx": settings.google_cse_engine_id,
            "q": keyword_term,
            "num": num_results,
            "sort": "date",
        }, timeout=15.0)
        response.raise_for_status()
        data = response.json()
    except Exception:
        return []

    results: List[RawMention] = []
    for item in data.get("items", []):
        results.append(RawMention(
            source_name=item.get("displayLink"),
            title=item.get("title"),
            excerpt=(item.get("snippet") or "")[:300],
            url=item.get("link"),
            author=None,
            published_at=datetime.now(timezone.utc),  # CSE doesn't reliably return publish dates
        ))

    return results
