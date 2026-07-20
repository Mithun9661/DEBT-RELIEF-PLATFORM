"""
Pydantic schemas used for request validation and response serialization.
Kept separate from ORM models (app.models) so the API contract can evolve
independently of the database schema.
"""
from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, EmailStr, Field, ConfigDict

from app.models import LoanType, LoanStatus


# ---------- Auth ----------

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    full_name: str
    monthly_income: float = Field(default=0.0, ge=0)
    monthly_expenses: float = Field(default=0.0, ge=0)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    full_name: str
    monthly_income: float
    monthly_expenses: float
    created_at: datetime


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    monthly_income: Optional[float] = Field(default=None, ge=0)
    monthly_expenses: Optional[float] = Field(default=None, ge=0)


# ---------- Loans ----------

class LoanCreate(BaseModel):
    creditor_name: str
    loan_type: LoanType = LoanType.other
    original_balance: float = Field(gt=0)
    current_balance: float = Field(ge=0)
    interest_rate: float = Field(default=0.0, ge=0)
    minimum_payment: float = Field(default=0.0, ge=0)
    status: LoanStatus = LoanStatus.active
    months_delinquent: int = Field(default=0, ge=0)


class LoanUpdate(BaseModel):
    creditor_name: Optional[str] = None
    loan_type: Optional[LoanType] = None
    current_balance: Optional[float] = Field(default=None, ge=0)
    interest_rate: Optional[float] = Field(default=None, ge=0)
    minimum_payment: Optional[float] = Field(default=None, ge=0)
    status: Optional[LoanStatus] = None
    months_delinquent: Optional[int] = Field(default=None, ge=0)


class LoanOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    creditor_name: str
    loan_type: LoanType
    original_balance: float
    current_balance: float
    interest_rate: float
    minimum_payment: float
    status: LoanStatus
    months_delinquent: int
    created_at: datetime
    updated_at: datetime


# ---------- Financial Analysis ----------

class FinancialHealthOut(BaseModel):
    monthly_income: float
    monthly_expenses: float
    total_debt: float
    total_minimum_payments: float
    debt_to_income_ratio: float
    disposable_income: float
    financial_health_score: float  # 0-100
    health_label: str
    risk_flags: List[str]


# ---------- Settlement Prediction ----------

class SettlementPredictionRequest(BaseModel):
    loan_id: int
    lump_sum_available: Optional[float] = Field(default=None, ge=0)


class SettlementPredictionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    loan_id: int
    predicted_settlement_pct: float
    predicted_settlement_amount: float
    confidence_score: float
    strategy_summary: Optional[str]
    created_at: datetime


# ---------- Negotiation Letters ----------

class NegotiationLetterRequest(BaseModel):
    loan_id: int
    tone: str = Field(default="professional", pattern="^(professional|firm|empathetic)$")
    offer_amount: Optional[float] = Field(default=None, ge=0)
    hardship_reason: Optional[str] = None


class NegotiationLetterOut(BaseModel):
    loan_id: int
    letter: str
    generated_at: datetime


# ---------- AI History ----------

class AIHistoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    request_type: str
    prompt_summary: Optional[str]
    response_text: Optional[str]
    created_at: datetime
