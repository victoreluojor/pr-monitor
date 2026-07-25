"""
Reddit connector.
Free tier via a 'script' app (praw). Generous rate limits (roughly 100
requests/min) - not the bottleneck in this stack, but still be a good citizen
and search only, don't crawl every subreddit on every run.
"""
from datetime import datetime, timezone
from typing import List

import praw

from app.config import settings
from app.connectors.base import RawMention

_reddit_client = None


def _get_client():
    global _reddit_client
    if _reddit_client is None:
        if not settings.reddit_client_id or not settings.reddit_client_secret:
            return None
        _reddit_client = praw.Reddit(
            client_id=settings.reddit_client_id,
            client_secret=settings.reddit_client_secret,
            user_agent=settings.reddit_user_agent,
        )
    return _reddit_client


def fetch_reddit_mentions(keyword_terms: List[str], limit_per_term: int = 15) -> List[RawMention]:
    client = _get_client()
    if client is None:
        return []

    results: List[RawMention] = []
    for term in keyword_terms:
        try:
            for submission in client.subreddit("all").search(term, sort="new", limit=limit_per_term):
                results.append(RawMention(
                    source_name=f"reddit.com/r/{submission.subreddit.display_name}",
                    title=submission.title,
                    excerpt=(submission.selftext or "")[:300],
                    url=f"https://reddit.com{submission.permalink}",
                    author=str(submission.author) if submission.author else None,
                    published_at=datetime.fromtimestamp(submission.created_utc, tz=timezone.utc),
                ))
        except Exception:
            continue

    return results
