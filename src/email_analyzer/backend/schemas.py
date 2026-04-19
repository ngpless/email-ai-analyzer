"""Pydantic-схемы для HTTP-API."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from email_analyzer.db.models import Category, Role


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=64)
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)
    full_name: Optional[str] = None
    role: Role = Role.USER


class UserPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: str
    full_name: Optional[str] = None
    role: Role
    is_active: bool


class LoginRequest(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class EmailIn(BaseModel):
    subject: str = ""
    body: str = ""
    sender: str = ""
    recipient: str = ""


class AnalyzeResponse(BaseModel):
    category: Category
    confidence: float
    is_spam: bool
    is_phishing: bool
    spam_score: float
    summary: str
    entities: dict[str, list[str]]


class EmailPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    subject: str
    sender: str
    recipient: str
    sent_at: Optional[datetime]
    is_read: bool
