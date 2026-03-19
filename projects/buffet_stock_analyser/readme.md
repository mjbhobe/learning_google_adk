# 💰 Buffett-Bot: Agentic Value Stock Analyser

An agentic AI application that applies **Warren Buffett's value-investing criteria** to any publicly traded stock and generates an investor-grade Markdown report — powered by **Google ADK** and **Claude 4.6 Sonnet**.

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

## Agent Architecture

The app uses a **Google ADK `SequentialAgent`** pipeline with two LLM-backed sub-agents:

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
- **`analyst_agent`** — Receives company info and raw financials from session state. Performs ROE, D/E, moat, DCF, and margin-of-safety analysis. Writes output to session key `investment_reasoning`.
- **`reporter_agent`** — Reads all prior state (financials + analysis) and produces a well-formatted Markdown report with metrics table, qualitative analysis, and a final recommendation. Writes to `final_markdown_report`.

Both agents use **Claude 4.6 Sonnet** via ADK's `LiteLlm` wrapper.

---

## Project Structure

```
buffet_stock_analyser/
├── .env                                    # API keys (not committed to git)
├── main.py                                 # CLI entry point — interactive ticker loop
├── streamlit_app.py                        # Streamlit GUI entry point
├── utils.py                                # yfinance data fetcher + ADK Runner helper
├── logger.py                               # Logging config (Rich console + rotating file)
├── logs/                                   # Auto-generated log files
│
└── buffet_bot/                             # ADK agent package
    ├── __init__.py                         # Package init — imports agent module
    ├── agent.py                            # Root SequentialAgent (orchestrates sub-agents)
    └── subagents/
        ├── analyst_agent/
        │   ├── __init__.py
        │   ├── agent.py                    # LlmAgent — Buffett-style financial analysis
        │   └── prompt.py                   # Analyst prompt template with Buffett criteria
        └── reporter_agent/
            ├── __init__.py
            ├── agent.py                    # LlmAgent — Markdown report generation
            └── prompt.py                   # Reporter prompt template with report layout
```

---

## Environment Setup

**Prerequisites:** Python ≥ 3.14, [uv](https://docs.astral.sh/uv/)

```bash
# 1. Clone the repo and navigate to the project
git clone https://github.com/<your-username>/learning_google_adk.git
cd learning_google_adk/projects/buffet_stock_analyser

# 2. Create and activate a virtual environment
uv venv
# Windows:
.venv\Scripts\activate
# macOS / Linux:
source .venv/bin/activate

# 3. Install dependencies
uv pip install google-adk litellm yfinance python-dotenv rich streamlit nest-asyncio
```

### API Keys

Create a `.env` file in the `buffet_stock_analyser/` directory:

```bash
ANTHROPIC_API_KEY=sk-ant-...your-key-here...
```

The app validates on startup that `ANTHROPIC_API_KEY` is set.

---

## Running the Application

### CLI Mode

```bash
uv run main.py
```

Enter a ticker symbol (e.g. `TSLA`, `GOOGL`) at the prompt. The agent pipeline will fetch live data, run the analysis, and render the Markdown report in your terminal. Type `exit` to quit.

### Streamlit GUI

```bash
streamlit run streamlit_app.py
```

Opens a web UI where you enter a ticker, click **"Analyze Stock"**, and view the final report rendered in the browser.
