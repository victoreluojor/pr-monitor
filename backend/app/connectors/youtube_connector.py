"""
YouTube Data API v3 connector.
Free quota: 10,000 units/day. A search.list call costs 100 units, so budget
roughly 100 searches/day across ALL clients combined - the caller is
responsible for rationing calls (see scheduler.py).
"""
from datetime import datetime, timezone
from typing import List

import httpx

from app.config import settings
from app.connectors.base import RawMention

SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"


def fetch_youtube_mentions(keyword_term: str, max_results: int = 5) -> List[RawMention]:
    if not settings.youtube_api_key:
        return []

    try:
        response = httpx.get(SEARCH_URL, params={
            "part": "snippet",
            "q": keyword_term,
            "type": "video",
            "order": "date",
            "maxResults": max_results,
            "key": settings.youtube_api_key,
        }, timeout=15.0)
        response.raise_for_status()
        data = response.json()
    except Exception:
        return []

    results: List[RawMention] = []
    for item in data.get("items", []):
        snippet = item.get("snippet", {})
        video_id = item.get("id", {}).get("videoId")
        if not video_id:
            continue
        published = None
        if snippet.get("publishedAt"):
            published = datetime.fromisoformat(snippet["publishedAt"].replace("Z", "+00:00"))

        results.append(RawMention(
            source_name="youtube.com",
            title=snippet.get("title"),
            excerpt=(snippet.get("description") or "")[:300],
            url=f"https://www.youtube.com/watch?v={video_id}",
            author=snippet.get("channelTitle"),
            published_at=published,
        ))

    return results
