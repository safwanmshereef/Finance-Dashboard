from collections import defaultdict
from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

import schemas
from database import get_db
from models import FinancialRecord, User
from security import require_dashboard_access

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/summary", response_model=schemas.DashboardSummary)
def get_summary(
    _: Annotated[User, Depends(require_dashboard_access)],
    db: Annotated[Session, Depends(get_db)],
    start_date: date | None = Query(default=None),
    end_date: date | None = Query(default=None),
):
    base_query = db.query(FinancialRecord)
    if start_date:
        base_query = base_query.filter(FinancialRecord.date >= start_date)
    if end_date:
        base_query = base_query.filter(FinancialRecord.date <= end_date)

    total_income = (
        base_query.with_entities(func.coalesce(
            func.sum(FinancialRecord.amount), 0.0))
        .filter(FinancialRecord.type == "income")
        .scalar()
    )
    total_expenses = (
        base_query.with_entities(func.coalesce(
            func.sum(FinancialRecord.amount), 0.0))
        .filter(FinancialRecord.type == "expense")
        .scalar()
    )

    income_by_category_rows = (
        base_query.with_entities(
            FinancialRecord.category, func.sum(FinancialRecord.amount))
        .filter(FinancialRecord.type == "income")
        .group_by(FinancialRecord.category)
        .order_by(func.sum(FinancialRecord.amount).desc())
        .all()
    )
    expense_by_category_rows = (
        base_query.with_entities(
            FinancialRecord.category, func.sum(FinancialRecord.amount))
        .filter(FinancialRecord.type == "expense")
        .group_by(FinancialRecord.category)
        .order_by(func.sum(FinancialRecord.amount).desc())
        .all()
    )

    dialect_name = db.bind.dialect.name if db.bind is not None else "sqlite"
    if dialect_name.startswith("postgresql"):
        month_expr = func.to_char(FinancialRecord.date, "YYYY-MM").label("month")
    elif dialect_name.startswith("sqlite"):
        month_expr = func.strftime("%Y-%m", FinancialRecord.date).label("month")
    else:
        month_expr = func.to_char(FinancialRecord.date, "YYYY-MM").label("month")

    trends_rows = (
        base_query.with_entities(
            month_expr,
            FinancialRecord.type,
            func.sum(FinancialRecord.amount).label("total"),
        )
        .group_by(month_expr, FinancialRecord.type)
        .order_by(month_expr)
        .all()
    )
    trend_map = defaultdict(lambda: {"income": 0.0, "expense": 0.0})
    for month, record_type, total in trends_rows:
        trend_map[month][record_type] = float(total or 0.0)

    monthly_trends = [
        schemas.TrendPoint(
            month=month, income=vals["income"], expenses=vals["expense"])
        for month, vals in sorted(trend_map.items())
    ]

    recent_records = (
        base_query
        .order_by(FinancialRecord.date.desc(), FinancialRecord.id.desc())
        .limit(5)
        .all()
    )

    return schemas.DashboardSummary(
        total_income=float(total_income or 0.0),
        total_expenses=float(total_expenses or 0.0),
        net_balance=float((total_income or 0.0) - (total_expenses or 0.0)),
        by_category_income=[
            schemas.CategoryTotal(category=row[0], total=float(row[1] or 0.0))
            for row in income_by_category_rows
        ],
        by_category_expense=[
            schemas.CategoryTotal(category=row[0], total=float(row[1] or 0.0))
            for row in expense_by_category_rows
        ],
        recent_records=[schemas.RecordOut.model_validate(
            record) for record in recent_records],
        monthly_trends=monthly_trends,
    )
