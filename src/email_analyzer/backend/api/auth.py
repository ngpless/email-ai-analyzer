"""Роутер аутентификации."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from email_analyzer.backend.deps import current_user, get_db
from email_analyzer.backend.schemas import LoginRequest, Token, UserCreate, UserPublic
from email_analyzer.backend.services.users import UserService
from email_analyzer.db.models import User


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
def register(payload: UserCreate, db: Session = Depends(get_db)) -> User:
    service = UserService(db)
    try:
        user = service.create(
            username=payload.username,
            email=payload.email,
            password=payload.password,
            full_name=payload.full_name or "",
            role=payload.role,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=Token)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> Token:
    service = UserService(db)
    user = service.authenticate(payload.username, payload.password)
    if user is None:
        raise HTTPException(status_code=401, detail="invalid credentials")
    token = service.issue_token(user)
    return Token(access_token=token)


@router.get("/me", response_model=UserPublic)
def me(user: User = Depends(current_user)) -> User:
    return user
