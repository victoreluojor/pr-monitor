from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Mention, User, SourceType, SentimentLabel
from app.schemas import MentionOut
from app.security import get_current_user, require_client_access

router = APIRouter(prefix="/clients/{client_id}/mentions", tags=["mentions"])


@router.get("/", response_model=List[MentionOut])
def list_mentions(
    client_id: str,
    source_type: Optional[SourceType] = None,
    sentiment_label: Optional[SentimentLabel] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    search: Optional[str] = None,
    limit: int = Query(50, le=200),
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_client_access(client_id, current_user)

    query = db.query(Mention).filter(Mention.client_id == client_id)
    if source_type:
        query = query.filter(Mention.source_type == source_type)
    if sentiment_label:
        query = query.filter(Mention.sentiment_label == sentiment_label)
    if date_from:
        query = query.filter(Mention.fetched_at >= date_from)
    if date_to:
        query = query.filter(Mention.fetched_at <= date_to)
    if search:
        like = f"%{search}%"
        query = query.filter(Mention.title.ilike(like))

    return (
        query.order_by(Mention.fetched_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
