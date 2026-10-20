"""Private, durable reports of AI replies; only operators can read the queue."""
from typing import Literal
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from auth.router import get_current_user
from db.database import get_db
from db.models import Message, ContentReport

class ReportRequest(BaseModel):
    message_id: UUID
    reason: Literal['harmful', 'sexual', 'hate', 'incorrect', 'other']

router = APIRouter(tags=['content reports'])

@router.post('/content-reports')
def report_reply(data: ReportRequest, user=Depends(get_current_user, scope='function'), db: Session = Depends(get_db)):
    message_id = str(data.message_id)
    existing = db.get(ContentReport, message_id)
    if existing is not None and existing.user_id == user['id']:
        return {'status': 'received'}
    message = db.query(Message).filter_by(id=message_id, user_id=user['id'], role='assistant').first()
    if message is None:
        raise HTTPException(status_code=404, detail='This reply is no longer available.')
    # No client-supplied text or owner: report the actual saved reply.
    db.add(ContentReport(message_id=message.id, user_id=user['id'], reason=data.reason, content=message.content))
    db.flush()
    return {'status': 'received'}
