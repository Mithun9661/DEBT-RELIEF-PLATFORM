"""
Financial analysis endpoints: financial health score, debt-to-income ratio,
and AI-generated negotiation strategy narrative.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.core.deps import get_current_user
from app.database import get_db
from app.services.financial_calculations import calculate_financial_health, predict_settlement
from app.services import ai_service

router = APIRouter(prefix="/api/financial", tags=["Financial Analysis"])


@router.get("/health", response_model=schemas.FinancialHealthOut)
def financial_health(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    loans = db.query(models.Loan).filter(models.Loan.owner_id == current_user.id).all()
    result = calculate_financial_health(
        monthly_income=current_user.monthly_income,
        monthly_expenses=current_user.monthly_expenses,
        loans=loans,
    )
    return result


@router.get("/strategy/{loan_id}")
def negotiation_strategy(
    loan_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """AI-generated negotiation strategy paragraph for a specific loan."""
    loan = (
        db.query(models.Loan)
        .filter(models.Loan.id == loan_id, models.Loan.owner_id == current_user.id)
        .first()
    )
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")

    loans = db.query(models.Loan).filter(models.Loan.owner_id == current_user.id).all()
    financial_summary = calculate_financial_health(
        current_user.monthly_income, current_user.monthly_expenses, loans
    )
    prediction = predict_settlement(loan)

    try:
        strategy_text = ai_service.generate_negotiation_strategy(loan, financial_summary, prediction)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))

    history = models.AIHistory(
        owner_id=current_user.id,
        request_type="negotiation_strategy",
        prompt_summary=f"Strategy for loan #{loan.id} ({loan.creditor_name})",
        response_text=strategy_text,
    )
    db.add(history)
    db.commit()

    return {"loan_id": loan.id, "strategy": strategy_text}
