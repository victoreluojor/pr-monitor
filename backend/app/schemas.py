from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, EmailStr

from app.models import UserRole, SourceType, SentimentLabel


# ---------- Auth ----------
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    role: UserRole = UserRole.client_user
    client_id: Optional[str] = None


class UserOut(BaseModel):
    id: str
    email: EmailStr
    role: UserRole
    client_id: Optional[str] = None

    class Config:
        from_attributes = True


# ---------- Clients ----------
class ClientCreate(BaseModel):
    name: str
    primary_website: Optional[str] = None
    rss_feeds: Optional[str] = None  # newline separated URLs
    alert_email: Optional[str] = None
    negative_spike_threshold: float = 0.4


class ClientOut(BaseModel):
    id: str
    name: str
    primary_website: Optional[str]
    rss_feeds: Optional[str]
    alert_email: Optional[str]
    negative_spike_threshold: float
    last_polled_at: Optional[datetime]

    class Config:
        from_attributes = True


# ---------- Keywords ----------
class KeywordCreate(BaseModel):
    term: str
    is_competitor: bool = False


class KeywordOut(BaseModel):
    id: str
    term: str
    is_competitor: bool

    class Config:
        from_attributes = True


# ---------- Mentions ----------
class MentionOut(BaseModel):
    id: str
    client_id: str
    source_type: SourceType
    source_name: Optional[str]
    title: Optional[str]
    excerpt: Optional[str]
    url: str
    author: Optional[str]
    published_at: Optional[datetime]
    fetched_at: datetime
    sentiment_label: SentimentLabel
    sentiment_score: Optional[float]

    class Config:
        from_attributes = True


class MentionFilter(BaseModel):
    source_type: Optional[SourceType] = None
    sentiment_label: Optional[SentimentLabel] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    search: Optional[str] = None


# ---------- Dashboard ----------
class SentimentBreakdown(BaseModel):
    positive: int
    negative: int
    neutral: int
    unscored: int


class DashboardSummary(BaseModel):
    client_id: str
    total_mentions: int
    mentions_last_7_days: int
    sentiment_breakdown: SentimentBreakdown
    top_sources: List[dict]
    volume_by_day: List[dict]


# ---------- Alerts ----------
class AlertOut(BaseModel):
    id: str
    client_id: str
    triggered_at: datetime
    reason: str
    negative_ratio: Optional[float]
    mention_count: Optional[float]
    email_sent: bool

    class Config:
        from_attributes = True
