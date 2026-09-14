from __future__ import annotations

import asyncio
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from utils.gemini_limiter import gemini_semaphore
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from config import GEMINI_MODEL

from prompts import (
    IMAGE_SYSTEM_PROMPT,
    IMAGE_USER_PROMPT,
)

from state import NewsLetterState

from schemas import (
    ImageAssignments,
)

from tools.web_search import tavily_search


# =========================================================
# Gemini
# =========================================================

def get_image_llm():

    return ChatGoogleGenerativeAI(
        model=GEMINI_MODEL,
        temperature=0,
    )


# =========================================================
# Extract image from original webpage
# =========================================================

def extract_image_url(
    page_url: str,
) -> str | None:

    if not page_url:
        return None

    try:

        response = requests.get(
            page_url,
            timeout=10,
            headers={
                "User-Agent": "Mozilla/5.0"
            },
        )

        if response.status_code != 200:
            return None

        soup = BeautifulSoup(
            response.text,
            "html.parser",
        )

        # -------------------------------------------------
        # Open Graph image
        # -------------------------------------------------

        og_image = soup.find(
            "meta",
            property="og:image",
        )

        if (
            og_image
            and og_image.get("content")
        ):

            image_url = urljoin(
                page_url,
                og_image["content"],
            )

            if image_url.startswith("http"):
                return image_url

        # -------------------------------------------------
        # Twitter image
        # -------------------------------------------------

        twitter_image = soup.find(
            "meta",
            attrs={
                "name": "twitter:image"
            },
        )

        if (
            twitter_image
            and twitter_image.get("content")
        ):

            image_url = urljoin(
                page_url,
                twitter_image["content"],
            )

            if image_url.startswith("http"):
                return image_url

        # -------------------------------------------------
        # First usable image
        # -------------------------------------------------

        for img in soup.find_all("img"):

            src = img.get("src")

            if not src:
                continue

            image_url = urljoin(
                page_url,
                src,
            )

            if image_url.startswith("http"):

                return image_url

    except Exception as e:

        print(
            f"Image extraction failed: "
            f"{page_url} -> {e}"
        )

    return None


# =========================================================
# Exa fallback image search
# =========================================================

async def search_images(
    query: str,
    time_window: str,
) -> list[dict]:

    max_retries = 3

    for attempt in range(
        1,
        max_retries + 1,
    ):

        try:

            results = await tavily_search(
                query,
                max_results=5,
                time_window=time_window,
            )

            image_results = []

            for result in results:

                page_url = result.get(
                    "url",
                    "",
                )

                if not page_url:
                    continue

                image_url = extract_image_url(
                    page_url,
                )

                if image_url:

                    image_results.append(
                        {
                            "title": result.get(
                                "title",
                                "",
                            ),
                            "page_url": page_url,
                            "image_url": image_url,
                            "source": result.get(
                                "source",
                                "",
                            ),
                        }
                    )

            return image_results

        except Exception as e:

            print(
                f"Image search attempt "
                f"{attempt}/{max_retries} failed: "
                f"{e}"
            )

            if attempt < max_retries:

                await asyncio.sleep(
                    2 * attempt,
                )

            else:

                print(
                    f"Skipping image search for: "
                    f"{query}"
                )

    return []


# =========================================================
# Image Agent
# =========================================================

async def image_agent_node(
    state: NewsLetterState,
) -> dict:

    print("\n" + "=" * 80)
    print("RUNNING IMAGE AGENT")
    print("=" * 80)

    news = state.get(
        "news",
        [],
    )

    startups = state.get(
        "startups",
        [],
    )

    tweets = state.get(
        "tweets",
        [],
    )

    github_repos = state.get(
        "github_repos",
        [],
    )

    papers = state.get(
        "research_papers",
        [],
    )

    time_window = state.get(
        "time_window",
        "",
    )

    print(
        "NEWS:",
        len(news),
    )

    print(
        "STARTUPS:",
        len(startups),
    )

    print(
        "PEOPLE:",
        len(tweets),
    )

    print(
        "GITHUB:",
        len(github_repos),
    )

    print(
        "PAPERS:",
        len(papers),
    )

    # =====================================================
    # Build item list
    # =====================================================

    items = []

    for item in news:

        items.append(
            {
                "category": "news",
                "title": item.title,
                "url": str(item.url),
                "image_url": item.image_url,
            }
        )

    for item in startups:

        items.append(
            {
                "category": "startup",
                "title": item.startup_name,
                "url": (
                    str(item.url)
                    if item.url
                    else ""
                ),
                "image_url": item.image_url,
            }
        )

    for item in tweets:

        items.append(
            {
                "category": "person",
                "title": item.person,
                "url": str(item.url),
                "image_url": item.image_url,
            }
        )

    for item in github_repos:

        items.append(
            {
                "category": "github",
                "title": item.repo_name,
                "url": str(item.url),
                "image_url": item.image_url,
            }
        )

    for item in papers:

        items.append(
            {
                "category": "paper",
                "title": item.title,
                "url": str(item.url),
                "image_url": item.image_url,
            }
        )

    # =====================================================
    # Image candidates
    # =====================================================

    image_results = []

    fallback_searches = 0
    direct_images = 0

    # =====================================================
    # First:
    # use image_url already supplied by News Agent
    # =====================================================

    for item in items:

        if item["image_url"]:

            image_results.append(
                {
                    "category": item["category"],
                    "item_title": item["title"],
                    "page_url": item["url"],
                    "image_url": item["image_url"],
                    "source": "news_agent",
                }
            )

            direct_images += 1

    # =====================================================
    # Second:
    # try original source webpage
    # =====================================================

    for item in items:

        if item["image_url"]:
            continue

        page_url = item["url"]

        if not page_url:
            continue

        image_url = await asyncio.to_thread(
            extract_image_url,
            page_url,
        )

        if image_url:

            image_results.append(
                {
                    "category": item["category"],
                    "item_title": item["title"],
                    "page_url": page_url,
                    "image_url": image_url,
                    "source": "original_page",
                }
            )

            direct_images += 1

    # =====================================================
    # Third:
    # Exa fallback
    #
    # ONLY search when the original source has no image.
    # =====================================================

    matched_titles = {
        result["item_title"]
        for result in image_results
    }

    for item in items:

        if item["title"] in matched_titles:
            continue

        if item["category"] == "news":

            query = (
                f"{item['title']} AI"
            )

        elif item["category"] == "startup":

            query = (
                f"{item['title']} AI startup"
            )

        elif item["category"] == "person":

            query = (
                f"{item['title']} AI"
            )

        elif item["category"] == "github":

            query = (
                f"{item['title']} GitHub AI"
            )

        else:

            query = (
                f"{item['title']} "
                f"AI research paper"
            )

        print(
            "\nIMAGE FALLBACK SEARCH:",
            query,
        )

        results = await search_images(
            query,
            time_window,
        )

        fallback_searches += 1

        for result in results:

            image_results.append(
                {
                    "category": item["category"],
                    "item_title": item["title"],
                    **result,
                }
            )

    # =====================================================
    # Deduplicate image URLs
    # =====================================================

    unique_images = []

    seen_images = set()

    for result in image_results:

        image_url = result.get(
            "image_url",
            "",
        )

        if not image_url:
            continue

        if image_url in seen_images:
            continue

        seen_images.add(
            image_url
        )

        unique_images.append(
            result
        )

    image_results = unique_images

    # =====================================================
    # Debug
    # =====================================================

    print("\n" + "=" * 80)
    print("IMAGE COLLECTION COMPLETE")
    print("=" * 80)

    print(
        "DIRECT IMAGES:",
        direct_images,
    )

    print(
        "EXA FALLBACK SEARCHES:",
        fallback_searches,
    )

    print(
        "UNIQUE IMAGE CANDIDATES:",
        len(image_results),
    )

    # =====================================================
    # Gemini image selection
    # =====================================================

    llm = get_image_llm().with_structured_output(
        ImageAssignments
    )

    research_data = {
        "news": news,
        "startups": startups,
        "tweets": tweets,
        "github_repos": github_repos,
        "papers": papers,
    }

    async with gemini_semaphore:

        response = await llm.ainvoke(
            [
                SystemMessage(
                    content=IMAGE_SYSTEM_PROMPT
                ),

                HumanMessage(
                    content=IMAGE_USER_PROMPT.format(
                        research_data=research_data,
                        image_results=image_results,
                    )
                ),
            ]
        )

    print("\n" + "=" * 80)
    print("IMAGE AGENT COMPLETE")
    print("=" * 80)

    print(
        "IMAGE ASSIGNMENTS:",
        len(response.assignments),
    )

    return {
        "image_results": response.assignments,
        "progress": [
            "image_agent: selected newsletter images"
        ],
    }