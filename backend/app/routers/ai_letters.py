"""
AI negotiation letter generation endpoints.
"""
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.core.deps import get_current_user
from app.database import get_db
from app.services import ai_service

router = APIRouter(prefix="/api/letters", tags=["AI Letter Generator"])


@router.post("/generate", response_model=schemas.NegotiationLetterOut)
def generate_letter(
    payload: schemas.NegotiationLetterRequest,
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

    try:
        letter_text = ai_service.generate_negotiation_letter(
            loan=loan,
            tone=payload.tone,
            offer_amount=payload.offer_amount,
            hardship_reason=payload.hardship_reason,
            borrower_name=current_user.full_name,
        )
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))

    # Save to the most recent settlement record for this loan, if any, and log to AI history
    latest_settlement = (
        db.query(models.SettlementRecord)
        .filter(
            models.SettlementRecord.owner_id == current_user.id,
            models.SettlementRecord.loan_id == loan.id,
        )
        .order_by(models.SettlementRecord.created_at.desc())
        .first()
    )
    if latest_settlement:
        latest_settlement.negotiation_letter = letter_text

    history = models.AIHistory(
        owner_id=current_user.id,
        request_type="negotiation_letter",
        prompt_summary=f"Letter for loan #{loan.id} ({loan.creditor_name}), tone={payload.tone}",
        response_text=letter_text,
    )
    db.add(history)
    db.commit()

    return {
        "loan_id": loan.id,
        "letter": letter_text,
        "generated_at": datetime.utcnow(),
    }


@router.get("/history", response_model=list[schemas.AIHistoryOut])
def letter_history(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return (
        db.query(models.AIHistory)
        .filter(
            models.AIHistory.owner_id == current_user.id,
            models.AIHistory.request_type == "negotiation_letter",
        )
        .order_by(models.AIHistory.created_at.desc())
        .all()
    )
