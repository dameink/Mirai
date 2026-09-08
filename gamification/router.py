from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from db.database import get_db
from auth.router import get_current_user

from gamification.service import get_gamification_data


router = APIRouter(
    prefix="/gamification",
    tags=["Gamification"],
)


@router.get("")
def get_gamification(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return get_gamification_data(
        db,
        current_user["id"],
    )