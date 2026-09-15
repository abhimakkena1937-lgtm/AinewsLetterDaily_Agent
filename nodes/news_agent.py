import asyncio

from utils.gemini_limiter import gemini_semaphore

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from config import GEMINI_MODEL

from prompts import (
    NEWS_EXTRACTION_SYSTEM_PROMPT,
    NEWS_EXTRACTION_USER_PROMPT,
)

from schemas import AllResearchItems, ToolOfTheDay
from state import NewsLetterState

from tools.web_search import format_research, tavily_search


# =========================================================
# SEARCH QUERIES
# =========================================================

NEWS_QUERIES = [
    "latest AI news",
    "latest AI model releases",
    "latest AI product launches",
    "latest AI agents agentic AI",
    "latest OpenAI Anthropic Google Meta AI news",
    "latest AI industry developments",
    "latest generative AI developments",
    "latest AI developer tools",
    "latest open source AI news",
    "latest AI infrastructure hardware",
    "latest AI policy safety",
]


STARTUP_QUERIES = [
    "latest AI startup funding",
    "latest AI startup acquisitions",
    "latest AI startup launches",
    "latest AI venture funding",
]


PEOPLE_QUERIES = [
    "latest AI researcher posts",
    "latest AI founder posts",
    "latest AI executive posts",
    "important AI posts X Twitter",
]


GITHUB_QUERIES = [
    "new AI GitHub repositories",
    "new LLM GitHub repositories",
    "new agentic AI GitHub projects",
    "new generative AI open source repositories",
]


PAPER_QUERIES = [
    "new AI research papers",
    "new LLM research papers",
    "new agentic AI research papers",
    "new generative AI research papers",
]


# =========================================================
# EXA CONCURRENCY CONTROL
# =========================================================

exa_semaphore = asyncio.Semaphore(3)


# =========================================================
# EXA SEARCH WITH RETRY
# =========================================================

async def research_query(
    query: str,
    time_window: str,
    max_retries: int = 4,
) -> list[dict]:

    for attempt in range(max_retries):

        try:

            async with exa_semaphore:

                print(
                    f"\nEXA SEARCH | "
                    f"attempt {attempt + 1}/{max_retries} | "
                    f"{query}"
                )

                results = await tavily_search(
                    query,
                    max_results=5,
                    time_window=time_window,
                )

                print(
                    f"EXA SUCCESS | "
                    f"{query} | "
                    f"{len(results)} results"
                )

                return results

        except Exception as e:

            error_text = str(e)

            print(
                f"\nEXA SEARCH FAILED | "
                f"attempt {attempt + 1}/{max_retries}"
            )

            print("QUERY:", query)
            print("ERROR:", error_text)

            # -------------------------------------------------
            # Last attempt
            # -------------------------------------------------

            if attempt == max_retries - 1:

                print(
                    f"\nEXA GIVING UP AFTER "
                    f"{max_retries} ATTEMPTS:"
                )

                print(query)

                return []

            # -------------------------------------------------
            # Exponential backoff
            # -------------------------------------------------

            delay = 2 ** (attempt + 1)

            print(
                f"Retrying in {delay} seconds..."
            )

            await asyncio.sleep(delay)

    return []


# =========================================================
# SEARCH CATEGORY
# =========================================================

async def search_category(
    category: str,
    queries: list[str],
    time_window: str,
) -> list[dict]:

    print("\n" + "=" * 80)
    print(f"SEARCHING {category.upper()}")
    print("=" * 80)

    results = await asyncio.gather(
        *(
            research_query(
                query,
                time_window,
            )
            for query in queries
        )
    )

    combined = []

    for query, result in zip(
        queries,
        results,
    ):

        print(
            f"{category} | "
            f"{query} | "
            f"{len(result)} results"
        )

        for item in result:

            print(
                "TITLE:",
                item.get("title"),
            )

            print(
                "PUBLISHED:",
                item.get("published_at"),
            )

            print(
                "URL:",
                item.get("url"),
            )

        combined.extend(result)

    print(
        f"\n{category} raw results:",
        len(combined),
    )

    return combined


# =========================================================
# NORMALIZE TEXT
# =========================================================

def normalize_text(
    value: str,
) -> str:

    return " ".join(
        value.lower()
        .strip()
        .split()
    )


# =========================================================
# DEDUPLICATION
# =========================================================

def deduplicate_results(
    results: list[dict],
) -> list[dict]:

    seen_urls = set()
    seen_titles = set()

    unique_results = []

    for item in results:

        url = normalize_text(
            str(
                item.get(
                    "url",
                    "",
                )
            )
        )

        title = normalize_text(
            str(
                item.get(
                    "title",
                    "",
                )
            )
        )

        if not url and not title:
            continue

        # -----------------------------------------------------
        # Duplicate URL
        # -----------------------------------------------------

        if url and url in seen_urls:
            continue

        # -----------------------------------------------------
        # Duplicate title
        # -----------------------------------------------------

        if title and title in seen_titles:
            continue

        if url:
            seen_urls.add(url)

        if title:
            seen_titles.add(title)

        unique_results.append(item)

    return unique_results


# =========================================================
# COLLECT CATEGORY
# =========================================================

async def collect_category(
    category: str,
    queries: list[str],
    time_window: str,
) -> list[dict]:

    raw_results = await search_category(
        category,
        queries,
        time_window,
    )

    unique_results = deduplicate_results(
        raw_results
    )

    print(
        f"{category} unique results:",
        len(unique_results),
    )

    return unique_results


# =========================================================
# COLLECT ALL RESEARCH
# =========================================================

async def collect_all_research(
    time_window: str,
) -> dict:

    (
        news_results,
        startup_results,
        people_results,
        github_results,
        paper_results,
    ) = await asyncio.gather(

        collect_category(
            "news",
            NEWS_QUERIES,
            time_window,
        ),

        collect_category(
            "startups",
            STARTUP_QUERIES,
            time_window,
        ),

        collect_category(
            "people",
            PEOPLE_QUERIES,
            time_window,
        ),

        collect_category(
            "github",
            GITHUB_QUERIES,
            time_window,
        ),

        collect_category(
            "papers",
            PAPER_QUERIES,
            time_window,
        ),
    )

    return {
        "news": news_results,
        "startups": startup_results,
        "people": people_results,
        "github": github_results,
        "papers": paper_results,
    }


# =========================================================
# GEMINI
# =========================================================

def get_news_llm():

    return ChatGoogleGenerativeAI(
        model=GEMINI_MODEL,
        temperature=0,
    ).with_structured_output(
        AllResearchItems
    )


# =========================================================
# TOOL OF THE DAY GEMINI
# =========================================================

def get_tool_llm():

    return ChatGoogleGenerativeAI(
        model=GEMINI_MODEL,
        temperature=0.2,
    ).with_structured_output(
        ToolOfTheDay
    )


# =========================================================
# FORMAT CATEGORY
# =========================================================

def format_category(
    category: str,
    results: list[dict],
) -> str:

    if not results:

        return (
            f"\n\n===== {category.upper()} =====\n"
            "No results found."
        )

    return (
        f"\n\n===== {category.upper()} =====\n"
        + format_research(results)
    )


# =========================================================
# TOOL OF THE DAY
# =========================================================

async def generate_tool_of_the_day(
    research: dict,
    time_window: str,
) -> ToolOfTheDay | None:

    print("\n" + "#" * 80)
    print("GENERATING TOOL OF THE DAY")
    print("#" * 80)

    # -----------------------------------------------------
    # Use current research as the source
    # -----------------------------------------------------

    tool_research = ""

    tool_research += format_category(
        "AI NEWS",
        research.get("news", []),
    )

    tool_research += format_category(
        "AI STARTUPS",
        research.get("startups", []),
    )

    tool_research += format_category(
        "AI GITHUB",
        research.get("github", []),
    )

    # -----------------------------------------------------
    # Tool selection prompt
    # -----------------------------------------------------

    system_prompt = """
You are the Tool of the Day selector for an AI newsletter.

Select ONE genuinely useful AI tool, platform, library,
developer product, or AI application.

Rules:

1. Select only a real tool.
2. Prefer tools that are relevant to current AI developments.
3. Prefer tools that developers, researchers, founders,
   or AI users can actually explore.
4. Do not invent a tool.
5. Do not invent URLs.
6. Use information from the supplied research.
7. The tool should be different from ordinary news reporting.
8. Return exactly one ToolOfTheDay object.
9. Keep the description concise and useful.
10. If a reliable URL is available in the research, use it.
11. If no reliable URL is available, return null for the URL.
12. Do not use a random or unrelated website.
"""

    user_prompt = f"""
Select the best Tool of the Day from the research below.

TIME WINDOW:
{time_window}

RESEARCH:
{tool_research}

Return one useful AI tool.
"""

    try:

        llm = get_tool_llm()

        async with gemini_semaphore:

            response = await llm.ainvoke(
                [
                    SystemMessage(
                        content=system_prompt
                    ),

                    HumanMessage(
                        content=user_prompt
                    ),
                ]
            )

        print(
            "\nTOOL OF THE DAY SELECTED:"
        )

        print(
            "NAME:",
            response.name
        )

        print(
            "DESCRIPTION:",
            response.description
        )

        print(
            "URL:",
            response.url
        )

        return response

    except Exception as e:

        print(
            "\nTOOL OF THE DAY GENERATION FAILED"
        )

        print(
            "ERROR:",
            str(e)
        )

        return None


# =========================================================
# EXTRACT ALL RESEARCH
# =========================================================

async def extract_all_research(
    time_window: str,
) -> dict:

    research = await collect_all_research(
        time_window
    )

    # =====================================================
    # RESEARCH COUNTS
    # =====================================================

    print("\n" + "#" * 80)
    print("FINAL RESEARCH COUNTS")
    print("#" * 80)

    print(
        "NEWS:",
        len(research["news"]),
    )

    print(
        "STARTUPS:",
        len(research["startups"]),
    )

    print(
        "PEOPLE:",
        len(research["people"]),
    )

    print(
        "GITHUB:",
        len(research["github"]),
    )

    print(
        "PAPERS:",
        len(research["papers"]),
    )

    # =====================================================
    # FORMAT ALL RESEARCH
    # =====================================================

    research_text = ""

    research_text += format_category(
        "AI NEWS",
        research["news"],
    )

    research_text += format_category(
        "AI STARTUPS",
        research["startups"],
    )

    research_text += format_category(
        "AI PEOPLE / POSTS",
        research["people"],
    )

    research_text += format_category(
        "AI GITHUB",
        research["github"],
    )

    research_text += format_category(
        "AI RESEARCH PAPERS",
        research["papers"],
    )

    # =====================================================
    # GEMINI INPUT SIZE
    # =====================================================

    print("\n" + "#" * 80)
    print("RESEARCH SENT TO GEMINI")
    print("#" * 80)

    print(
        "Formatted research characters:",
        len(research_text),
    )

    # =====================================================
    # GEMINI EXTRACTION
    # =====================================================

    llm = get_news_llm()

    async with gemini_semaphore:

        response = await llm.ainvoke(
            [
                SystemMessage(
                    content=NEWS_EXTRACTION_SYSTEM_PROMPT
                ),

                HumanMessage(
                    content=NEWS_EXTRACTION_USER_PROMPT.format(
                        research_results=research_text,
                        time_window=time_window,
                    )
                ),
            ]
        )

    # =====================================================
    # GEMINI RESULTS
    # =====================================================

    print("\n" + "#" * 80)
    print("GEMINI EXTRACTION RESULTS")
    print("#" * 80)

    print(
        "NEWS:",
        len(response.news),
    )

    print(
        "STARTUPS:",
        len(response.startups),
    )

    print(
        "PEOPLE:",
        len(response.tweets),
    )

    print(
        "GITHUB:",
        len(response.repositories),
    )

    print(
        "PAPERS:",
        len(response.papers),
    )

    # =====================================================
    # RETURN
    # =====================================================

    return {
        "news": response.news,
        "startups": response.startups,
        "tweets": response.tweets,
        "github_repos": response.repositories,
        "research_papers": response.papers,
    }


# =========================================================
# COMBINED NEWS AGENT
# =========================================================

async def news_agent_node(
    state: NewsLetterState,
) -> dict:

    print("\n" + "=" * 80)
    print("RUNNING COMBINED NEWS AGENT")
    print("=" * 80)

    time_window = state.get(
        "time_window",
        "",
    )

    # =====================================================
    # COLLECT + EXTRACT RESEARCH
    # =====================================================

    research = await collect_all_research(
        time_window=time_window
    )

    # =====================================================
    # EXTRACT STRUCTURED NEWSLETTER ITEMS
    # =====================================================

    # Format all research
    research_text = ""

    research_text += format_category(
        "AI NEWS",
        research["news"],
    )

    research_text += format_category(
        "AI STARTUPS",
        research["startups"],
    )

    research_text += format_category(
        "AI PEOPLE / POSTS",
        research["people"],
    )

    research_text += format_category(
        "AI GITHUB",
        research["github"],
    )

    research_text += format_category(
        "AI RESEARCH PAPERS",
        research["papers"],
    )

    print("\n" + "#" * 80)
    print("RESEARCH SENT TO GEMINI")
    print("#" * 80)

    print(
        "Formatted research characters:",
        len(research_text),
    )

    llm = get_news_llm()

    async with gemini_semaphore:

        response = await llm.ainvoke(
            [
                SystemMessage(
                    content=NEWS_EXTRACTION_SYSTEM_PROMPT
                ),

                HumanMessage(
                    content=NEWS_EXTRACTION_USER_PROMPT.format(
                        research_results=research_text,
                        time_window=time_window,
                    )
                ),
            ]
        )

    # =====================================================
    # GENERATE TOOL OF THE DAY
    # =====================================================

    tool_of_the_day = await generate_tool_of_the_day(
        research=research,
        time_window=time_window,
    )

    # =====================================================
    # RESULTS
    # =====================================================

    print("\n" + "#" * 80)
    print("GEMINI EXTRACTION RESULTS")
    print("#" * 80)

    print(
        "NEWS:",
        len(response.news),
    )

    print(
        "STARTUPS:",
        len(response.startups),
    )

    print(
        "PEOPLE:",
        len(response.tweets),
    )

    print(
        "GITHUB:",
        len(response.repositories),
    )

    print(
        "PAPERS:",
        len(response.papers),
    )

    print(
        "TOOL OF THE DAY:",
        (
            tool_of_the_day.name
            if tool_of_the_day
            else "None"
        ),
    )

    # =====================================================
    # RETURN STATE UPDATE
    # =====================================================

    return {

        "news": response.news,

        "startups": response.startups,

        "tweets": response.tweets,

        "github_repos": response.repositories,

        "research_papers": response.papers,

        "tool_of_the_day": tool_of_the_day,

        "progress": [
            "news_agent: collected and extracted news, startups, people, GitHub, papers, and Tool of the Day"
        ],
    }