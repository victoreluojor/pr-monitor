from collections import Counter
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Mention, User, SentimentLabel
from app.schemas import DashboardSummary, SentimentBreakdown
from app.security import get_current_user, require_client_access

router = APIRouter(prefix="/clients/{client_id}/dashboard", tags=["dashboard"])


@router.get("/", response_model=DashboardSummary)
def get_dashboard(client_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    require_client_access(client_id, current_user)

    all_mentions = db.query(Mention).filter(Mention.client_id == client_id).all()
    seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)
    recent = [m for m in all_mentions if m.fetched_at and m.fetched_at >= seven_days_ago]

    sentiment_counts = Counter(m.sentiment_label for m in all_mentions)
    source_counts = Counter(m.source_name for m in all_mentions if m.source_name)

    volume_by_day = Counter(
        m.fetched_at.date().isoformat() for m in recent if m.fetched_at
    )

    return DashboardSummary(
        client_id=client_id,
        total_mentions=len(all_mentions),
        mentions_last_7_days=len(recent),
        sentiment_breakdown=SentimentBreakdown(
            positive=sentiment_counts.get(SentimentLabel.positive, 0),
            negative=sentiment_counts.get(SentimentLabel.negative, 0),
            neutral=sentiment_counts.get(SentimentLabel.neutral, 0),
            unscored=sentiment_counts.get(SentimentLabel.unscored, 0),
        ),
        top_sources=[{"source": s, "count": c} for s, c in source_counts.most_common(5)],
        volume_by_day=[{"date": d, "count": c} for d, c in sorted(volume_by_day.items())],
    )
