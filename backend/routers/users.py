from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import schemas
from database import get_db
from models import User
from security import get_password_hash, require_admin

router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=list[schemas.UserOut])
def list_users(
    _: Annotated[User, Depends(require_admin)],
    db: Annotated[Session, Depends(get_db)],
):
    return db.query(User).order_by(User.id.asc()).all()


@router.post("", response_model=schemas.UserOut)
def create_user_by_admin(
    user_in: schemas.UserCreate,
    _: Annotated[User, Depends(require_admin)],
    db: Annotated[Session, Depends(get_db)],
):
    existing = db.query(User).filter(User.email == user_in.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already exists")

    user = User(
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        role=user_in.role,
        status="active",
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.patch("/{user_id}", response_model=schemas.UserOut)
def update_user(
    user_id: int,
    update_in: schemas.UserUpdate,
    admin_user: Annotated[User, Depends(require_admin)],
    db: Annotated[Session, Depends(get_db)],
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.id == admin_user.id and update_in.status == "inactive":
        raise HTTPException(status_code=400, detail="Admin cannot deactivate self")

    if update_in.role is not None:
        user.role = update_in.role
    if update_in.status is not None:
        user.status = update_in.status
        user.is_active = update_in.status == "active"

    db.commit()
    db.refresh(user)
    return user
