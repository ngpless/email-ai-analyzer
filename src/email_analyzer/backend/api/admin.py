"""Админский роутер (только для роли admin)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from email_analyzer.backend.deps import get_db, require_admin
from email_analyzer.backend.schemas import UserPublic
from email_analyzer.backend.services.users import UserService
from email_analyzer.db.models import Role, User


router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/users", response_model=list[UserPublic])
def list_users(
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> list[User]:
    return UserService(db).list_all()


@router.post("/users/{user_id}/role", response_model=UserPublic)
def change_role(
    user_id: int,
    role: Role,
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> User:
    try:
        user = UserService(db).set_role(user_id, role)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    db.commit()
    db.refresh(user)
    return user


@router.post("/users/{user_id}/deactivate", response_model=UserPublic)
def deactivate_user(
    user_id: int,
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> User:
    try:
        user = UserService(db).deactivate(user_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    db.commit()
    db.refresh(user)
    return user
