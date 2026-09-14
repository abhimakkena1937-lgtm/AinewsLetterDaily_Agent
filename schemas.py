from  __future__ import annotations
from pydantic import BaseModel,Field,HttpUrl, field_validator
from typing import List

class NewsItem(BaseModel):
    title:str
    company:str |None=None
    summary:str
    published_at:str|None=None
    source:str
    url:HttpUrl
    category:str
    importance_score:float=0.0
    image_url: str | None = None

class NewsItems(BaseModel):
    news:list[NewsItem]=Field(default_factory=list)

class DiscoveredEntity(BaseModel):
    name:str
    entity_type:str
    reason:str
    

class DiscoveredEntities(BaseModel):
    entities: list[DiscoveredEntity] = Field(default_factory=list)

class StartUpItem(BaseModel):
    startup_name:str
    description:str
    funding:str | None=None
    investors:List[str]=Field(default_factory=list)
    source:str |None=None
    url:HttpUrl |None=None
    evidence_id:int |None=None
    image_url: str | None = None

class FreshnessCheck(BaseModel):
    is_recent:bool
    event_date:str |None=None
    reason:str

class StartUpItems(BaseModel):
    startups:List[StartUpItem]=Field(default_factory=list)

class ResearchEvidence(BaseModel):
    title: str
    content: str
    url: str
    published_at: str | None = None
    source: str | None = None

class TweetItem(BaseModel):
    person:str
    tweet:str
    summary:str
    url:HttpUrl
    engagement:str|None=None
    image_url: str | None = None
    @field_validator("tweet")
    @classmethod
    def validate_tweet(cls, value):
        value = value.strip()

        if len(value) < 15:
            raise ValueError("Tweet text is too short")

        if value.isdigit():
            raise ValueError("Tweet cannot be only a number")

        return value
class TweetItems(BaseModel):
    tweets: list[TweetItem] = Field(
        default_factory=list
    )
class GitHubItem(BaseModel):
    repo_name: str
    description: str
    url: HttpUrl
    reason: str
    stars: int | None = None
    language: str | None = None
    image_url: str | None = None

class GitHubItems(BaseModel):
    repositories: list[GitHubItem] = Field(default_factory=list)

class PaperItem(BaseModel):
    title: str
    authors: list[str] = Field(default_factory=list)
    summary: str
    reason: str
    url: HttpUrl
    image_url: str | None = None

class PaperItems(BaseModel):
    papers: list[PaperItem] = Field(
        default_factory=list
    )
class ToolOfTheDay(BaseModel):
    name: str
    description: str
    url: HttpUrl | None = None
    image_url: str | None = None
class RankedContext(BaseModel):
    top_news:List[NewsItem]=Field(default_factory=list)
    top_start_ups:List[StartUpItem]=Field(default_factory=list)
    top_tweets:List[TweetItem]=Field(default_factory=list)
    top_github_repos:List[GitHubItem]=Field(default_factory=list)
    top_papers:List[PaperItem]=Field(default_factory=list)
    tool_of_the_day: ToolOfTheDay | None = None


class AllResearchItems(BaseModel):
    news: list[NewsItem] = Field(
        default_factory=list
    )

    startups: list[StartUpItem] = Field(
        default_factory=list
    )

    tweets: list[TweetItem] = Field(
        default_factory=list
    )

    repositories: list[GitHubItem] = Field(
        default_factory=list
    )

    papers: list[PaperItem] = Field(
        default_factory=list
    )

class ImageAssignment(BaseModel):
    category: str
    item_title: str
    image_url: str | None = None


class ImageAssignments(BaseModel):
    assignments: list[ImageAssignment] = Field(
        default_factory=list
    )





