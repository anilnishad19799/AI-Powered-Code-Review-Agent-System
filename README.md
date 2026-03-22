# 🤖 AI-Powered Code Review Agent System

> A production-ready multi-agent system that automatically reviews your Pull Requests using AI — checking code quality, security vulnerabilities, and performance issues — then posts a detailed review comment directly on GitHub.

---

## ✨ What It Does

Every time you open or update a Pull Request, this system automatically:

1. **Fetches** the PR diff from GitHub
2. **Runs 3 AI agents in parallel** to analyze the code
3. **Synthesizes** all findings into one final review
4. **Posts** a detailed Markdown comment directly on your PR — in under 30 seconds

```
PR Opened on GitHub
        │
        ▼
FastAPI Webhook  ──▶  Redis Queue  ──▶  ARQ Worker
                                              │
                              ┌───────────────┼───────────────┐
                              ▼               ▼               ▼
                         Agent 1         Agent 2         Agent 3
                        Quality         Security       Performance
                              └───────────────┼───────────────┘
                                              ▼
                                         Agent 4
                                      Final Reviewer
                                              │
                                              ▼
                                   Comment Posted on PR ✅
```

### Sample Output on GitHub PR

```
## 🤖 AI Code Review

**Overall Verdict:** ⚠️ NEEDS CHANGES
**Score:** 5.33/10

### 📋 Code Quality
Function naming is unclear. Code duplication detected across files...

### 🔒 Security
Critical: Hardcoded API key found on line 4.
Critical: SQL injection vulnerability on line 10...

### ⚡ Performance
Nested loop detected — O(n²) complexity.
N+1 query problem in get_user()...

### 🚨 Must Fix Before Merge
- Remove hardcoded API_KEY — use environment variables
- Parameterize SQL queries to prevent injection
- Refactor nested loops for better performance
```

---

## 🏗️ Architecture

### Tech Stack

| Layer | Technology |
|---|---|
| **API Framework** | FastAPI |
| **Agent Orchestration** | LangGraph |
| **LLM Providers** | Claude (Anthropic) / OpenAI (switchable) |
| **Job Queue** | ARQ + Redis |
| **GitHub Integration** | PyGitHub |
| **Containerization** | Docker + Docker Compose |
| **Logging** | Loguru |
| **Config** | Pydantic Settings |

### Agent Roles

| Agent | Role | Output |
|---|---|---|
| **Agent 1 — Quality** | Naming, DRY, error handling, readability | Score + Issues JSON |
| **Agent 2 — Security** | SQL injection, hardcoded secrets, auth flaws | Score + Vulnerabilities JSON |
| **Agent 3 — Performance** | N+1 queries, nested loops, blocking I/O | Score + Improvements JSON |
| **Agent 4 — Reviewer** | Synthesizes all 3 reports → GitHub comment | Markdown comment |

Agents 1, 2, and 3 run **in parallel** — Agent 4 waits for all three before writing the final review.

---

## 📁 Project Structure

```
AI-Powered-Code-Review-Agent-System/
│
├── app/
│   ├── main.py                        # FastAPI entrypoint
│   │
│   ├── api/
│   │   └── webhook.py                 # GitHub webhook receiver
│   │
│   ├── core/
│   │   ├── config.py                  # Pydantic settings (env vars)
│   │   ├── logger.py                  # Loguru setup
│   │   ├── security.py                # HMAC webhook verification
│   │   └── exceptions.py              # Custom exception classes
│   │
│   ├── graph/
│   │   ├── state.py                   # LangGraph shared state schema
│   │   ├── builder.py                 # Graph wiring + parallel edges
│   │   └── node/
│   │       ├── fetch_pr.py            # Fetches PR diff from GitHub
│   │       ├── agent_quality.py       # Agent 1: Code quality
│   │       ├── agent_security.py      # Agent 2: Security
│   │       ├── agent_performance.py   # Agent 3: Performance
│   │       └── agent_reviewer.py      # Agent 4: Final review
│   │
│   ├── services/
│   │   ├── github_service.py          # GitHub API wrapper
│   │   └── llm/
│   │       ├── base.py                # Abstract LLM interface
│   │       ├── claude.py              # Anthropic Claude implementation
│   │       ├── openai.py              # OpenAI implementation
│   │       └── factory.py             # LLM provider switcher
│   │
│   ├── models/
│   │   └── schemas.py                 # Pydantic request/response models
│   │
│   ├── prompts/
│   │   └── agent_prompts.py           # System prompts for all 4 agents
│   │
│   └── workers/
│       └── review_worker.py           # ARQ async job execution
│
├── docker/
│   └── .dockerignore
│
├── tests/
├── scripts/
├── logs/
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── requirements-dev.txt
├── pyproject.toml
├── .env.example
└── README.md
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Docker + Docker Compose
- [ngrok](https://ngrok.com) account (free)
- GitHub Personal Access Token
- Anthropic API Key **or** OpenAI API Key

---

### Step 1 — Clone the Repo

```bash
git clone https://github.com/anilnishad19799/AI-Powered-Code-Review-Agent-System.git
cd AI-Powered-Code-Review-Agent-System
```

---

### Step 2 — Create `.env` File

```bash
cp .env.example .env
```

Open `.env` and fill in your values:

```env
# ── LLM Provider ──────────────────────────────────────
LLM_PROVIDER=openai               # "claude" or "openai"

# ── Anthropic (if LLM_PROVIDER=claude) ────────────────
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxx
ANTHROPIC_MODEL=claude-sonnet-4-20250514

# ── OpenAI (if LLM_PROVIDER=openai) ───────────────────
OPENAI_API_KEY=sk-xxxxxxxxxxxx
OPENAI_MODEL=gpt-4o-mini

# ── GitHub ─────────────────────────────────────────────
GITHUB_TOKEN=ghp_xxxxxxxxxxxx
GITHUB_WEBHOOK_SECRET=your_random_secret_string
GITHUB_REPO_OWNER=your-github-username
GITHUB_REPO_NAME=your-repo-name

# ── Redis ──────────────────────────────────────────────
REDIS_URL=redis://redis:6379      # use this for Docker
# REDIS_URL=redis://localhost:6379  # use this for local run

# ── App ────────────────────────────────────────────────
APP_ENV=development
APP_PORT=8000
LOG_LEVEL=INFO
```

---

### Step 3 — Get Your API Keys

**GitHub Personal Access Token:**
```
github.com → Settings → Developer Settings
→ Personal access tokens → Tokens (classic)
→ Generate new token
→ Check: repo, write:discussion
→ Copy token → paste as GITHUB_TOKEN
```

**Anthropic API Key:**
```
console.anthropic.com → API Keys → Create Key
→ Copy → paste as ANTHROPIC_API_KEY
```

**OpenAI API Key:**
```
platform.openai.com → API Keys → Create Key
→ Copy → paste as OPENAI_API_KEY
```

---

### Step 4 — Run with Docker (Recommended)

```bash
docker compose up --build
```

This starts **3 services** in the correct order:
1. 🔴 **Redis** — job queue
2. 🟢 **FastAPI** — webhook receiver (waits for Redis)
3. 🟡 **ARQ Worker** — runs AI agents (waits for Redis + API)

Expected output:
```
pr_review_redis  | Ready to accept connections
pr_review_api    | 🚀 PR Review Agent starting
pr_review_api    |    Environment : development
pr_review_api    | INFO: Application startup complete.
pr_review_worker | Starting worker for 1 functions: run_pr_review
pr_review_worker | redis_version=7.0.0 mem_usage=1.35M
```

**Verify it's running:**
```bash
curl http://localhost:8000/health
# {"status": "healthy", "env": "development"}
```

---

### Step 5 — Expose with ngrok

In a **separate terminal**:

```bash
ngrok http 8000
```

Copy the `https://` URL shown:
```
Forwarding  https://abc123.ngrok-free.app -> http://localhost:8000
```

---

### Step 6 — Configure GitHub Webhook

```
1. Go to your repo on GitHub
2. Settings → Webhooks → Add webhook

   Payload URL:    https://abc123.ngrok-free.app/api/webhook
   Content type:   application/json
   Secret:         (same value as GITHUB_WEBHOOK_SECRET in .env)
   Events:         ✅ Pull requests only

3. Click "Add webhook"
4. GitHub sends a ping → you'll see green ✅
```

---

### Step 7 — Trigger a Review

```bash
# Create a feature branch
git checkout -b feature/my-new-feature

# Make some changes
echo "print('hello')" > scripts/test.py

# Push and open a PR
git add .
git commit -m "Add test script"
git push origin feature/my-new-feature

# Go to GitHub → open a Pull Request
# The AI review will appear as a comment within ~30 seconds
```

---

## 🏃 Run Without Docker (Local Development)

If you prefer running locally without Docker:

**Terminal 1 — Redis:**
```bash
# Mac
brew install redis && brew services start redis

# Windows (Docker just for Redis)
docker run -d -p 6379:6379 redis:7-alpine

# Linux
sudo apt install redis-server && sudo systemctl start redis
```

**Terminal 2 — FastAPI:**
```bash
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Change REDIS_URL in .env to redis://localhost:6379
uvicorn app.main:app --reload --port 8000
```

**Terminal 3 — ARQ Worker:**
```bash
source venv/bin/activate
arq app.workers.review_worker.WorkerSettings
```

**Terminal 4 — ngrok:**
```bash
ngrok http 8000
```

---

## 🔄 Switching LLM Provider

Change one line in `.env`:

```env
# Use Claude
LLM_PROVIDER=claude

# Use OpenAI
LLM_PROVIDER=openai
```

No code changes needed — the factory pattern handles everything.

| Feature | Claude | OpenAI |
|---|---|---|
| JSON reliability | Good | Better (native JSON mode) |
| Speed | Fast | Fast |
| Cost | Varies by model | Varies by model |
| Recommended model | claude-sonnet-4-20250514 | gpt-4o-mini |

---

## 🐳 Docker Commands

```bash
# Start everything (first time or after code changes)
docker compose up --build

# Start in background
docker compose up --build -d

# Watch logs
docker compose logs -f

# Watch specific service
docker compose logs -f worker
docker compose logs -f api

# Stop everything
docker compose down

# Stop and wipe Redis data
docker compose down -v

# Restart one service
docker compose restart worker
docker compose restart api

# Check container status
docker compose ps
```

---

## 🔍 How It Works — Deep Dive

### 1. Webhook Flow
```
GitHub PR opened
      │
      ▼ HTTP POST + HMAC-SHA256 signature
FastAPI /api/webhook
      │
      ├── Verifies HMAC signature (security.py)
      ├── Parses pull_request event
      ├── Enqueues job to Redis (non-blocking)
      └── Returns 202 Accepted to GitHub in < 1 second
```

> **Why Redis queue?** GitHub expects a webhook response within 10 seconds. A full AI review takes 20-30 seconds. The queue lets us return immediately and process in the background.

### 2. LangGraph Pipeline
```
GraphState initialized
      │
      ▼
fetch_pr_node          → GitHub API → PR diff text
      │
      ├──────────────────┬────────────────────┐
      ▼                  ▼                    ▼
agent_quality_node  agent_security_node  agent_performance_node
(parallel)          (parallel)           (parallel)
      │                  │                    │
      └──────────────────┴────────────────────┘
                         │
                         ▼
                agent_reviewer_node
                         │
                         ▼
              GitHub PR comment posted
```

### 3. State Management

Each agent returns **only its own output key** — no full state copy. This prevents LangGraph parallel write conflicts:

```python
# ✅ Correct — agent only returns what it owns
async def agent_quality_node(state: GraphState) -> dict:
    ...
    return {"quality_review": review}   # not {**state, "quality_review": review}
```

---

## ⚙️ Environment Variables Reference

| Variable | Required | Description |
|---|---|---|
| `LLM_PROVIDER` | Yes | `claude` or `openai` |
| `ANTHROPIC_API_KEY` | If claude | Your Anthropic API key |
| `ANTHROPIC_MODEL` | No | Default: `claude-sonnet-4-20250514` |
| `OPENAI_API_KEY` | If openai | Your OpenAI API key |
| `OPENAI_MODEL` | No | Default: `gpt-4o-mini` |
| `GITHUB_TOKEN` | Yes | Personal access token with `repo` scope |
| `GITHUB_WEBHOOK_SECRET` | Yes | Random string — must match GitHub webhook config |
| `GITHUB_REPO_OWNER` | Yes | Your GitHub username |
| `GITHUB_REPO_NAME` | Yes | Repository name to watch |
| `REDIS_URL` | Yes | `redis://redis:6379` (Docker) or `redis://localhost:6379` (local) |
| `APP_ENV` | No | `development` or `production` |
| `LOG_LEVEL` | No | `DEBUG`, `INFO`, `WARNING` |

---

## 🧯 Troubleshooting

**Webhook returns 500:**
```
Check uvicorn terminal for traceback.
Most common cause: import error in webhook.py
Fix: ensure no response_model on the webhook route
```

**"PR not found" error:**
```
Check GITHUB_REPO_OWNER and GITHUB_REPO_NAME in .env
Must match the repo where the webhook is configured
```

**Worker not picking up jobs:**
```
Check Redis is running: redis-cli ping → PONG
Check REDIS_URL matches between API and worker
Restart worker after .env changes
```

**ngrok 502 error:**
```
FastAPI is not running on port 8000
Run: curl http://localhost:8000/health
Start uvicorn first, then test ngrok
```

**ngrok URL changed:**
```
Every ngrok restart = new URL
Update webhook Payload URL in GitHub Settings → Webhooks
```

---

## 📊 Performance

Based on real runs during development:

| Metric | Value |
|---|---|
| Webhook response time | < 1 second |
| Full review time | ~25-30 seconds |
| Parallel agent speedup | ~3x vs sequential |
| Files supported | Any language in PR diff |

---

## 🔐 Security

- **HMAC-SHA256 verification** on every webhook request — spoofed requests are rejected
- **Non-root Docker user** — container runs as `appuser`, not root
- **Secrets via environment variables** — never hardcoded
- **`.env` in `.gitignore`** — secrets never committed to repo

---

## 📄 License

MIT License — feel free to fork, modify, and use in your own projects.

---

## 🙏 Built With

- [FastAPI](https://fastapi.tiangolo.com/)
- [LangGraph](https://github.com/langchain-ai/langgraph)
- [Anthropic Claude](https://anthropic.com)
- [OpenAI](https://openai.com)
- [ARQ](https://arq-docs.helpmanual.io/)
- [PyGitHub](https://pygithub.readthedocs.io/)
- [Loguru](https://loguru.readthedocs.io/)
