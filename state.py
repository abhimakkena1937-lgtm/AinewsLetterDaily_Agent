from typing import TypedDict, List, Annotated

import operator

from schemas import (
    NewsItem,
    StartUpItem,
    PaperItem,
    TweetItem,
    GitHubItem,
    DiscoveredEntity,
    ToolOfTheDay,
)


class NewsLetterState(
    TypedDict,
    total=False
):

    # =====================================================
    # Planner
    # =====================================================

    date: str

    time_window: str


    # =====================================================
    # Research
    # =====================================================

    discovered_entities: Annotated[
        List[DiscoveredEntity],
        operator.add
    ]

    news: Annotated[
        List[NewsItem],
        operator.add
    ]

    startups: Annotated[
        List[StartUpItem],
        operator.add
    ]

    tweets: Annotated[
        List[TweetItem],
        operator.add
    ]

    github_repos: Annotated[
        List[GitHubItem],
        operator.add
    ]

    research_papers: Annotated[
        List[PaperItem],
        operator.add
    ]


    # =====================================================
    # Tool of the Day
    # =====================================================

    tool_of_the_day: ToolOfTheDay | None


    # =====================================================
    # Image Agent
    # =====================================================

    image_results: list


    # =====================================================
    # Workflow
    # =====================================================

    progress: Annotated[
        List[str],
        operator.add
    ]

    errors: Annotated[
        List[str],
        operator.add
    ]


    # =====================================================
    # Final Newsletter
    # =====================================================

    newsletter_markdown: str

    newsletter_html: str