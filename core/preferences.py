from typing import Optional, Literal
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from auth.router import get_current_user
from core.state_store import read_document, write_document

router = APIRouter(tags=['preferences'])
DEFAULTS = {'language': 'English', 'mode': 'Auto'}


class PreferencesPatch(BaseModel):
    language: Optional[Literal['English', 'Japanese', 'Spanish']] = None
    mode: Optional[Literal['Auto', 'Casual', 'Learning']] = None


@router.get('/preferences')
def preferences(user=Depends(get_current_user, scope='function')):
    return read_document(user['id'], 'preferences', DEFAULTS)


@router.patch('/preferences')
def update_preferences(data: PreferencesPatch, user=Depends(get_current_user, scope='function')):
    current = read_document(user['id'], 'preferences', DEFAULTS)
    current.update(data.model_dump(exclude_none=True))
    write_document(user['id'], 'preferences', current)
    return current
