import json
import os
from pathlib import Path

from newsletter_data import load_newsletter_data

from fastapi import FastAPI, Query, Header, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, EmailStr

from google_sheets_api import (
    subscribe,
    unsubscribe,
    check_subscriber,
)


app = FastAPI(title="AI Daily Newsletter API")


# =====================================================
# STATIC FILES
# =====================================================

app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static"
)


# =====================================================
# REQUEST MODELS
# =====================================================

class SubscribeRequest(BaseModel):
    email: EmailStr


class CheckSubscriberRequest(BaseModel):
    email: EmailStr


class PublishNewsletterRequest(BaseModel):
    data: dict


# =====================================================
# HOME
# =====================================================

@app.get("/", response_class=HTMLResponse)
def home():

    return Path(
        "templates/index.html"
    ).read_text(
        encoding="utf-8"
    )


# =====================================================
# SUBSCRIBE
# =====================================================

@app.post("/subscribe")
def subscribe_user(
    request: SubscribeRequest
):

    result = subscribe(
        str(request.email)
    )

    return result


# =====================================================
# UNSUBSCRIBE
# =====================================================

@app.post("/unsubscribe")
def remove_subscriber(
    request: SubscribeRequest
):

    result = unsubscribe(
        str(request.email)
    )

    return result


# =====================================================
# CHECK SUBSCRIBER
# =====================================================

@app.post("/api/check-subscriber")
def check_subscriber_user(
    request: CheckSubscriberRequest
):

    result = check_subscriber(
        str(request.email)
    )

    return result


# =====================================================
# UNSUBSCRIBE PAGE
# =====================================================

@app.get(
    "/unsubscribe",
    response_class=HTMLResponse
)
def unsubscribe_user(
    email: EmailStr = Query(...)
):

    result = unsubscribe(
        str(email)
    )

    if not result.get("success"):

        message = result.get(
            "message",
            "This email is not currently subscribed."
        )

    else:

        message = (
            "You have been successfully "
            "unsubscribed from AI Daily."
        )

    return f"""
    <!DOCTYPE html>

    <html>

    <head>

        <title>
            AI Daily - Unsubscribe
        </title>

        <meta
            name="viewport"
            content="width=device-width, initial-scale=1"
        >

        <style>

            body {{
                font-family:
                    Arial,
                    sans-serif;

                background:
                    #f5f7fa;

                display:
                    flex;

                justify-content:
                    center;

                align-items:
                    center;

                min-height:
                    100vh;

                margin:
                    0;
            }}

            .card {{
                background:
                    white;

                padding:
                    40px;

                border-radius:
                    12px;

                text-align:
                    center;

                box-shadow:
                    0 4px 20px
                    rgba(0,0,0,0.08);

                max-width:
                    500px;

                margin:
                    20px;
            }}

            h1 {{
                margin-bottom:
                    15px;
            }}

            p {{
                color:
                    #555;

                line-height:
                    1.6;
            }}

        </style>

    </head>

    <body>

        <div class="card">

            <h1>
                AI Daily
            </h1>

            <p>
                {message}
            </p>

        </div>

    </body>

    </html>
    """


# =====================================================
# PUBLISH NEWSLETTER
# =====================================================

@app.post("/api/publish-newsletter")
def publish_newsletter(
    request: PublishNewsletterRequest,
    x_newsletter_key: str | None = Header(
        default=None
    ),
):

    # -------------------------------------------------
    # Get secret configured in Render
    # -------------------------------------------------

    expected_key = os.getenv(
        "NEWSLETTER_PUBLISH_KEY"
    )

    if not expected_key:

        raise HTTPException(
            status_code=500,
            detail=(
                "NEWSLETTER_PUBLISH_KEY "
                "is not configured on Render."
            ),
        )

    # -------------------------------------------------
    # Verify GitHub Actions secret
    # -------------------------------------------------

    if x_newsletter_key != expected_key:

        raise HTTPException(
            status_code=401,
            detail="Invalid newsletter publish key."
        )

    # -------------------------------------------------
    # Validate newsletter data
    # -------------------------------------------------

    newsletter_data = request.data

    if not isinstance(
        newsletter_data,
        dict
    ):

        raise HTTPException(
            status_code=400,
            detail="Newsletter data must be a JSON object."
        )

    # -------------------------------------------------
    # Make sure expected fields exist
    # -------------------------------------------------

    newsletter_data.setdefault(
        "date",
        None
    )

    newsletter_data.setdefault(
        "time_window",
        None
    )

    newsletter_data.setdefault(
        "news",
        []
    )

    newsletter_data.setdefault(
        "startups",
        []
    )

    newsletter_data.setdefault(
        "people",
        []
    )

    newsletter_data.setdefault(
        "tweets",
        []
    )

    newsletter_data.setdefault(
        "github_repos",
        []
    )

    newsletter_data.setdefault(
        "research_papers",
        []
    )

    newsletter_data.setdefault(
        "discovered_entities",
        []
    )

    newsletter_data.setdefault(
        "tool_of_the_day",
        None
    )

    # -------------------------------------------------
    # Output directory
    # -------------------------------------------------

    output_dir = Path(
        "output"
    )

    output_dir.mkdir(
        exist_ok=True
    )

    json_file = (
        output_dir
        / "newsletter.json"
    )

    # -------------------------------------------------
    # Write temporary file first
    # -------------------------------------------------

    temp_file = (
        output_dir
        / "newsletter.tmp.json"
    )

    try:

        temp_file.write_text(
            json.dumps(
                newsletter_data,
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

        # -------------------------------------------------
        # Atomic replacement
        # -------------------------------------------------

        temp_file.replace(
            json_file
        )

    except Exception as error:

        # -------------------------------------------------
        # Remove temporary file if necessary
        # -------------------------------------------------

        try:

            if temp_file.exists():
                temp_file.unlink()

        except Exception:
            pass

        raise HTTPException(
            status_code=500,
            detail=(
                f"Failed to publish newsletter: "
                f"{error}"
            ),
        )

    # -------------------------------------------------
    # Success
    # -------------------------------------------------

    print(
        "\n" + "=" * 80
    )

    print(
        "NEWSLETTER PUBLISHED TO RENDER"
    )

    print(
        "=" * 80
    )

    print(
        "DATE:",
        newsletter_data.get("date")
    )

    print(
        "NEWS:",
        len(
            newsletter_data.get(
                "news",
                []
            )
        )
    )

    print(
        "STARTUPS:",
        len(
            newsletter_data.get(
                "startups",
                []
            )
        )
    )

    print(
        "PEOPLE:",
        len(
            newsletter_data.get(
                "people",
                []
            )
        )
    )

    print(
        "GITHUB:",
        len(
            newsletter_data.get(
                "github_repos",
                []
            )
        )
    )

    print(
        "RESEARCH:",
        len(
            newsletter_data.get(
                "research_papers",
                []
            )
        )
    )

    tool = newsletter_data.get(
        "tool_of_the_day"
    )

    print(
        "TOOL OF THE DAY:",
        (
            tool.get("name")
            if isinstance(tool, dict)
            else "None"
        )
    )

    print(
        "=" * 80
    )

    return {
        "success": True,
        "message": "Newsletter published successfully.",
        "date": newsletter_data.get(
            "date"
        ),
        "tool_of_the_day": tool,
    }


# =====================================================
# NEWS API
# =====================================================

@app.get("/api/news")
def get_news():

    data = load_newsletter_data()

    return {
        "date": data.get("date"),
        "items": data.get(
            "news",
            []
        ),
    }


# =====================================================
# STARTUPS API
# =====================================================

@app.get("/api/startups")
def get_startups():

    data = load_newsletter_data()

    return {
        "date": data.get("date"),
        "items": data.get(
            "startups",
            []
        ),
    }


# =====================================================
# PEOPLE API
# =====================================================

@app.get("/api/people")
def get_people():

    data = load_newsletter_data()

    return {
        "date": data.get("date"),
        "items": data.get(
            "people",
            []
        ),
    }


# =====================================================
# GITHUB API
# =====================================================

@app.get("/api/github")
def get_github():

    data = load_newsletter_data()

    return {
        "date": data.get("date"),
        "items": data.get(
            "github_repos",
            []
        ),
    }


# =====================================================
# RESEARCH API
# =====================================================

@app.get("/api/research")
def get_research():

    data = load_newsletter_data()

    return {
        "date": data.get("date"),
        "items": data.get(
            "research_papers",
            []
        ),
    }


# =====================================================
# TOOL OF THE DAY API
# =====================================================

@app.get("/api/tool-of-the-day")
def get_tool_of_the_day():

    data = load_newsletter_data()

    return {
        "date": data.get("date"),
        "tool": data.get(
            "tool_of_the_day"
        ),
    }


# =====================================================
# FULL NEWSLETTER API
# =====================================================

@app.get("/api/newsletter")
def get_newsletter():

    return load_newsletter_data()