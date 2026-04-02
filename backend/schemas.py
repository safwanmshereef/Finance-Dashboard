from datetime import date, datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field

RoleType = Literal["viewer", "analyst", "admin"]
StatusType = Literal["active", "inactive"]
RecordType = Literal["income", "expense"]


class Token(BaseModel):
    access_token: str
    token_type: str
    role: RoleType
    email: EmailStr


class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)
    role: RoleType = "viewer"


class UserUpdate(BaseModel):
    role: Optional[RoleType] = None
    status: Optional[StatusType] = None


class UserOut(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    role: RoleType
    status: StatusType
    is_active: bool
    created_at: datetime


class RecordBase(BaseModel):
    amount: float = Field(gt=0)
    type: RecordType
    category: str = Field(min_length=2, max_length=100)
    date: date
    notes: Optional[str] = Field(default=None, max_length=500)


class RecordCreate(RecordBase):
    pass


class RecordUpdate(BaseModel):
    amount: Optional[float] = Field(default=None, gt=0)
    type: Optional[RecordType] = None
    category: Optional[str] = Field(default=None, min_length=2, max_length=100)
    date: Optional[date] = None
    notes: Optional[str] = Field(default=None, max_length=500)


class RecordOut(RecordBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    created_at: datetime


class CategoryTotal(BaseModel):
    category: str
    total: float


class TrendPoint(BaseModel):
    month: str
    income: float
    expenses: float


class DashboardSummary(BaseModel):
    total_income: float
    total_expenses: float
    net_balance: float
    by_category_income: list[CategoryTotal]
    by_category_expense: list[CategoryTotal]
    recent_records: list[RecordOut]
    monthly_trends: list[TrendPoint]
