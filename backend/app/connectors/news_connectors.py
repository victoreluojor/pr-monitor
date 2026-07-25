"""
News connectors that are actually free for production/commercial use
(unlike NewsAPI.org's free tier, which forbids deployed/commercial use).

Guardian Open Platform: free, 5,000 calls/day, commercial use permitted.
Currents API: free, 600 calls/day, commercial use permitted.
"""
from datetime import datetime, timezone
from typing import List

import httpx

from app.config import settings
from app.connectors.base import RawMention

GUARDIAN_URL = "https://content.guardianapis.com/search"
CURRENTS_URL = "https://api.currentsapi.services/v1/search"


def fetch_guardian_mentions(keyword_term: str, page_size: int = 10) -> List[RawMention]:
    if not settings.guardian_api_key:
        return []
    try:
        response = httpx.get(GUARDIAN_URL, params={
            "q": keyword_term,
            "api-key": settings.guardian_api_key,
            "page-size": page_size,
            "order-by": "newest",
        }, timeout=15.0)
        response.raise_for_status()
        data = response.json()
    except Exception:
        return []

    results: List[RawMention] = []
    for item in data.get("response", {}).get("results", []):
        published = None
        if item.get("webPublicationDate"):
            published = datetime.fromisoformat(item["webPublicationDate"].replace("Z", "+00:00"))
        results.append(RawMention(
            source_name="theguardian.com",
            title=item.get("webTitle"),
            excerpt=None,  # Guardian free tier body text is used for linking only, not reproduced
            url=item.get("webUrl"),
            author=None,
            published_at=published,
        ))
    return results


def fetch_currents_mentions(keyword_term: str, page_size: int = 10) -> List[RawMention]:
    if not settings.currents_api_key:
        return []
    try:
        response = httpx.get(CURRENTS_URL, params={
            "keywords": keyword_term,
            "apiKey": settings.currents_api_key,
            "language": "en",
        }, timeout=15.0)
        response.raise_for_status()
        data = response.json()
    except Exception:
        return []

    results: List[RawMention] = []
    for item in data.get("news", [])[:page_size]:
        published = None
        if item.get("published"):
            try:
                published = datetime.fromisoformat(item["published"].replace("Z", "+00:00"))
            except ValueError:
                published = None
        results.append(RawMention(
            source_name=item.get("author") or "currentsapi",
            title=item.get("title"),
            excerpt=(item.get("description") or "")[:300],
            url=item.get("url"),
            author=item.get("author"),
            published_at=published,
        ))
    return results
