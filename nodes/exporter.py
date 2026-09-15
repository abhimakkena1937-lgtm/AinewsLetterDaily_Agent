from markdown import markdown
from pathlib import Path
import webbrowser
import json
import re

from state import NewsLetterState


# ============================================================
# SERIALIZE ITEMS
# ============================================================

def serialize_items(items):
    """
    Convert Pydantic models into JSON-serializable dictionaries.
    """

    serialized = []

    for item in items or []:

        if hasattr(item, "model_dump"):

            serialized.append(
                item.model_dump(mode="json")
            )

        elif isinstance(item, dict):

            serialized.append(item)

        else:

            serialized.append(
                dict(item)
            )

    return serialized


# ============================================================
# TEXT NORMALIZATION
# ============================================================

def normalize_text(value):
    """
    Normalize text so image assignments can be matched to
    newsletter items even when capitalization or punctuation differs.
    """

    if not value:
        return ""

    value = str(value).lower().strip()

    value = re.sub(
        r"[^a-z0-9\s]",
        " ",
        value
    )

    value = re.sub(
        r"\s+",
        " ",
        value
    )

    return value


# ============================================================
# ITEM TITLE
# ============================================================

def get_item_title(item, item_type):
    """
    Return the title/name used to match an image assignment
    with a structured newsletter item.
    """

    if item_type == "news":
        return item.get("title", "")

    if item_type == "startup":
        return item.get("startup_name", "")

    if item_type == "people":
        return item.get("person", "")

    if item_type == "github":
        return item.get("repo_name", "")

    if item_type == "research":
        return item.get("title", "")

    if item_type == "tool":
        return item.get("name", "")

    return ""


# ============================================================
# FLATTEN IMAGE RESULTS
# ============================================================

def flatten_image_results(image_results):
    """
    Image Agent results can arrive as:
    - a normal list
    - a dictionary containing assignments/candidates
    - Pydantic objects inside a list

    This function converts the outer structure into one list.
    """

    if not image_results:
        return []

    if isinstance(image_results, dict):

        for key in (
            "assignments",
            "images",
            "results",
            "image_results",
            "candidates",
        ):

            value = image_results.get(key)

            if isinstance(value, list):
                return value

        return [image_results]

    if isinstance(image_results, list):
        return image_results

    return []


# ============================================================
# GENERIC OBJECT FIELD READER
# ============================================================

def get_field_value(obj, *field_names):
    """
    Safely get a field from:
    - dict
    - Pydantic model
    - normal Python object
    """

    # --------------------------------------------------------
    # Dictionary
    # --------------------------------------------------------

    if isinstance(obj, dict):

        for field_name in field_names:

            value = obj.get(field_name)

            if value is not None:
                return value

    # --------------------------------------------------------
    # Pydantic model / normal object
    # --------------------------------------------------------

    for field_name in field_names:

        if hasattr(obj, field_name):

            value = getattr(
                obj,
                field_name
            )

            if value is not None:
                return value

    return ""


# ============================================================
# IMAGE URL
# ============================================================

def get_image_url(image):
    """
    Get image URL from the actual Image Agent object.
    """

    value = get_field_value(
        image,
        "image_url",
        "url",
        "image",
        "src",
    )

    if value and str(value).startswith(
        ("http://", "https://")
    ):
        return str(value).strip()

    return ""


# ============================================================
# IMAGE TITLE
# ============================================================

def get_image_title(image):
    """
    Get the title/name associated with the image.
    """

    value = get_field_value(
        image,
        "item_title",
        "title",
        "name",
        "item",
    )

    return str(value).strip() if value else ""


# ============================================================
# IMAGE CATEGORY
# ============================================================

def get_image_category(image):
    """
    Get the category associated with the image.
    """

    value = get_field_value(
        image,
        "category",
    )

    return normalize_text(value) if value else ""


# ============================================================
# ATTACH IMAGES
# ============================================================

def attach_images(items, item_type, image_results):
    """
    Attach Image Agent image URLs to the corresponding
    structured newsletter items.

    Existing item.image_url values are preserved.
    """

    if not items:
        return items

    images = flatten_image_results(
        image_results
    )

    if not images:

        print(
            f"WARNING: No image results received for {item_type}."
        )

        return items

    assignments = []

    # ========================================================
    # PARSE IMAGE RESULTS
    # ========================================================

    for image in images:

        image_url = get_image_url(image)

        image_title = normalize_text(
            get_image_title(image)
        )

        image_category = get_image_category(
            image
        )

        if not image_url:
            continue

        assignments.append(
            {
                "url": image_url,
                "title": image_title,
                "category": image_category,
            }
        )

    # ========================================================
    # NO VALID ASSIGNMENTS
    # ========================================================

    if not assignments:

        print(
            f"WARNING: No usable image assignments "
            f"found for {item_type}."
        )

        return items

    print(
        f"Parsed {len(assignments)} image assignments "
        f"for {item_type}"
    )

    # ========================================================
    # MATCH IMAGES TO ITEMS
    # ========================================================

    for item in items:

        # ----------------------------------------------------
        # Keep an image already attached to the item
        # ----------------------------------------------------

        if item.get("image_url"):
            continue

        item_title = normalize_text(
            get_item_title(
                item,
                item_type
            )
        )

        if not item_title:
            continue

        best_match = None
        best_score = 0

        # ====================================================
        # CHECK EVERY IMAGE ASSIGNMENT
        # ====================================================

        for assignment in assignments:

            assignment_title = assignment["title"]

            if not assignment_title:
                continue

            score = 0

            # ------------------------------------------------
            # Exact title match
            # ------------------------------------------------

            if item_title == assignment_title:

                score = 100

            # ------------------------------------------------
            # One title contains the other
            # ------------------------------------------------

            elif (
                item_title in assignment_title
                or assignment_title in item_title
            ):

                score = 80

            # ------------------------------------------------
            # Word overlap
            # ------------------------------------------------

            else:

                item_words = set(
                    item_title.split()
                )

                assignment_words = set(
                    assignment_title.split()
                )

                if (
                    item_words
                    and assignment_words
                ):

                    overlap = (
                        len(
                            item_words
                            &
                            assignment_words
                        )
                        /
                        max(
                            len(item_words),
                            len(assignment_words)
                        )
                    )

                    if overlap >= 0.65:
                        score = 60

            # ------------------------------------------------
            # Category preference
            # ------------------------------------------------

            if score and assignment["category"]:

                category = assignment["category"]

                if item_type == "news":

                    if category in (
                        "news",
                        "ai news",
                        "ai",
                        "ai ml",
                        "ai & ml",
                        "ai safety",
                        "ai policy",
                        "model release",
                        "product launch",
                        "hardware",
                        "developer tools",
                        "company development",
                    ):

                        score += 5

                elif item_type == "startup":

                    if "startup" in category:
                        score += 5

                elif item_type == "people":

                    if (
                        "people" in category
                        or "person" in category
                    ):

                        score += 5

                elif item_type == "github":

                    if "github" in category:
                        score += 5

                elif item_type == "research":

                    if "research" in category:
                        score += 5

                elif item_type == "tool":

                    if (
                        "tool" in category
                        or "product" in category
                        or "developer" in category
                    ):
                        score += 5

            # ------------------------------------------------
            # Keep best match
            # ------------------------------------------------

            if score > best_score:

                best_score = score
                best_match = assignment

        # ====================================================
        # ATTACH BEST MATCH
        # ====================================================

        if (
            best_match
            and best_score >= 60
        ):

            item["image_url"] = (
                best_match["url"]
            )

    return items


# ============================================================
# EXPORTER NODE
# ============================================================

async def exporter_node(
    state: NewsLetterState
) -> dict:

    markdown_text = state[
        "newsletter_markdown"
    ]

    print("\n" + "=" * 80)
    print("RUNNING EXPORTER")
    print("=" * 80)

    # ========================================================
    # CONVERT MARKDOWN TO HTML
    # ========================================================

    content_html = markdown(
        markdown_text,
        extensions=["extra"]
    )

    html = f"""
<!DOCTYPE html>
<html lang="en">

<head>

    <meta charset="UTF-8">

    <meta
        name="viewport"
        content="width=device-width, initial-scale=1.0"
    >

    <title>AI Daily</title>

    <style>

        * {{
            box-sizing: border-box;
        }}

        body {{
            margin: 0;
            padding: 0;
            background: #f5f5f5;
            font-family: Arial, Helvetica, sans-serif;
            color: #222;
        }}

        .container {{
            max-width: 750px;
            margin: 40px auto;
            background: white;
            padding: 35px;
            border-radius: 10px;
        }}

        h1 {{
            margin-top: 0;
            font-size: 32px;
        }}

        h2 {{
            margin-top: 35px;
            padding-bottom: 8px;
            border-bottom: 1px solid #ddd;
            font-size: 22px;
        }}

        h3 {{
            margin-top: 25px;
            margin-bottom: 8px;
            font-size: 18px;
        }}

        p {{
            line-height: 1.6;
        }}

        li {{
            margin-bottom: 12px;
            line-height: 1.5;
        }}

        a {{
            text-decoration: none;
            word-break: break-word;
        }}

        img {{
            display: block;
            width: 100%;
            max-width: 100%;
            height: auto;
            margin: 15px 0 20px 0;
            border-radius: 8px;
        }}

        ul {{
            padding-left: 25px;
        }}

        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            font-size: 13px;
            color: #777;
            text-align: center;
        }}

        @media (max-width: 800px) {{

            body {{
                background: white;
            }}

            .container {{
                margin: 0;
                padding: 20px;
                border-radius: 0;
            }}

            h1 {{
                font-size: 28px;
            }}

        }}

    </style>

</head>

<body>

    <div class="container">

        {content_html}

        <div class="footer">
            AI Daily — Automated AI research newsletter
        </div>

    </div>

</body>

</html>
"""

    # ========================================================
    # CREATE OUTPUT DIRECTORY
    # ========================================================

    output_dir = Path("output")

    output_dir.mkdir(
        exist_ok=True
    )

    # ========================================================
    # SAVE MARKDOWN
    # ========================================================

    markdown_file = (
        output_dir
        / "ai_daily.md"
    )

    markdown_file.write_text(
        markdown_text,
        encoding="utf-8"
    )

    # ========================================================
    # SAVE HTML
    # ========================================================

    html_file = (
        output_dir
        / "ai_daily.html"
    )

    html_file.write_text(
        html,
        encoding="utf-8"
    )

    # ========================================================
    # PREPARE STRUCTURED DATA
    # ========================================================

    news = serialize_items(
        state.get(
            "news",
            []
        )
    )

    startups = serialize_items(
        state.get(
            "startups",
            []
        )
    )

    tweets = serialize_items(
        state.get(
            "tweets",
            []
        )
    )

    github_repos = serialize_items(
        state.get(
            "github_repos",
            []
        )
    )

    research_papers = serialize_items(
        state.get(
            "research_papers",
            []
        )
    )

    discovered_entities = serialize_items(
        state.get(
            "discovered_entities",
            []
        )
    )

    # ========================================================
    # TOOL OF THE DAY
    # ========================================================

    tool_of_the_day = state.get(
        "tool_of_the_day",
        None
    )

    if tool_of_the_day is not None:

        if hasattr(
            tool_of_the_day,
            "model_dump"
        ):

            tool_of_the_day = (
                tool_of_the_day.model_dump(
                    mode="json"
                )
            )

        elif isinstance(
            tool_of_the_day,
            dict
        ):

            tool_of_the_day = dict(
                tool_of_the_day
            )

        else:

            try:

                tool_of_the_day = dict(
                    tool_of_the_day
                )

            except Exception:

                tool_of_the_day = None

    # ========================================================
    # IMAGE RESULTS
    # ========================================================

    image_results = state.get(
        "image_results",
        []
    )

    # ========================================================
    # TEMPORARY DIAGNOSTIC
    # ========================================================

    print("\nIMAGE RESULT TYPES:")

    for i, image in enumerate(
        image_results[:5]
    ):

        print(
            i,
            type(image),
            repr(image)
        )

    # ========================================================
    # ATTACH IMAGE AGENT IMAGES
    # ========================================================

    print(
        "\nATTACHING IMAGES TO NEWSLETTER JSON"
    )

    news = attach_images(
        news,
        "news",
        image_results
    )

    startups = attach_images(
        startups,
        "startup",
        image_results
    )

    tweets = attach_images(
        tweets,
        "people",
        image_results
    )

    github_repos = attach_images(
        github_repos,
        "github",
        image_results
    )

    research_papers = attach_images(
        research_papers,
        "research",
        image_results
    )

    # Tool of the Day is also allowed to receive
    # an image from the Image Agent.
    if tool_of_the_day:

        tool_list = [
            tool_of_the_day
        ]

        tool_list = attach_images(
            tool_list,
            "tool",
            image_results
        )

        tool_of_the_day = tool_list[0]

    # ========================================================
    # IMAGE COUNTS
    # ========================================================

    print(
        f"News images:       "
        f"{sum(bool(item.get('image_url')) for item in news)} "
        f"/ {len(news)}"
    )

    print(
        f"Startup images:    "
        f"{sum(bool(item.get('image_url')) for item in startups)} "
        f"/ {len(startups)}"
    )

    print(
        f"People images:     "
        f"{sum(bool(item.get('image_url')) for item in tweets)} "
        f"/ {len(tweets)}"
    )

    print(
        f"GitHub images:     "
        f"{sum(bool(item.get('image_url')) for item in github_repos)} "
        f"/ {len(github_repos)}"
    )

    print(
        f"Research images:   "
        f"{sum(bool(item.get('image_url')) for item in research_papers)} "
        f"/ {len(research_papers)}"
    )

    if tool_of_the_day:

        print(
            "Tool image:        ",
            bool(
                tool_of_the_day.get(
                    "image_url"
                )
            )
        )

    # ========================================================
    # NEWSLETTER JSON
    # ========================================================

    newsletter_data = {

        "date": state.get(
            "date"
        ),

        "time_window": state.get(
            "time_window"
        ),

        "news": news,

        "startups": startups,

        # Frontend calls this "people"
        # while the existing backend stores them as tweets.
        "people": tweets,

        # Keep original tweets field too.
        "tweets": tweets,

        "github_repos": github_repos,

        "research_papers": research_papers,

        "discovered_entities": discovered_entities,

        # Actual Tool of the Day
        "tool_of_the_day": tool_of_the_day
    }

    # ========================================================
    # SAVE JSON
    # ========================================================

    json_file = (
        output_dir
        / "newsletter.json"
    )

    json_file.write_text(
        json.dumps(
            newsletter_data,
            ensure_ascii=False,
            indent=2
        ),
        encoding="utf-8"
    )

    # ========================================================
    # OPEN NEWSLETTER IN BROWSER
    # ========================================================

    webbrowser.open(
        html_file.resolve().as_uri()
    )

    # ========================================================
    # LOGGING
    # ========================================================

    print(
        "\nNEWSLETTER GENERATED"
    )

    print("=" * 80)

    print(
        f"News:              {len(news)}"
    )

    print(
        f"Startups:          {len(startups)}"
    )

    print(
        f"People/Tweets:     {len(tweets)}"
    )

    print(
        f"GitHub:            {len(github_repos)}"
    )

    print(
        f"Research Papers:   {len(research_papers)}"
    )

    print(
        f"Tool of the Day:   "
        f"{'Available' if tool_of_the_day else 'Not available'}"
    )

    print("-" * 80)

    print(
        f"Markdown: "
        f"{markdown_file.resolve()}"
    )

    print(
        f"HTML:     "
        f"{html_file.resolve()}"
    )

    print(
        f"JSON:     "
        f"{json_file.resolve()}"
    )

    print("=" * 80)

    # ========================================================
    # RETURN STATE
    # ========================================================

    return {

        "newsletter_html": html,

        "progress": [

            "exporter: generated newsletter HTML",

            f"exporter: saved {html_file}",

            f"exporter: saved {json_file}"

        ]

    }