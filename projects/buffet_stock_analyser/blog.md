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
Otherwise                                   →  Avoid
```

Our goal is to build an **agentic AI application** that ingests real-time financial data for any publicly-traded stock, applies the five criteria above, and produces an investor-grade Markdown report — all orchestrated by **Google ADK** (Agent Development Kit).

---

## Google ADK Implementation

### High-Level Architecture

The application follows a classic **pipeline** (sequential) pattern:

```
User Input (Ticker Symbol)
        │
        ▼
  ┌──────────────┐
  │  yfinance    │  ← Fetch live financial data
  │  data pull   │
  └─────┬────────┘
        │  company_info + raw_financials
        ▼
  ┌────────────────────────────────────────────┐
  │  SequentialAgent  (buffett_stock_analysis) │
  │                                            │
  │   ┌───────────────┐   ┌─────────────────┐  │
  │   │ analyst_agent │──▶│ reporter_agent  │  │
  │   └───────────────┘   └─────────────────┘  │
  └────────────────────────────────────────────┘
        │
        ▼
  Final Markdown Report
```

1. **Data ingestion** — We pull live market data from Yahoo Finance via `yfinance`.
2. **Analysis** — The `analyst_agent` (an LLM-backed agent) applies Buffett's five criteria.
3. **Reporting** — The `reporter_agent` takes the raw analysis and polishes it into a professional Markdown report.

Both agents run sequentially inside a Google ADK `SequentialAgent`, which guarantees ordered execution and passes shared state from one agent to the next.

---

### Step 1 — Downloading & Preparing Financial Data

All data fetching lives in `utils.py`. We use `yfinance` to pull a stock's `info` dictionary and then slice it into two clean dictionaries that will be injected into the agent session state:

```python
import yfinance as yf

def get_stock_info(symbol: str) -> (dict, dict):
    """Extracts company info and raw financial metrics for a given ticker."""
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

### Step 2 — The SequentialAgent Orchestrator

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

The pipeline is simple:

1. `analyst_agent` reads `symbol`, `company_info`, and `raw_financials` from session state, performs the Buffett analysis, and writes its output to the state key `investment_reasoning`.
2. `reporter_agent` reads everything — including `investment_reasoning` — and produces the final polished report, stored under `final_markdown_report`.

This clean separation of concerns means you can swap out either agent independently. For example, you could replace the analyst with a tool-calling agent that runs its own DCF calculation in Python, without touching the reporter.

---

### Step 3 — The Analyst Agent

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

### Step 4 — The Reporter Agent

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

Here `{investment_reasoning}` is the output from the previous analyst step — ADK resolves it from session state automatically. The final report is written to `final_markdown_report` in state.

---

### Step 5 — Running the Agent Pipeline

The `run_agent_query` helper in `utils.py` wires everything together using ADK's `Runner`:

```python
from google.adk.runners import Runner
from google.genai import types

async def run_agent_query(agent, session_service, app_name,
                          user_id, user_query, session):
    runner = Runner(
        agent=agent,
        session_service=session_service,
        app_name=app_name,
    )

    user_content = types.Content(
        role="user",
        parts=[types.Part.from_text(text=user_query)],
    )

    async for event in runner.run_async(
        user_id=user_id,
        session_id=session.id,
        new_message=user_content,
    ):
        if event.is_final_response():
            if event.content and event.content.parts:
                return event.content.parts[0].text
```

The `Runner` streams events from the agent pipeline. We iterate until we hit the **final response event**, which contains the reporter's polished Markdown. This is the text we render to the user.

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
uv pip install -r requirements.txt
# or, if using pyproject.toml:
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
| `nest-asyncio` | Allows nested `asyncio.run()` calls inside Streamlit's own event loop |

### API Keys

Create a `.env` file in the project root with your API keys:

```bash
ANTHROPIC_API_KEY=sk-ant-...your-key-here...
# Optional — only if you want to use OpenAI or Google models
GOOGLE_API_KEY=...
OPENAI_API_KEY=...
```

The application validates on startup that `ANTHROPIC_API_KEY` is present.

---

### Project File Structure

```
buffet_stock_analyser/
├── .env                          # API keys (not committed to git)
├── main.py                       # CLI entry point
├── streamlit_app.py              # Streamlit GUI entry point
├── utils.py                      # Data fetching (yfinance) + agent runner helper
├── logger.py                     # Logging setup (Rich console + rotating file)
├── logs/                         # Auto-generated log files
│
└── buffet_bot/                   # The ADK agent package
    ├── __init__.py
    ├── agent.py                  # Root SequentialAgent definition
    │
    └── subagents/
        ├── analyst_agent/
        │   ├── __init__.py
        │   ├── agent.py          # LlmAgent — Buffett-style financial analysis
        │   └── prompt.py         # ANALYST_PROMPT template
        │
        └── reporter_agent/
            ├── __init__.py
            ├── agent.py          # LlmAgent — Markdown report generation
            └── prompt.py         # REPORTER_PROMPT template
```

**Design rationale:**

- **Separation of prompts from agent definitions.** Each sub-agent has its own `prompt.py`. This makes it trivial to iterate on prompt engineering without touching any infrastructure code.
- **Flat utility layer.** Data fetching (`utils.py`) and logging (`logger.py`) sit at the project root — they are shared across both the CLI and Streamlit entry points.
- **ADK conventions.** The `buffet_bot/` package follows the standard ADK project layout: a root `agent.py` that exports `root_agent`, with sub-agents nested under `subagents/`.

---

## How to Run the Application

### Option 1 — CLI Mode

The CLI interface is in `main.py`. It runs an interactive loop: enter a ticker, get a report, repeat.

```bash
uv run main.py
```

You'll be prompted:

```
Enter Stock Symbol (e.g., TSLA, GOOGL) or exit to quit:
```

Type a ticker (say `AAPL`) and press Enter. The agent pipeline will fetch data, run the analysis, and render the final Markdown report directly in your terminal using Rich:

```python
# main.py — core loop (simplified)
async def main():
    console = Console()
    session_service = InMemorySessionService()
    app_name = Path(__file__).parent.resolve().name
    user_id = "buffet_analyst_007"
    session_id = str(uuid.uuid4())

    while True:
        symbol = input("Enter Stock Symbol: ").strip().upper()
        if symbol.lower() == "exit":
            break

        company_info, raw_financials = get_stock_info(symbol)
        initial_state = {
            "symbol": symbol,
            "company_info": company_info,
            "raw_financials": raw_financials,
        }

        # Create or reuse session
        my_session = await session_service.get_session(...)
        if my_session is None:
            my_session = await session_service.create_session(
                ..., state=initial_state
            )
        else:
            my_session.state = initial_state

        final_report = await run_agent_query(
            agent=workflow, ..., user_query=f"Analyse the stock {symbol}",
            session=my_session,
        )

        console.print(Markdown(final_report))
```

**Session management note:** The CLI reuses the same `session_id` across iterations. On the first run, a new `InMemorySession` is created. On subsequent runs within the same loop, the existing session's state is updated with the new ticker's data, avoiding redundant session creation.

---

### Option 2 — Streamlit GUI

For a more polished experience, there's a Streamlit front-end:

```bash
streamlit run streamlit_app.py
```

This launches a web UI with:

- A **text input** for the ticker symbol (defaults to `AAPL`).
- An **"Analyze Stock"** button that triggers the pipeline.
- A **live status indicator** ("Agents are working…") while the analysis runs.
- The final **Markdown report rendered beautifully** in the browser.

```python
# streamlit_app.py — key section
import nest_asyncio
nest_asyncio.apply()  # Required: Streamlit already runs an event loop

st.title("💰 Buffett-Bot: Agentic Value Analyst")
symbol = st.text_input("Enter Ticker Symbol", value="AAPL").strip().upper()

if st.button("Analyze Stock"):
    with st.status("Agents are working...", expanded=True) as status:
        async def run_ui():
            company_info, raw_financials = get_stock_info(symbol)
            my_session = await session_service.create_session(
                ..., state={"symbol": symbol, "company_info": company_info,
                            "raw_financials": raw_financials}
            )
            return await run_agent_query(
                agent=workflow, ..., user_query=f"Analyse the stock {symbol}",
                session=my_session,
            )

        final_report = asyncio.run(run_ui())
        status.update(label="Analysis Complete!", state="complete")

    st.markdown(final_report)
```

> **Why `nest_asyncio`?** Streamlit internally manages its own `asyncio` event loop. Calling `asyncio.run()` from within a Streamlit callback would normally raise `RuntimeError: This event loop is already running`. The `nest_asyncio.apply()` call patches the loop to allow nested runs — a clean one-liner fix.

---

## Conclusion

We've built a fully functional, agentic stock analyser that applies Warren Buffett's core value-investing criteria — ROE, Debt/Equity, Economic Moat, DCF Intrinsic Value, and Margin of Safety — to any publicly traded stock.

**What makes this approach interesting:**

- **Agent separation of concerns.** The analyst *thinks*; the reporter *writes*. Neither knows about the other's internals. You can upgrade, swap, or fine-tune each independently.
- **Google ADK's `SequentialAgent`** handles orchestration without needing its own LLM. It's a free, deterministic pipeline coordinator.
- **State-driven data flow.** Session state acts as a shared blackboard. Agents read inputs and write outputs via named keys — no explicit message passing, no serialisation boilerplate.
- **Model-agnostic via LiteLlm.** Changing from Claude to GPT-4o or Gemini is a one-line change: `LiteLlm(model="openai/gpt-4o")`.

The full code is available on GitHub. Clone it, add your API key, and start analysing stocks the Buffett way — one agent at a time. 🚀

---

*If you enjoyed this post, follow me for more on agentic AI, financial engineering, and building practical AI-powered tools with Google ADK.*
