"""
Negative-sentiment spike detection. Run after each ingestion batch, or on
its own schedule. Uses Resend's free tier (3,000 emails/month, no credit
card) for notification email delivery.
"""
from datetime import datetime, timedelta, timezone

import resend
from sqlalchemy.orm import Session

from app.config import settings
from app.database import SessionLocal
from app.models import Client, Mention, AlertLog, SentimentLabel

resend.api_key = settings.resend_api_key

WINDOW_HOURS = 24
MIN_MENTIONS_TO_EVALUATE = 5  # don't alert on noise from 1-2 mentions


def _send_alert_email(client: Client, negative_ratio: float, mention_count: int):
    if not settings.resend_api_key or not client.alert_email:
        return False
    try:
        resend.Emails.send({
            "from": settings.alert_from_email,
            "to": client.alert_email,
            "subject": f"PR alert: negative sentiment spike for {client.name}",
            "html": (
                f"<p><strong>{client.name}</strong> has {round(negative_ratio * 100)}% "
                f"negative mentions out of {mention_count} in the last {WINDOW_HOURS} hours.</p>"
                f"<p>Log in to the dashboard to review the mention feed.</p>"
            ),
        })
        return True
    except Exception:
        return False


def check_client_for_spike(db: Session, client: Client):
    window_start = datetime.now(timezone.utc) - timedelta(hours=WINDOW_HOURS)
    recent = (
        db.query(Mention)
        .filter(Mention.client_id == client.id, Mention.fetched_at >= window_start)
        .all()
    )
    if len(recent) < MIN_MENTIONS_TO_EVALUATE:
        return

    negative = [m for m in recent if m.sentiment_label == SentimentLabel.negative]
    ratio = len(negative) / len(recent)

    if ratio >= client.negative_spike_threshold:
        sent = _send_alert_email(client, ratio, len(recent))
        db.add(AlertLog(
            client_id=client.id,
            reason="negative_sentiment_spike",
            negative_ratio=ratio,
            mention_count=len(recent),
            email_sent=sent,
        ))
        db.commit()


def run_alert_checks():
    db = SessionLocal()
    try:
        for client in db.query(Client).all():
            check_client_for_spike(db, client)
    finally:
        db.close()


if __name__ == "__main__":
    run_alert_checks()
