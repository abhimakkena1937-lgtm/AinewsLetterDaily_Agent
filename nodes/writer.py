from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from config import GEMINI_MODEL

from prompts import (
    WRITER_SYSTEM_PROMPT,
    WRITER_USER_PROMPT,
)

from state import NewsLetterState

from utils.gemini_limiter import gemini_semaphore


# =========================================================
# Gemini model
# =========================================================

def get_writer_llm():

    return ChatGoogleGenerativeAI(
        model=GEMINI_MODEL,
        temperature=0.3,
    )


# =========================================================
# Writer Agent
# =========================================================

async def writer_node(
    state: NewsLetterState,
) -> dict:

    # -----------------------------------------------------
    # Get research data from state
    # -----------------------------------------------------

    news = state.get(
        "news",
        []
    )

    startups = state.get(
        "startups",
        []
    )

    tweets = state.get(
        "tweets",
        []
    )

    github_repos = state.get(
        "github_repos",
        []
    )

    papers = state.get(
        "research_papers",
        []
    )

    image_results = state.get(
        "image_results",
        []
    )

    # -----------------------------------------------------
    # Start
    # -----------------------------------------------------

    print("\n" + "=" * 80)
    print("RUNNING WRITER AGENT")
    print("=" * 80)

    # -----------------------------------------------------
    # Content sent to Writer
    # -----------------------------------------------------

    print("\n" + "=" * 80)
    print("CONTENT SENT TO WRITER")
    print("=" * 80)

    print(
        "NEWS:",
        len(news)
    )

    print(
        "STARTUPS:",
        len(startups)
    )

    print(
        "PEOPLE:",
        len(tweets)
    )

    print(
        "GITHUB:",
        len(github_repos)
    )

    print(
        "PAPERS:",
        len(papers)
    )

    print(
        "IMAGE RESULTS:",
        len(image_results)
    )

    # -----------------------------------------------------
    # Build complete newsletter data
    # -----------------------------------------------------

    newsletter_data = {
        "news": news,
        "startups": startups,
        "tweets": tweets,
        "github_repos": github_repos,
        "papers": papers,
    }

    # -----------------------------------------------------
    # Gemini
    # -----------------------------------------------------

    llm = get_writer_llm()

    async with gemini_semaphore:

        response = await llm.ainvoke(
            [
                SystemMessage(
                    content=WRITER_SYSTEM_PROMPT
                ),

                HumanMessage(
                    content=WRITER_USER_PROMPT.format(
                        research_data=newsletter_data,
                        image_results=image_results,
                    )
                ),
            ]
        )

    # -----------------------------------------------------
    # Extract Gemini response
    # -----------------------------------------------------

    newsletter = response.content

    # -----------------------------------------------------
    # Handle Gemini response
    # -----------------------------------------------------

    if isinstance(
        newsletter,
        list
    ):

        newsletter = "".join(
            block.get("text", "")
            for block in newsletter
            if isinstance(
                block,
                dict
            )
        )

    # Make sure the result is a string
    if not isinstance(
        newsletter,
        str
    ):

        newsletter = str(
            newsletter
        )

    # -----------------------------------------------------
    # Output
    # -----------------------------------------------------

    print("\n" + "=" * 80)
    print("NEWSLETTER GENERATED")
    print("=" * 80)

    print(newsletter)

    # -----------------------------------------------------
    # Return state update
    # -----------------------------------------------------

    return {
        "newsletter_markdown": newsletter,

        "progress": [
            "writer: generated newsletter"
        ],
    }