"""Роутер /stats."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from email_analyzer.backend.deps import current_user
from email_analyzer.backend.services.stats import StatsService
from email_analyzer.db.models import User


router = APIRouter(prefix="/stats", tags=["stats"])


@router.post("/compute")
def compute_stats(
    emails: list[dict],
    _: User = Depends(current_user),
) -> dict:
    result = StatsService().compute(emails)
    return {
        "total": result.total,
        "by_category": result.by_category,
        "spam_count": result.spam_count,
        "phishing_count": result.phishing_count,
        "avg_confidence": result.avg_confidence,
    }
