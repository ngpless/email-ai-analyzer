"""Роутер анализа писем."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from email_analyzer.backend.deps import current_user
from email_analyzer.backend.schemas import AnalyzeResponse, EmailIn
from email_analyzer.backend.services.analysis import AnalysisService
from email_analyzer.db.models import User


router = APIRouter(prefix="/analyze", tags=["analysis"])


_shared_service: AnalysisService | None = None


def get_analysis_service() -> AnalysisService:
    global _shared_service
    if _shared_service is None:
        _shared_service = AnalysisService()
    return _shared_service


@router.post("/email", response_model=AnalyzeResponse)
def analyze_email(
    payload: EmailIn,
    _: User = Depends(current_user),
    service: AnalysisService = Depends(get_analysis_service),
) -> AnalyzeResponse:
    result = service.analyze(
        subject=payload.subject,
        body=payload.body,
        sender=payload.sender,
    )
    return AnalyzeResponse(
        category=result.category,
        confidence=result.confidence,
        is_spam=result.is_spam,
        is_phishing=result.is_phishing,
        spam_score=result.spam_score,
        summary=result.summary,
        entities=result.entities,
    )
