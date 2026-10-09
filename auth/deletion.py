"""Account deletion plus a durable retry queue for legacy filesystem cleanup."""
import logging
import shutil
from pathlib import Path
from uuid import UUID
from sqlalchemy import delete, select
from db.database import Base, SessionLocal
from db.models import User, AccountErasureJob

logger = logging.getLogger(__name__)


def delete_account_data(db, user_id):
    # Explicit child deletes also support legacy databases lacking FK cascades.
    for table in reversed(Base.metadata.sorted_tables):
        if table.name != "account_erasure_jobs" and "user_id" in table.c:
            db.execute(delete(table).where(table.c.user_id == user_id))
    db.execute(delete(User).where(User.id == user_id))
    db.add(AccountErasureJob(user_id=user_id))
    db.flush()


def purge_deleted_files(user_id=None):
    from core.user_state import BASE_DIR
    report = {"completed": 0, "pending": 0}
    with SessionLocal() as db:
        statement = select(AccountErasureJob)
        if user_id is not None:
            statement = statement.where(AccountErasureJob.user_id == user_id)
        statement = statement.with_for_update(skip_locked=True)
        for job in db.scalars(statement).all():
            try:
                if str(UUID(job.user_id)) != job.user_id:
                    raise ValueError("Invalid erasure identifier")
                path = Path(BASE_DIR) / job.user_id
                if path.is_symlink():
                    path.unlink()  # remove only the link, never its target
                elif path.exists():
                    shutil.rmtree(path)
                db.delete(job)
                db.commit()
                report["completed"] += 1
            except Exception:
                db.rollback()
                report["pending"] += 1
                logger.error("Legacy account erasure pending; run db.manage purge-deleted")
    return report
