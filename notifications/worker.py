"""Run one dedicated worker; never start implicitly in API processes."""
import argparse
import logging
import time
from datetime import datetime, timedelta, timezone
from sqlalchemy import select
from db.database import SessionLocal
from db.models import User, PushReceipt, PushToken
from db.init_db import check_schema
from db.unit_of_work import user_transaction, bind_session, UserUnavailableError
from notifications.scheduler import check_user_notifications_for_user
from notifications.notifications import send_notification
from notifications.push import get_push_receipts

logger = logging.getLogger(__name__)


def poll_receipts():
    now = datetime.now(timezone.utc)
    with SessionLocal() as db:
        pending = db.scalars(select(PushReceipt).where(PushReceipt.created_at <= now - timedelta(minutes=15)).order_by(PushReceipt.created_at).limit(100)).all()
        snapshot = [(r.ticket_id, r.user_id, r.token, r.created_at) for r in pending]
    if not snapshot: return
    result = get_push_receipts([r[0] for r in snapshot])
    for ticket_id, uid, token, created in snapshot:
        with SessionLocal() as db:
            try:
                with user_transaction(db, uid):
                    receipt = db.get(PushReceipt, ticket_id)
                    if receipt is None: continue
                    status = result.get(ticket_id)
                    created = created.replace(tzinfo=timezone.utc) if created.tzinfo is None else created
                    if not status and created > now - timedelta(hours=24): continue
                    if status and status.get('details', {}).get('error') == 'DeviceNotRegistered':
                        db.query(PushToken).filter_by(user_id=uid, token=token).delete(synchronize_session=False)
                    if not status or status.get('status') != 'ok':
                        logger.warning('Push delivery failed or receipt expired')
                    db.delete(receipt)
            except UserUnavailableError:
                continue


def run_once():
    poll_receipts()
    with SessionLocal() as db:
        ids = list(db.scalars(select(User.id).where(User.notifications_enabled == True, User.email_verified == True)))
    for uid in ids:
        with SessionLocal() as db:
            try:
                with user_transaction(db, uid), bind_session(db):
                    notification = check_user_notifications_for_user(db, uid)
                    if notification: send_notification(db, uid, notification)
            except UserUnavailableError:
                continue
            except Exception:
                logger.error('Notification worker could not process an account')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--once', action='store_true')
    args = parser.parse_args()
    from core.operations import validate_environment
    validate_environment()
    check_schema()
    while True:
        try: run_once()
        except Exception: logger.error('Notification worker cycle failed')
        if args.once: break
        time.sleep(60)


if __name__ == '__main__': main()
