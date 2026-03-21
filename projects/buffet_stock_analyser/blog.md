# Building a Warren Buffett Stock Analyser with Google ADK: An Agentic AI Approach

*Automating value-investing fundamentals with a multi-agent pipeline powered by Google's Agent Development Kit and Claude 4.6 Sonnet.*

---

> **⚠️ Disclaimer:** I am not a financial advisor and this blog post should not be construed as financial advice. The purpose of this article is purely educational — to demonstrate how Google ADK agent workflows can be constructed using a real-world use case. If you are considering investing in stocks, please seek professional financial advice before making any decisions.

## Introduction — Warren Buffett's Value-Investing Framework

Warren Buffett's investment philosophy distils decades of disciplined stock-picking into a remarkably small set of quantitative and qualitative tests. Before handing any stock a "Buy" recommendation, Buffett asks:

| # | Criterion | What to Look For | Threshold |
|---|-----------|-----------------|-----------| 
| 1 | **Return on Equity (ROE)** | Consistently high profitability relative to shareholder equity | **ROE > 15 %** |
| 2 | **Debt-to-Equity Ratio (D/E)** | Conservative leverage; the company can service its debt easily | **D/E < 0.5** |
| 3 | **Economic Moat** | Durable competitive advantages — brand, patents, network effects, switching costs | Qualitative assessment |
| 4 | **Intrinsic Value (DCF)** | Discounted Cash Flow valuation using a **10 % discount rate** | Calculated from free cash flow |
| 5 | **Margin of Safety** | Only buy when the market price is *significantly* below intrinsic value | **Price < 70 % of Intrinsic Value** |

The formulae we'll use throughout the code are:

**Intrinsic Value (simplified DCF):**

```
Intrinsic Value = Free Cash Flow / Discount Rate
```

where the **discount rate = 10 %**.

**Margin of Safety rule:**

```
If Current Price < 0.70 × Intrinsic Value  →  Buy
If Current Price is within 70–100 % of IV  →  Hold
Otherwise                                  →  Avoid
```

Our goal is to build an **Agentic AI application** that ingests real-time financial data for any publicly-traded stock, applies the five criteria above, and produces an investor-grade Markdown report — all orchestrated by **Google ADK** (Agent Development Kit).

For downloading financial data, we'll use the `yfinance` library and ask user to specify the stock symbol of interest as used on Yahoo! Finance - for example `AAPL` (Apple Inc), `MSFT` (Microsoft Corporation), `HDFCBANK.NS` (HDFC Bank Ltd), `RELIANCE.NS` (Reliance Industries Ltd), `TCS.NS` (Tata Consultancy Services Ltd) etc.

> **⚠️ Tip** Navigate to the [Yahoo! Finance](https://finance.yahoo.com/) website and type in the name of the company of interest in the `Search` bar (for e.g., `Reliance Industries`). It will display a drop-down with all matches, including the stock symbol. Use the stock symbol displayed.

---
## Google ADK Implementation

### High-Level Architecture

The application has been refactored into a **service-oriented architecture**. The _core_ ADK agent pipeline is a `SequentialAgent` that is deployed as a **FastAPI/Uvicorn HTTP service** running on `localhost:8080` by default. 

The front-ends (CLI and Streamlit) _ask_ user for the stock symbol (such as `AAPL`) and downloads financial data, which is _fed_ as a payload to this end-point  via a simple `POST /run` request.

The diagram below, and the text following describe the complete workflow.

```
   CLI (main.py)          Streamlit (streamlit_app.py)
         │                          │
         └──────────┬───────────────┘
                    │  POST /run  { symbol, company_info, raw_financials }
                    ▼
        ┌─────────────────────────┐
        │  FastAPI Agent Service  │   ← uvicorn on :8000
        │  buffet_bot.agents      │
        └───────────┬─────────────┘
                    │
                    ▼
        ┌──────────────────────────────────────────┐
        │  SequentialAgent (buffett_stock_analysis) │
        │                                           │
        │  ┌───────────────┐    ┌────────────────┐ │
        │  │ analyst_agent │ ──▶│ reporter_agent  │ │
        │  └───────────────┘    └────────────────┘ │
        └──────────────────────────────────────────┘
                    │
                    ▼
        { "formatted_report": { "analysis_report": "...markdown..." } }
```

1. **Data ingestion** — Both front-ends pull live market data from Yahoo Finance via `yfinance` and build a JSON payload.
2. **HTTP dispatch** — The payload is `POST`-ed to `http://localhost:8000/run`. The FastAPI service is started separately via `servers.sh` (or `uvicorn`) before running any front-end.
3. **Analysis** — The `analyst_agent` (an LLM-backed agent) applies Buffett's five criteria and writes results to session state key `investment_reasoning`.
4. **Reporting** — The `reporter_agent` takes the raw analysis and polishes it into a professional Markdown report, stored under `analysis_report`.
5. **Response** — The service returns `{ "formatted_report": { "analysis_report": "...markdown..." } }` which both front-ends render.

---

### Step 1 — Downloading & Preparing Financial Data

All data fetching lives in `utils.py`. We use `yfinance` to pull a stock's `info` dictionary and then slice it into two clean dictionaries that will be sent as the HTTP payload:

```python
import yfinance as yf

def get_stock_info(symbol: str) -> (dict, dict):
    """Extracts company info and raw financial metrics for a given ticker. The symbol parameter is the stock symbol (e.g. AAPL)_"""
    ticker = yf.Ticker(symbol)
    info = ticker.info

    company_info = {
        "company_name": info.get("longName"),
        "sector": info.get("sector", "Unknown"),
        "industry": info.get("industry", "Unknown"),
        "description": info.get("longBusinessSummary", "No description available."),
    }

    raw_financials = {
        "symbol": symbol,
        "stock_price": info.get("currentPrice"),
        "return_on_equity": info.get("returnOnEquity"),
        "debt_to_equity_ratio": info.get("debtToEquity", 0) / 100,  # Normalised
        "free_cash_flow": info.get("freeCashflow", 0),
        "price_to_earnings_ratio": info.get("trailingPE"),
        "market_cap": info.get("marketCap"),
        "beta": info.get("beta"),
    }

    return company_info, raw_financials
```

**Key design decisions:**

- `debtToEquity` from Yahoo Finance is reported as a percentage (e.g. `45` means 0.45). We normalise it by dividing by 100 so the LLM sees a ratio directly comparable to the 0.5 threshold.
- We deliberately pull `beta` and `market_cap` as supplementary context even though they are not core Buffett metrics — they help the LLM write a richer qualitative analysis.

---

### Step 2 — The FastAPI Agent Service

Instead of the agent pipeline being imported directly into the front-end scripts, it now runs as a standalone FastAPI service. The entry point is `buffet_bot/agents/__main__.py`:

```python
from buffet_bot.common.a2a_server import create_app
from .task_manager import run

app = create_app(agent=type("Agent", (), {"execute": run}))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, port=8000)
```

The shared `create_app` helper in `buffet_bot/common/a2a_server.py` builds the FastAPI app with a single `POST /run` route:

```python
from fastapi import FastAPI

def create_app(agent):
    app = FastAPI()

    @app.post("/run")
    async def run(payload: dict):
        return await agent.execute(payload)

    return app
```

`type("Agent", (), {"execute": run})` is Python's dynamic class creation — it creates an anonymous class with a single `execute` method pointing to the `task_manager.run` coroutine, satisfying the interface `create_app` expects without needing a formal class definition.

The `task_manager.run` function calls through to the ADK agent pipeline and wraps the result:

```python
from .agent import execute

async def run(payload):
    formatted_report = await execute(payload)
    return {"formatted_report": formatted_report}
```

---

### Step 3 — The SequentialAgent Orchestrator

Google ADK's `SequentialAgent` is a non-LLM orchestrator that runs its sub-agents in strict left-to-right order. Because it does not itself need a model, it is free — all inference cost is in the sub-agents.

```python
from google.adk.agents import SequentialAgent
from .subagents.analyst_agent.agent import analyst_agent
from .subagents.reporter_agent.agent import reporter_agent

root_agent = SequentialAgent(
    name="buffett_stock_analysis_workflow",
    # NOTE: No model required for SequentialAgent!
    sub_agents=[analyst_agent, reporter_agent],
    description=(
        "A pipeline that analyses raw financial metrics of a stock "
        "and generates a recommendation & a structured report"
    ),
)
```

The `execute` coroutine in `buffet_bot/agents/agent.py` wires the `Runner` to the `SequentialAgent`. It creates a fresh session on every call (using `uuid4()` for the session ID), injects the full payload into session state, and runs the pipeline:

```python
async def execute(request):
    session_service = InMemorySessionService()
    runner = Runner(agent=root_agent, app_name=APP_NAME, session_service=session_service)

    await session_service.create_session(
        app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID,
        state=request,   # ← payload becomes shared session state for sub-agents
    )

    prompt = f"Analyse the stock {request['symbol']}"
    message = types.Content(role="user", parts=[types.Part(text=prompt)])

    async for event in runner.run_async(user_id=USER_ID, session_id=SESSION_ID, new_message=message):
        if event.is_final_response():
            if event.content and event.content.parts:
                return {"analysis_report": event.content.parts[0].text}
```

The pipeline is:

1. `analyst_agent` reads `symbol`, `company_info`, and `raw_financials` from session state, performs the Buffett analysis, and writes its output to the state key `investment_reasoning`.
2. `reporter_agent` reads everything — including `investment_reasoning` — and produces the final polished report, stored under `analysis_report`.

---

### Step 4 — The Analyst Agent

The `analyst_agent` is an `LlmAgent` backed by **Claude 4.6 Sonnet** (accessed through ADK's `LiteLlm` wrapper, which lets us use any model provider — OpenAI, Anthropic, Google — with a unified interface).

```python
from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm

llm_model = LiteLlm(model="anthropic/claude-sonnet-4-6")

analyst_agent = LlmAgent(
    name="analyst_agent",
    model=llm_model,
    instruction=ANALYST_PROMPT,
    output_key="investment_reasoning",
)
```

The `output_key="investment_reasoning"` tells ADK to persist the agent's final text response into the session state under that key — making it automatically available to all downstream agents.

The prompt instructs the LLM to act as a Buffett-style analyst and perform the five checks:

```python
ANALYST_PROMPT = """
You are an expert Financial Analyst specializing in Warren Buffett's Value Investing.
Analyze the following financial data for {symbol}:

Company Info: 
{company_info}

Raw Financials:
{raw_financials}

Your task:
1. ROE Analysis: Is it > 15%? Explain the trend.
2. Debt/Equity: Is it < 0.5? Can the company handle its obligations?
3. Moat Analysis: Based on the company name and margins, does it have a 'moat'?
4. DCF Valuation: Calculate Intrinsic Value using a 10% discount rate.
5. Decision: Provide a 'Buy', 'Hold', or 'Avoid' recommendation based strictly 
   on Buffett's Margin of Safety (Price < 70% of Intrinsic Value).
"""
```

Notice the `{symbol}`, `{company_info}`, and `{raw_financials}` placeholders — ADK automatically interpolates these from the session state at runtime.

---

### Step 5 — The Reporter Agent

The `reporter_agent` is also an `LlmAgent` on the same Claude model, but its job is pure editorial:

```python
reporter_agent = LlmAgent(
    name="reporter_agent",
    model=llm_model,
    instruction=REPORTER_PROMPT,
    output_key="final_markdown_report",
)
```

Its prompt focuses on formatting:

```python
REPORTER_PROMPT = """
You are a Professional Financial Editor. 
Convert the provided analysis into a beautiful, investor-grade Markdown report.

Use the following information available to you:

Company Info: {company_info}

Raw Financials:
{raw_financials}

Analysis:
{investment_reasoning}

Create a well-formatted Markdown report using the following layout:
- Header with Company Name and Ticker
- Paragraph giving brief description of the company, and the industry & sector it operates in.
- A Summary Table of Key Metrics (ROE, D/E, PE Ratio, Current Price vs Intrinsic Value)
- Detailed Qualitative Analysis (The 'Moat' and Management)
- Final Recommendation in a Bold Callout Box.
"""
```

Here `{investment_reasoning}` is the output from the previous analyst step — ADK resolves it from session state automatically.

---

## Setup & Project Organisation

### Python Environment Setup

This project uses [**uv**](https://docs.astral.sh/uv/) as the Python environment and package manager. You'll need **Python ≥ 3.14**.

```bash
# 1. Clone the repository
git clone https://github.com/<your-username>/learning_google_adk.git
cd learning_google_adk

# 2. Create and activate a virtual environment with uv
uv venv
# On Windows:
.venv\Scripts\activate
# On macOS / Linux:
source .venv/bin/activate

# 3. Install dependencies
uv sync
```

The key dependencies for this project:

| Package | Purpose |
|---------|---------|
| `google-adk` | Google Agent Development Kit — SequentialAgent, LlmAgent, Runner |
| `litellm` | Unified LLM API gateway (routes to Anthropic, OpenAI, Google, etc.) |
| `yfinance` | Free, real-time stock data from Yahoo Finance |
| `python-dotenv` | Loads API keys from a `.env` file |
| `rich` | Beautiful terminal output (Markdown rendering, colour) |
| `streamlit` | Web UI framework for the GUI front-end |
| `fastapi` | HTTP framework powering the agent service endpoint |
| `uvicorn` | ASGI server that runs the FastAPI service |
| `requests` | HTTP client used by `main.py` and `streamlit_app.py` to call the service |
| `nest-asyncio` | Allows nested `asyncio` calls (kept for compatibility) |

### API Keys

Create a `.env` file in the project root with your API keys:

```bash
ANTHROPIC_API_KEY=sk-ant-...your-key-here...
# Optional — only if you want to use OpenAI or Google models
GOOGLE_API_KEY=...
OPENAI_API_KEY=...
# Optional — override the default agent service URL
HOST_AGENT_URL=http://localhost:8000/run
```

The application validates on startup that `ANTHROPIC_API_KEY` is present.

---

### Project File Structure

```
buffet_stock_analyser/
├── .env                              # API keys (not committed to git)
├── main.py                           # CLI entry point (HTTP client → agent service)
├── streamlit_app.py                  # Streamlit GUI entry point (HTTP client → agent service)
├── servers.sh                        # Bash helper script (Linux / macOS / Git Bash)
├── servers.ps1                       # PowerShell helper script (Windows)
├── utils.py                          # Data fetching (yfinance)
├── logger.py                         # Logging setup (Rich console + rotating file)
├── logs/                             # Auto-generated log files
│
└── buffet_bot/                       # The ADK agent package
    ├── __init__.py
    ├── common/
    │   └── a2a_server.py             # Reusable FastAPI app factory (create_app)
    └── agents/
        ├── __init__.py
        ├── __main__.py               # FastAPI/Uvicorn entry point (app on :8000)
        ├── agent.py                  # SequentialAgent definition + execute() coroutine
        ├── task_manager.py           # Bridges FastAPI → execute()
        └── subagents/
            ├── analyst_agent/
            │   ├── __init__.py
            │   ├── agent.py          # LlmAgent — Buffett-style financial analysis
            │   └── prompt.py         # ANALYST_PROMPT template
            └── reporter_agent/
                ├── __init__.py
                ├── agent.py          # LlmAgent — Markdown report generation
                └── prompt.py         # REPORTER_PROMPT template
```

**Design rationale:**

- **Service separation.** The ADK agent pipeline is no longer imported directly into the front-end scripts. It runs as an independent FastAPI service, meaning you can swap, scale, or redeploy the agent layer without touching `main.py` or `streamlit_app.py`.
- **Mirrored front-ends.** `main.py` (CLI) and `streamlit_app.py` (web) both follow the same pattern: fetch data → build payload → POST to `HOST_AGENT_URL` → render response. Neither imports any ADK code directly.
- **Separation of prompts from agent definitions.** Each sub-agent has its own `prompt.py`. This makes it trivial to iterate on prompt engineering without touching any infrastructure code.
- **Flat utility layer.** Data fetching (`utils.py`) and logging (`logger.py`) sit at the project root — they are shared across both the CLI and Streamlit entry points.

---

## How to Run the Application

Running the application is now a **two-step process**: first start the agent service, then run your chosen front-end.

### Step 1 — Start the Agent Service

There are three ways to start the service depending on your OS/shell:

**Linux / macOS / WSL / Git Bash** — use `servers.sh`:

```bash
chmod u+x servers.sh   # first time only
./servers.sh
```

**Windows PowerShell (native)** — use `servers.ps1`:

```powershell
.\servers.ps1
```

> **Execution policy note:** If PowerShell refuses to run the script, allow local scripts once with:
> ```powershell
> Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
> ```

**Universal fallback (any OS, any shell):**

```bash
uvicorn buffet_bot.agents.__main__:app --port 8000
```

All three options start the FastAPI agent service at `http://localhost:8000`. Keep this terminal open and press **Ctrl+C** when you want to stop.

### Option 1 — CLI Mode

In a second terminal:

```bash
uv run main.py
```

You'll be prompted:

```
Enter Stock Symbol (e.g., TSLA, GOOGL) or exit to quit:
```

Type a ticker (say `AAPL`) and press Enter. `main.py` fetches live data, POSTs it to the agent service, and renders the returned Markdown report in the terminal using Rich:

```python
# main.py — core loop (simplified)
async def main():
    while True:
        symbol = input(...).strip().upper()
        if symbol.lower() == "exit":
            break

        company_info, raw_financials = get_stock_info(symbol)
        payload = {"symbol": symbol, "company_info": company_info, "raw_financials": raw_financials}

        response = requests.post(HOST_AGENT_URL, json=payload)
        if response.ok:
            data = response.json()["formatted_report"]
            console.print(Markdown(data["analysis_report"]))
```

### Option 2 — Streamlit GUI

In a second terminal:

```bash
streamlit run streamlit_app.py
```

This launches a web UI. `streamlit_app.py` mirrors `main.py` exactly — the only difference is the front-end: instead of `console.print`, it uses `st.markdown` to render the report. No ADK imports, no `asyncio`, no `nest_asyncio` needed:

```python
# streamlit_app.py — key section
response = requests.post(HOST_AGENT_URL, json=payload, timeout=120)
if response.ok:
    data = response.json().get("formatted_report", {})
    st.markdown(data.get("analysis_report"))
```

> **Why no `nest_asyncio` anymore?** The old Streamlit app had to apply `nest_asyncio.apply()` because it called ADK's `asyncio`-based runner directly inside Streamlit's own event loop. Now that the agent runs in a separate process (the FastAPI server), `streamlit_app.py` makes a plain synchronous `requests.post()` call — no event loop conflicts, no workaround needed.

---

## Conclusion

We've built a fully functional, agentic stock analyser that applies Warren Buffett's core value-investing criteria — ROE, Debt/Equity, Economic Moat, DCF Intrinsic Value, and Margin of Safety — to any publicly traded stock.

**What makes this approach interesting:**

- **Service-oriented agent deployment.** The ADK pipeline runs as a standalone FastAPI/Uvicorn service. Both the CLI and the Streamlit web app are thin HTTP clients — they know nothing about ADK, sessions, or runners. This is the same pattern used in production multi-agent systems.
- **Agent separation of concerns.** The analyst *thinks*; the reporter *writes*. Neither knows about the other's internals. You can upgrade, swap, or fine-tune each independently.
- **Google ADK's `SequentialAgent`** handles orchestration without needing its own LLM. It's a free, deterministic pipeline coordinator.
- **State-driven data flow.** Session state acts as a shared blackboard. Agents read inputs and write outputs via named keys — no explicit message passing, no serialisation boilerplate.
- **Model-agnostic via LiteLlm.** Changing from Claude to GPT-4o or Gemini is a one-line change: `LiteLlm(model="openai/gpt-4o")`.

The full code is available on GitHub. Clone it, add your API key, start the service, and start analysing stocks the Buffett way — one agent at a time. 🚀

---

*If you enjoyed this post, follow me for more on agentic AI, financial engineering, and building practical AI-powered tools with Google ADK.*
