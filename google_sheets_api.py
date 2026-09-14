import os
import requests

from dotenv import load_dotenv

load_dotenv()

GOOGLE_APPS_SCRIPT_URL = os.getenv("GOOGLE_APPS_SCRIPT_URL")


def _call_apps_script(payload: dict):
    if not GOOGLE_APPS_SCRIPT_URL:
        raise RuntimeError(
            "GOOGLE_APPS_SCRIPT_URL is missing"
        )

    response = requests.post(
        GOOGLE_APPS_SCRIPT_URL,
        json=payload,
        timeout=30,
    )

    response.raise_for_status()

    result = response.json()

    if not result.get("success"):
        raise RuntimeError(
            result.get(
                "error",
                "Google Apps Script request failed"
            )
        )

    return result


def subscribe(email: str):
    return _call_apps_script({
        "action": "subscribe",
        "email": email,
    })


def unsubscribe(email: str):
    return _call_apps_script({
        "action": "unsubscribe",
        "email": email,
    })