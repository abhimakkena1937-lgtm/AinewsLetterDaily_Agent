# AI NewsLetter Daily Agent

An automated AI newsletter platform that researches the latest AI developments, generates a structured daily newsletter, publishes it to a web application, and delivers it to subscribers by email.

The project combines **Python, LangGraph, LangChain, Google Gemini, Exa, FastAPI, PostgreSQL/Supabase, Google Sheets, Google Apps Script, Gmail, GitHub Actions, Render, HTML, CSS, and JavaScript** into one automated workflow.

---

## 🚀 Features

### 📰 AI News

- Latest AI and machine learning news
- Automated web research using Exa
- Time-window based research
- Structured news extraction using Gemini
- Source URLs preserved

### 🚀 Startup & Funding

- AI startup discovery
- Funding information
- Product launches
- Company developments
- Startup URLs and source information

### 👤 AI People

- AI leaders
- Researchers
- Builders
- Important AI-related people and posts

### 💻 GitHub Repositories

- New AI and machine learning repositories
- Repository name
- Description
- Programming language
- GitHub stars
- Repository URL
- Repository images
- GitHub image fallback when the Image Agent does not provide an image

GitHub image priority:

```text
Image Agent image
       ↓
GitHub Open Graph preview
       ↓
GitHub placeholder
```

### 📄 Research Papers

- Newly discovered AI research
- Paper title
- Summary
- Authors
- Source
- URL

### 🛠️ Tool of the Day

The newsletter includes one useful AI-related tool, platform, library, or product discovered from the researched content.

Example:

```json
{
  "name": "Tool Name",
  "description": "Tool description",
  "url": "https://example.com"
}
```

### 🖼️ Image Agent

The Image Agent assigns relevant images to newsletter items.

Supported categories include:

```text
News
Startup
AI People
GitHub
Research
Tool of the Day
```

Image matching uses:

- Exact title matching
- Partial title matching
- Word overlap
- Category matching

### 🧠 LangGraph Workflow

Current workflow:

```text
Planner
   ↓
Combined News Agent
   ↓
Image Agent
   ↓
Writer
   ↓
Exporter
   ↓
Gmail Agent
```

### 📧 Automated Email Delivery

- Automated email delivery
- Google Sheets subscriber storage
- Google Apps Script subscriber API
- Gmail-based newsletter delivery
- Subscribe
- Unsubscribe
- Subscriber status checking

### 🌐 Web Application

The frontend includes:

- Home
- Categories
- Newsletter
- About
- Search
- Subscribe
- Sign In UI
- AI & ML topic
- Startup topic
- Tech & Products topic
- GitHub topic
- Tool of the Day topic
- Research topic
- AI People topic

The Explore Topics cards are displayed in a single horizontal row on desktop and can scroll horizontally on smaller screens.

### 💾 Persistent Newsletter Storage

Newsletter data is stored using:

```text
PostgreSQL
     ↓
Supabase
```

This prevents newsletter data from depending on Render's local filesystem.

### ⏰ Daily Automation

GitHub Actions runs the newsletter generation workflow automatically.

---

# 🏗️ System Architecture

```text
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
                              │  Writer │
                              └────┬────┘
                                   │
                                   ▼
                             ┌──────────┐
                             │ Exporter │
                             └────┬─────┘
                                  │
                 ┌────────────────┴────────────────┐
                 │                                 │
                 ▼                                 ▼
        newsletter.json                       Render API
                 │                                 │
                 │                                 ▼
                 │                           Supabase
                 │                           PostgreSQL
                 │                                 │
                 ▼                                 ▼
          Gmail Agent                         Website
                 │
                 ▼
            Subscribers
```

---

# 🔄 LangGraph Workflow

The graph currently contains:

```text
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
```

There is no Reducer node in the current graph.

---

# 🧩 Components

## 1. Planner

The Planner prepares the research process.

It determines:

- Current date
- Research time window
- Research topics
- Search queries

Example:

```text
Current time
     ↓
Determine time window
     ↓
Create research queries
```

The resulting time window is passed to the research agent.

---

# 2. Combined News Agent

The Combined News Agent performs research using **Exa**.

It searches for:

```text
AI News
Startups
AI People
GitHub repositories
Research Papers
```

The agent performs:

- Concurrent research
- Exa searching
- Retry handling
- Result collection
- Deduplication
- Structured extraction using Gemini
- Tool of the Day generation

---

## Exa Request Concurrency

The project uses:

```python
exa_semaphore = asyncio.Semaphore(3)
```

This controls the number of simultaneous Exa requests.

It does not limit the total number of newsletter items.

---

## Retry Handling

Research requests use retry logic with exponential backoff.

Example:

```text
Attempt 1
   ↓
Wait 2 seconds

Attempt 2
   ↓
Wait 4 seconds

Attempt 3
   ↓
Wait 8 seconds
```

This helps handle temporary Exa/network failures.

---

# 3. Image Agent

The Image Agent produces image assignments for newsletter content.

The exporter supports image values such as:

```text
image_url
url
image
src
```

Images are matched against newsletter items using normalized titles.

The matching process supports:

```text
Exact title
      ↓
Partial title
      ↓
Word overlap
      ↓
Category preference
```

For GitHub repositories, the website also supports a GitHub Open Graph preview fallback.

Example:

```text
https://opengraph.githubassets.com/1/OWNER/REPOSITORY
```

---

# 4. Writer

The Writer converts structured research results into the final newsletter.

Current newsletter structure:

```text
AI Daily

📰 AI News

🚀 Startup & Funding

👤 AI People

💻 New GitHub Repositories

📄 New Research Papers

🛠️ Tool of the Day
```

The Writer is instructed to:

- Use supplied information
- Preserve URLs
- Preserve image URLs
- Avoid inventing content
- Generate the newsletter from structured data

---

# 5. Exporter

The Exporter generates:

```text
output/
├── ai_daily.md
├── ai_daily.html
└── newsletter.json
```

The JSON structure contains:

```json
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
```

The exporter also attaches images to structured newsletter items.

---

# 6. Gmail Agent

The Gmail Agent sends the generated newsletter to subscribers.

The subscriber flow is:

```text
Google Sheets
      ↓
Google Apps Script
      ↓
Subscriber API
      ↓
Gmail Agent
      ↓
Subscribers
```

Supported actions:

```text
subscribe
unsubscribe
check_subscriber
```

---

# 👥 Subscriber Management

Subscriber information is managed through:

```text
Google Sheets
+
Google Apps Script
```

The Python application communicates with the Apps Script endpoint.

Example:

```json
{
  "action": "subscribe",
  "email": "user@example.com"
}
```

---

# 💾 Database

The application uses PostgreSQL hosted through Supabase.

## Database Table

```sql
create table newsletters (
    id bigint generated by default as identity primary key,
    data jsonb not null,
    created_at timestamptz default now()
);
```

## Index

```sql
create index newsletters_created_at_idx
on newsletters (created_at desc);
```

Newsletter data is stored in the:

```text
data
```

JSONB column.

The latest newsletter is loaded using:

```sql
SELECT data
FROM newsletters
ORDER BY created_at DESC, id DESC
LIMIT 1;
```

---

# 🌐 FastAPI Backend

FastAPI provides the backend API.

Important endpoints:

```text
/api/newsletter
/api/publish-newsletter
```

## Newsletter API

```text
GET /api/newsletter
```

Returns the latest newsletter.

## Publish API

```text
POST /api/publish-newsletter
```

GitHub Actions sends the generated newsletter to this endpoint.

The publish request is protected using:

```text
X-Newsletter-Key
```

---

# 🖥️ Frontend

The frontend is built using:

```text
HTML
CSS
JavaScript
```

The Explore Topics section includes:

```text
AI & ML
Startups
Tech & Products
GitHub
Tool of the Day
Research
AI People
```

The topic cards appear in a single horizontal row on desktop.

On smaller screens, horizontal scrolling is enabled.

---

# 💻 GitHub Repository Cards

GitHub cards display:

```text
Repository name
Description
Language
Stars
Repository URL
Image
```

Example:

```text
┌───────────────────────────────┐
│                               │
│      GitHub Repository        │
│                               │
├───────────────────────────────┤
│ GitHub                        │
│                               │
│ repository-name               │
│ Repository description...     │
│                               │
│ Python          ★ 120         │
│                               │
│ View Repository →             │
└───────────────────────────────┘
```

GitHub image handling:

```text
Image Agent image
       ↓
GitHub Open Graph preview
       ↓
GitHub placeholder
```

Fallback URL format:

```text
https://opengraph.githubassets.com/1/OWNER/REPOSITORY
```

---

# 🛠️ Tool of the Day

The Tool of the Day feature uses Gemini structured output.

It selects a useful AI-related:

```text
Tool
Platform
Library
Product
```

The tool is selected from information discovered during the research process.

Example:

```json
{
  "name": "Example AI Tool",
  "description": "Useful AI tool for developers.",
  "url": "https://example.com"
}
```

---

# 📁 Project Structure

```text
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
├── exa_utils.py
├── google_sheets_api.py
├── newsletter_data.py
├── graph.py
├── schemas.py
├── state.py
│
├── pyproject.toml
├── uv.lock
├── .gitignore
└── README.md
```

---

# ⚙️ Requirements

The project uses:

```text
Python >= 3.13,<3.14
```

Main libraries:

```text
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
```

---

# 🔑 Environment Variables

Create a local `.env` file:

```env
GEMINI_API_KEY=your_gemini_api_key
EXA_API_KEY=your_exa_api_key
GOOGLE_APPS_SCRIPT_URL=your_google_apps_script_url
NEWSLETTER_PUBLISH_KEY=your_publish_key
DATABASE_URL=your_postgresql_connection_string
```

Never commit `.env` to GitHub.

---

# 🔒 Security

Never commit:

```text
.env
API keys
Database passwords
Private tokens
Google credentials
Newsletter publish keys
```

The `.gitignore` contains:

```gitignore
.env
.env.*
```

If a secret is accidentally exposed, rotate the secret immediately.

---

# 🧪 Local Installation

## Clone the repository

```bash
git clone https://github.com/abhimakkena1937-lgtm/AinewsLetterDaily_Agent.git
cd AinewsLetterDaily_Agent
```

---

## Install dependencies

Using `uv`:

```bash
uv sync
```

---

## Configure environment

Create:

```text
.env
```

and add the required variables.

---

## Run the newsletter locally

```bash
uv run python daily_runner.py
```

Generated files:

```text
output/
```

---

# 🌐 Run FastAPI Locally

```bash
uv run uvicorn api_google:app --host 0.0.0.0 --port 8000
```

Open:

```text
http://localhost:8000
```

---

# ⏰ GitHub Actions

The newsletter is automatically generated using GitHub Actions.

Current schedule:

```yaml
on:
  schedule:
    - cron: "30 16 * * *"

  workflow_dispatch:
```

This corresponds to:

```text
16:30 UTC
22:00 IST
```

The workflow can also be started manually using:

```text
workflow_dispatch
```

Scheduled GitHub Actions workflows can sometimes start later than the configured schedule.

---

# 🔐 GitHub Actions Secrets

Configure these repository secrets:

```text
GEMINI_API_KEY
EXA_API_KEY
GOOGLE_APPS_SCRIPT_URL
NEWSLETTER_PUBLISH_KEY
```

The secrets are accessed inside the workflow without hard-coding credentials.

---

# 🚀 Production Flow

The production system follows:

```text
GitHub Actions
       ↓
daily_runner.py
       ↓
LangGraph
       ↓
newsletter.json
       ↓
POST /api/publish-newsletter
       ↓
Render FastAPI
       ↓
Supabase PostgreSQL
       ↓
Website
       ↓
Gmail Agent
       ↓
Subscribers
```

---

# 🌍 Deployment

The web application is deployed using Render.

Production architecture:

```text
GitHub Actions
       ↓
Render API
       ↓
FastAPI
       ↓
Supabase PostgreSQL
       ↓
Frontend
```

The frontend retrieves the latest newsletter through:

```text
/api/newsletter
```

---

# 🧰 Troubleshooting

## Newsletter is not generated

Check:

```text
GEMINI_API_KEY
EXA_API_KEY
```

Run:

```bash
uv run python daily_runner.py
```

---

## Exa request failures

Possible causes:

```text
Temporary network problem
Exa rate limit
Invalid Exa API key
```

The project contains retry handling and exponential backoff.

---

## Website does not show the latest newsletter

Check:

```text
1. GitHub Actions run
2. newsletter.json generation
3. Publish API response
4. Render deployment
5. Supabase database
6. /api/newsletter endpoint
7. Browser cache
```

Perform a hard refresh:

```text
Ctrl + Shift + R
```

---

## GitHub topic card does not appear

Make sure the frontend contains:

```javascript
selectCategory('GitHub')
```

and:

```javascript
else if (category === "GitHub") {

    items = (newsletterData.github_repos || []).map(item => ({
        type: "github",
        data: item
    }));

}
```

The frontend should also contain:

```javascript
function createGithubCard(item)
```

---

## GitHub images do not appear

The frontend first checks:

```javascript
item.image_url
```

Then it creates a fallback from the GitHub repository URL:

```text
https://opengraph.githubassets.com/1/OWNER/REPOSITORY
```

If no valid GitHub URL exists, the existing GitHub placeholder is displayed.

---

# 📊 Newsletter Data Flow

```text
Exa Search
    ↓
Raw Research
    ↓
Gemini Structured Output
    ↓
NewsLetterState
    ↓
Image Agent
    ↓
Writer
    ↓
Exporter
    ↓
newsletter.json
```

---

# 🔄 Newsletter Execution

```text
10:00 PM IST
     ↓
GitHub Actions starts
     ↓
Planner creates research window
     ↓
Exa researches AI information
     ↓
Gemini structures content
     ↓
Tool of the Day generated
     ↓
Image Agent assigns images
     ↓
Writer creates newsletter
     ↓
Exporter creates JSON/HTML/Markdown
     ↓
GitHub Actions publishes JSON
     ↓
Render receives newsletter
     ↓
Supabase stores newsletter
     ↓
Gmail Agent sends newsletter
     ↓
Subscribers receive email
```

---

# 🧠 Technology Stack

| Technology | Purpose |
|---|---|
| Python | Core application |
| uv | Dependency and environment management |
| LangGraph | Workflow orchestration |
| LangChain | LLM framework |
| Google Gemini | Structured generation |
| Exa | Web research |
| FastAPI | Backend API |
| PostgreSQL | Persistent data storage |
| Supabase | Hosted PostgreSQL |
| Google Sheets | Subscriber storage |
| Google Apps Script | Subscriber API |
| Gmail | Email delivery |
| GitHub Actions | Daily scheduling |
| Render | Deployment |
| HTML | Frontend structure |
| CSS | Frontend styling |
| JavaScript | Frontend logic |

---

# 📈 Future Improvements

Potential future features:

- User authentication
- Personalized newsletters
- Topic preferences
- Newsletter history
- Historical newsletter search
- Subscriber dashboard
- Admin dashboard
- Analytics
- Email unsubscribe links
- More research sources
- Better image ranking
- AI-generated summaries
- Multiple newsletter schedules
- User-specific content recommendations

---

# 👨‍💻 Author

## Abhinay Makkena

AI/ML Engineer | Generative AI | Agentic AI | LangGraph | RAG

---

# 📄 License

Add the project's preferred license before publishing the repository under an open-source license.

---

# ⭐ Project

GitHub Repository:

https://github.com/abhimakkena1937-lgtm/AinewsLetterDaily_Agent