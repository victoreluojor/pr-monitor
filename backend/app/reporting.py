"""
Twice-daily digest reports + risk grading.
Sends a summary email (mention count, sentiment breakdown, risk color) to
every address listed for a client, separate from the existing threshold-
based spike alerts in alerts.py.
"""
from datetime import datetime, timedelta, timezone

import resend
from sqlalchemy.orm import Session

from app.config import settings
from app.database import SessionLocal
from app.models import Client, Mention, SentimentLabel

resend.api_key = settings.resend_api_key

REPORT_WINDOW_HOURS = 12  # matches a twice-daily schedule


def compute_risk_level(negative_ratio: float, threshold: float) -> str:
    """green = calm, amber = watch, red = at or above the client's own alert threshold."""
    if negative_ratio >= threshold:
        return "red"
    if negative_ratio >= threshold / 2:
        return "amber"
    return "green"


def _recipient_list(client: Client) -> list[str]:
    if not client.alert_email:
        return []
    return [addr.strip() for addr in client.alert_email.split(",") if addr.strip()]


def _build_report_html(client: Client, mentions: list[Mention], risk_level: str) -> str:
    negative = [m for m in mentions if m.sentiment_label == SentimentLabel.negative]
    positive = [m for m in mentions if m.sentiment_label == SentimentLabel.positive]
    neutral = [m for m in mentions if m.sentiment_label == SentimentLabel.neutral]

    risk_colors = {"green": "#0F6E56", "amber": "#854F0B", "red": "#993C1D"}
    top_stories = "".join(
        f"<li><a href='{m.url}'>{m.title or m.url}</a> "
        f"({m.sentiment_label.value})</li>"
        for m in mentions[:5]
    )

    return f"""
    <h2>{client.name} - media summary</h2>
    <p>Risk level:
      <strong style="color:{risk_colors[risk_level]}">{risk_level.upper()}</strong>
    </p>
    <p>{len(mentions)} mentions in the last {REPORT_WINDOW_HOURS} hours -
       {len(positive)} positive, {len(negative)} negative, {len(neutral)} neutral</p>
    <ul>{top_stories or '<li>No mentions in this window</li>'}</ul>
    """


def send_report_for_client(db: Session, client: Client):
    recipients = _recipient_list(client)
    if not recipients:
        return

    window_start = datetime.now(timezone.utc) - timedelta(hours=REPORT_WINDOW_HOURS)
    mentions = (
        db.query(Mention)
        .filter(Mention.client_id == client.id, Mention.fetched_at >= window_start)
        .order_by(Mention.fetched_at.desc())
        .all()
    )

    negative_count = len([m for m in mentions if m.sentiment_label == SentimentLabel.negative])
    ratio = negative_count / len(mentions) if mentions else 0
    risk_level = compute_risk_level(ratio, client.negative_spike_threshold)

    html = _build_report_html(client, mentions, risk_level)

    if not settings.resend_api_key:
        return

    try:
        resend.Emails.send({
            "from": settings.alert_from_email,
            "to": recipients,
            "subject": f"{client.name} media report - risk: {risk_level.upper()}",
            "html": html,
        })
    except Exception:
        pass


def run_all_reports():
    db = SessionLocal()
    try:
        for client in db.query(Client).all():
            send_report_for_client(db, client)
    finally:
        db.close()


if __name__ == "__main__":
    run_all_reports()
