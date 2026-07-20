"""
Deterministic (non-AI) financial math.

Keeping this logic separate and rule-based means the numbers borrowers see
are always explainable and reproducible, while the Gemini AI service layer
is reserved for qualitative reasoning (negotiation strategy, letter tone).
"""
from typing import List

from app.models import Loan, LoanStatus


def calculate_dti(monthly_income: float, total_minimum_payments: float) -> float:
    """Debt-to-income ratio, expressed as a fraction (0.35 = 35%)."""
    if monthly_income <= 0:
        return 1.0
    return round(total_minimum_payments / monthly_income, 4)


def calculate_financial_health(
    monthly_income: float,
    monthly_expenses: float,
    loans: List[Loan],
) -> dict:
    """
    Produces a 0-100 financial health score plus supporting figures.

    Score weighting (heuristic, transparent by design):
      - 40 pts: debt-to-income ratio (lower is better)
      - 25 pts: disposable income relative to income
      - 20 pts: proportion of loans delinquent/in collections
      - 15 pts: overall debt load relative to annual income
    """
    total_debt = sum(l.current_balance for l in loans)
    total_min_payments = sum(l.minimum_payment for l in loans)
    dti = calculate_dti(monthly_income, total_min_payments)
    disposable_income = monthly_income - monthly_expenses - total_min_payments

    # --- DTI component (0-40) ---
    # DTI <= 20% -> full marks, DTI >= 60% -> zero
    dti_score = max(0.0, min(40.0, 40.0 * (1 - (dti - 0.20) / 0.40))) if dti > 0.20 else 40.0

    # --- Disposable income component (0-25) ---
    disposable_ratio = (disposable_income / monthly_income) if monthly_income > 0 else -1
    disposable_score = max(0.0, min(25.0, 25.0 * (disposable_ratio + 0.1) / 0.4))

    # --- Delinquency component (0-20) ---
    if loans:
        troubled = sum(
            1 for l in loans
            if l.status in (LoanStatus.delinquent, LoanStatus.in_collections)
        )
        troubled_ratio = troubled / len(loans)
    else:
        troubled_ratio = 0.0
    delinquency_score = 20.0 * (1 - troubled_ratio)

    # --- Overall debt load vs annual income (0-15) ---
    annual_income = monthly_income * 12
    debt_to_annual_income = (total_debt / annual_income) if annual_income > 0 else 5.0
    debt_load_score = max(0.0, min(15.0, 15.0 * (1 - debt_to_annual_income / 2.0)))

    score = round(dti_score + disposable_score + delinquency_score + debt_load_score, 1)
    score = max(0.0, min(100.0, score))

    if score >= 80:
        label = "Excellent"
    elif score >= 60:
        label = "Good"
    elif score >= 40:
        label = "Fair"
    elif score >= 20:
        label = "At Risk"
    else:
        label = "Critical"

    risk_flags = []
    if dti > 0.43:
        risk_flags.append("Debt-to-income ratio exceeds typical lending threshold (43%).")
    if disposable_income < 0:
        risk_flags.append("Monthly expenses and minimum payments exceed income.")
    if troubled_ratio > 0.3:
        risk_flags.append("More than 30% of accounts are delinquent or in collections.")
    if total_debt > annual_income * 0.75 and annual_income > 0:
        risk_flags.append("Total debt exceeds 75% of annual income.")

    return {
        "monthly_income": monthly_income,
        "monthly_expenses": monthly_expenses,
        "total_debt": round(total_debt, 2),
        "total_minimum_payments": round(total_min_payments, 2),
        "debt_to_income_ratio": dti,
        "disposable_income": round(disposable_income, 2),
        "financial_health_score": score,
        "health_label": label,
        "risk_flags": risk_flags,
    }


def predict_settlement(loan: Loan, lump_sum_available: float | None = None) -> dict:
    """
    Heuristic settlement-percentage predictor based on well-documented
    debt-settlement industry patterns:
      - Older / more delinquent debt settles lower (creditors write it off sooner).
      - Debt already in collections settles lower than debt still with the
        original creditor.
      - Credit card / unsecured debt settles more readily than secured debt.
      - Offering a lump sum improves the settlement percentage further.

    Returns a percentage of current_balance the borrower might realistically
    expect to settle for, with a confidence score reflecting how much
    historical pattern-matching supports the estimate (this is a heuristic,
    not a guarantee, and is always paired with a human-readable rationale).
    """
    balance = loan.current_balance
    base_pct = 0.60  # start assuming settle at 60% of balance

    # Delinquency reduces the settlement percentage (creditor more eager to close the file)
    months = loan.months_delinquent or 0
    delinquency_discount = min(0.25, months * 0.015)
    base_pct -= delinquency_discount

    # Status adjustments
    if loan.status == LoanStatus.in_collections:
        base_pct -= 0.10
    elif loan.status == LoanStatus.delinquent:
        base_pct -= 0.05

    # Loan type adjustments (secured debt is harder to settle down)
    from app.models import LoanType
    if loan.loan_type in (LoanType.mortgage, LoanType.auto_loan):
        base_pct += 0.15  # secured debt settles less aggressively
    elif loan.loan_type == LoanType.credit_card:
        base_pct -= 0.03  # unsecured revolving debt is most negotiable
    elif loan.loan_type == LoanType.medical_debt:
        base_pct -= 0.08  # medical debt is very commonly settled steeply

    # Lump sum offers typically get better settlements than payment plans
    confidence = 0.55
    if lump_sum_available and balance > 0:
        coverage = min(1.0, lump_sum_available / balance)
        base_pct -= 0.10 * coverage
        confidence += 0.15 * coverage

    base_pct = max(0.15, min(0.90, base_pct))
    confidence = max(0.3, min(0.9, confidence + min(0.2, months * 0.01)))

    predicted_amount = round(balance * base_pct, 2)

    return {
        "predicted_settlement_pct": round(base_pct, 3),
        "predicted_settlement_amount": predicted_amount,
        "confidence_score": round(confidence, 2),
    }
