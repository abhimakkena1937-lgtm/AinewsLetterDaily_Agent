import os
import requests
from dotenv import load_dotenv

load_dotenv()

GOOGLE_APPS_SCRIPT_URL = os.getenv("GOOGLE_APPS_SCRIPT_URL")


def send_newsletter(
    subject: str,
    html: str,
):
    if not GOOGLE_APPS_SCRIPT_URL:
        raise RuntimeError(
            "GOOGLE_APPS_SCRIPT_URL is missing"
        )

    payload = {
        "action": "send_newsletter",
        "subject": subject,
        "html": html,
    }

    response = requests.post(
        GOOGLE_APPS_SCRIPT_URL,
        json=payload,
        timeout=60,
    )

    response.raise_for_status()

    result = response.json()

    if not result.get("success"):
        raise RuntimeError(
            result.get(
                "error",
                "Google Apps Script failed"
            )
        )

    print(
        f"Newsletter sent to "
        f"{result.get('sent', 0)} subscribers"
    )

    return result