import asyncio

from state import NewsLetterState
from gmail_email_sender import send_newsletter


async def gmail_email_node(state: NewsLetterState) -> dict:
    print("\n" + "=" * 80)
    print("RUNNING GMAIL EMAIL AGENT")
    print("=" * 80)

    html = state["newsletter_html"]
    date = state["date"]

    subject = f"AI Daily — {date}"

    max_retries = 3

    for attempt in range(1, max_retries + 1):
        try:
            result = send_newsletter(
                subject=subject,
                html=html,
            )

            sent = result.get("sent", 0)
            failed = result.get("failed", 0)

            print(
                f"Gmail newsletter completed "
                f"(attempt {attempt})"
            )

            print("Subscribers sent:", sent)
            print("Failed:", failed)

            return {
                "progress": [
                    f"gmail_email: sent to {sent} subscribers",
                    f"gmail_email: {failed} failures",
                ]
            }

        except Exception as e:
            print(
                f"Gmail email attempt "
                f"{attempt}/{max_retries} failed -> {e}"
            )

            if attempt < max_retries:
                await asyncio.sleep(2)
            else:
                print("Gmail email permanently failed.")

                return {
                    "errors": [
                        f"gmail_email: {e}"
                    ],
                    "progress": [
                        "gmail_email: delivery failed"
                    ],
                }