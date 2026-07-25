from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class RawMention:
    """Common shape every connector normalizes its results into before saving."""
    source_name: str
    title: Optional[str]
    excerpt: Optional[str]
    url: str
    author: Optional[str]
    published_at: Optional[datetime]
