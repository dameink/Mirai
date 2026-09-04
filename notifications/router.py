from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from notifications.notifications import send_notification
from db.database import get_db
from db.models import PushToken, Notification
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

    notification = {
        "type": "test",
        "title": "Mirai 🌸",
        "body": "Hey! I'm here. Come talk to me.",
        "data": {
            "type": "test",
        },
    }

    result = send_notification(
        db=db,
        user_id=current_user["id"],
        notification=notification,
    )

    return result


@router.post("/{notification_id}/opened")
def mark_notification_opened(
    notification_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    notification = (
        db.query(Notification)
        .filter(
            Notification.id == notification_id,
            Notification.user_id == current_user["id"],
        )
        .first()
    )

    if not notification:
        return {
            "success": False,
            "message": "Notification not found",
        }

    if notification.opened_at is None:
        notification.opened_at = datetime.now(timezone.utc)
        db.commit()

    return {
        "success": True,
        "message": "Notification marked as opened",
    }


class NotificationSettingsRequest(BaseModel):
    enabled: bool


@router.get("/settings")
def get_notification_settings(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    from db.models import User

    user = (
        db.query(User)
        .filter(User.id == current_user["id"])
        .first()
    )

    if not user:
        return {
            "success": False,
            "message": "User not found",
        }

    return {
        "success": True,
        "notifications_enabled": user.notifications_enabled,
    }


@router.patch("/settings")
def update_notification_settings(
    data: NotificationSettingsRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    from db.models import User

    user = (
        db.query(User)
        .filter(User.id == current_user["id"])
        .first()
    )

    if not user:
        return {
            "success": False,
            "message": "User not found",
        }

    user.notifications_enabled = data.enabled

    db.commit()

    return {
        "success": True,
        "notifications_enabled": user.notifications_enabled,
    }