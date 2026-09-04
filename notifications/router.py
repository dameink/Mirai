from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from db.database import get_db
from db.models import PushToken
from auth.router import get_current_user


router = APIRouter(prefix="/notifications", tags=["notifications"])


class PushTokenRequest(BaseModel):
    token: str
    platform: str


@router.post("/register")
def register_push_token(
    data: PushTokenRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    existing = (
        db.query(PushToken)
        .filter(PushToken.token == data.token)
        .first()
    )

    if existing:
        existing.user_id = current_user.id
        existing.platform = data.platform
        existing.last_used_at = datetime.now(timezone.utc)
    else:
        push_token = PushToken(
            user_id=current_user["id"],
            token=data.token,
            platform=data.platform,
        )
        db.add(push_token)

    db.commit()

    return {
        "message": "Push token registered"
    }

@router.post("/test")
def test_notification(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    push_token = (
        db.query(PushToken)
        .filter(PushToken.user_id == current_user["id"])
        .first()
    )

    if not push_token:
        return {
            "success": False,
            "message": "No push token registered"
        }

    from notifications.push import send_push_notification

    result = send_push_notification(
        token=push_token.token,
        title="Mirai 🌸",
        body="Hey! I'm here. Come talk to me.",
        data={
            "type": "test",
        },
    )

    return result