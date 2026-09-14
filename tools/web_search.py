from __future__ import annotations

from typing import Any

from exa_py import Exa

from config import EXA_API_KEY

from urllib.parse import urlparse


# =========================================================
# EXA CLIENT
# =========================================================

if not EXA_API_KEY:
    raise RuntimeError(
        "EXA_API_KEY is not found. Add it to .env"
    )


client = Exa(EXA_API_KEY)


# =========================================================
# EXA RESULT NORMALIZATION
# =========================================================

def normalize_exa_results(
    response: Any,
) -> list[dict[str, Any]]:

    results = []

    for result in response.results:

        url = result.url or ""

        results.append(
            {
                "title": result.title or "",

                "url": url,

                "content": (
                    getattr(
                        result,
                        "text",
                        "",
                    )
                    or ""
                ),

                "published_at": (
                    getattr(
                        result,
                        "published_date",
                        "",
                    )
                    or ""
                ),

                "source": (
                    urlparse(url).netloc
                    if url
                    else ""
                ),
            }
        )

    return results


# =========================================================
# EXA SEARCH
# =========================================================

async def tavily_search(
    query: str,
    *,
    max_results: int = 5,
    time_window: str,
) -> list[dict[str, Any]]:

    start_date, end_date = time_window.split(
        " to "
    )

    response = client.search_and_contents(
        query,

        num_results=max_results,

        start_published_date=start_date,

        end_published_date=end_date,

        text=True,
    )

    return normalize_exa_results(
        response
    )


# =========================================================
# CONTENT COMPRESSION
# =========================================================

def compress_content(
    content: str,
    max_characters: int = 1500,
) -> str:

    if not content:
        return ""

    content = content.strip()

    # -----------------------------------------------------
    # Already small enough
    # -----------------------------------------------------

    if len(content) <= max_characters:
        return content

    # -----------------------------------------------------
    # Keep beginning + ending
    # -----------------------------------------------------

    first_part = int(
        max_characters * 0.75
    )

    last_part = (
        max_characters
        - first_part
    )

    return (
        content[:first_part]

        + "\n\n[...content shortened...]\n\n"

        + content[-last_part:]
    )


# =========================================================
# FORMAT RESEARCH
# =========================================================

def format_research(
    results: list[dict[str, Any]],
) -> str:

    chunks = []

    for index, result in enumerate(
        results,
        start=1,
    ):

        content = compress_content(
            result.get(
                "content",
                "",
            ),
            max_characters=1500,
        )

        chunks.append(
            f"""
Evidence_ID: {index}
Title: {result.get("title", "")}
URL: {result.get("url", "")}
Published: {result.get("published_at", "")}
Source: {result.get("source", "")}
Content: {content}
"""
        )

    return "\n\n".join(
        chunks
    )