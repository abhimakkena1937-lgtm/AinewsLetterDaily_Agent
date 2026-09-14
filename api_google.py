from pathlib import Path

from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, EmailStr

from google_sheets_api import subscribe, unsubscribe


app = FastAPI(title="AI Daily Newsletter API")


class SubscribeRequest(BaseModel):
    email: EmailStr


@app.get("/", response_class=HTMLResponse)
def home():
    return Path("templates/index.html").read_text(encoding="utf-8")


@app.post("/subscribe")
def subscribe_user(request: SubscribeRequest):
    result = subscribe(str(request.email))
    return result


@app.post("/unsubscribe")
def remove_subscriber(request: SubscribeRequest):
    result = unsubscribe(str(request.email))
    return result


@app.get("/unsubscribe", response_class=HTMLResponse)
def unsubscribe_user(email: EmailStr = Query(...)):
    result = unsubscribe(str(email))

    if not result.get("success"):
        message = result.get(
            "message",
            "This email is not currently subscribed."
        )
    else:
        message = "You have been successfully unsubscribed from AI Daily."

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>AI Daily - Unsubscribe</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">

        <style>
            body {{
                font-family: Arial, sans-serif;
                background: #f5f7fa;
                display: flex;
                justify-content: center;
                align-items: center;
                min-height: 100vh;
                margin: 0;
            }}

            .card {{
                background: white;
                padding: 40px;
                border-radius: 12px;
                text-align: center;
                box-shadow: 0 4px 20px rgba(0,0,0,0.08);
                max-width: 500px;
                margin: 20px;
            }}

            h1 {{
                margin-bottom: 15px;
            }}

            p {{
                color: #555;
                line-height: 1.6;
            }}
        </style>
    </head>

    <body>
        <div class="card">
            <h1>AI Daily</h1>
            <p>{message}</p>
        </div>
    </body>
    </html>
    """