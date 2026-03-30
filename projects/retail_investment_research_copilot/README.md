# 📊 Retail Investment Research Copilot

A multi-service agentic AI application that gathers live market data and news for any publicly traded stock, then synthesises them into a structured, professional-grade investment memo — powered by **Google ADK**, **Claude Sonnet**, and three independent **FastAPI/Uvicorn agent services**.

> **⚠️ Disclaimer:** This project is purely educational — built to demonstrate Google ADK multi-agent workflows. It is **not** financial advice. Please seek advice from a qualified financial professional before making any investment decisions.

---

## What It Does

Business users — relationship managers, financial advisors, wealth desk analysts, or serious retail investors — repeatedly perform the same research workflow: pull together fundamentals, interpret price behaviour, scan recent news, and write a defensible memo. This project automates that workflow using a pipeline of specialised ADK agents.

Given a **stock ticker** (e.g. `MSFT`, `AAPL`, `TCS.NS`, `RELIANCE.NS`) plus an investment horizon and risk appetite, the pipeline:

1. Fetches live market data — fundamentals and technicals — from Yahoo Finance,
2. Fetches and analyses recent news from Google News RSS feeds,
3. Combines both into a structured investment memo, which is iteratively refined by an automated critic → rewriter loop before being returned.

---

## ADK Workflow Design

The project deliberately uses all three classic ADK orchestration primitives:

| ADK Primitive | Where Used | Purpose |
|---|---|---|
| `SequentialAgent` | All three services (outer pipeline) | Deterministic left-to-right execution — intake → research → synthesis |
| `ParallelAgent` | Market Data & News services | Concurrent specialist analysis for speed |
| `LoopAgent` | Memo service (refinement stage) | Critic → rewriter loop for iterative quality improvement |

---

## Architecture

The application is split into three independent **FastAPI/Uvicorn microservices**. Both front-ends (`main.py` CLI and `streamlit_app.py` web UI) are thin HTTP clients — they know nothing about ADK, sessions, or runners.

```
   CLI (main.py)          Streamlit (streamlit_app.py)
         │                          │
         └──────────┬───────────────┘
                    │  1. POST /invoke  { ticker }
                    ▼
       ┌─────────────────────────────┐
       │  Market Data Service :8101  │  ← SequentialAgent
       │  (yfinance + LLM analysis)  │    [intake → parallel(snapshot, interpret) → packager]
       └─────────────────────────────┘
                    │ market_data_analysis (markdown note)
                    │  2. POST /invoke  { ticker }
                    ▼
       ┌─────────────────────────────┐
       │  News Service        :8102  │  ← SequentialAgent
       │  (Google News RSS)          │    [fetcher → parallel(sentiment, risk) → synthesis]
       └─────────────────────────────┘
                    │ news_analysis (markdown note)
                    │  3. POST /invoke  { ticker, horizon, risk, market_note, news_note }
                    ▼
       ┌─────────────────────────────┐
       │  Memo Service        :8103  │  ← SequentialAgent
       │  (parallel specialists      │    [intake → parallel(valuation, momentum, risk)
       │   + LoopAgent refinement)   │     → writer → loop(critic, rewriter)]
       └─────────────────────────────┘
                    │
                    ▼
          { "result": "...markdown investment memo..." }
```

**Service responsibilities:**

- **Market Data Service (`:8101`)** — Runs a `SequentialAgent` with an inner `ParallelAgent`. The `snapshot_agent` uses the `render_market_snapshot` tool (yfinance) to fetch fundamentals, price history, and technicals. The `interpretation_agent` runs concurrently to interpret and contextualise the data. A final `packager_agent` combines both into a single markdown note.
- **News Service (`:8102`)** — Runs a `SequentialAgent` with an inner `ParallelAgent`. A `fetcher_agent` calls the `fetch_rss_news` tool (Google News RSS). A `sentiment_agent` and a `risk_agent` run in parallel to independently classify the news. A `synthesis_agent` merges all three into a markdown note.
- **Memo Service (`:8103`)** — The most complex pipeline. An `intake_agent` parses the combined payload; three specialist agents (`valuation`, `momentum`, `risk`) run in parallel; a `writer_agent` produces a first-draft memo; and a `LoopAgent` (critic → rewriter, 1 iteration) refines it to emit the polished report.

All agents use **Claude Sonnet** via ADK's `LiteLlm` wrapper. All orchestration agents (`SequentialAgent`, `ParallelAgent`, `LoopAgent`) require no model — they are free, deterministic pipeline coordinators.

---

## Project Structure

```
retail_investment_research_copilot/
├── .env                                   # API keys (not committed to git)
├── .env.example                           # Template — copy this to .env
├── main.py                                # CLI entry point (HTTP client)
├── streamlit_app.py                       # Streamlit web UI entry point (HTTP client)
├── logger.py                              # Shared logging setup (Rich console)
├── pyproject.toml                         # Project metadata & dependencies (uv)
├── scripts/
│   └── start_services.py                  # Launches all three uvicorn services
└── agents/
    ├── __init__.py
    ├── common/
    │   ├── __init__.py
    │   ├── runtime.py                     # Shared ADK Runner wrapper
    │   └── models.py                      # Shared Pydantic request/response models
    ├── market_data_service/
    │   ├── agent.py                       # SequentialAgent + ParallelAgent pipeline
    │   ├── tools.py                       # yfinance data-fetching tool
    │   ├── runtime.py                     # Per-service runtime (re-exports common)
    │   ├── service_app.py                 # FastAPI app (/health + /invoke)
    │   └── models.py                      # Per-service models (re-exports common)
    ├── news_service/
    │   ├── agent.py                       # SequentialAgent + ParallelAgent pipeline
    │   ├── tools.py                       # Google News RSS fetcher tool
    │   ├── runtime.py                     # Per-service runtime (re-exports common)
    │   ├── service_app.py                 # FastAPI app (/health + /invoke)
    │   └── models.py                      # Per-service models (re-exports common)
    └── memo_service/
        ├── agent.py                       # SequentialAgent + ParallelAgent + LoopAgent
        ├── runtime.py                     # Per-service runtime (re-exports common)
        ├── service_app.py                 # FastAPI app (/health + /invoke)
        └── models.py                      # Per-service models (re-exports common)
```

---

## Environment Setup

**Prerequisites:**
1. Python ≥ 3.11
2. [uv](https://docs.astral.sh/uv/) — fast Python environment and package manager

As a first step, clone this repo to your local disk. For the rest of this section, assume you cloned it to `~/code/learning_google_adk` (macOS/Linux) or `c:\code\learning_google_adk` (Windows).

```bash
# 1. Change to the directory where the repo was cloned
cd ~/code/learning_google_adk        # macOS / Linux
# or
cd c:\code\learning_google_adk       # Windows

# 2. Sync the uv-managed virtual environment
#    This installs all required packages (see dependency table below)
uv sync

# 3. Activate the virtual environment
# macOS / Linux:
source .venv/bin/activate
# Windows (PowerShell):
.venv\Scripts\Activate.ps1
# Windows (cmd):
.venv\Scripts\activate.bat

# 4. Change to this project's sub-folder
cd ~/code/learning_google_adk/projects/retail_investment_research_copilot   # macOS / Linux
# or
cd c:\code\learning_google_adk\projects\retail_investment_research_copilot  # Windows
```

### Key Dependencies

| Package | Purpose |
|---------|---------|
| `google-adk` | SequentialAgent, ParallelAgent, LoopAgent, LlmAgent, Runner |
| `litellm` | Unified LLM gateway (Anthropic, OpenAI, Google, …) |
| `yfinance` | Free real-time stock data from Yahoo Finance |
| `feedparser` | Google News RSS feed parser |
| `fastapi` | HTTP framework for each agent service |
| `uvicorn` | ASGI server running the FastAPI services |
| `requests` | HTTP client used by `main.py` and `streamlit_app.py` |
| `streamlit` | Web UI framework |
| `python-dotenv` | Loads `.env` API keys at runtime |
| `pydantic` | Request/response model validation |
| `rich` | Terminal Markdown rendering and colour output |

### Configure API Keys

Copy `.env.example` to `.env` in the `retail_investment_research_copilot/` directory and fill in your key:

```bash
# macOS / Linux
cp .env.example .env

# Windows (PowerShell)
Copy-Item .env.example .env
```

Edit `.env`:

```bash
ANTHROPIC_API_KEY=sk-ant-...your-key-here...
```

> **Note:** This project uses Anthropic Claude Sonnet by default. You can switch to any LLM supported by Google ADK via LiteLlm. To change the model, update the `MODEL` constant at the top of each `agent.py` file:
>
> ```python
> # Default
> MODEL = LiteLlm(model="anthropic/claude-sonnet-4-6")
> # Switch to OpenAI
> MODEL = LiteLlm(model="openai/gpt-4o")
> # Switch to Google Gemini
> MODEL = LiteLlm(model="google/gemini-2.5-flash")
> ```

> **Tip:** You'll need an Anthropic account with API access. Pre-load some credit at [Claude Billing](https://platform.claude.com/settings/billing).

---

## Running the Application

> **Important:** Running the app is a **two-step process**. You must start all three agent services first, then run a front-end in a separate terminal.

### Step 1 — Start All Three Agent Services

From the project root, run:

```bash
python scripts/start_services.py
```

This launches all three FastAPI/Uvicorn services simultaneously:

| Service | Port | Module |
|---|---|---|
| Market Data Service | `:8101` | `agents.market_data_service.service_app` |
| News Service | `:8102` | `agents.news_service.service_app` |
| Memo Service | `:8103` | `agents.memo_service.service_app` |

You should see output like:

```
Starting market-data-service on port 8101...
Starting news-service on port 8102...
Starting memo-service on port 8103...
```

Keep this terminal open. Press **Ctrl+C** to stop all services.

> **Alternative — start each service manually** in three separate terminals:
> ```bash
> uvicorn agents.market_data_service.service_app:app --host 127.0.0.1 --port 8101 --reload
> uvicorn agents.news_service.service_app:app         --host 127.0.0.1 --port 8102 --reload
> uvicorn agents.memo_service.service_app:app         --host 127.0.0.1 --port 8103 --reload
> ```
> Each service also exposes a `/health` endpoint you can use to verify it is running:
> ```bash
> curl http://127.0.0.1:8101/health
> # {"status":"ok","service":"market_data_service"}
> ```

### Option 1 — CLI Mode

In a second terminal (with the virtual environment activated):

```bash
python main.py
```

You will be prompted for three inputs:

```
Enter ticker (example: MSFT or TCS.NS): AAPL
Investment horizon (example: 3 years): 3 years
Risk appetite (low/medium/high): medium
```

`main.py` calls the market data and news services in sequence, combines the results with your inputs, and sends the combined payload to the memo service. The final investment memo is rendered in the terminal via `rich`.

### Option 2 — Streamlit Web UI

In a second terminal:

```bash
streamlit run streamlit_app.py
```

This opens the web UI at `http://localhost:8501`. Enter the ticker, choose a horizon and risk appetite from the dropdowns, click **Generate memo**, and the rendered Markdown investment memo will appear on the page.

---

## Suggested Demo Tickers

| Ticker | Company |
|--------|---------|
| `MSFT` | Microsoft Corporation |
| `AAPL` | Apple Inc. |
| `GOOGL` | Alphabet Inc. |
| `TCS.NS` | Tata Consultancy Services (NSE) |
| `INFY.NS` | Infosys Ltd (NSE) |
| `RELIANCE.NS` | Reliance Industries Ltd (NSE) |

> **Tip:** For any company, visit [Yahoo! Finance](https://finance.yahoo.com/) and search by company name to confirm the correct ticker symbol, including the exchange suffix (e.g. `.NS` for NSE India, `.BO` for BSE India).

---

## Caveats

- This is an educational demo, **not** investment advice.
- Free data from Yahoo Finance and Google News can be delayed, incomplete, or inconsistent. The memo quality is only as good as the underlying data.
- LLM outputs are non-deterministic — two runs for the same ticker may produce different memos.
- The `LoopAgent` refinement loop adds latency. Expect a full run to take 45–90 seconds depending on model response times.
