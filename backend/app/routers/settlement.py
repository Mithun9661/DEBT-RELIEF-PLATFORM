"""
Settlement prediction endpoints: generate and persist settlement predictions
for a given loan, and review past predictions.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.core.deps import get_current_user
from app.database import get_db
from app.services.financial_calculations import predict_settlement

router = APIRouter(prefix="/api/settlement", tags=["Settlement Prediction"])


@router.post("/predict", response_model=schemas.SettlementPredictionOut)
def create_prediction(
    payload: schemas.SettlementPredictionRequest,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    loan = (
        db.query(models.Loan)
        .filter(models.Loan.id == payload.loan_id, models.Loan.owner_id == current_user.id)
        .first()
    )
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")

    result = predict_settlement(loan, payload.lump_sum_available)

    summary = (
        f"Based on a {loan.status.value.replace('_', ' ')} {loan.loan_type.value.replace('_', ' ')} "
        f"account, {loan.months_delinquent} months delinquent, a settlement around "
        f"{result['predicted_settlement_pct']:.0%} of the ${loan.current_balance:,.2f} balance "
        f"(~${result['predicted_settlement_amount']:,.2f}) is a reasonable starting expectation."
    )

    record = models.SettlementRecord(
        owner_id=current_user.id,
        loan_id=loan.id,
        predicted_settlement_pct=result["predicted_settlement_pct"],
        predicted_settlement_amount=result["predicted_settlement_amount"],
        confidence_score=result["confidence_score"],
        strategy_summary=summary,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.get("/history", response_model=list[schemas.SettlementPredictionOut])
def prediction_history(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return (
        db.query(models.SettlementRecord)
        .filter(models.SettlementRecord.owner_id == current_user.id)
        .order_by(models.SettlementRecord.created_at.desc())
        .all()
    )


@router.get("/history/{loan_id}", response_model=list[schemas.SettlementPredictionOut])
def prediction_history_for_loan(
    loan_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return (
        db.query(models.SettlementRecord)
        .filter(
            models.SettlementRecord.owner_id == current_user.id,
            models.SettlementRecord.loan_id == loan_id,
        )
        .order_by(models.SettlementRecord.created_at.desc())
        .all()
    )
