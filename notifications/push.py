import httpx
from typing import Optional


EXPO_PUSH_URL = "https://exp.host/--/api/v2/push/send"


def send_push_notification(
    token: str,
    title: str,
    body: str,
    data: Optional[dict] = None,
    ):
    payload = {
        "to": token,
        "title": title,
        "body": body,
        "data": data or {},
    }

    try:
        response = httpx.post(
            EXPO_PUSH_URL,
            json=payload,
            timeout=10.0,
        )

        response.raise_for_status()

        return response.json()

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }