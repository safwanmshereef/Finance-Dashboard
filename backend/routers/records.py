from datetime import date
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session

import schemas
from database import get_db
from models import FinancialRecord, User
from security import require_admin, require_analyst_or_admin

router = APIRouter(prefix="/records", tags=["records"])


@router.post("", response_model=schemas.RecordOut, status_code=201)
def create_record(
    record_in: schemas.RecordCreate,
    admin_user: Annotated[User, Depends(require_admin)],
    db: Annotated[Session, Depends(get_db)],
):
    record = FinancialRecord(**record_in.model_dump(), user_id=admin_user.id)
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.get("", response_model=list[schemas.RecordOut])
def list_records(
    _: Annotated[User, Depends(require_analyst_or_admin)],
    db: Annotated[Session, Depends(get_db)],
    category: Optional[str] = None,
    type: Optional[schemas.RecordType] = None,
    q: Optional[str] = None,
    start_date: Optional[date] = Query(default=None),
    end_date: Optional[date] = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
):
    query = db.query(FinancialRecord)

    if category:
        query = query.filter(FinancialRecord.category.ilike(f"%{category}%"))
    if type:
        query = query.filter(FinancialRecord.type == type)
    if q:
        like_query = f"%{q}%"
        query = query.filter(
            or_(
                FinancialRecord.category.ilike(like_query),
                FinancialRecord.notes.ilike(like_query),
            )
        )
    if start_date:
        query = query.filter(FinancialRecord.date >= start_date)
    if end_date:
        query = query.filter(FinancialRecord.date <= end_date)

    return query.order_by(FinancialRecord.date.desc()).offset(skip).limit(limit).all()


@router.get("/{record_id}", response_model=schemas.RecordOut)
def get_record(
    record_id: int,
    _: Annotated[User, Depends(require_analyst_or_admin)],
    db: Annotated[Session, Depends(get_db)],
):
    record = db.query(FinancialRecord).filter(
        FinancialRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    return record


@router.put("/{record_id}", response_model=schemas.RecordOut)
def update_record(
    record_id: int,
    record_in: schemas.RecordUpdate,
    _: Annotated[User, Depends(require_admin)],
    db: Annotated[Session, Depends(get_db)],
):
    record = db.query(FinancialRecord).filter(
        FinancialRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")

    payload = record_in.model_dump(exclude_unset=True)
    for key, value in payload.items():
        setattr(record, key, value)

    db.commit()
    db.refresh(record)
    return record


@router.delete("/{record_id}", status_code=204)
def delete_record(
    record_id: int,
    _: Annotated[User, Depends(require_admin)],
    db: Annotated[Session, Depends(get_db)],
):
    record = db.query(FinancialRecord).filter(
        FinancialRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")

    db.delete(record)
    db.commit()
    return None
