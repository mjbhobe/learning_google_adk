# 💰 Buffett-Bot: Agentic Value Stock Analyser

An agentic AI application that applies **Warren Buffett's value-investing criteria** to any publicly traded stock and generates an investor-grade Markdown report — powered by **Google ADK**, **Claude 4.6 Sonnet**, and a **FastAPI agent service**.

> **⚠️ Disclaimer:** This project is purely educational — built to demonstrate Google ADK agent workflows. It is not financial advice. Seek a professional advisor before making investment decisions.

---

## Buffett's Value-Investing Method

The application evaluates stocks against five core criteria:

| Criterion | Formula / Metric | Threshold |
|-----------|-----------------|-----------|
| **Return on Equity (ROE)** | Net Income / Shareholder Equity | **> 15 %** |
| **Debt-to-Equity (D/E)** | Total Debt / Shareholder Equity | **< 0.5** |
| **Economic Moat** | Brand strength, margins, competitive position | Qualitative |
| **Intrinsic Value (DCF)** | `Free Cash Flow / Discount Rate` (discount rate = **10 %**) | Calculated |
| **Margin of Safety** | `Current Price < 70 % × Intrinsic Value` → **Buy** | **Price < 70 % of IV** |

---

## Architecture

The application uses a **service-oriented** design. The ADK agent pipeline runs as a standalone **FastAPI/Uvicorn HTTP service**; both front-ends (`main.py` CLI and `streamlit_app.py` web UI) are thin HTTP clients that POST a payload and render the response.

```
   CLI (main.py)          Streamlit (streamlit_app.py)
         │                          │
         └──────────┬──────────────┘
                    │  POST /run  { symbol, company_info, raw_financials }
                    ▼
        ┌─────────────────────────┐
        │  FastAPI Agent Service   │   ← uvicorn on :8000
        │  buffet_bot.agents       │
        └───────────┬─────────────┘
                    │
                    ▼
        ┌──────────────────────────────────────────┐
        │  SequentialAgent (buffett_stock_analysis) │
        │                                           │
        │  ┌───────────────┐   ┌─────────────────┐ │
        │  │ analyst_agent │──▶│ reporter_agent   │ │
        │  └───────────────┘   └─────────────────┘ │
        └──────────────────────────────────────────┘
                    │
                    ▼
        { "formatted_report": { "analysis_report": "...markdown..." } }
```

- **`analyst_agent`** — Reads `symbol`, `company_info`, and `raw_financials` from session state. Performs ROE, D/E, moat, DCF, and margin-of-safety checks. Writes output to `investment_reasoning`.
- **`reporter_agent`** — Reads all prior state (financials + `investment_reasoning`) and produces a formatted Markdown report. Writes to `analysis_report`.

Both agents use **Claude 4.6 Sonnet** via ADK's `LiteLlm` wrapper. The `SequentialAgent` itself requires no model — it is a free, deterministic pipeline coordinator.

---

## Project Structure

```
buffet_stock_analyser/
├── .env                              # API keys (not committed to git)
├── main.py                           # CLI entry point (HTTP client → agent service)
├── streamlit_app.py                  # Streamlit GUI entry point (HTTP client → agent service)
├── servers.sh                        # Bash helper script (Linux / macOS / Git Bash)
├── servers.ps1                       # PowerShell helper script (Windows)
├── utils.py                          # yfinance data fetcher
├── logger.py                         # Logging config (Rich console + rotating file)
├── logs/                             # Auto-generated log files
│
└── buffet_bot/                       # ADK agent package
    ├── __init__.py
    ├── common/
    │   └── a2a_server.py             # Reusable FastAPI app factory (create_app)
    └── agents/
        ├── __init__.py
        ├── __main__.py               # FastAPI/Uvicorn entry point (serves :8000)
        ├── agent.py                  # SequentialAgent + execute() coroutine
        ├── task_manager.py           # Bridges FastAPI route → execute()
        └── subagents/
            ├── analyst_agent/
            │   ├── __init__.py
            │   ├── agent.py          # LlmAgent — Buffett-style financial analysis
            │   └── prompt.py         # Analyst prompt template
            └── reporter_agent/
                ├── __init__.py
                ├── agent.py          # LlmAgent — Markdown report generation
                └── prompt.py         # Reporter prompt template
```

---

## Environment Setup

**Prerequisites:** 
1. Python ≥ 3.14, 
2. [uv](https://docs.astral.sh/uv/) - for managing local Python environment

As a first step, clone this repo to your local disk. For the rest of this section, let's 
assume you cloned it to `~/code/learning_google_adk` folder on Mac or Linux or the 
`c:\code\learning_google_adk` on Windows.

```bash
# 1. change to directory where the repo was cloned
cd ~/code/learning_google_adk  # on Mac or Linux
or 
cd c:\code\learning_google_adk  # on Windows

# 2. sync the uv managed local environment
# it will install all the required modules (see key-dependencies table below)
uv sync

# 3. activate the virtual environment
# Windows:
.venv\Scripts\activate
# macOS / Linux:
source .venv/bin/activate

# 4. change to this project's sub-folder
cd ~/code/learning_google_adk/projects/buffet_stock_analyser  # on Mac or Linux
or 
cd c:\code\learning_google_adk\projects\buffet_stock_analyser  # on Windows
```

Key dependencies:

| Package | Purpose |
|---------|---------|
| `google-adk` | SequentialAgent, LlmAgent, Runner |
| `litellm` | Unified LLM gateway (Anthropic, OpenAI, Google, …) |
| `yfinance` | Real-time stock data from Yahoo Finance |
| `python-dotenv` | Loads `.env` API keys |
| `rich` | Terminal Markdown rendering & colour |
| `fastapi` | HTTP framework for the agent service |
| `uvicorn` | ASGI server running the FastAPI service |
| `requests` | HTTP client used by `main.py` & `streamlit_app.py` |
| `streamlit` | Web UI framework |

### Create your API Keys

Create a `.env` file in the `buffet_stock_analyser/` directory:

```bash
ANTHROPIC_API_KEY=sk-ant-...your-key-here...
# Optional overrides
HOST_AGENT_URL=http://localhost:8000/run
```

NOTE: we have used Anthropic Claude Sonnet in this example. You can use any LLM supported by Google ADK.
To change the LLM used, you'll need to modify the the following line in the `subagents/analyst_agent/agent.py` and `subagents/reporter_agent/agent.py` files:

```python
# LLM used
llm_model = LiteLlm(model="anthropic/claude-sonnet-4-6")
# to use OpenAI
llm_model = LiteLlm(model="openai/gpt-4o")
# to use Google Gemini
llm_model = LiteLlm(model="google/gemini-2.5-flash")
```
---

## Running the Application

> **Important:** Running the app is a two-step process. You must start the agent service first, then run a front-end.

### Step 1 — Start the Agent Service

**Linux / macOS / WSL / Git Bash:**

```bash
cd ~/code/learning_google_adk/projects/buffet_stock_analyser 
chmod u+x servers.sh   # first time only
./servers.sh
```

**Windows PowerShell (native):**

```powershell
cd c:\code\learning_google_adk\projects\buffet_stock_analyser
.\servers.ps1
```

> If PowerShell blocks the script with an execution-policy error, run:
> ```powershell
> Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
> ```

**Universal fallback (any OS, any shell):**

```bash
uvicorn buffet_bot.agents.__main__:app --port 8000
```

Keep this terminal open. The service listens at `http://localhost:8000/run`. Press **Ctrl+C** to stop.

### Option 1 — CLI Mode

In a second terminal:

```bash
uv run main.py
```

Enter a ticker symbol (e.g. `TSLA`, `GOOGL`) at the prompt. `main.py` fetches live data, POSTs it to the agent service, and renders the Markdown report in your terminal via Rich. Type `exit` to quit.

### Option 2 — Streamlit GUI

In a second terminal:

```bash
streamlit run streamlit_app.py
```

Opens a web UI where you enter a ticker, click **"Analyze Stock"**, and view the final report rendered in the browser. `streamlit_app.py` mirrors `main.py` exactly — both are simple HTTP clients with no ADK imports.
