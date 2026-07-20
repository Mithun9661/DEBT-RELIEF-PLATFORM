"""
User profile endpoints (view + update the authenticated user's own profile).
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import models, schemas
from app.core.deps import get_current_user
from app.database import get_db

router = APIRouter(prefix="/api/users", tags=["Users"])


@router.get("/me", response_model=schemas.UserOut)
def read_my_profile(current_user: models.User = Depends(get_current_user)):
    return current_user


@router.patch("/me", response_model=schemas.UserOut)
def update_my_profile(
    payload: schemas.UserUpdate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(current_user, field, value)
    db.commit()
    db.refresh(current_user)
    return current_user
