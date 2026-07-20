"""
Loan/debt management endpoints: create, list, update, delete.
All operations are scoped to the authenticated user's own loans.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.core.deps import get_current_user
from app.database import get_db

router = APIRouter(prefix="/api/loans", tags=["Loans"])


def _get_owned_loan(loan_id: int, user: models.User, db: Session) -> models.Loan:
    loan = (
        db.query(models.Loan)
        .filter(models.Loan.id == loan_id, models.Loan.owner_id == user.id)
        .first()
    )
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")
    return loan


@router.post("", response_model=schemas.LoanOut, status_code=status.HTTP_201_CREATED)
def create_loan(
    payload: schemas.LoanCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    loan = models.Loan(owner_id=current_user.id, **payload.model_dump())
    db.add(loan)
    db.commit()
    db.refresh(loan)
    return loan


@router.get("", response_model=list[schemas.LoanOut])
def list_loans(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return (
        db.query(models.Loan)
        .filter(models.Loan.owner_id == current_user.id)
        .order_by(models.Loan.created_at.desc())
        .all()
    )


@router.get("/{loan_id}", response_model=schemas.LoanOut)
def get_loan(
    loan_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return _get_owned_loan(loan_id, current_user, db)


@router.patch("/{loan_id}", response_model=schemas.LoanOut)
def update_loan(
    loan_id: int,
    payload: schemas.LoanUpdate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    loan = _get_owned_loan(loan_id, current_user, db)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(loan, field, value)
    db.commit()
    db.refresh(loan)
    return loan


@router.delete("/{loan_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_loan(
    loan_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    loan = _get_owned_loan(loan_id, current_user, db)
    db.delete(loan)
    db.commit()
    return None
