import os
import httpx

EXPO_PUSH_URL = 'https://exp.host/--/api/v2/push/send'
EXPO_RECEIPTS_URL = 'https://exp.host/--/api/v2/push/getReceipts'


def provider_headers():
    token = os.getenv('EXPO_ACCESS_TOKEN')
    return {'Authorization': 'Bearer ' + token} if token else {}


def send_push_notification(token, title, body, data=None):
    try:
        response = httpx.post(EXPO_PUSH_URL, json={'to': token, 'title': title, 'body': body, 'data': data or {}}, headers=provider_headers(), timeout=10.0)
        response.raise_for_status()
        result = response.json()
        ticket = result.get('data', {})
        if not isinstance(ticket, dict) or ticket.get('status') != 'ok' or not ticket.get('id'):
            return {'success': False, 'error': 'Push provider rejected the notification', 'code': ticket.get('details', {}).get('error') if isinstance(ticket, dict) else None}
        return {'success': True, 'ticket_id': ticket['id']}
    except (httpx.HTTPError, ValueError, TypeError, AttributeError):
        return {'success': False, 'error': 'Push provider temporarily unavailable'}


def get_push_receipts(ids):
    response = httpx.post(EXPO_RECEIPTS_URL, json={'ids': ids}, headers=provider_headers(), timeout=10.0)
    response.raise_for_status()
    return response.json().get('data', {})
