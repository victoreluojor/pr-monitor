"""
Sentiment scoring using HuggingFace's free Inference API.
Model: distilbert-base-uncased-finetuned-sst-2-english (binary positive/negative).
Falls back to 'neutral' on any error so ingestion never crashes on a bad response.
"""
import httpx

from app.config import settings
from app.models import SentimentLabel

HF_MODEL_URL = (
    "https://api-inference.huggingface.co/models/"
    "distilbert-base-uncased-finetuned-sst-2-english"
)


def score_text(text: str) -> tuple[SentimentLabel, float]:
    if not text or not settings.huggingface_api_key:
        return SentimentLabel.unscored, 0.0

    try:
        response = httpx.post(
            HF_MODEL_URL,
            headers={"Authorization": f"Bearer {settings.huggingface_api_key}"},
            json={"inputs": text[:512]},  # keep payload small, free tier is rate limited
            timeout=15.0,
        )
        response.raise_for_status()
        data = response.json()

        # Expected shape: [[{"label": "POSITIVE", "score": 0.98}, {"label": "NEGATIVE", "score": 0.02}]]
        scores = {item["label"]: item["score"] for item in data[0]}
        positive_score = scores.get("POSITIVE", 0.5)
        negative_score = scores.get("NEGATIVE", 0.5)

        if abs(positive_score - negative_score) < 0.15:
            return SentimentLabel.neutral, positive_score - negative_score
        if positive_score > negative_score:
            return SentimentLabel.positive, positive_score - negative_score
        return SentimentLabel.negative, positive_score - negative_score

    except Exception:
        # Free-tier model can be "cold" (503) or rate limited - don't block ingestion
        return SentimentLabel.unscored, 0.0
