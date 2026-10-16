"""Request diagnostics with no bodies, query strings, IDs, headers or exception text."""
import logging
import time
import uuid

from fastapi.responses import JSONResponse

logger = logging.getLogger('mirai.requests')


async def diagnose_request(request, call_next):
    request_id = uuid.uuid4().hex
    started = time.monotonic()
    failure_type = None
    try:
        response = await call_next(request)
    except Exception as error:
        # The user transaction has unwound before call_next raises. Do not forward
        # arbitrary exception strings (SQL parameters can include private data).
        failure_type = type(error).__name__
        response = JSONResponse(status_code=500, content={'detail': 'Mirai could not complete this request. Please try again.', 'code': 'internal_error'})
    response.headers['X-Request-ID'] = request_id
    elapsed_ms = round((time.monotonic() - started) * 1000)
    if response.status_code >= 400 or elapsed_ms >= 5000:
        route = getattr(request.scope.get('route'), 'path', 'unmatched')
        # Only router-declared templates are logged; never the supplied URL.
        category = getattr(request.state, 'failure_code', None)
        if category is None:
            category = ('authentication' if response.status_code in (401, 403) else
                        'rate_limit' if response.status_code == 429 else
                        'server_error' if response.status_code >= 500 else
                        'client_error' if response.status_code >= 400 else 'slow_request')
        logger.warning('request id=%s route=%s status=%s duration_ms=%s category=%s error_type=%s',
                       request_id, route, response.status_code, elapsed_ms, category, failure_type or 'none')
    return response
