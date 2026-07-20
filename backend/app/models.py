"""
SQLAlchemy ORM models.

Tables:
- users:             account + profile + income info
- loans:              individual debts/loans belonging to a user
- settlement_records:  saved settlement predictions / offers
- ai_history:          log of every AI-generated analysis/letter for auditing
"""
import enum
from datetime import datetime

from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, Enum
)
from sqlalchemy.orm import relationship

from app.database import Base


class LoanType(str, enum.Enum):
    credit_card = "credit_card"
    personal_loan = "personal_loan"
    medical_debt = "medical_debt"
    student_loan = "student_loan"
    auto_loan = "auto_loan"
    mortgage = "mortgage"
    other = "other"


class LoanStatus(str, enum.Enum):
    active = "active"
    delinquent = "delinquent"
    in_collections = "in_collections"
    settled = "settled"
    paid_off = "paid_off"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)

    monthly_income = Column(Float, default=0.0)
    monthly_expenses = Column(Float, default=0.0)

    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    loans = relationship("Loan", back_populates="owner", cascade="all, delete-orphan")
    settlements = relationship("SettlementRecord", back_populates="owner", cascade="all, delete-orphan")
    ai_history = relationship("AIHistory", back_populates="owner", cascade="all, delete-orphan")


class Loan(Base):
    __tablename__ = "loans"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    creditor_name = Column(String, nullable=False)
    loan_type = Column(Enum(LoanType), default=LoanType.other)
    original_balance = Column(Float, nullable=False)
    current_balance = Column(Float, nullable=False)
    interest_rate = Column(Float, default=0.0)          # annual %
    minimum_payment = Column(Float, default=0.0)
    status = Column(Enum(LoanStatus), default=LoanStatus.active)
    months_delinquent = Column(Integer, default=0)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    owner = relationship("User", back_populates="loans")
    settlements = relationship("SettlementRecord", back_populates="loan", cascade="all, delete-orphan")


class SettlementRecord(Base):
    __tablename__ = "settlement_records"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    loan_id = Column(Integer, ForeignKey("loans.id"), nullable=False)

    predicted_settlement_pct = Column(Float, nullable=False)   # e.g. 0.45 = settle at 45%
    predicted_settlement_amount = Column(Float, nullable=False)
    confidence_score = Column(Float, default=0.0)              # 0-1
    strategy_summary = Column(Text, nullable=True)
    negotiation_letter = Column(Text, nullable=True)

    accepted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    owner = relationship("User", back_populates="settlements")
    loan = relationship("Loan", back_populates="settlements")


class AIHistory(Base):
    """Audit log of every AI request/response for transparency & debugging."""
    __tablename__ = "ai_history"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    request_type = Column(String, nullable=False)  # e.g. "financial_analysis", "negotiation_letter"
    prompt_summary = Column(Text, nullable=True)
    response_text = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    owner = relationship("User", back_populates="ai_history")
