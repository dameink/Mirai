"""Production configuration gates and non-sensitive health checks."""
import os
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from db.init_db import check_schema

router = APIRouter(tags=['operations'])


def closed_beta():
    return os.getenv('MIRAI_CLOSED_BETA', 'false').lower() == 'true'


def validate_environment():
    if os.getenv('MIRAI_ENV', 'development') != 'production':
        return
    from db.database import engine
    failures = []
    if engine.dialect.name != 'postgresql': failures.append('DATABASE_URL must use PostgreSQL')
    for flag in ('MIRAI_EMAIL_DEV_MODE', 'MIRAI_AUTO_MIGRATE'):
        if os.getenv(flag, 'false').lower() == 'true': failures.append(flag + ' must be false')
    required = ['OPENROUTER_API_KEY', 'MIRAI_LLM_MODEL']
    if not closed_beta():
        required += ['RESEND_API_KEY', 'RESEND_FROM_EMAIL']
    for key in required:
        if not os.getenv(key, '').strip(): failures.append(key + ' is required')
    if failures:
        raise RuntimeError('Invalid production configuration: ' + '; '.join(failures))


@router.get('/health/live')
def live():
    return {'status': 'ok'}


@router.get('/health/ready')
def ready():
    try:
        check_schema()
    except Exception:
        return JSONResponse(status_code=503, content={'status': 'unavailable'})
    return {'status': 'ready'}
