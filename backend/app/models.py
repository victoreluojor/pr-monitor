import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Column, String, DateTime, ForeignKey, Enum, Float, Boolean, Text, UniqueConstraint
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


def gen_uuid():
    return str(uuid.uuid4())


def utcnow():
    return datetime.now(timezone.utc)


class UserRole(str, enum.Enum):
    agency_admin = "agency_admin"   # sees all clients
    client_user = "client_user"     # sees only their assigned client


class SourceType(str, enum.Enum):
    rss = "rss"
    website_scrape = "website_scrape"
    reddit = "reddit"
    youtube = "youtube"
    google_search = "google_search"
    guardian_news = "guardian_news"
    currents_news = "currents_news"


class SentimentLabel(str, enum.Enum):
    positive = "positive"
    negative = "negative"
    neutral = "neutral"
    unscored = "unscored"


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.client_user)
    # Only set for client_user role. NULL for agency_admin (sees everything).
    client_id = Column(UUID(as_uuid=False), ForeignKey("clients.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utcnow)

    client = relationship("Client", back_populates="users")


class Client(Base):
    __tablename__ = "clients"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    name = Column(String, nullable=False)
    # e.g. website to scrape directly for brand mentions / press page
    primary_website = Column(String, nullable=True)
    # RSS feed URLs (blog, newsroom) - stored as newline-separated for simplicity
    rss_feeds = Column(Text, nullable=True)
    alert_email = Column(String, nullable=True)
    negative_spike_threshold = Column(Float, default=0.4)  # % negative in window that triggers alert
    created_at = Column(DateTime(timezone=True), default=utcnow)
    # Rotation bookkeeping: when this client was last polled by the scheduler
    last_polled_at = Column(DateTime(timezone=True), nullable=True)

    users = relationship("User", back_populates="client")
    keywords = relationship("Keyword", back_populates="client", cascade="all, delete-orphan")
    mentions = relationship("Mention", back_populates="client", cascade="all, delete-orphan")
    alerts = relationship("AlertLog", back_populates="client", cascade="all, delete-orphan")


class Keyword(Base):
    __tablename__ = "keywords"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    client_id = Column(UUID(as_uuid=False), ForeignKey("clients.id"), nullable=False)
    term = Column(String, nullable=False)          # brand name, competitor, hashtag
    is_competitor = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=utcnow)

    client = relationship("Client", back_populates="keywords")

    __table_args__ = (UniqueConstraint("client_id", "term", name="uq_client_keyword"),)


class Mention(Base):
    __tablename__ = "mentions"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    client_id = Column(UUID(as_uuid=False), ForeignKey("clients.id"), nullable=False)
    keyword_id = Column(UUID(as_uuid=False), ForeignKey("keywords.id"), nullable=True)

    source_type = Column(Enum(SourceType), nullable=False)
    source_name = Column(String, nullable=True)      # e.g. "reddit.com/r/marketing"
    title = Column(String, nullable=True)
    excerpt = Column(Text, nullable=True)             # short snippet only, never full article
    url = Column(String, nullable=False)
    author = Column(String, nullable=True)

    published_at = Column(DateTime(timezone=True), nullable=True)
    fetched_at = Column(DateTime(timezone=True), default=utcnow)

    sentiment_label = Column(Enum(SentimentLabel), default=SentimentLabel.unscored)
    sentiment_score = Column(Float, nullable=True)   # -1.0 to 1.0

    client = relationship("Client", back_populates="mentions")

    __table_args__ = (UniqueConstraint("client_id", "url", name="uq_client_url"),)


class AlertLog(Base):
    __tablename__ = "alert_log"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    client_id = Column(UUID(as_uuid=False), ForeignKey("clients.id"), nullable=False)
    triggered_at = Column(DateTime(timezone=True), default=utcnow)
    reason = Column(String, nullable=False)
    negative_ratio = Column(Float, nullable=True)
    mention_count = Column(Float, nullable=True)
    email_sent = Column(Boolean, default=False)

    client = relationship("Client", back_populates="alerts")
