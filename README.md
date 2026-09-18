AI NewsLetter Daily Agent

An automated AI newsletter platform that researches the latest AI developments, generates a structured daily newsletter, publishes it to a web application, and delivers it to subscribers by email.

The project combines LangGraph, Google Gemini, Exa, FastAPI, PostgreSQL/Supabase, Google Apps Script, Google Sheets, Gmail, GitHub Actions, and a web frontend into one automated workflow.

🚀 Features

📰 Daily AI News

Latest AI and machine learning news

Research performed through Exa

Time-window based research

🚀 Startup & Funding Updates

AI startup discoveries

Funding and company-development information

👤 AI People

Important AI-related people and posts

💻 GitHub Repositories

Newly discovered AI repositories

Repository name, description, language, stars, and URL

GitHub image preview fallback when an Image Agent image is unavailable

📄 Research Papers

Newly discovered AI research

Paper title, summary, source, and URL

🛠️ Tool of the Day

Selects a useful AI tool, platform, library, or product from researched information

Uses structured Gemini output

🖼️ Image Agent

Finds and assigns images to newsletter items

Supports image matching by title and category

GitHub repositories have an additional image fallback

🧠 LangGraph Workflow

Planner

Combined News Agent

Image Agent

Writer

Exporter

Gmail Agent

📧 Automated Email Delivery

Sends the generated newsletter to subscribers

Subscriber management through Google Sheets + Apps Script

🌐 Web Application

AI NewsLetter website

Category pages

Newsletter view

Search

GitHub repository cards

Tool of the Day section

Subscribe functionality

💾 Persistent Newsletter Storage

PostgreSQL database hosted through Supabase

Render's ephemeral filesystem is not used for permanent newsletter storage

⏰ Daily Automation

GitHub Actions runs the newsletter workflow daily

The generated newsletter is published to the Render API

🏗️ Architecture

                         ┌─────────────────────┐
                         │   GitHub Actions    │
                         │   Daily Scheduler   │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │    LangGraph App    │
                         └──────────┬──────────┘
                                    │
                                    ▼
                              ┌───────────┐
                              │  Planner  │
                              └─────┬─────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │ Combined News Agent │
                         │                     │
                         │ Exa + Gemini        │
                         └──────────┬──────────┘
                                    │
                                    ▼
                            ┌──────────────┐
                            │ Image Agent  │
                            └──────┬───────┘
                                   │
                                   ▼
                              ┌─────────┐
                              │ Writer  │
                              └────┬────┘
                                   │
                                   ▼
                             ┌──────────┐
                             │ Exporter │
                             └────┬─────┘
                                  │
                    ┌─────────────┴─────────────┐
                    │                           │
                    ▼                           ▼
             newsletter.json              PostgreSQL
                    │                     / Supabase
                    │                           │
                    ▼                           │
          Render Publish API ◄──────────────────┘
                    │
                    ▼
             Website Frontend
                    │
                    ▼
             ┌───────────────┐
             │ Gmail Agent   │
             └───────┬───────┘
                     │
                     ▼
                Subscribers

🔄 LangGraph Workflow

The current graph is:

START
  │
  ▼
Planner
  │
  ▼
Combined News Agent
  │
  ▼
Image Agent
  │
  ▼
Writer
  │
  ▼
Exporter
  │
  ▼
Gmail Agent
  │
  ▼
END

There is no Reducer node in the current workflow.

🧩 Main Components

1. Planner

The Planner determines:

Current date

Research time window

Topics/queries required for the newsletter

The resulting time window is passed to the research agents.

2. Combined News Agent

The Combined News Agent performs research using Exa.

It collects information for:

AI news

Startups

AI people

GitHub repositories

Research papers

The agent:

Runs multiple research queries

Uses concurrent Exa requests

Uses a semaphore to control concurrent requests

Retries failed Exa requests

Deduplicates research results

Uses Gemini structured output to create structured newsletter data

Exa concurrency

The project uses:

exa_semaphore = asyncio.Semaphore(3)

This controls simultaneous Exa requests without limiting the number of final newsletter items.

🖼️ Image Agent

The Image Agent generates image assignments for newsletter content.

Images are matched against newsletter items using:

Exact title matching

Partial title matching

Word overlap

Category matching

The exporter supports image fields such as:

image_url
url
image
src

For GitHub repositories, the frontend additionally falls back to the GitHub Open Graph preview when no Image Agent image is available.

Example:

https://opengraph.githubassets.com/1/OWNER/REPOSITORY

Image priority for GitHub cards:

Image Agent image
        ↓
GitHub Open Graph preview
        ↓
GitHub placeholder

✍️ Writer

The Writer converts structured research information into the final newsletter.

Current newsletter sections:

AI Daily

📰 AI News
🚀 Startup & Funding
👤 AI People
💻 New GitHub Repositories
📄 New Research Papers
🛠️ Tool of the Day

The Writer is instructed to:

Use supplied research only

Preserve URLs

Preserve image URLs

Avoid inventing information

Generate the newsletter from structured data

📦 Exporter

The Exporter creates:

output/ai_daily.md
output/ai_daily.html
output/newsletter.json

The JSON structure contains:

{
  "date": "...",
  "time_window": "...",
  "news": [],
  "startups": [],
  "people": [],
  "tweets": [],
  "github_repos": [],
  "research_papers": [],
  "discovered_entities": [],
  "tool_of_the_day": {}
}

The exporter also attaches Image Agent results to the structured newsletter items.

📧 Gmail Agent

The Gmail Agent sends the generated newsletter to subscribed users.

The current workflow:

Google Sheets
      │
      ▼
Google Apps Script
      │
      ▼
Subscriber API
      │
      ▼
Gmail Agent
      │
      ▼
Subscribers

The project supports:

Subscribe

Unsubscribe

Subscriber status checking

👥 Subscriber Management

Subscriber information is managed using:

Google Sheets

Google Apps Script

The Python application communicates with the Apps Script endpoint.

Example operations:

subscribe
unsubscribe
check_subscriber

The Apps Script URL is stored as an environment variable.

💾 Database

The project uses PostgreSQL through Supabase for persistent newsletter storage.

Table:

create table newsletters (
    id bigint generated by default as identity primary key,
    data jsonb not null,
    created_at timestamptz default now()
);

create index newsletters_created_at_idx
on newsletters (created_at desc);

Newsletter data is stored in the data JSONB column.

The latest newsletter is loaded using:

SELECT data
FROM newsletters
ORDER BY created_at DESC, id DESC
LIMIT 1;

Why PostgreSQL?

The Render web service filesystem is ephemeral. Therefore, generated newsletter data should not depend on local files for permanent storage.

🌐 Backend API

The application uses FastAPI.

Important API endpoints include:

/api/publish-newsletter
/api/newsletter

The publish endpoint receives the generated newsletter from GitHub Actions.

Publishing is protected using:

X-Newsletter-Key

The secret is stored in environment variables rather than source code.

🖥️ Frontend

The frontend provides:

Home page

Categories

Newsletter

About

Search

Subscribe

Sign In UI

Topic cards

Article cards

GitHub repository cards

Research cards

Startup cards

AI People cards

Tool of the Day

Explore Topics

The topic cards include:

AI & ML
Startups
Tech & Products
GitHub
Tool of the Day
Research
AI People

The cards are displayed in a single horizontal row on desktop.

On smaller screens, horizontal scrolling is enabled.

💻 GitHub Repository Cards

Each GitHub repository can display:

Repository name

Description

Language

Stars

Repository URL

Image

Example card information:

GitHub

Repository Name

Repository description...

Language

★ Stars

View Repository →

If an Image Agent image is unavailable, the frontend derives a GitHub preview image from the repository URL.

🛠️ Tool of the Day

The Tool of the Day feature uses Gemini structured output.

It selects one useful real-world AI:

Tool

Platform

Library

Product

The selection is based on information already discovered by the research workflow.

The newsletter stores:

{
  "tool_of_the_day": {
    "name": "...",
    "description": "...",
    "url": "..."
  }
}

📁 Project Structure

A simplified project structure:

Ai_news_letter/
│
├── .github/
│   └── workflows/
│       └── newsletter.yml
│
├── nodes/
│   ├── planner.py
│   ├── news_agent.py
│   ├── image_agent.py
│   ├── writer.py
│   ├── exporter.py
│   └── gmail_agent.py
│
├── static/
│   └── style.css
│
├── templates/
│   └── index.html
│
├── output/
│   ├── ai_daily.md
│   ├── ai_daily.html
│   └── newsletter.json
│
├── api_google.py
├── config.py
├── daily_runner.py
├── graph.py
├── google_sheets_api.py
├── newsletter_data.py
├── schemas.py
├── state.py
├── exa_utils.py
├── pyproject.toml
├── uv.lock
├── .gitignore
└── README.md

⚙️ Requirements

The project currently targets:

Python >= 3.13,<3.14

Main dependencies include:

LangGraph

LangChain

Google Gemini

Exa

FastAPI

PostgreSQL

psycopg

Pydantic

Uvicorn

Requests

BeautifulSoup

Markdown

python-dotenv

APScheduler

🔑 Environment Variables

Create a local .env file:

GEMINI_API_KEY=your_gemini_api_key
EXA_API_KEY=your_exa_api_key
GOOGLE_APPS_SCRIPT_URL=your_google_apps_script_url
NEWSLETTER_PUBLISH_KEY=your_publish_key
DATABASE_URL=your_postgresql_connection_string

Do not commit .env to GitHub.

The project .gitignore already excludes environment files.

🧪 Local Setup

1. Clone the repository

git clone https://github.com/abhimakkena1937-lgtm/AinewsLetterDaily_Agent.git
cd AinewsLetterDaily_Agent

2. Install uv

Install uv if it is not already available.

Then install the project dependencies:

uv sync

3. Configure environment variables

Create:

.env

and add the required API keys and configuration.

4. Run the newsletter locally

uv run python daily_runner.py

The generated files will appear in:

output/

🌐 Running FastAPI

Start the API locally with:

uv run uvicorn api_google:app --host 0.0.0.0 --port 8000

Then open:

http://localhost:8000

If the application serves the frontend through the configured routes, use the corresponding application URL.

⏰ GitHub Actions Automation

The newsletter is scheduled through GitHub Actions.

Current schedule:

on:
  schedule:
    - cron: "30 16 * * *"

  workflow_dispatch:

The cron time is:

16:30 UTC
22:00 IST

GitHub Actions scheduled workflows can sometimes start later than the scheduled time because GitHub may delay scheduled workflow execution.

The workflow can also be manually triggered using:

workflow_dispatch

🚀 Deployment

The web application is deployed on Render.

The production architecture is:

GitHub Actions
      │
      │ Generate newsletter
      ▼
output/newsletter.json
      │
      │ POST /api/publish-newsletter
      ▼
Render FastAPI
      │
      ▼
Supabase PostgreSQL
      │
      ▼
Frontend

The Render service should contain the required environment variables.

🔐 GitHub Actions Secrets

Configure these repository secrets:

GEMINI_API_KEY
EXA_API_KEY
GOOGLE_APPS_SCRIPT_URL
NEWSLETTER_PUBLISH_KEY

The workflow uses these secrets instead of hard-coding credentials.

🔒 Security

Never commit:

.env
API keys
Database passwords
Private tokens
Newsletter publish keys
Google credentials

The .gitignore contains:

.env
.env.*

If a secret is accidentally exposed, rotate/revoke it immediately.

🧰 Troubleshooting

Exa connection errors

Exa requests can fail due to:

Network errors

Rate limits

Temporary service failures

The project includes retry logic with exponential backoff.

Newsletter not appearing on website

Check:

GitHub Actions completed successfully.

output/newsletter.json was generated.

The publish step returned HTTP 200.

Render environment variables are configured.

Supabase contains the latest newsletter row.

The frontend requests the correct API endpoint.

Hard refresh the browser.

GitHub images not appearing

GitHub cards use:

Image Agent image

first.

If unavailable, they use:

GitHub Open Graph preview

and finally:

</>

placeholder.

If the repository URL is missing or invalid, the GitHub preview cannot be generated.

📊 Example Newsletter Pipeline

A typical run looks like:

Planner
   ↓
Research AI news
   ↓
Research startups
   ↓
Research AI people
   ↓
Research GitHub repositories
   ↓
Research papers
   ↓
Generate Tool of the Day
   ↓
Image Agent
   ↓
Writer
   ↓
Exporter
   ↓
newsletter.json
   ↓
Publish to Render
   ↓
Save to Supabase
   ↓
Gmail Agent
   ↓
Subscribers

📌 Design Goals

The project is designed around:

Automated AI research

Structured information extraction

Agent-based workflows

Reliable newsletter generation

Persistent storage

Automated email delivery

Web-based content discovery

Open-source AI project discovery

🧠 Technologies

Technology

Purpose

Python

Core application

LangGraph

Agent workflow orchestration

LangChain

LLM integration

Google Gemini

Structured generation and reasoning

Exa

AI web research

FastAPI

Backend API

PostgreSQL

Persistent storage

Supabase

Hosted PostgreSQL

Google Sheets

Subscriber data

Google Apps Script

Subscriber API

Gmail

Newsletter delivery

GitHub Actions

Daily automation

Render

Web/API deployment

HTML/CSS/JavaScript

Frontend

uv

Python environment and dependency management

📈 Future Improvements

Possible future additions:

User authentication

Personalized newsletters

Topic preferences

Email unsubscribe links

Newsletter history

Search across previous newsletters

More AI research sources

Better image ranking

Analytics dashboard

Subscriber analytics

Admin dashboard

Multiple newsletter schedules

👨‍💻 Author

Abhinay Makkena

AI/ML Engineer | Generative AI | Agentic AI | LangGraph | RAG

📄 License

Add the project's preferred license here before publishing the repository publicly.