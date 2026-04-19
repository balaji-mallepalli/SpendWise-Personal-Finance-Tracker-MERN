from pydantic import BaseModel, Field
from typing import Optional


class BudgetCreate(BaseModel):
    category_id: str
    month: int = Field(..., ge=1, le=12)
    year: int = Field(..., ge=2000)
    limit_amount: float = Field(..., gt=0)


class BudgetUpdate(BaseModel):
    category_id: Optional[str] = None
    month: Optional[int] = Field(default=None, ge=1, le=12)
    year: Optional[int] = Field(default=None, ge=2000)
    limit_amount: Optional[float] = Field(default=None, gt=0)


class BudgetResponse(BaseModel):
    id: str
    user_id: str
    category_id: str
    month: int
    year: int
    limit_amount: float


class BudgetStatus(BaseModel):
    id: str
    category_id: str
    category_name: str
    category_color: str
    category_icon: str
    month: int
    year: int
    limit_amount: float
    spent_amount: float
    percentage: float
    exceeded: bool
